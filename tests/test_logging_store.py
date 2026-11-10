"""The decision log (A8). Coverage, required fields, and survival across reopen.

A8 is checked by counting rows against tickets processed. A log that drops
the failures, or that only exists in memory, fails that check.
"""

from src.classify import Classification
from src.logging_store import DecisionLog
from src.models import Ticket
from src.retrieve import Passage
from src.route import route


def ticket(ticket_id="DEV-0001", **overrides):
    values = dict(
        ticket_id=ticket_id,
        channel="chat",
        subject="",
        body="How do I rotate an API key?",
        received_at=None,
        customer_id="CUST-9",
        customer_tier="enterprise",
        customer_region="latam",
        language_fluency="non_fluent",
    )
    values.update(overrides)
    return Ticket(**values)


def classification(**overrides):
    values = dict(
        intent="api_key_issue",
        urgency="low",
        confidence=0.88,
        reason="The customer wants to rotate a key.",
        alternatives=[{"intent": "account_access", "confidence": 0.07}],
        prompt_version="PR-01 v1.0",
        degraded=False,
    )
    values.update(overrides)
    return Classification(**values)


def passage():
    return Passage(
        doc_id="DOC-API-002",
        title="Rotating API keys",
        category="api",
        text="Keys can be rotated from the console.",
        similarity=0.81,
        chunk_index=1,
    )


def log_one(store, run_id, ticket_id="DEV-0001", **classification_overrides):
    item = ticket(ticket_id)
    result = classification(**classification_overrides)
    found = [passage()]
    decision = route(item, result, found)
    store.record(item, result, decision, found, run_id=run_id)
    return decision


class TestCoverage:
    def test_every_ticket_is_logged_including_escalations(self, tmp_path):
        store = DecisionLog(str(tmp_path / "decisions.db"))
        log_one(store, "run-1", "DEV-0001")
        log_one(store, "run-1", "DEV-0002", confidence=0.10)
        report = store.reconcile("run-1", tickets_processed=2)
        assert report["complete"]
        assert report["logged"] == 2
        store.close()

    def test_a_gap_is_visible(self, tmp_path):
        """Processed three, logged two. A8 exists to catch exactly this."""
        store = DecisionLog(str(tmp_path / "decisions.db"))
        log_one(store, "run-1", "DEV-0001")
        log_one(store, "run-1", "DEV-0002")
        report = store.reconcile("run-1", tickets_processed=3)
        assert not report["complete"]
        assert report["logged"] == 2
        store.close()

    def test_runs_are_counted_separately(self, tmp_path):
        store = DecisionLog(str(tmp_path / "decisions.db"))
        log_one(store, "monday", "DEV-0001")
        log_one(store, "tuesday", "DEV-0001")
        assert store.count("monday") == 1
        assert store.count() == 2
        store.close()


class TestRequiredFields:
    def test_the_brief_fields_are_all_present(self, tmp_path):
        store = DecisionLog(str(tmp_path / "decisions.db"))
        log_one(store, "run-1")
        row = store.for_run("run-1")[0]

        assert row["body"] == "How do I rotate an API key?"
        assert row["intent"] == "api_key_issue"
        assert row["confidence"] == 0.88
        assert "DOC-API-002" in row["sources_json"]
        assert row["action"] in ("auto_respond", "escalate")
        assert row["reason"]
        assert row["customer_tier"] == "enterprise"
        assert row["customer_region"] == "latam"
        assert "account_access" in row["alternatives_json"]
        store.close()

    def test_customer_name_is_not_a_column(self, tmp_path):
        store = DecisionLog(str(tmp_path / "decisions.db"))
        log_one(store, "run-1")
        columns = set(store.for_run("run-1")[0])
        assert "customer_name" not in columns
        store.close()


class TestPersistence:
    def test_rows_survive_reopening_the_file(self, tmp_path):
        path = str(tmp_path / "decisions.db")
        store = DecisionLog(path)
        log_one(store, "run-1")
        store.close()

        reopened = DecisionLog(path)
        assert reopened.count("run-1") == 1
        reopened.close()
