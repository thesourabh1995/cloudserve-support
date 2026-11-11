"""One ticket, end to end.

Used by the local console. The unattended harness will call the same function
over a file. Nothing here reads labels: the decision is made from the ticket
text, the model and the retrieved passages only.
"""

import uuid
from dataclasses import asdict, dataclass

from src import killswitch
from src.classify import Classifier
from src.config import settings
from src.generate import ABSTAIN, Draft, Generator
from src.guardrails import GuardrailReport, release, review
from src.ingest import normalise_ticket
from src.llm import LLMClient
from src.logging_store import DecisionLog
from src.models import Ticket
from src.retrieve import Retriever
from src.route import AUTO_RESPOND, route


# Escalations where drafting a reply would spend a model call on something no
# one can use. The brief asks escalations to carry a drafted summary, and they
# do for the cases where the system understood the ticket and simply was not
# confident enough to send its answer. These are the other cases: a category
# that must never be answered automatically, a ticket we could not classify,
# and a ticket with no text. The retrieved sources are still attached, since
# those cost nothing further.
NO_DRAFT_RULES = frozenset(
    {
        "protected_category",
        "classification_unusable",
        "empty_ticket",
        # The usual reason to stop automation is that the answers are wrong.
        # Drafting more of them spends tokens on text nobody should trust, and
        # puts a bad suggestion in front of the person handling the incident.
        "automation_halted",
    }
)


def skip_draft(rule: str) -> Draft:
    """A recorded non-answer, so the row still says why nothing was drafted."""
    return Draft(
        answer=ABSTAIN,
        citations=[],
        known=False,
        reason=f"no draft attempted: {rule}",
    )


@dataclass
class Outcome:
    ticket: Ticket
    classification: object
    passages: list
    decision: object
    draft: Draft
    guardrail: GuardrailReport
    final_action: str
    sent_answer: str | None

    def as_dict(self) -> dict:
        """A JSON-ready view of the decision, for the console and for curl."""
        return {
            "ticket_id": self.ticket.ticket_id,
            "channel": self.ticket.channel,
            "final_action": self.final_action,
            "sent_answer": self.sent_answer,
            "classification": {
                "intent": self.classification.intent,
                "urgency": self.classification.urgency,
                "confidence": self.classification.confidence,
                "reason": self.classification.reason,
                "alternatives": self.classification.alternatives,
                "degraded": self.classification.degraded,
                "prompt_version": self.classification.prompt_version,
            },
            "passages": [
                {
                    "doc_id": passage.doc_id,
                    "title": passage.title,
                    "similarity": passage.similarity,
                    "citation": passage.citation(),
                }
                for passage in self.passages
            ],
            "routing": {
                "action": self.decision.action,
                "rule": self.decision.rule,
                "reason": self.decision.reason,
                "threshold": self.decision.threshold,
            },
            "draft": {
                "known": self.draft.known,
                "degraded": self.draft.degraded,
                "reason": self.draft.reason,
                "answer": self.draft.answer,
                "citations": [asdict(citation) for citation in self.draft.citations],
                "prompt_version": self.draft.prompt_version,
            },
            "guardrail": {
                "blocked": self.guardrail.blocked,
                "findings": [asdict(finding) for finding in self.guardrail.findings],
            },
        }


def _final_action(decision, draft: Draft, report: GuardrailReport) -> tuple[str, str | None]:
    """What the customer actually receives.

    Routing can say answer, and the guardrail can still refuse to send it.
    An escalation never sends the draft, even when the draft itself is clean.
    """
    if decision.action != AUTO_RESPOND:
        return "escalate", None
    if report.blocked:
        return "blocked", None
    sent = release(draft, report)
    if sent is None:
        return "escalate", None
    return "auto_respond", sent


class Pipeline:
    """Holds the components so a local server builds them once, not per ticket."""

    def __init__(
        self,
        classifier: Classifier = None,
        retriever: Retriever = None,
        generator: Generator = None,
        decision_log: DecisionLog = None,
        run_id: str = "local",
    ):
        self.classifier = classifier
        self.retriever = retriever
        self.generator = generator
        self.decision_log = decision_log
        self.run_id = run_id
        self._client = None

    def client(self) -> LLMClient:
        """One model client for the whole run.

        Shared so that the token and call totals cover classification and
        generation together, which is what the free-tier budget is spent on.
        """
        if self._client is None:
            self._client = LLMClient()
        return self._client

    def usage(self) -> dict:
        if self._client is None:
            return {"tokens": 0, "calls": 0, "by_task": {}}
        return {
            "tokens": self._client.tokens_used,
            "calls": self._client.calls_made,
            "by_task": {
                task: {"tokens": tokens, "calls": self._client.calls_by_task.get(task, 0)}
                for task, tokens in sorted(self._client.tokens_by_task.items())
            },
        }

    def _classifier(self) -> Classifier:
        if self.classifier is None:
            self.classifier = Classifier(client=self.client())
        return self.classifier

    def _retriever(self) -> Retriever:
        if self.retriever is None:
            self.retriever = Retriever()
        return self.retriever

    def _generator(self) -> Generator:
        if self.generator is None:
            self.generator = Generator(client=self.client())
        return self.generator

    def _log(self) -> DecisionLog:
        if self.decision_log is None:
            self.decision_log = DecisionLog(settings.decision_db_path)
        return self.decision_log

    def handle(self, raw: dict) -> Outcome:
        """Process one ticket and write the decision, whatever the outcome."""
        if not raw.get("ticket_id"):
            raw = dict(raw)
            raw["ticket_id"] = "LOCAL-" + uuid.uuid4().hex[:8]

        ticket = normalise_ticket(raw)
        classification = self._classifier().classify(ticket)
        passages = [] if ticket.is_empty else self._retriever().search(ticket.text)
        # Read once per ticket, so engaging the switch takes effect on the next
        # ticket rather than the next restart.
        decision = route(ticket, classification, passages, halt=killswitch.status())

        if decision.rule in NO_DRAFT_RULES:
            draft = skip_draft(decision.rule)
        else:
            draft = self._generator().draft(ticket, passages)

        report = review(draft, passages)
        final_action, sent = _final_action(decision, draft, report)

        self._log().record(
            ticket,
            classification,
            decision,
            passages,
            run_id=self.run_id,
            answer=draft.answer,
            citations=[asdict(citation) for citation in draft.citations],
            known=draft.known,
            generation_prompt=draft.prompt_version,
            guardrail_blocked=report.blocked,
            guardrail_findings=[asdict(finding) for finding in report.findings],
        )
        return Outcome(ticket, classification, passages, decision, draft, report, final_action, sent)
