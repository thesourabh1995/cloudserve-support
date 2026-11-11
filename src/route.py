"""Routing: answer automatically, or hand the ticket to a person.

Acceptance criterion A5. The same inputs always produce the same decision,
and the reason is written in language a support manager can read.

The tree below is the policy in the development labels, counted rather than
assumed. Of the 500 development tickets, `expected_route` is exactly:

  * escalate, for the four categories in NEVER_AUTO_RESPOND (87 tickets);
  * escalate, when the ticket is not answerable from the documentation (87);
  * escalate, for a high-urgency database or performance incident even when
    the documentation does cover it (15) — a wrong answer during an outage
    costs more than the wait;
  * auto_respond, otherwise (311).

Confidence is a separate gate on top of that policy, because A5 requires a
threshold and the labels do not contain one. 0.80 is the brief's illustrative
figure and is not yet calibrated; docs/routing_rules.md says why it has not
been moved.
"""

from dataclasses import dataclass

from src.classify import Classification, NEVER_AUTO_RESPOND
from src.config import settings
from src.killswitch import Halt
from src.models import Ticket

AUTO_RESPOND = "auto_respond"
ESCALATE = "escalate"

# High-urgency production incidents. Every such ticket in the development set
# is labelled escalate, including the ones the documentation can answer.
LIVE_INCIDENT_INTENTS = frozenset({"database_issue", "performance_degradation"})

_PROTECTED_REASON = {
    "security_incident": (
        "Security incidents are never answered automatically. A partial answer "
        "can make an active incident worse."
    ),
    "compliance_request": (
        "Compliance requests are escalated. They need someone who can speak "
        "for the company, not a drafted answer."
    ),
    "feature_request": (
        "Feature requests are product decisions, not support answers, so they "
        "go to a human."
    ),
    "unclear_request": (
        "The request is not clear enough to answer safely, so it goes to a human."
    ),
}


@dataclass(frozen=True)
class RoutingDecision:
    """One routing outcome. Frozen so a caller cannot quietly change it."""

    action: str
    rule: str
    reason: str
    confidence: float
    threshold: float

    @property
    def escalated(self) -> bool:
        return self.action == ESCALATE


def _escalate(rule: str, reason: str, confidence: float, threshold: float) -> RoutingDecision:
    return RoutingDecision(ESCALATE, rule, reason, confidence, threshold)


def route(
    ticket: Ticket,
    classification: Classification,
    passages: list,
    threshold: float = None,
    halt: Halt = None,
) -> RoutingDecision:
    """Decide once. Pure: no clock, no randomness, no model call.

    `passages` is whatever retrieval returned after the relevance floor, so an
    empty list means nothing relevant was found rather than that retrieval was
    skipped.

    `halt` is the state of the stop control, read by the caller rather than
    here. Reading a file inside this function would make the same inputs
    produce different decisions at different moments, which is exactly what A5
    forbids, so the IO stays at the edge and the decision stays a function of
    its arguments.
    """
    threshold = settings.confidence_threshold if threshold is None else threshold
    confidence = classification.confidence

    # First, ahead of everything. When someone has stopped automation they have
    # stopped it, and no later rule may decide a ticket is safe enough to answer.
    if halt is not None and halt.engaged:
        return _escalate(
            "automation_halted",
            "Automatic answering is stopped by the kill switch "
            f"({halt.note}). The ticket is classified and queued for a person.",
            confidence,
            threshold,
        )

    if ticket.is_empty:
        return _escalate(
            "empty_ticket",
            "The ticket has no text, so there is nothing to answer.",
            confidence,
            threshold,
        )

    if classification.degraded:
        return _escalate(
            "classification_unusable",
            "Classification could not be trusted "
            f"({classification.reason}), so the ticket goes to a human "
            "rather than being answered on a guess.",
            confidence,
            threshold,
        )

    if classification.intent in NEVER_AUTO_RESPOND:
        reason = _PROTECTED_REASON.get(
            classification.intent,
            f"{classification.intent} is never answered automatically.",
        )
        return _escalate("protected_category", reason, confidence, threshold)

    if confidence < threshold:
        return _escalate(
            "below_threshold",
            f"Confidence {confidence:.2f} is below the threshold of "
            f"{threshold:.2f}, so the ticket is escalated with its context "
            "attached rather than answered.",
            confidence,
            threshold,
        )

    if not passages:
        return _escalate(
            "no_supporting_passage",
            "No documentation passage cleared the relevance floor, so an "
            "automatic answer would not be grounded in anything we can cite.",
            confidence,
            threshold,
        )

    if classification.urgency == "high" and classification.intent in LIVE_INCIDENT_INTENTS:
        return _escalate(
            "live_incident",
            "This is a high-urgency database or performance incident. Those "
            "are escalated even when the documentation covers them, because a "
            "wrong answer during an outage costs more than the wait.",
            confidence,
            threshold,
        )

    return RoutingDecision(
        action=AUTO_RESPOND,
        rule="confident_and_grounded",
        reason=(
            f"Confidence {confidence:.2f} meets the threshold of {threshold:.2f} "
            "and a supporting passage was retrieved, so the ticket is answered "
            "automatically."
        ),
        confidence=confidence,
        threshold=threshold,
    )
