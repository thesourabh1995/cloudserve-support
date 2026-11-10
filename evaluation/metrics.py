"""Figures the harness must produce on its own.

The groups are the ones the build specification requires: volume, business,
technical and governance. A figure that needs labels is reported as
unavailable when the file has none, which is what the hidden set may look
like to the system while it is running. Labels are read here, after every
ticket has been decided, and never by the pipeline.
"""

import statistics


def _ratio(numerator: int, denominator: int):
    if denominator == 0:
        return None
    return numerator / denominator


def _percentile(values: list[float], fraction: float):
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


def _label(labels: dict, ticket_id: str) -> dict:
    entry = labels.get(ticket_id) or {}
    inner = entry.get("labels")
    return inner if isinstance(inner, dict) else {}


def summarise(rows: list[dict], labels: dict | None = None) -> dict:
    """Turn one row per ticket into the report.

    Each row carries the decision the pipeline already made: final_action,
    latency_seconds, intent, confidence, retrieved_doc_ids, citations_offered,
    citations_resolved, guardrail findings, and the customer group fields.
    """
    labels = labels or {}
    total = len(rows)
    answered = sum(1 for row in rows if row["final_action"] == "auto_respond")
    escalated = sum(1 for row in rows if row["final_action"] == "escalate")
    blocked = sum(1 for row in rows if row["final_action"] == "blocked")

    activations: dict[str, int] = {}
    outbound_private = 0
    for row in rows:
        for finding in row.get("findings") or []:
            if finding.get("blocked"):
                activations[finding["check"]] = activations.get(finding["check"], 0) + 1
        if row["final_action"] == "auto_respond" and any(
            finding.get("check") == "private_data" and finding.get("blocked")
            for finding in row.get("findings") or []
        ):
            outbound_private += 1

    reply_times = [row["latency_seconds"] for row in rows if row["final_action"] == "auto_respond"]
    all_times = [row["latency_seconds"] for row in rows if row.get("latency_seconds") is not None]

    citations_offered = sum(row.get("citations_offered", 0) for row in rows)
    citations_resolved = sum(row.get("citations_resolved", 0) for row in rows)

    report = {
        "volume": {
            "tickets_processed": total,
            "answered_automatically": answered,
            "escalated": escalated,
            "blocked_by_guardrails": blocked,
        },
        "business": {
            "first_contact_resolution": _ratio(answered, total),
            "escalation_rate": _ratio(escalated + blocked, total),
            "reply_time_seconds": _timing(reply_times),
        },
        "technical": {
            "latency_seconds": _timing(all_times),
            "citation_accuracy": _ratio(citations_resolved, citations_offered),
            "citations_offered": citations_offered,
            "citations_resolved": citations_resolved,
        },
        "governance": {
            "decisions_logged": sum(1 for row in rows if row.get("logged")),
            "log_complete": total > 0 and all(row.get("logged") for row in rows) and sum(1 for row in rows if row.get("logged")) == total,
            "guardrail_activations": activations,
            "private_data_in_outbound_replies": outbound_private,
        },
    }

    paired = [(row, _label(labels, row["ticket_id"])) for row in rows]
    paired = [(row, label) for row, label in paired if label.get("intent")]
    if paired:
        report["technical"]["classification"] = _classification(paired)
        report["technical"]["retrieval_hit_rate"] = _retrieval(paired)
        report["governance"]["confidence_calibration"] = _calibration(paired)
    else:
        report["technical"]["classification"] = None
        report["technical"]["retrieval_hit_rate"] = None
        report["governance"]["confidence_calibration"] = None

    report["governance"]["quality_by_group"] = _groups(rows, labels)
    return report


def _timing(values: list[float]) -> dict:
    if not values:
        return {"mean": None, "median": None, "p95": None, "n": 0}
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p95": _percentile(values, 0.95),
        "n": len(values),
    }


def _classification(paired: list[tuple]) -> dict:
    classes = sorted({label["intent"] for _, label in paired} | {row["intent"] for row, _ in paired})
    per_class = {}
    correct = 0
    for name in classes:
        tp = sum(1 for row, label in paired if row["intent"] == name and label["intent"] == name)
        fp = sum(1 for row, label in paired if row["intent"] == name and label["intent"] != name)
        fn = sum(1 for row, label in paired if row["intent"] != name and label["intent"] == name)
        correct += tp
        per_class[name] = {
            "precision": _ratio(tp, tp + fp),
            "recall": _ratio(tp, tp + fn),
            "support": tp + fn,
        }
    return {
        "accuracy": _ratio(correct, len(paired)),
        "per_class": per_class,
        "evaluated": len(paired),
    }


def _retrieval(paired: list[tuple]) -> dict:
    eligible = [
        (row, label)
        for row, label in paired
        if label.get("expected_doc_ids")
    ]
    hits = 0
    for row, label in eligible:
        found = set(row.get("retrieved_doc_ids") or [])
        if found & set(label["expected_doc_ids"]):
            hits += 1
    return {"hit_rate": _ratio(hits, len(eligible)), "eligible": len(eligible), "hits": hits}


def _calibration(paired: list[tuple]) -> list[dict]:
    """Stated confidence against accuracy, in bands of 0.2."""
    bands = []
    for start in (0.0, 0.2, 0.4, 0.6, 0.8):
        group = [
            (row, label)
            for row, label in paired
            if start <= float(row.get("confidence") or 0) < start + 0.2 or (start == 0.8 and float(row.get("confidence") or 0) == 1.0)
        ]
        if not group:
            continue
        stated = statistics.fmean(float(row["confidence"]) for row, _ in group)
        observed = sum(1 for row, label in group if row["intent"] == label["intent"]) / len(group)
        bands.append({
            "from": start,
            "to": round(start + 0.2, 1),
            "n": len(group),
            "stated_confidence": stated,
            "observed_accuracy": observed,
            "gap": stated - observed,
        })
    return bands


def _groups(rows: list[dict], labels: dict) -> dict:
    """Automatic-answer rate by customer group, and the spread between groups.

    The governance condition is under five percentage points. A spread on a
    handful of tickets is reported, and it is not a verdict.
    """
    result = {}
    for field in ("customer_tier", "customer_region", "language_fluency"):
        buckets: dict[str, list] = {}
        for row in rows:
            buckets.setdefault(row.get(field) or "unknown", []).append(row)
        rates = {}
        for name, members in sorted(buckets.items()):
            rates[name] = {
                "n": len(members),
                "first_contact_resolution": _ratio(
                    sum(1 for row in members if row["final_action"] == "auto_respond"),
                    len(members),
                ),
            }
        figures = [item["first_contact_resolution"] for item in rates.values() if item["n"] and item["first_contact_resolution"] is not None]
        spread = (max(figures) - min(figures)) if len(figures) >= 2 else None
        result[field] = {"groups": rates, "spread": spread}
    return result


def _pct(value) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _seconds(value) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}s"


def render_markdown(report: dict) -> str:
    """The results table the evaluation framework asks the run to produce."""
    volume = report["volume"]
    business = report["business"]
    technical = report["technical"]
    governance = report["governance"]
    reply = business["reply_time_seconds"]
    latency = technical["latency_seconds"]
    classification = technical.get("classification") or {}
    accuracy = classification.get("accuracy") if classification else None
    spread = governance["quality_by_group"]["customer_tier"]["spread"]

    lines = [
        "# Evaluation run",
        "",
        "Produced by the harness. Figures that need a labelled file are marked n/a when the input had no labels.",
        "",
        "| Measure | Baseline | Target | Achieved | Notes |",
        "|---|---|---|---|---|",
        f"| First contact resolution | 42% | 60% or better | {_pct(business['first_contact_resolution'])} | Share of tickets answered with no person involved. |",
        f"| Mean time to first reply | 8 to 12 hours | Under 5 minutes | {_seconds(reply['mean'])} | Processing time of the tickets that were answered. Median {_seconds(reply['median'])}. |",
        "| Satisfaction proxy | 3.2 / 5 | 4.0 or better | n/a | Needs a human review of a sample. This run does not invent one. |",
        f"| Escalation rate | 58% | 30% or lower | {_pct(business['escalation_rate'])} | Escalated and blocked tickets. Both leave the queue for a person. |",
        f"| Classification accuracy | — | 85% precision | {_pct(accuracy)} | Per-class precision and recall are in the JSON report. |",
        "| Hallucination rate | — | 5% or lower | n/a | The framework requires two human reviewers of at least fifty replies. |",
        f"| Citation accuracy | — | 95% or better | {_pct(technical['citation_accuracy'])} | {technical['citations_resolved']} of {technical['citations_offered']} citations resolved to a retrieved passage. |",
        f"| Latency, 95th percentile | — | Under 3 seconds | {_seconds(latency['p95'])} | End to end, including retrieval and both model calls. Mean {_seconds(latency['mean'])}. |",
        f"| Private data in outbound replies | — | Zero | {governance['private_data_in_outbound_replies']} | Guardrail activations: {governance['guardrail_activations'] or 'none'}. |",
        f"| Cross-group variation, by tier | — | Under 5 points | {_pct(spread)} | Spread in automatic-answer rate across customer tiers. |",
        "",
        "## Volume",
        "",
        f"- Tickets processed: {volume['tickets_processed']}",
        f"- Answered automatically: {volume['answered_automatically']}",
        f"- Escalated: {volume['escalated']}",
        f"- Blocked by guardrails: {volume['blocked_by_guardrails']}",
        "",
        "## Governance",
        "",
        f"- Decisions logged: {governance['decisions_logged']} of {volume['tickets_processed']}",
        f"- Log reconciles: {governance['log_complete']}",
        "",
    ]
    retrieval = technical.get("retrieval_hit_rate")
    if retrieval:
        lines.append(
            f"Retrieval hit rate: {_pct(retrieval['hit_rate'])} "
            f"({retrieval['hits']} of {retrieval['eligible']} tickets with an expected document)."
        )
        lines.append("")
    return "\n".join(lines)
