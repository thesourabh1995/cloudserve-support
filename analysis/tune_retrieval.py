"""Choose the chunking configuration from measurement rather than from defaults.

The setup guide supplies chunk_size=800, overlap=120 and says plainly that
these are a starting point and that the choice is a design decision to be
justified. This script provides the justification.

Every development ticket labelled `answerable_from_docs` carries the
`expected_doc_ids` a correct answer should cite, which gives a direct measure:
for what share of those tickets does retrieval surface at least one of the
expected articles in its top k?

    python -m analysis.tune_retrieval --output docs/retrieval_tuning.md
"""

import argparse
import json
import shutil
import tempfile

from src.ingest import load_tickets
from src.retrieve import Retriever, load_documents

CONFIGURATIONS = [
    (400, 80),
    (600, 100),
    (800, 120),   # the pack's suggested starting point
    (1200, 200),
    (1600, 240),
]


def expected_doc_ids(tickets_path: str) -> dict[str, list[str]]:
    """Ticket id -> the articles a correct answer should cite."""
    with open(tickets_path, encoding="utf-8") as handle:
        records = json.load(handle)
    wanted = {}
    for record in records:
        labels = record.get("labels", {})
        if labels.get("answerable_from_docs") and labels.get("expected_doc_ids"):
            wanted[record["ticket_id"]] = labels["expected_doc_ids"]
    return wanted


def evaluate(chunk_size, chunk_overlap, tickets, wanted, documents, min_similarity):
    """Index at this configuration and measure recall at 1, 3 and 5."""
    workspace = tempfile.mkdtemp(prefix="tune_")
    try:
        retriever = Retriever(
            chroma_path=workspace,
            collection_name=f"tune_{chunk_size}_{chunk_overlap}",
            min_similarity=min_similarity,
        )
        # Patch the configuration for this run only.
        import src.retrieve as retrieve_module

        original = (retrieve_module.settings.chunk_size, retrieve_module.settings.chunk_overlap)
        object.__setattr__(retrieve_module.settings, "chunk_size", chunk_size)
        object.__setattr__(retrieve_module.settings, "chunk_overlap", chunk_overlap)
        passages = retriever.index(documents)
        object.__setattr__(retrieve_module.settings, "chunk_size", original[0])
        object.__setattr__(retrieve_module.settings, "chunk_overlap", original[1])

        hits = {1: 0, 3: 0, 5: 0}
        empty = 0
        evaluated = 0

        for ticket in tickets:
            if ticket.ticket_id not in wanted:
                continue
            evaluated += 1
            expected = set(wanted[ticket.ticket_id])
            results = retriever.search(ticket.text, top_k=5)
            if not results:
                empty += 1
                continue
            returned = [p.doc_id for p in results]
            for k in (1, 3, 5):
                if expected & set(returned[:k]):
                    hits[k] += 1

        return {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "passages": passages,
            "evaluated": evaluated,
            "recall_at_1": 100.0 * hits[1] / evaluated if evaluated else 0.0,
            "recall_at_3": 100.0 * hits[3] / evaluated if evaluated else 0.0,
            "recall_at_5": 100.0 * hits[5] / evaluated if evaluated else 0.0,
            "returned_nothing": 100.0 * empty / evaluated if evaluated else 0.0,
        }
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tickets", default="data/development_tickets.json")
    parser.add_argument("--docs", default="data/documentation.json")
    parser.add_argument("--min-similarity", type=float, default=0.30)
    parser.add_argument("--output", default="docs/retrieval_tuning.md")
    args = parser.parse_args()

    tickets = load_tickets(args.tickets)
    wanted = expected_doc_ids(args.tickets)
    documents = load_documents(args.docs)

    print(f"measuring {len(CONFIGURATIONS)} configurations "
          f"against {len(wanted)} answerable tickets\n")

    rows = []
    for chunk_size, chunk_overlap in CONFIGURATIONS:
        print(f"  chunk_size={chunk_size} overlap={chunk_overlap} ...", flush=True)
        rows.append(
            evaluate(chunk_size, chunk_overlap, tickets, wanted, documents, args.min_similarity)
        )

    best = max(rows, key=lambda r: r["recall_at_3"])

    lines = [
        "# Retrieval chunking: measured, not assumed",
        "",
        f"Measured against the {rows[0]['evaluated']} development tickets labelled "
        "`answerable_from_docs` that carry `expected_doc_ids`. A hit means retrieval "
        "surfaced at least one of the expected articles within the top k. Similarity "
        f"floor {args.min_similarity}.",
        "",
        "| Chunk size | Overlap | Passages | Recall@1 | Recall@3 | Recall@5 | Returned nothing |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        marker = " **(chosen)**" if row is best else ""
        lines.append(
            f"| {row['chunk_size']}{marker} | {row['chunk_overlap']} | {row['passages']} | "
            f"{row['recall_at_1']:.1f}% | {row['recall_at_3']:.1f}% | {row['recall_at_5']:.1f}% | "
            f"{row['returned_nothing']:.1f}% |"
        )

    lines += [
        "",
        f"Chosen: **chunk_size={best['chunk_size']}, overlap={best['chunk_overlap']}**, "
        f"on recall@3 of {best['recall_at_3']:.1f}%.",
        "",
        "Recall@3 is the figure the choice turns on, because generation is given the "
        "top passages rather than only the first, so an expected article appearing at "
        "rank two or three is still available to be cited.",
        "",
        "The 'returned nothing' column matters independently. Those are tickets the "
        "labels say are answerable from the documentation where retrieval found no "
        "passage above the floor. They become escalations, which is safe but is the "
        "cost side of the threshold, and it is the figure to revisit if the escalation "
        "rate comes in above target.",
    ]

    with open(args.output, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines[4:]))
    print(f"\nWritten to {args.output}")


if __name__ == "__main__":
    main()
