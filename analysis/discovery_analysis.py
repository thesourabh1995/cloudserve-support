"""Stage 1 discovery analysis.

Produces the evidence tables for the discovery workbook from the development
ticket set and the knowledge base, and checks the factual claims made in the
stakeholder interviews against the data.

Standard library only, so it runs before the project dependencies are installed.

    python -m analysis.discovery_analysis --tickets data/development_tickets.json \
                                          --docs data/documentation.json \
                                          --output docs/discovery_findings.md
"""

import argparse
import json
import statistics
from collections import Counter, defaultdict


def load(path):
    with open(path) as handle:
        return json.load(handle)


def pct(part, whole):
    return 0.0 if whole == 0 else 100.0 * part / whole


def share_table(counter, total, first_column):
    """Render a Counter as a markdown table ordered by descending count."""
    lines = [f"| {first_column} | Tickets | Share |", "|---|---:|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key} | {count} | {pct(count, total):.1f}% |")
    return "\n".join(lines)


def volume_by_channel(tickets):
    counts = Counter(t["channel"] for t in tickets)
    return share_table(counts, len(tickets), "Channel")


def answerable_by_channel(tickets):
    """How much of each channel's volume already has an answer in the docs.

    This is the central discovery question: if the answers already exist, the
    problem is delivery rather than knowledge.
    """
    totals = Counter()
    answerable = Counter()
    for ticket in tickets:
        channel = ticket["channel"]
        totals[channel] += 1
        if ticket["labels"]["answerable_from_docs"]:
            answerable[channel] += 1

    lines = ["| Channel | Tickets | Answerable from docs | Share |", "|---|---:|---:|---:|"]
    for channel, total in totals.most_common():
        lines.append(
            f"| {channel} | {total} | {answerable[channel]} | {pct(answerable[channel], total):.1f}% |"
        )
    overall = sum(answerable.values())
    lines.append(f"| **All channels** | **{len(tickets)}** | **{overall}** | "
                 f"**{pct(overall, len(tickets)):.1f}%** |")
    return "\n".join(lines)


def intent_breakdown(tickets):
    """Intent distribution with the two facts that drive routing design."""
    totals = Counter()
    answerable = Counter()
    escalate = Counter()
    never_auto = set()

    for ticket in tickets:
        labels = ticket["labels"]
        intent = labels["intent"]
        totals[intent] += 1
        if labels["answerable_from_docs"]:
            answerable[intent] += 1
        if labels["expected_route"] == "escalate":
            escalate[intent] += 1
        if labels["must_not_auto_respond"]:
            never_auto.add(intent)

    lines = [
        "| Intent | Tickets | Share | Answerable | Expected escalation | Never auto-respond |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for intent, count in totals.most_common():
        lines.append(
            f"| {intent} | {count} | {pct(count, len(tickets)):.1f}% | "
            f"{pct(answerable[intent], count):.0f}% | "
            f"{pct(escalate[intent], count):.0f}% | "
            f"{'yes' if intent in never_auto else ''} |"
        )
    return "\n".join(lines), sorted(never_auto)


def historical_baseline(tickets):
    """What happened when humans handled these tickets. This is the baseline
    every business metric in the evaluation is measured against."""
    history = [t["history"] for t in tickets]
    resolution_times = [h["resolution_time_minutes"] for h in history]
    ratings = [h["csat_rating"] for h in history]

    rows = [
        ("Tickets in set", f"{len(tickets)}"),
        ("First contact resolution",
         f"{pct(sum(1 for h in history if h['first_contact_resolution']), len(history)):.1f}%"),
        ("Escalation rate",
         f"{pct(sum(1 for h in history if h['escalated']), len(history)):.1f}%"),
        ("Repeat contact rate",
         f"{pct(sum(1 for h in history if h['repeat_contact']), len(history)):.1f}%"),
        ("Mean resolution time", f"{statistics.mean(resolution_times):.0f} min"),
        ("Median resolution time", f"{statistics.median(resolution_times):.0f} min"),
        ("Mean CSAT", f"{statistics.mean(ratings):.2f} / 5"),
    ]
    lines = ["| Measure | Value |", "|---|---:|"]
    lines += [f"| {name} | {value} |" for name, value in rows]
    return "\n".join(lines)


def segment_table(tickets, field, label):
    """Outcome quality split by a customer attribute.

    Used twice: as discovery evidence now, and as the starting point for the
    fairness audit later, which asks for under five points of variation.
    """
    groups = defaultdict(list)
    for ticket in tickets:
        groups[ticket[field]].append(ticket)

    lines = [
        f"| {label} | Tickets | FCR | Mean CSAT | Median resolution |",
        "|---|---:|---:|---:|---:|",
    ]
    rates = {}
    for key, group in sorted(groups.items(), key=lambda item: -len(item[1])):
        history = [t["history"] for t in group]
        fcr = pct(sum(1 for h in history if h["first_contact_resolution"]), len(history))
        rates[key] = fcr
        csat = statistics.mean(h["csat_rating"] for h in history)
        median_time = statistics.median(h["resolution_time_minutes"] for h in history)
        lines.append(f"| {key} | {len(group)} | {fcr:.1f}% | {csat:.2f} | {median_time:.0f} min |")

    spread = max(rates.values()) - min(rates.values())
    lines.append(f"\nSpread between best and worst group: **{spread:.1f} percentage points**.")
    return "\n".join(lines)


def check_interview_claims(tickets):
    """Settle the factual disagreements in the transcripts against the data.

    The Stage 1 workbook asks for claims to be resolved with evidence rather
    than by deciding whose account sounds more convincing.
    """
    history = [t["history"] for t in tickets]
    answerable = sum(1 for t in tickets if t["labels"]["answerable_from_docs"])

    escalated = [t for t in tickets if t["history"]["escalated"]]
    avoidable = [t for t in escalated if t["labels"]["answerable_from_docs"]]

    by_fluency = defaultdict(list)
    for ticket in tickets:
        by_fluency[ticket["language_fluency"]].append(ticket["history"]["csat_rating"])

    by_tier = defaultdict(list)
    tier_within_hour = defaultdict(list)
    for ticket in tickets:
        minutes = ticket["history"]["resolution_time_minutes"]
        by_tier[ticket["customer_tier"]].append(minutes)
        tier_within_hour[ticket["customer_tier"]].append(minutes <= 60)

    fcr_rate = pct(sum(1 for h in history if h["first_contact_resolution"]), len(history))
    answerable_rate = pct(answerable, len(tickets))
    avoidable_rate = pct(len(avoidable), len(escalated))
    fluent_csat = statistics.mean(by_fluency["fluent"])
    non_fluent_csat = statistics.mean(by_fluency["non_fluent"])
    enterprise_hour = pct(
        sum(tier_within_hour["enterprise"]), len(tier_within_hour["enterprise"])
    )

    # Each verdict is derived from the figure beside it rather than typed in, so
    # that a claim cannot be recorded as settled against a number that moved.
    claims = [
        ("Sofia: 'seven out of ten I could answer without looking anything up'",
         f"{answerable_rate:.1f}% of tickets are answerable from the "
         f"knowledge base ({answerable} of {len(tickets)})",
         "supported" if 65 <= answerable_rate <= 75 else "not supported"),
        ("Daniel: 'about half of what reaches me tier one could have resolved'",
         f"{avoidable_rate:.1f}% of escalated tickets "
         f"({len(avoidable)} of {len(escalated)}) were answerable from the docs",
         "supported" if 40 <= avoidable_rate <= 60 else "not supported"),
        ("Marcus: 'we are at forty-two per cent' first contact resolution",
         f"{fcr_rate:.1f}% in this sample",
         "supported" if abs(fcr_rate - 42) <= 3 else "not supported"),
        ("Sofia: non-fluent English tickets 'have our worst satisfaction scores'",
         "; ".join(f"{name}: {statistics.mean(values):.2f}"
                   for name, values in sorted(by_fluency.items())),
         "contradicted" if non_fluent_csat >= fluent_csat else "supported"),
        ("Ravi: enterprise customers 'get answers in about an hour'",
         "; ".join(f"{name}: {statistics.median(values):.0f} min median"
                   for name, values in sorted(by_tier.items()))
         + f"; {enterprise_hour:.0f}% of enterprise tickets resolved within the hour",
         "contradicted" if statistics.median(by_tier["enterprise"])
         > statistics.median(by_tier["business"]) else "supported"),
    ]

    lines = ["| Claim | What the data shows | Verdict |", "|---|---|---|"]
    lines += [f"| {claim} | {evidence} | {verdict} |" for claim, evidence, verdict in claims]
    return "\n".join(lines)


def documentation_coverage(tickets, docs):
    """Which articles the tickets actually need, and which are never cited.

    Ines believes the articles are good but unfindable. If some are never the
    expected answer, that is a content gap rather than a retrieval problem.
    """
    cited = Counter()
    for ticket in tickets:
        for doc_id in ticket["labels"]["expected_doc_ids"]:
            cited[doc_id] += 1

    by_id = {doc["doc_id"]: doc for doc in docs}
    never_cited = sorted(set(by_id) - set(cited))

    lines = ["| Article | Title | Tickets needing it |", "|---|---|---:|"]
    for doc_id, count in cited.most_common(10):
        doc = by_id.get(doc_id, {})
        lines.append(f"| {doc_id} | {doc.get('title', 'unknown')} | {count} |")

    summary = [
        f"\nKnowledge base holds **{len(docs)} articles**. "
        f"**{len(cited)}** are the expected source for at least one ticket.",
    ]
    if never_cited:
        summary.append(f"Never cited as an expected source: {', '.join(never_cited)}.")

    review_ages = {d.get("last_reviewed_days_ago") for d in docs}
    if review_ages == {0}:
        summary.append(
            "Every article was reviewed within the current cycle, so the knowledge base "
            "itself is not stale. Daniel's warning about answers that were correct two "
            "years ago therefore applies to the agents' unreviewed private snippet files, "
            "not to these articles — evidence for retrieving from the knowledge base "
            "rather than learning from past agent replies."
        )
    return "\n".join(lines) + "\n" + "\n".join(summary)


def build_report(tickets, docs):
    intents, never_auto = intent_breakdown(tickets)
    sections = [
        "# Stage 1 — Discovery findings",
        "",
        f"Generated from {len(tickets)} development tickets and {len(docs)} "
        "knowledge base articles by `analysis/discovery_analysis.py`.",
        "",
        "## 1. Where the volume comes from",
        "",
        volume_by_channel(tickets),
        "",
        "## 2. How much of it is already answered in the documentation",
        "",
        answerable_by_channel(tickets),
        "",
        "## 3. What the tickets are about",
        "",
        intents,
        "",
        f"Intents that must never be answered automatically: "
        f"{', '.join(never_auto) if never_auto else 'none'}.",
        "",
        "## 4. The human baseline",
        "",
        historical_baseline(tickets),
        "",
        "## 5. Outcomes by customer group",
        "",
        segment_table(tickets, "customer_tier", "Customer tier"),
        "",
        segment_table(tickets, "language_fluency", "Language fluency"),
        "",
        segment_table(tickets, "customer_region", "Region"),
        "",
        "## 6. Interview claims checked against the data",
        "",
        check_interview_claims(tickets),
        "",
        "## 7. Documentation coverage",
        "",
        documentation_coverage(tickets, docs),
    ]
    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tickets", default="data/development_tickets.json")
    parser.add_argument("--docs", default="data/documentation.json")
    parser.add_argument("--output", default="docs/discovery_findings.md")
    args = parser.parse_args()

    report = build_report(load(args.tickets), load(args.docs))
    with open(args.output, "w") as handle:
        handle.write(report + "\n")
    print(report)
    print(f"\nWritten to {args.output}")


if __name__ == "__main__":
    main()
