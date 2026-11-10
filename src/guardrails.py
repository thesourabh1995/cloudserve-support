"""Checks that run on every draft before it can be sent.

Acceptance criterion A7. A guardrail that only warns is not a guardrail, so
each check here can block, and a blocked draft is not released.

Two checks, both required by the build specification:

Private data. An outbound reply that contains an email address, a phone
number or a key-shaped token is blocked. There is no acceptable rate for this.

Unsupported claims. A citation must name a passage that was actually
retrieved, and the span it quotes must occur in that passage. A reply that
claims to know something without such a citation is blocked too. This is also
how A6 is checked: the citation is followed to the text.

Every check is recorded whether or not it blocked, because the governance
report counts activations by type and a silent pass is not the same as a
check that did not run.
"""

import re
from dataclasses import dataclass

from src.generate import Draft

# Deliberately ordinary patterns. They catch the secrets a customer pastes
# into a ticket and a model then copies, which is the failure mode, not a
# general data-loss-prevention product.
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?:\+\d|\b0)[\d\s().-]{8,}\d")
_SECRET = re.compile(
    r"\b(?:sk|gsk|pk|rk|ghp)_[A-Za-z0-9_-]{8,}\b|\bAKIA[0-9A-Z]{16}\b",
)

# A quote shorter than this matches by accident ("the", "a key") and proves
# nothing about the passage.
_MIN_QUOTE = 12


@dataclass(frozen=True)
class Finding:
    check: str
    blocked: bool
    detail: str


@dataclass(frozen=True)
class GuardrailReport:
    findings: tuple[Finding, ...]

    @property
    def blocked(self) -> bool:
        return any(finding.blocked for finding in self.findings)

    def activations(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.blocked]


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _private_data(answer: str) -> Finding:
    found = []
    if _EMAIL.search(answer):
        found.append("an email address")
    if _PHONE.search(answer):
        found.append("a phone number")
    if _SECRET.search(answer):
        found.append("a key or token")
    if found:
        return Finding(
            "private_data",
            True,
            "The reply contains " + " and ".join(found) + ", so it is not sent.",
        )
    return Finding("private_data", False, "No email address, phone number or key-shaped token.")


def citation_tally(draft: Draft, passages: list) -> tuple[int, int]:
    """Citations offered, and how many of them resolve to a retrieved passage.

    A draft that does not claim to know offers nothing to check, so both
    numbers are zero. A claim with no citation at all is caught separately
    by the unsupported-claim guardrail; it is not a citation that failed.
    """
    if not draft.known or not draft.citations:
        return 0, 0

    by_id = {}
    for passage in passages or []:
        by_id.setdefault(passage.doc_id, []).append(passage)

    resolved = 0
    for citation in draft.citations:
        candidates = by_id.get(citation.doc_id, [])
        quote = _normalise(citation.supports)
        if len(quote) < _MIN_QUOTE:
            continue
        if any(quote in _normalise(passage.text) for passage in candidates):
            resolved += 1
    return len(draft.citations), resolved


def _unsupported(draft: Draft, passages: list) -> Finding:
    if not draft.known:
        return Finding(
            "unsupported_claim",
            False,
            "The draft does not claim to answer from the documentation.",
        )

    offered, resolved = citation_tally(draft, passages)
    if offered == 0:
        return Finding(
            "unsupported_claim",
            True,
            "The reply claims to answer the ticket but cites nothing.",
        )
    if resolved < offered:
        return Finding(
            "unsupported_claim",
            True,
            f"{offered - resolved} of {offered} citation(s) do not resolve to a retrieved passage, so the reply is not sent.",
        )
    return Finding(
        "unsupported_claim",
        False,
        f"{resolved} citation(s) resolve to the retrieved passages.",
    )


def review(draft: Draft, passages: list) -> GuardrailReport:
    """Run every check. Always returns a report; never raises."""
    return GuardrailReport(findings=(_private_data(draft.answer), _unsupported(draft, passages)))


def release(draft: Draft, report: GuardrailReport) -> str | None:
    """The text a customer may receive, or None when it must not be sent."""
    if not draft.releasable or report.blocked:
        return None
    return draft.answer
