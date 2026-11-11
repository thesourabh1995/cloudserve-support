"""Token-cost decisions, pinned so a later change cannot quietly undo them.

The free tier is capped in tokens, and the hidden evaluation set has to fit
inside one day's allowance on an assessor's own key. These are the three
measures that made that possible; see docs/run_cost.md.
"""

from src.classify import Classification
from src.generate import Citation, Draft, distinct_sources
from src.logging_store import DecisionLog
from src.pipeline import NO_DRAFT_RULES, Pipeline
from src.retrieve import Passage


def passage(doc_id, chunk_index, similarity):
    return Passage(doc_id, f"Title {doc_id}", "cat", f"text of {doc_id} chunk {chunk_index}", similarity, chunk_index)


class TestDistinctSources:
    def test_near_duplicate_chunks_of_one_article_collapse(self):
        """Three chunks of the same doc cost tokens without adding evidence."""
        retrieved = [
            passage("DOC-A", 0, 0.84),
            passage("DOC-A", 1, 0.77),
            passage("DOC-A", 2, 0.76),
            passage("DOC-B", 1, 0.52),
        ]
        chosen = distinct_sources(retrieved, limit=3)
        assert [p.doc_id for p in chosen] == ["DOC-A", "DOC-B"]

    def test_the_best_chunk_of_each_document_is_the_one_kept(self):
        retrieved = [passage("DOC-A", 2, 0.9), passage("DOC-A", 0, 0.4)]
        assert distinct_sources(retrieved, limit=3)[0].chunk_index == 2

    def test_the_document_limit_is_respected(self):
        retrieved = [passage(f"DOC-{i}", 0, 0.9 - i / 10) for i in range(6)]
        assert len(distinct_sources(retrieved, limit=3)) == 3


class ExplodingGenerator:
    """Fails the test if generation is attempted at all."""

    def draft(self, ticket, passages):
        raise AssertionError("generation should not have been called")


class StubClassifier:
    def __init__(self, classification):
        self.classification = classification

    def classify(self, ticket):
        return self.classification


class StubRetriever:
    def search(self, query, top_k=None):
        return [passage("DOC-A", 0, 0.8)]


def ticket_payload():
    return {"ticket_id": "T-1", "channel": "email", "subject": "s", "body": "Someone stole our API keys."}


class TestNoWastedGeneration:
    def test_a_protected_category_does_not_spend_a_model_call(self, tmp_path):
        store = DecisionLog(str(tmp_path / "d.db"))
        pipeline = Pipeline(
            classifier=StubClassifier(
                Classification(
                    intent="security_incident",
                    urgency="high",
                    confidence=0.97,
                    reason="Possible credential theft.",
                    prompt_version="PR-01 v1.0",
                )
            ),
            retriever=StubRetriever(),
            generator=ExplodingGenerator(),
            decision_log=store,
            run_id="t",
        )
        outcome = pipeline.handle(ticket_payload())

        assert outcome.final_action == "escalate"
        assert outcome.sent_answer is None
        assert "protected_category" in outcome.draft.reason
        # The decision is still logged, with its sources attached.
        row = store.for_run("t")[0]
        assert row["action"] == "escalate"
        assert "DOC-A" in row["sources_json"]
        store.close()

    def test_an_unusable_classification_does_not_spend_a_model_call(self, tmp_path):
        store = DecisionLog(str(tmp_path / "d.db"))
        pipeline = Pipeline(
            classifier=StubClassifier(
                Classification(
                    intent="unclear_request",
                    urgency="medium",
                    confidence=0.0,
                    reason="model unavailable",
                    degraded=True,
                )
            ),
            retriever=StubRetriever(),
            generator=ExplodingGenerator(),
            decision_log=store,
            run_id="t",
        )
        assert pipeline.handle(ticket_payload()).final_action == "escalate"
        store.close()

    def test_a_low_confidence_ticket_still_gets_a_draft_for_the_agent(self, tmp_path):
        """The brief asks escalations to carry a drafted summary. This is that case."""
        store = DecisionLog(str(tmp_path / "d.db"))

        class Generator:
            def draft(self, ticket, passages):
                return Draft(
                    answer="text of DOC-A chunk 0",
                    citations=[Citation("DOC-A", "text of DOC-A chunk 0")],
                    known=True,
                    prompt_version="PR-02 v1.0",
                )

        pipeline = Pipeline(
            classifier=StubClassifier(
                Classification(
                    intent="deployment_failure",
                    urgency="medium",
                    confidence=0.41,
                    reason="Possibly a deployment problem.",
                    prompt_version="PR-01 v1.0",
                )
            ),
            retriever=StubRetriever(),
            generator=Generator(),
            decision_log=store,
            run_id="t",
        )
        outcome = pipeline.handle(ticket_payload())

        assert outcome.final_action == "escalate"
        assert outcome.decision.rule == "below_threshold"
        assert outcome.draft.known
        assert "below_threshold" not in NO_DRAFT_RULES
        store.close()
