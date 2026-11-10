"""Ingest: turn a raw ticket from any of the four channels into one Ticket.

Acceptance criterion A2. The rule this module exists to enforce is that no
component after it has to know which channel a ticket arrived on.

Ingest never raises on bad input. A ticket that cannot be parsed is still
returned, with the problem recorded in `Ticket.issues`, because the unattended
run must account for every ticket in the input file and a dropped ticket is
indistinguishable from one that was never there.
"""

import json
import re
import unicodedata
from datetime import datetime
from typing import Any, Iterable, Optional

from src.models import CHANNELS, Ticket

# Matches C0 and C1 control characters except tab and newline, which carry
# meaning in pasted logs and stack traces.
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def clean_text(value: Any) -> str:
    """Normalise text without destroying what the customer wrote.

    Unicode is folded to NFKC so that visually identical characters compare
    equal during retrieval; smart quotes and full-width characters are common
    in pasted terminal output. Control characters are stripped because they
    break both the vector store and the JSON written to the decision log.
    Runs of blank lines collapse, but single newlines survive, since code
    blocks and error traces lose their meaning without them.
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)

    value = unicodedata.normalize("NFKC", value)
    value = CONTROL_CHARACTERS.sub("", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def parse_timestamp(value: Any) -> Optional[datetime]:
    """Parse an ISO 8601 timestamp, returning None rather than raising.

    Response time is reported against this field, so an unparseable value has
    to be visible as missing instead of silently becoming "now", which would
    make the latency figures quietly wrong.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def normalise_channel(value: Any, issues: list[str]) -> str:
    """Map an incoming channel onto the four we handle.

    An unrecognised channel is recorded and passed through as "unknown" rather
    than rejected: the ticket still deserves an answer, and the operator needs
    to find out that a fifth channel has appeared.
    """
    channel = clean_text(value).lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "e_mail": "email",
        "mail": "email",
        "live_chat": "chat",
        "docs": "docs_comment",
        "documentation_comment": "docs_comment",
        "community": "forum",
        "community_forum": "forum",
    }
    channel = aliases.get(channel, channel)

    if channel not in CHANNELS:
        issues.append(f"unrecognised channel: {value!r}")
        return "unknown"
    return channel


def normalise_ticket(raw: dict) -> Ticket:
    """Build a Ticket from one raw record."""
    issues: list[str] = []

    if not isinstance(raw, dict):
        return Ticket(
            ticket_id="UNKNOWN",
            channel="unknown",
            subject="",
            body="",
            received_at=None,
            customer_id="",
            customer_tier="unknown",
            customer_region="unknown",
            language_fluency="unknown",
            raw_text=str(raw),
            issues=[f"record is {type(raw).__name__}, not an object"],
        )

    ticket_id = clean_text(raw.get("ticket_id"))
    if not ticket_id:
        ticket_id = "UNKNOWN"
        issues.append("missing ticket_id")

    subject = clean_text(raw.get("subject"))
    body = clean_text(raw.get("body"))
    if not body:
        issues.append("empty body")

    received_at = parse_timestamp(raw.get("received_at"))
    if received_at is None and raw.get("received_at"):
        issues.append(f"unparseable received_at: {raw.get('received_at')!r}")

    original = "\n\n".join(
        part for part in (str(raw.get("subject") or ""), str(raw.get("body") or "")) if part
    )

    return Ticket(
        ticket_id=ticket_id,
        channel=normalise_channel(raw.get("channel"), issues),
        subject=subject,
        body=body,
        received_at=received_at,
        customer_id=clean_text(raw.get("customer_id")),
        customer_tier=clean_text(raw.get("customer_tier")) or "unknown",
        customer_region=clean_text(raw.get("customer_region")) or "unknown",
        language_fluency=clean_text(raw.get("language_fluency")) or "unknown",
        raw_text=original,
        issues=issues,
    )


def load_tickets(path: str) -> list[Ticket]:
    """Read a ticket file and normalise every record in it.

    Accepts either a bare list or an object wrapping one, because the hidden
    evaluation file is only promised to use the same schema, not the same
    top-level shape.
    """
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                payload = value
                break

    if not isinstance(payload, list):
        raise ValueError(f"{path}: expected a list of tickets, found {type(payload).__name__}")

    return [normalise_ticket(record) for record in payload]


def load_labels(path: str) -> dict[str, dict]:
    """Read the ground truth labels, keyed by ticket id.

    Kept separate from `load_tickets` so that only the evaluation harness ever
    holds them. Returns an empty mapping for files that carry no labels, which
    is what an unlabelled production feed would look like.
    """
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                payload = value
                break

    labels = {}
    for record in payload if isinstance(payload, list) else []:
        if isinstance(record, dict) and record.get("labels"):
            labels[str(record.get("ticket_id"))] = {
                "labels": record["labels"],
                "history": record.get("history", {}),
            }
    return labels


def summarise(tickets: Iterable[Ticket]) -> dict:
    """Counts used by the harness to confirm nothing was dropped."""
    tickets = list(tickets)
    by_channel: dict[str, int] = {}
    for ticket in tickets:
        by_channel[ticket.channel] = by_channel.get(ticket.channel, 0) + 1
    return {
        "tickets": len(tickets),
        "by_channel": by_channel,
        "with_issues": sum(1 for t in tickets if t.issues),
        "empty": sum(1 for t in tickets if t.is_empty),
    }
