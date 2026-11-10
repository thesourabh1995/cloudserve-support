"""Classification: intent, urgency and a confidence that means something.

Acceptance criterion A3. Every ticket leaves here with a class and a numeric
confidence between zero and one.

Two requirements shape this module. It must never raise: a classifier that
throws ends the unattended run, so every failure path returns a defined
fallback instead. And it must record the alternatives it considered, not only
the option it chose, because an escalation is far more useful to a tier two
engineer when it says what the system was torn between.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.llm import LLMClient, ModelUnavailable, extract_json
from src.models import UNKNOWN_INTENT, Ticket
from src.prompts import load_prompt

INTENTS = (
    "account_access",
    "api_key_issue",
    "api_usage_question",
    "authentication_failure",
    "billing_query",
    "compliance_request",
    "configuration_help",
    "database_issue",
    "data_export",
    "data_residency",
    "deployment_failure",
    "feature_request",
    "integration_help",
    "onboarding",
    "performance_degradation",
    "quota_or_overage",
    "rate_limit",
    "rollback_request",
    "security_incident",
    "sso_configuration",
    "unclear_request",
    "webhook_issue",
)

URGENCIES = ("high", "medium", "low")

# Categories that are never answered automatically, whatever the confidence.
# Taken from the development set's `must_not_auto_respond` flag and corroborated
# by Daniel, who named security, billing disputes and data location as the
# classes where an automated answer does the most damage. Routing enforces this;
# classification only reports it.
NEVER_AUTO_RESPOND = frozenset(
    {"security_incident", "compliance_request", "feature_request", UNKNOWN_INTENT}
)


@dataclass
class Classification:
    intent: str
    urgency: str
    confidence: float
    reason: str
    alternatives: list[dict] = field(default_factory=list)
    prompt_version: str = ""
    degraded: bool = False

    @property
    def must_escalate(self) -> bool:
        return self.intent in NEVER_AUTO_RESPOND


def _coerce_confidence(value) -> float:
    """Clamp to [0, 1]. Models return 85, "0.85" and 0.85 interchangeably."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number > 1.0:
        number = number / 100.0 if number <= 100.0 else 1.0
    return max(0.0, min(1.0, number))


def _clean_alternatives(raw, chosen: str) -> list[dict]:
    if not isinstance(raw, list):
        return []
    cleaned = []
    for item in raw[:3]:
        if not isinstance(item, dict):
            continue
        intent = str(item.get("intent", "")).strip().lower()
        if intent in INTENTS and intent != chosen:
            cleaned.append(
                {"intent": intent, "confidence": _coerce_confidence(item.get("confidence"))}
            )
    return cleaned


def fallback(reason: str) -> Classification:
    """The defined result when classification cannot be trusted.

    Confidence is zero rather than absent. A missing confidence must never be
    read as a high one, so the value is explicit and routing escalates on it.
    """
    return Classification(
        intent=UNKNOWN_INTENT,
        urgency="medium",
        confidence=0.0,
        reason=reason,
        alternatives=[],
        degraded=True,
    )


class Classifier:
    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or LLMClient()
        self.prompt = load_prompt("build/classify.md")

    def classify(self, ticket: Ticket) -> Classification:
        """Classify one ticket. Never raises."""
        if ticket.is_empty:
            return fallback("ticket contains no text to classify")

        rendered = self.prompt.render_user(
            channel=ticket.channel,
            subject=ticket.subject or "(none)",
            body=ticket.body,
        )

        try:
            completion = self.client.complete(
                prompt=rendered, system=self.prompt.system, temperature=0.0
            )
        except ModelUnavailable as error:
            # A11: the provider being unreachable degrades this ticket to a
            # human, it does not stop the run.
            return fallback(f"model unavailable: {error}")

        parsed = extract_json(completion.text)
        if not parsed:
            return fallback("classifier response was not valid JSON")

        intent = str(parsed.get("intent", "")).strip().lower()
        if intent not in INTENTS:
            return fallback(f"classifier returned an unknown intent: {intent!r}")

        urgency = str(parsed.get("urgency", "")).strip().lower()
        if urgency not in URGENCIES:
            urgency = "medium"

        reason = str(parsed.get("reason", "")).strip() or "no reason given"

        return Classification(
            intent=intent,
            urgency=urgency,
            confidence=_coerce_confidence(parsed.get("confidence")),
            reason=reason[:500],
            alternatives=_clean_alternatives(parsed.get("alternatives"), intent),
            prompt_version=self.prompt.reference,
        )
