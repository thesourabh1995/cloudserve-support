"""Build a sheet for the human hallucination review, and score it once filled.

The Evaluation Framework defines hallucination rate as the proportion of
generated responses containing at least one claim not supported by the
retrieved sources, and says it requires human judgement. The harness therefore
reports it as n/a rather than inventing a figure. This produces the sheet that
judgement is recorded on, and tallies the result afterwards.

The sheet puts each reply next to the full text of every article it cited, so
the reviewer can check a claim without going and finding the documentation.
That is the whole reason the task is slow when done by hand, and it is the
part a script can legitimately remove.

    generate:  python -m analysis.hallucination_review --run <dir>
    score:     python -m analysis.hallucination_review --score docs/hallucination_review.md
"""

import argparse
import json
import os
import re
import sqlite3
import textwrap

from src.retrieve import load_documents

VERDICTS = ("supported", "unsupported", "unclear")


def _articles(path: str) -> dict:
    """doc_id -> the article, so a cited source can be read in full."""
    return {doc["doc_id"]: doc for doc in load_documents(path)}


def build(run_dir: str, docs_path: str, limit: int) -> str:
    connection = sqlite3.connect(os.path.join(run_dir, "decisions.db"))
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "select ticket_id, subject, body, answer, citations_json, sources_json "
        "from decisions where action = 'auto_respond' and answer != '' "
        "order by ticket_id"
    ).fetchall()
    connection.close()

    articles = _articles(docs_path)
    selected = rows[:limit] if limit else rows

    out = [
        "# Hallucination review",
        "",
        f"{len(selected)} generated replies from `{run_dir}`. The Evaluation "
        "Framework asks for at least fifty.",
        "",
        "## How to score this",
        "",
        "For each reply, read the answer, then read the source article under it. "
        "Ask one question: **does every factual claim in the answer follow from "
        "the source text?** A claim the article does not make is unsupported, "
        "even if it happens to be true, and even if it sounds reasonable. "
        "Generic courtesy and offers to escalate are not factual claims.",
        "",
        "Replace the word after `verdict:` with `supported`, `unsupported` or "
        "`unclear`, and write a short note when you mark anything other than "
        "supported. Then run:",
        "",
        "```bash",
        ".venv/bin/python -m analysis.hallucination_review "
        "--score docs/hallucination_review.md",
        "```",
        "",
        "Record who scored it and when. If only one person scored it, the "
        "report must say so: the framework asks for two independent assessors "
        "and an agreement rate, and one assessor cannot produce one.",
        "",
        "- Assessor:",
        "- Date:",
        "",
        "---",
        "",
    ]

    for index, row in enumerate(selected, start=1):
        cited = []
        for citation in json.loads(row["citations_json"] or "[]"):
            if citation["doc_id"] not in cited:
                cited.append(citation["doc_id"])

        out += [
            f"## {index}. {row['ticket_id']}",
            "",
            f"**Ticket.** {row['subject'] or '(no subject)'}",
            "",
            textwrap.fill(row["body"] or "", 88),
            "",
            "**Reply sent.**",
            "",
            textwrap.fill(row["answer"], 88),
            "",
            "**Quoted as support.**",
            "",
        ]
        for citation in json.loads(row["citations_json"] or "[]"):
            quote = citation["supports"].strip().replace("\n", " ")
            out.append(f"- `{citation['doc_id']}` — \"{quote}\"")
        out.append("")

        for doc_id in cited:
            article = articles.get(doc_id)
            out += [
                f"**Source: {doc_id} — {article['title'] if article else 'NOT IN CORPUS'}**",
                "",
            ]
            if article is None:
                # A citation to a document that is not in the corpus is a
                # finding in itself, not something for the reviewer to puzzle over.
                out += ["> This document is not in the knowledge base.", ""]
            else:
                body = article.get("content") or article.get("body") or ""
                out += [textwrap.indent(textwrap.fill(body, 86), "> "), ""]

        out += [
            "verdict: UNSCORED",
            "",
            "note:",
            "",
            "---",
            "",
        ]

    return "\n".join(out)


def score(path: str) -> dict:
    """Tally a filled sheet. Refuses to guess at anything left unscored."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()

    found = [match.lower() for match in re.findall(r"^verdict:\s*(\S+)", text, re.M)]
    tally = {verdict: found.count(verdict) for verdict in VERDICTS}
    unscored = [item for item in found if item not in VERDICTS]

    total = len(found)
    judged = sum(tally.values())
    report = {
        "responses_in_sheet": total,
        "scored": judged,
        "unscored": len(unscored),
        **tally,
    }
    if judged:
        # The framework's definition: a response counts against us if it
        # contains any unsupported claim. "unclear" is counted separately
        # rather than folded into either side.
        report["hallucination_rate"] = round(tally["unsupported"] / judged, 4)
    return report


def main(argv=None) -> dict:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", help="a finished results directory")
    parser.add_argument("--docs", default="data/documentation.json")
    parser.add_argument("--limit", type=int, default=0, help="0 means every reply")
    parser.add_argument("--output", default="docs/hallucination_review.md")
    parser.add_argument("--score", help="tally an already-filled sheet")
    args = parser.parse_args(argv)

    if args.score:
        report = score(args.score)
        for key, value in report.items():
            print(f"{key}: {value}")
        if report["unscored"]:
            print(
                f"\n{report['unscored']} replies are still UNSCORED. "
                "The rate above is only over the ones you have judged."
            )
        return report

    if not args.run:
        parser.error("--run is required unless you are scoring with --score")

    if os.path.exists(args.output):
        parser.error(
            f"{args.output} already exists. Scoring is manual work; refusing to "
            "overwrite it. Move it aside first if you really want a fresh sheet."
        )

    text = build(args.run, args.docs, args.limit)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(text)
    scorable = len(re.findall(r"^verdict:", text, re.M))
    print(f"wrote {args.output}: {scorable} replies to score")
    return {}


if __name__ == "__main__":
    main()
