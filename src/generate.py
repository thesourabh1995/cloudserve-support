"""Draft a reply grounded in the passages that were actually retrieved.

Acceptance criterion A6. A citation is a document id plus a span copied from
that document, so it can be followed and checked against the text rather than
believed. The guardrail in src/guardrails.py does that check and can refuse
to send the draft.

This module never raises. A provider outage or a response that is not JSON
becomes a draft that says it does not know, which routing already treats as
something a person must handle.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.config import settings
from src.llm import LLMClient, ModelUnavailable, extract_json
from src.models import Ticket
from src.prompts import load_prompt

ABSTAIN = (
    "The documentation we retrieved does not support an answer to this "
    "request, so it needs a person."
)


@dataclass
class Citation:
    doc_id: str
    supports: str


@dataclass
class Draft:
    answer: str
    citations: list[Citation] = field(default_factory=list)
    known: bool = False
    prompt_version: str = ""
    degraded: bool = False
    reason: str = ""

    @property
    def releasable(self) -> bool:
        """A draft may be sent only when it claims to know and the model call worked.

        The guardrail can still block it. This property does not consult the
        guardrail; the caller runs that separately so a block is recorded as
        its own decision rather than disappearing inside generation.
        """
        return self.known and not self.degraded


def _abstain(reason: str, prompt_version: str = "", degraded: bool = False) -> Draft:
    return Draft(
        answer=ABSTAIN,
        citations=[],
        known=False,
        prompt_version=prompt_version,
        degraded=degraded,
        reason=reason,
    )


def distinct_sources(passages, limit: int = None) -> list:
    """The best passage from each of the top documents.

    Retrieval returns chunks, and the top five frequently contain two or three
    chunks of the same article. Those near-duplicates cost tokens without
    adding evidence, and the free tier is capped in tokens. Taking the best
    chunk per document puts more distinct material in front of the generator
    for less, and the guardrail still resolves every citation against whatever
    was actually retrieved.
    """
    limit = settings.generation_docs if limit is None else limit
    best: dict[str, object] = {}
    for passage in passages:
        if passage.doc_id not in best:
            best[passage.doc_id] = passage
    return list(best.values())[:limit]


def render_passages(passages) -> str:
    """One delimited block per passage, with the id the model is allowed to cite."""
    blocks = []
    for index, passage in enumerate(passages, start=1):
        blocks.append(
            f"<<<PASSAGE {index}\n"
            f"doc_id: {passage.doc_id}\n"
            f"title: {passage.title}\n\n"
            f"{passage.text}\n"
            f"PASSAGE {index}>>>"
        )
    return "\n\n".join(blocks)


def _citations(raw) -> list[Citation]:
    if not isinstance(raw, list):
        return []
    parsed = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        doc_id = str(item.get("doc_id", "")).strip()
        supports = str(item.get("supports", "")).strip()
        if doc_id and supports:
            parsed.append(Citation(doc_id=doc_id, supports=supports))
    return parsed


class Generator:
    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or LLMClient()
        self.prompt = load_prompt("build/generate.md")

    def draft(self, ticket: Ticket, passages: list) -> Draft:
        """Draft one reply. Never raises."""
        if not passages:
            # There is nothing to ground an answer in, and calling the model
            # here would spend the free allowance on a guess.
            return _abstain("no supporting passage", self.prompt.reference)

        rendered = self.prompt.render_user(
            passages=render_passages(distinct_sources(passages)),
            channel=ticket.channel,
            subject=ticket.subject or "(none)",
            body=ticket.body,
        )

        try:
            completion = self.client.complete(
                prompt=rendered,
                system=self.prompt.system,
                temperature=0.0,
                reasoning_effort=settings.generate_reasoning_effort,
                task="generate",
            )
        except ModelUnavailable as error:
            return _abstain(f"model unavailable: {error}", self.prompt.reference, degraded=True)

        parsed = extract_json(completion.text)
        if not parsed:
            return _abstain("generator response was not valid JSON", self.prompt.reference, degraded=True)

        known = bool(parsed.get("known"))
        answer = str(parsed.get("answer", "")).strip()
        if not answer:
            return _abstain("generator returned an empty answer", self.prompt.reference, degraded=True)

        if not known:
            return Draft(
                answer=answer,
                citations=[],
                known=False,
                prompt_version=self.prompt.reference,
                reason="model reported the passages do not cover the request",
            )

        return Draft(
            answer=answer,
            citations=_citations(parsed.get("citations")),
            known=True,
            prompt_version=self.prompt.reference,
        )
