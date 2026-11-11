"""The stop control has to actually stop things.

The Governance Framework asks how the kill switch is tested. This covers the
mechanism itself; the routing behaviour it produces is pinned in test_route.py
alongside the other rules, and the end-to-end effect is below.
"""

from src import killswitch
from src.classify import Classification
from src.generate import Citation, Draft
from src.logging_store import DecisionLog
from src.pipeline import Pipeline
from src.retrieve import Passage
from src.route import ESCALATE

SPAN = "rotate the key from the dashboard"


def test_engaging_and_releasing_round_trips(tmp_path, monkeypatch):
    monkeypatch.setenv("KILL_SWITCH_FILE", str(tmp_path / "STOP_AUTOMATION"))

    assert killswitch.status().engaged is False

    killswitch.engage("provider returning nonsense")
    status = killswitch.status()
    assert status.engaged is True
    assert status.note == "provider returning nonsense"

    killswitch.release()
    assert killswitch.status().engaged is False
    # Releasing twice is not an error. Someone doing this at 2am may not know
    # whether the first attempt worked.
    killswitch.release()


def test_an_empty_switch_file_still_halts(tmp_path, monkeypatch):
    """`touch` is the documented mechanism, so no content must still mean stop."""
    switch = tmp_path / "STOP_AUTOMATION"
    switch.write_text("")
    monkeypatch.setenv("KILL_SWITCH_FILE", str(switch))

    status = killswitch.status()
    assert status.engaged is True
    assert status.note == "no reason recorded"


def test_engage_creates_a_missing_directory(tmp_path, monkeypatch):
    """The switch must work on a fresh checkout, before any run has happened."""
    switch = tmp_path / "storage" / "STOP_AUTOMATION"
    monkeypatch.setenv("KILL_SWITCH_FILE", str(switch))

    killswitch.engage("first use")
    assert killswitch.status().engaged is True


class _Classifier:
    def classify(self, ticket):
        return Classification(
            intent="api_key_issue",
            urgency="low",
            confidence=0.95,
            reason="The customer asks how to rotate a key.",
            alternatives=[],
            prompt_version="PR-01 v1.0",
            degraded=False,
        )


class _Retriever:
    def search(self, query, top_k=None):
        return [Passage("DOC-API-001", "Rotating keys", "api", f"You can {SPAN}.", 0.8, 0)]


class _Generator:
    """Records whether a draft was ever asked for."""

    def __init__(self):
        self.called = False

    def draft(self, ticket, passages):
        self.called = True
        return Draft(
            answer=f"You can {SPAN}.",
            citations=[Citation("DOC-API-001", SPAN)],
            known=True,
            prompt_version="PR-02 v1.0",
            degraded=False,
            reason="",
        )


def test_the_halt_stops_generation_and_is_logged(tmp_path, monkeypatch):
    """End to end on a ticket the system would otherwise have answered."""
    monkeypatch.setenv("KILL_SWITCH_FILE", str(tmp_path / "STOP_AUTOMATION"))
    killswitch.engage("incident 4412")

    generator = _Generator()
    store = DecisionLog(str(tmp_path / "decisions.db"))
    built = Pipeline(
        classifier=_Classifier(),
        retriever=_Retriever(),
        generator=generator,
        decision_log=store,
        run_id="halted-run",
    )

    outcome = built.handle(
        {
            "ticket_id": "T-1",
            "channel": "email",
            "subject": "Key rotation",
            "body": "How do I rotate my API key?",
        }
    )

    assert outcome.final_action == ESCALATE
    assert outcome.decision.rule == "automation_halted"
    # Spending tokens on a reply nobody may send is what the halt prevents.
    assert generator.called is False

    rows = store.for_run("halted-run")
    assert len(rows) == 1
    assert rows[0]["rule"] == "automation_halted"
    assert "incident 4412" in rows[0]["reason"]
    store.close()
