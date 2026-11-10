"""One unattended run over a ticket file. Acceptance criterion A9.

    python -m evaluation.harness --input data/development_tickets.json --output evaluation/results/run1

The input path is an argument. The hidden evaluation file is not in this
repository, and a harness that only opens its own copy of the data cannot be
run on it.

Every record produces a logged decision. A ticket that throws is recorded as
an escalation with a reason, and the run continues. The metrics report is
written at the end without any further step.
"""

import argparse
import json
import os
import time
import traceback
from datetime import datetime, timezone

from src.classify import fallback
from src.generate import ABSTAIN, Draft
from src.guardrails import citation_tally, review
from src.ingest import load_labels, load_records, normalise_ticket
from src.logging_store import DecisionLog
from src.pipeline import Pipeline
from src.route import route

from evaluation.metrics import render_markdown, summarise


def _row_from_outcome(outcome, latency: float, logged: bool) -> dict:
    offered, resolved = citation_tally(outcome.draft, outcome.passages)
    return {
        "ticket_id": outcome.ticket.ticket_id,
        "final_action": outcome.final_action,
        "latency_seconds": latency,
        "intent": outcome.classification.intent,
        "confidence": outcome.classification.confidence,
        "retrieved_doc_ids": [passage.doc_id for passage in outcome.passages],
        "citations_offered": offered,
        "citations_resolved": resolved,
        "findings": [
            {"check": finding.check, "blocked": finding.blocked}
            for finding in outcome.guardrail.findings
        ],
        "customer_tier": outcome.ticket.customer_tier,
        "customer_region": outcome.ticket.customer_region,
        "language_fluency": outcome.ticket.language_fluency,
        "logged": logged,
    }


def _record_failure(pipeline: Pipeline, raw, error: Exception) -> dict:
    """A ticket the pipeline could not finish still gets a row in the log."""
    ticket = normalise_ticket(raw if isinstance(raw, dict) else {})
    if isinstance(raw, dict) and raw.get("ticket_id"):
        ticket.ticket_id = str(raw["ticket_id"])
    classification = fallback(f"pipeline failed: {error}")
    decision = route(ticket, classification, [])
    draft = Draft(answer=ABSTAIN, known=False, degraded=True, reason=str(error))
    report = review(draft, [])
    pipeline._log().record(
        ticket,
        classification,
        decision,
        [],
        run_id=pipeline.run_id,
        answer=draft.answer,
        known=False,
        guardrail_blocked=report.blocked,
        guardrail_findings=[{"check": finding.check, "blocked": finding.blocked} for finding in report.findings],
    )
    return {
        "ticket_id": ticket.ticket_id,
        "final_action": "escalate",
        "latency_seconds": None,
        "intent": classification.intent,
        "confidence": 0.0,
        "retrieved_doc_ids": [],
        "citations_offered": 0,
        "citations_resolved": 0,
        "findings": [{"check": finding.check, "blocked": finding.blocked} for finding in report.findings],
        "customer_tier": ticket.customer_tier,
        "customer_region": ticket.customer_region,
        "language_fluency": ticket.language_fluency,
        "logged": True,
        "error": str(error),
    }


def run(input_path: str, output_dir: str, pipeline: Pipeline = None) -> dict:
    """Process every record in `input_path` and write the report to `output_dir`."""
    os.makedirs(output_dir, exist_ok=True)
    records = load_records(input_path)
    labels = load_labels(input_path)

    if pipeline is None:
        run_id = "harness-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        pipeline = Pipeline(
            decision_log=DecisionLog(os.path.join(output_dir, "decisions.db")),
            run_id=run_id,
        )

    rows = []
    started = time.monotonic()
    total = len(records)
    for index, raw in enumerate(records, start=1):
        ticket_started = time.monotonic()
        try:
            outcome = pipeline.handle(raw if isinstance(raw, dict) else {})
            latency = time.monotonic() - ticket_started
            row = _row_from_outcome(outcome, latency, logged=True)
        except Exception as error:
            traceback.print_exc()
            row = _record_failure(pipeline, raw, error)
        rows.append(row)
        print(f"{index}/{total} {row['ticket_id']} {row['final_action']}", flush=True)

    report = summarise(rows, labels)
    report["run"] = {
        "input": os.path.abspath(input_path),
        "tickets": total,
        "run_id": pipeline.run_id,
        "seconds": round(time.monotonic() - started, 3),
        "log_reconciles": pipeline._log().reconcile(pipeline.run_id, total)["complete"],
    }
    report["governance"]["log_complete"] = report["run"]["log_reconciles"]
    report["governance"]["decisions_logged"] = pipeline._log().count(pipeline.run_id)

    with open(os.path.join(output_dir, "outcomes.jsonl"), "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    with open(os.path.join(output_dir, "metrics.json"), "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    with open(os.path.join(output_dir, "metrics.md"), "w", encoding="utf-8") as handle:
        handle.write(render_markdown(report))

    print(
        f"processed {total}, logged {report['governance']['decisions_logged']}, "
        f"reconciles {report['run']['log_reconciles']}",
        flush=True,
    )
    return report


def main(argv: list[str] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the support pipeline over a ticket file.")
    parser.add_argument("--input", required=True, help="Path to the ticket file. Not hardcoded.")
    parser.add_argument("--output", required=True, help="Directory for the metrics report and the decision log.")
    args = parser.parse_args(argv)
    run(args.input, args.output)


if __name__ == "__main__":
    main()
