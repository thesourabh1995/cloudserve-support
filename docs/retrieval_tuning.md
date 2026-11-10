# Retrieval chunking: measured, not assumed

Measured against the 357 development tickets labelled `answerable_from_docs` that carry `expected_doc_ids`. A hit means retrieval surfaced at least one of the expected articles within the top k. Similarity floor 0.3.

| Chunk size | Overlap | Passages | Recall@1 | Recall@3 | Recall@5 | Returned nothing |
|---:|---:|---:|---:|---:|---:|---:|
| 400 | 80 | 141 | 89.6% | 92.4% | 94.7% | 0.0% |
| 600 | 100 | 86 | 89.1% | 93.3% | 94.4% | 0.8% |
| 800 **(chosen)** | 120 | 59 | 89.6% | 94.7% | 96.1% | 0.6% |
| 1200 | 200 | 33 | 89.9% | 94.4% | 94.7% | 0.8% |
| 1600 | 240 | 29 | 89.6% | 94.1% | 94.4% | 0.8% |

Chosen: **chunk_size=800, overlap=120**, on recall@3 of 94.7%.

Recall@3 is the figure the choice turns on, because generation is given the top passages rather than only the first, so an expected article appearing at rank two or three is still available to be cited.

The 'returned nothing' column matters independently. Those are tickets the labels say are answerable from the documentation where retrieval found no passage above the floor. They become escalations, which is safe but is the cost side of the threshold, and it is the figure to revisit if the escalation rate comes in above target.
