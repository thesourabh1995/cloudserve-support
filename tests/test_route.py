"""Routing (A5). Every branch of the decision tree, and the determinism check.

The tree is policy plus a confidence gate. These tests pin both, so a later
change to "just use the threshold" fails loudly instead of quietly dropping
the categories that must never be answered automatically.
"""

from src.classify import Classification
from src.models import Ticket
from src.retrieve import Passage
from src.killswitch import Halt
from src.route import AUTO_RESPOND, ESCALATE, route


def ticket(body="My deployment keeps failing the health check.", **overrides):
    values = dict(
        ticket_id="DEV-0001",
        channel="email",
        subject="Deployment failing",
        body=body,
        received_at=None,
        customer_id="CUST-1",
        customer_tier="business",
        customer_region="europe",
        language_fluency="fluent",
    )
    values.update(overrides)
    return Ticket(**values)


def classification(**overrides):
    values = dict(
        intent="deployment_failure",
        urgency="medium",
        confidence=0.91,
        reason="The customer reports a deployment failing its health check.",
        alternatives=[],
        prompt_version="PR-01 v1.0",
        degraded=False,
    )
    values.update(overrides)
    return Classification(**values)


def passage():
    return Passage(
        doc_id="DOC-DEPLOY-001",
        title="Resolving container health check failures",
        category="deployment",
        text="Check the health endpoint.",
        similarity=0.72,
        chunk_index=0,
    )


class TestAutoRespond:
    def test_confident_grounded_ticket_is_answered(self):
        decision = route(ticket(), classification(), [passage()])
        assert decision.action == AUTO_RESPOND
        assert decision.rule == "confident_and_grounded"
        assert decision.reason

    def test_confidence_exactly_at_the_threshold_passes(self):
        decision = route(ticket(), classification(confidence=0.80), [passage()], threshold=0.80)
        assert decision.action == AUTO_RESPOND


class TestEscalation:
    def test_confidence_below_the_threshold_escalates(self):
        decision = route(ticket(), classification(confidence=0.79), [passage()], threshold=0.80)
        assert decision.action == ESCALATE
        assert decision.rule == "below_threshold"
        assert "0.79" in decision.reason
        assert "0.80" in decision.reason

    def test_no_supporting_passage_escalates_even_when_confident(self):
        decision = route(ticket(), classification(confidence=0.99), [])
        assert decision.action == ESCALATE
        assert decision.rule == "no_supporting_passage"

    def test_protected_categories_escalate_at_full_confidence(self):
        for intent in ("security_incident", "compliance_request", "feature_request", "unclear_request"):
            decision = route(ticket(), classification(intent=intent, confidence=1.0), [passage()])
            assert decision.action == ESCALATE, intent
            assert decision.rule == "protected_category"
            assert decision.reason

    def test_high_urgency_database_incident_escalates_despite_documentation(self):
        decision = route(
            ticket(),
            classification(intent="database_issue", urgency="high", confidence=0.95),
            [passage()],
        )
        assert decision.action == ESCALATE
        assert decision.rule == "live_incident"

    def test_the_same_incident_at_medium_urgency_is_answered(self):
        """The development labels escalate these only when urgency is high."""
        decision = route(
            ticket(),
            classification(intent="database_issue", urgency="medium", confidence=0.95),
            [passage()],
        )
        assert decision.action == AUTO_RESPOND

    def test_a_high_urgency_deployment_is_still_answered_when_grounded(self):
        """Not every high-urgency ticket escalates. Only the two incident classes do."""
        decision = route(
            ticket(),
            classification(intent="deployment_failure", urgency="high", confidence=0.95),
            [passage()],
        )
        assert decision.action == AUTO_RESPOND

    def test_an_unusable_classification_escalates_on_its_own_reason(self):
        decision = route(
            ticket(),
            classification(intent="unclear_request", confidence=0.0, degraded=True, reason="model unavailable"),
            [passage()],
        )
        assert decision.rule == "classification_unusable"
        assert "model unavailable" in decision.reason

    def test_an_empty_ticket_escalates(self):
        decision = route(ticket(subject="", body="   "), classification(degraded=True), [])
        assert decision.rule == "empty_ticket"


class TestDeterminism:
    def test_the_same_input_routes_the_same_way_twice(self):
        """A5 is checked by running one ticket twice."""
        kwargs = dict(
            ticket=ticket(),
            classification=classification(confidence=0.64),
            passages=[passage()],
            threshold=0.80,
        )
        first = route(**kwargs)
        second = route(**kwargs)
        assert first == second


class TestThresholdIsTheOneGiven:
    def test_a_caller_supplied_threshold_is_what_gets_applied(self):
        low_bar = route(ticket(), classification(confidence=0.50), [passage()], threshold=0.40)
        high_bar = route(ticket(), classification(confidence=0.50), [passage()], threshold=0.90)
        assert low_bar.action == AUTO_RESPOND
        assert high_bar.action == ESCALATE
        assert high_bar.threshold == 0.90


class TestTheKillSwitchOutranksEverything:
    """The stop control is the first rule, so no later rule can overrule it."""

    def test_a_ticket_that_would_be_answered_is_escalated_when_halted(self):
        answerable = dict(
            ticket=ticket(), classification=classification(), passages=[passage()]
        )
        assert route(**answerable, halt=Halt(engaged=False)).action == AUTO_RESPOND

        halted = route(**answerable, halt=Halt(engaged=True, note="bad answers"))
        assert halted.action == ESCALATE
        assert halted.rule == "automation_halted"
        # Whoever stopped it said why, and that reaches the decision log.
        assert "bad answers" in halted.reason

    def test_no_halt_argument_behaves_as_running(self):
        assert route(ticket(), classification(), [passage()]).action == AUTO_RESPOND
