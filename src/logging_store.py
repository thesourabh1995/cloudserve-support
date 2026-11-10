"""The decision log. Acceptance criterion A8.

Every automated decision is written here, including the ones that failed,
escalated or were blocked. A log that only records successes cannot be
reconciled against tickets processed, and that reconciliation is how A8 is
checked.

The columns are the fields the brief requires to be reconstructable months
later: the input, the prediction, the confidence, the sources used, the
action taken and the reason. Customer tier, region and fluency are stored
alongside them so the fairness audit can be run from the log without joining
back to the source file. Customer name is not stored; ingest already dropped it.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone

from src.classify import Classification
from src.models import Ticket
from src.route import RoutingDecision

_SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    ticket_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    customer_tier TEXT,
    customer_region TEXT,
    language_fluency TEXT,
    subject TEXT,
    body TEXT,
    intent TEXT NOT NULL,
    urgency TEXT NOT NULL,
    confidence REAL NOT NULL,
    alternatives_json TEXT NOT NULL,
    prompt_version TEXT,
    degraded INTEGER NOT NULL,
    sources_json TEXT NOT NULL,
    action TEXT NOT NULL,
    rule TEXT NOT NULL,
    reason TEXT NOT NULL,
    threshold REAL NOT NULL,
    answer TEXT NOT NULL DEFAULT '',
    citations_json TEXT NOT NULL DEFAULT '[]',
    known INTEGER NOT NULL DEFAULT 0,
    generation_prompt TEXT NOT NULL DEFAULT '',
    guardrail_blocked INTEGER NOT NULL DEFAULT 0,
    guardrail_json TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS idx_decisions_run ON decisions (run_id);
CREATE INDEX IF NOT EXISTS idx_decisions_ticket ON decisions (ticket_id);
"""


def sources_from(passages) -> list[dict]:
    """The part of a retrieval result worth keeping: identity and score."""
    records = []
    for passage in passages or []:
        citation = passage.citation() if hasattr(passage, "citation") else passage.doc_id
        records.append(
            {
                "doc_id": passage.doc_id,
                "similarity": round(float(passage.similarity), 4),
                "citation": citation,
            }
        )
    return records


class DecisionLog:
    """Append-only SQLite log. One row per ticket per run.

    Each `record` call commits immediately. A run that dies on ticket 40 must
    still have tickets 1 to 39 on disk, because those decisions were made and
    A8 counts gaps as failures.
    """

    def __init__(self, path: str):
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def record(
        self,
        ticket: Ticket,
        classification: Classification,
        decision: RoutingDecision,
        passages: list = None,
        run_id: str = "unspecified",
        answer: str = "",
        citations: list = None,
        known: bool = False,
        generation_prompt: str = "",
        guardrail_blocked: bool = False,
        guardrail_findings: list = None,
    ) -> int:
        """Write one decision. Returns the row id.

        Generation and guardrail fields default to empty so a ticket that
        never reached a draft is still logged. A8 counts that row; it does
        not require every ticket to have been answered.
        """
        cursor = self._conn.execute(
            """
            INSERT INTO decisions (
                run_id, recorded_at, ticket_id, channel,
                customer_tier, customer_region, language_fluency,
                subject, body, intent, urgency, confidence,
                alternatives_json, prompt_version, degraded,
                sources_json, action, rule, reason, threshold,
                answer, citations_json, known, generation_prompt,
                guardrail_blocked, guardrail_json
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?
            )
            """,
            (
                run_id,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                ticket.ticket_id,
                ticket.channel,
                ticket.customer_tier,
                ticket.customer_region,
                ticket.language_fluency,
                ticket.subject,
                ticket.body,
                classification.intent,
                classification.urgency,
                classification.confidence,
                json.dumps(classification.alternatives),
                classification.prompt_version,
                int(classification.degraded),
                json.dumps(sources_from(passages)),
                decision.action,
                decision.rule,
                decision.reason,
                decision.threshold,
                answer,
                json.dumps(citations or []),
                int(known),
                generation_prompt,
                int(guardrail_blocked),
                json.dumps(guardrail_findings or []),
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def count(self, run_id: str = None) -> int:
        if run_id is None:
            row = self._conn.execute("SELECT COUNT(*) AS n FROM decisions").fetchone()
        else:
            row = self._conn.execute(
                "SELECT COUNT(*) AS n FROM decisions WHERE run_id = ?", (run_id,)
            ).fetchone()
        return row["n"]

    def for_run(self, run_id: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM decisions WHERE run_id = ? ORDER BY id", (run_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def reconcile(self, run_id: str, tickets_processed: int) -> dict:
        """A8: logged decisions must equal tickets processed, with no gaps."""
        logged = self.count(run_id)
        return {
            "run_id": run_id,
            "logged": logged,
            "processed": tickets_processed,
            "complete": logged == tickets_processed,
        }
