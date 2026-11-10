"""The local pipeline joins the components and records every outcome.

No model and no vector store: both are injected, which is also how the
guardrail-blocked path is forced.
"""

from src.classify import Classification
from src.generate import Citation, Draft
from src.logging_store import DecisionLog
from src.pipeline import Pipeline
from src.retrieve import Passage


SPAN = "the container listens on the port named in the health check"


class StubClassifier:
    def __init__(self, classification):
        self.classification = classification

    def classify(self, ticket):
        return self.classification


class StubRetriever:
    def __init__(self, passages):
        self.passages = passages

    def search(self, query, top_k=None):
        return list(self.passages)


class StubGenerator:
    def __init__(self, result):
        self.result = result

    def draft(self, ticket, passages):
        return self.result


def classification(**overrides):
    values = dict(
        intent="deployment_failure",
        urgency="medium",
        confidence=0.92,
        reason="A deployment is failing its health check.",
        alternatives=[],
        prompt_version="PR-01 v1.0",
        degraded=False,
    )
    values.update(overrides)
    return Classification(**values)


def passage():
    return Passage("DOC-DEPLOY-001", "Health checks", "deployment", f"Check that {SPAN}.", 0.7, 0)


def draft(**overrides):
    values = dict(
        answer=f"Check that {SPAN}.",
        citations=[Citation("DOC-DEPLOY-001", SPAN)],
        known=True,
        prompt_version="PR-02 v1.0",
        degraded=False,
        reason="",
    )
    values.update(overrides)
    return Draft(**values)


def pipeline(tmp_path, classification, draft, passages=None):
    store = DecisionLog(str(tmp_path / "decisions.db"))
    built = Pipeline(
        classifier=StubClassifier(classification),
        retriever=StubRetriever(passages if passages is not None else [passage()]),
        generator=StubGenerator(draft),
        decision_log=store,
        run_id="test",
    )
    return built, store


RAW = {"channel": "email", "subject": "Health check", "body": "The health check keeps restarting the container."}


class TestOutcomes:
    def test_a_grounded_confident_ticket_is_answered_and_logged(self, tmp_path):
        built, store = pipeline(tmp_path, classification(), draft())
        outcome = built.handle(RAW)
        assert outcome.final_action == "auto_respond"
        assert outcome.sent_answer
        assert store.reconcile("test", 1)["complete"]
        row = store.for_run("test")[0]
        assert "DOC-DEPLOY-001" in row["citations_json"]
        assert row["guardrail_blocked"] == 0
        store.close()

    def test_a_reply_containing_an_email_is_blocked_rather_than_sent(self, tmp_path):
        leaked = draft(answer="Write to jane@example.com and we will reset it.")
        built, store = pipeline(tmp_path, classification(), leaked)
        outcome = built.handle(RAW)
        assert outcome.final_action == "blocked"
        assert outcome.sent_answer is None
        assert store.for_run("test")[0]["guardrail_blocked"] == 1
        store.close()

    def test_a_protected_category_is_escalated_even_with_a_clean_draft(self, tmp_path):
        built, store = pipeline(
            tmp_path,
            classification(intent="security_incident", confidence=0.99),
            draft(),
        )
        outcome = built.handle(RAW)
        assert outcome.final_action == "escalate"
        assert outcome.sent_answer is None
        assert outcome.as_dict()["routing"]["rule"] == "protected_category"
        store.close()
