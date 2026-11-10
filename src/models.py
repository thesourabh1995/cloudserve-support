"""Internal representations shared by every pipeline component.

One normalised ticket shape regardless of source channel, so that no component
downstream of ingest needs to know where a ticket came from.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

CHANNELS = ("email", "chat", "docs_comment", "forum")

# Returned by classify when it cannot produce a usable label. Routing treats it
# as an automatic escalation rather than a low-confidence answer.
UNKNOWN_INTENT = "unclear_request"


@dataclass
class Ticket:
    """A ticket after normalisation, as the rest of the system sees it.

    Deliberately excludes two things present in the source files:

    `labels` and `history` are ground truth. They are read by the evaluation
    harness for scoring and never attached here, because a component that can
    see the correct answer cannot be measured against it.

    `customer_name` is personal data that no component needs in order to
    classify, retrieve or draft. Dropping it at the boundary means it cannot
    reach a prompt or an outbound response by accident.
    """

    ticket_id: str
    channel: str
    subject: str
    body: str
    received_at: Optional[datetime]
    customer_id: str
    customer_tier: str
    customer_region: str
    language_fluency: str

    # The text as it arrived, kept so that a human reviewing an escalation sees
    # what the customer actually wrote rather than our cleaned version.
    raw_text: str = ""

    # Problems found during normalisation. Not errors: ingest never rejects a
    # ticket, because a dropped ticket is invisible and A9 forbids silent gaps.
    issues: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        """Subject and body as one block for classification and retrieval.

        Chat tickets carry an empty subject, so joining unconditionally would
        leave a leading separator on roughly a third of the corpus.
        """
        parts = [part for part in (self.subject, self.body) if part]
        return "\n\n".join(parts)

    @property
    def is_empty(self) -> bool:
        """True when there is nothing to work with. Routed straight to a human."""
        return not self.text.strip()
