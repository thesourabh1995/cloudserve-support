"""Segment the outcomes of an evaluation run and look for unequal treatment.

The Governance Framework asks whether the system serves some groups worse than
others, and sets a pass/fail condition of under five points of cross-group
variation. A single number cannot answer that, because a gap can come from the
system treating a group differently or from the groups sending different
tickets. So this reports each stage separately -- retrieval, classification and
the routing outcome -- which is what makes the two cases distinguishable.

Reads a finished run rather than calling the model, so it costs nothing to
re-run and can be pointed at any results directory.

    usage: python -m analysis.fairness_audit \
        --run evaluation/results/validation_01 \
        --tickets data/validation_tickets.json
"""

import argparse
import json
import math
import os
import sqlite3
from collections import defaultdict

# Cells smaller than this are reported but not treated as evidence. At n=8 a
# single ticket moves a rate by more than the whole pass/fail threshold.
SMALL_CELL = 15


def wilson(successes: int, total: int) -> tuple[float, float]:
    """95% confidence interval for a proportion.

    Wilson rather than the textbook normal interval because the cells here are
    small and some rates sit at 100%, where the normal interval has zero width
    and would imply a certainty the data does not support.
    """
    if total == 0:
        return (0.0, 0.0)
    z = 1.96
    p = successes / total
    denominator = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def segments(ticket: dict) -> dict:
    """The groups one ticket belongs to.

    Length is bucketed rather than reported raw because the question is whether
    terse tickets are served worse, not what the correlation coefficient is.
    """
    body = ticket.get("body") or ""
    words = len(body.split())
    if words < 20:
        length = "short (under 20 words)"
    elif words < 40:
        length = "medium (20 to 39 words)"
    else:
        length = "long (40 words or more)"
    return {
        "Customer tier": ticket.get("customer_tier"),
        "Language fluency": ticket.get("language_fluency"),
        "Region": ticket.get("customer_region"),
        "Ticket length": length,
    }


def measure(rows: list, tickets: dict) -> dict:
    """Per-segment counts for each stage of the pipeline."""
    tally = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for row in rows:
        ticket = tickets.get(row["ticket_id"])
        if ticket is None:
            continue
        labels = ticket.get("labels") or {}

        for dimension, group in segments(ticket).items():
            cell = tally[dimension][group]
            cell["n"] += 1

            if row["final_action"] == "auto_respond":
                cell["answered"] += 1

            if labels.get("intent"):
                cell["classified"] += 1
                cell["classified_right"] += row["intent"] == labels["intent"]

            expected = set(labels.get("expected_doc_ids") or [])
            if expected:
                cell["retrievable"] += 1
                cell["retrieved"] += bool(expected & set(row["retrieved_doc_ids"]))

            cell["citations_offered"] += row.get("citations_offered", 0)
            cell["citations_resolved"] += row.get("citations_resolved", 0)

    return tally


def _rate(cell: dict, hits: str, total: str) -> str:
    if not cell[total]:
        return "n/a"
    low, high = wilson(cell[hits], cell[total])
    return f"{cell[hits] / cell[total]:.0%} ({low:.0%}–{high:.0%})"


def render(tally: dict) -> str:
    lines = [
        "# Fairness audit",
        "",
        "Every figure carries a 95% confidence interval, because several of these "
        "groups are small enough that a point estimate on its own would overstate "
        "what the run shows.",
        "",
    ]

    for dimension, groups in tally.items():
        lines += [
            f"## {dimension}",
            "",
            "| Group | n | Answered automatically | Classification accuracy | Retrieval hit rate | Citations resolved |",
            "|---|---:|---|---|---|---|",
        ]
        for group, cell in sorted(groups.items(), key=lambda item: -item[1]["n"]):
            flag = " *" if cell["n"] < SMALL_CELL else ""
            lines.append(
                f"| {group}{flag} | {cell['n']} "
                f"| {_rate(cell, 'answered', 'n')} "
                f"| {_rate(cell, 'classified_right', 'classified')} "
                f"| {_rate(cell, 'retrieved', 'retrievable')} "
                f"| {_rate(cell, 'citations_resolved', 'citations_offered')} |"
            )

        spread = _spread(groups, "answered", "n")
        lines += [
            "",
            f"Spread in automatic-answer rate: **{spread:.1f} points** "
            f"(condition: under 5).",
            "",
        ]
        if any(cell["n"] < SMALL_CELL for cell in groups.values()):
            lines += [
                f"\\* Fewer than {SMALL_CELL} tickets. Reported for completeness, "
                "not relied on.",
                "",
            ]

    return "\n".join(lines)


def _spread(groups: dict, hits: str, total: str) -> float:
    rates = [
        cell[hits] / cell[total] for cell in groups.values() if cell[total]
    ]
    return (max(rates) - min(rates)) * 100 if rates else 0.0


def mechanism(rows: list, tickets: dict, log: dict) -> str:
    """Why each group escalated, and how confident the model was.

    A gap in the outcome is only unfair if the system caused it. Two things
    separate the cases: which rule fired, and whether stated confidence tracks
    accuracy within the group. Both are reported per segment so the claim in
    the audit can be checked rather than taken on trust.
    """
    lines = ["## Mechanism: which rule escalated whom", ""]

    for dimension in ("Language fluency", "Ticket length"):
        rules: dict = defaultdict(lambda: defaultdict(int))
        totals: dict = defaultdict(int)
        protected: dict = defaultdict(int)
        confidence: dict = defaultdict(list)
        correct: dict = defaultdict(list)

        for row in rows:
            ticket = tickets.get(row["ticket_id"])
            if ticket is None:
                continue
            group = segments(ticket)[dimension]
            totals[group] += 1
            labels = ticket.get("labels") or {}
            protected[group] += bool(labels.get("must_not_auto_respond"))

            entry = log.get(row["ticket_id"])
            if entry:
                if entry["action"] != "auto_respond":
                    rules[group][entry["rule"]] += 1
                if entry["confidence"] is not None:
                    confidence[group].append(entry["confidence"])
            if labels.get("intent"):
                correct[group].append(row["intent"] == labels["intent"])

        lines += [
            f"### {dimension}",
            "",
            "| Group | n | Must-not-auto-respond by label | Escalations by rule | Mean stated confidence | Classification accuracy |",
            "|---|---:|---:|---|---:|---:|",
        ]
        for group in sorted(totals, key=lambda item: -totals[item]):
            fired = ", ".join(
                f"{rule} {count}" for rule, count in sorted(rules[group].items())
            )
            mean = (
                f"{sum(confidence[group]) / len(confidence[group]):.3f}"
                if confidence[group]
                else "n/a"
            )
            accuracy = (
                f"{sum(correct[group]) / len(correct[group]):.0%}"
                if correct[group]
                else "n/a"
            )
            lines.append(
                f"| {group} | {totals[group]} "
                f"| {protected[group] / totals[group]:.0%} "
                f"| {fired or 'none'} | {mean} | {accuracy} |"
            )
        lines.append("")

    return "\n".join(lines)


def main(argv=None) -> str:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="a finished results directory")
    parser.add_argument("--tickets", required=True, help="the input ticket file")
    parser.add_argument("--output", default="docs/fairness_tables.md")
    args = parser.parse_args(argv)

    with open(os.path.join(args.run, "outcomes.jsonl"), encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    with open(args.tickets, encoding="utf-8") as handle:
        tickets = {ticket["ticket_id"]: ticket for ticket in json.load(handle)}

    # The rule and the confidence live in the decision log, which is the record
    # the governance framework asks to be auditable. Read it rather than
    # recomputing, so the audit reflects what the system actually wrote down.
    connection = sqlite3.connect(os.path.join(args.run, "decisions.db"))
    connection.row_factory = sqlite3.Row
    log = {
        entry["ticket_id"]: entry
        for entry in connection.execute(
            "select ticket_id, action, rule, confidence from decisions"
        )
    }
    connection.close()

    text = render(measure(rows, tickets)) + "\n" + mechanism(rows, tickets, log)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(text)
    return text


if __name__ == "__main__":
    main()
