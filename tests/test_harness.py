"""The unattended run (A9) and the report it has to write (A10).

The model and the vector store are stubbed. What is checked is that every
record is accounted for, including one that throws, and that the report
contains the figures the build specification lists.
"""

import json

import pytest

from evaluation.harness import main, run
from evaluation.metrics import summarise
from src.classify import Classification
from src.generate import Citation, Draft
from src.logging_store import DecisionLog
from src.pipeline import Pipeline
from src.retrieve import Passage

SPAN = "the container listens on the port named in the health check"


class SelectiveClassifier:
    def classify(self, ticket):
        if "boom" in ticket.body:
            raise RuntimeError("fell over")
        return Classification(
            intent="deployment_failure",
            urgency="medium",
            confidence=0.91,
            reason="A deployment is failing.",
            prompt_version="PR-01 v1.0",
        )


class StubRetriever:
    def search(self, query, top_k=None):
        return [Passage("DOC-DEPLOY-001", "Health checks", "deployment", f"Check that {SPAN}.", 0.8, 0)]


class StubGenerator:
    def draft(self, ticket, passages):
        return Draft(
            answer=f"Check that {SPAN}.",
            citations=[Citation("DOC-DEPLOY-001", SPAN)],
            known=True,
            prompt_version="PR-02 v1.0",
        )


def test_a_throwing_ticket_is_logged_and_the_run_continues(tmp_path):
    source = tmp_path / "tickets.json"
    source.write_text(json.dumps([
        {
            "ticket_id": "T-1",
            "channel": "email",
            "subject": "Health check",
            "body": "The health check keeps restarting the container.",
            "labels": {"intent": "deployment_failure", "expected_doc_ids": ["DOC-DEPLOY-001"]},
        },
        {
            "ticket_id": "T-2",
            "channel": "chat",
            "subject": "",
            "body": "boom",
            "labels": {"intent": "billing_query", "expected_doc_ids": []},
        },
    ]), encoding="utf-8")

    output = tmp_path / "out"
    store = DecisionLog(str(output / "decisions.db"))
    pipeline = Pipeline(
        classifier=SelectiveClassifier(),
        retriever=StubRetriever(),
        generator=StubGenerator(),
        decision_log=store,
        run_id="test-run",
    )

    report = run(str(source), str(output), pipeline=pipeline)

    assert report["volume"]["tickets_processed"] == 2
    assert report["volume"]["answered_automatically"] == 1
    assert report["volume"]["escalated"] == 1
    assert report["run"]["log_reconciles"]
    assert report["technical"]["classification"]["accuracy"] == 0.5
    assert report["technical"]["retrieval_hit_rate"]["hits"] == 1
    assert (output / "metrics.md").exists()
    assert (output / "outcomes.jsonl").exists()

    # Every row names the rule that decided it. Without this the outcomes file
    # says what happened but not why, and the reader has to open the database.
    written = [
        json.loads(line)
        for line in (output / "outcomes.jsonl").read_text().splitlines()
    ]
    assert len(written) == 2
    assert all(row["rule"] for row in written)
    store.close()


def test_the_command_requires_both_paths():
    with pytest.raises(SystemExit):
        main([])


def test_unlabelled_tickets_do_not_invent_an_accuracy():
    report = summarise([
        {
            "ticket_id": "T-1",
            "final_action": "escalate",
            "latency_seconds": 1.0,
            "intent": "unclear_request",
            "confidence": 0.0,
            "retrieved_doc_ids": [],
            "citations_offered": 0,
            "citations_resolved": 0,
            "findings": [],
            "customer_tier": "standard",
            "customer_region": "europe",
            "language_fluency": "fluent",
            "logged": True,
        }
    ], labels={})
    assert report["technical"]["classification"] is None
    assert report["business"]["first_contact_resolution"] == 0.0
    assert report["governance"]["private_data_in_outbound_replies"] == 0
