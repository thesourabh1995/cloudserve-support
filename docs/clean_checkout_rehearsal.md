# Clean-checkout rehearsal

Evidence for A1 and for the pass/fail gate. The gate is that the repository is cloned onto a machine that is not the author's, the README is followed literally, and the harness processes the whole ticket set in one unattended run.

Rehearsed on 11 November 2026 by cloning from the remote into an empty directory with no Chroma index, no response cache, no `.env` and no environment variables set, and then doing only what the README says, in the order it says it.

## What was run

```
git clone https://github.com/thesourabh1995/cloudserve-support.git
cp .env.example .env            # key pasted in, as an assessor would
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m evaluation.harness --input data/sample_tickets.json --output evaluation/results/run1
PORT=8021 .venv/bin/python -m src.api
```

## Result

| Step | Outcome |
|---|---|
| Clone | Succeeded. `data/documentation.json` present, ticket sets correctly absent |
| Dependency install | Clean from the pinned `requirements.txt`, 33 seconds, no resolution conflicts |
| Test suite | 148 passed, 36 seconds, no network and no API key needed |
| Index build | Built itself on first search: 59 passages from 29 articles, unprompted |
| Unattended run | 12 tickets in 57 seconds. 8 answered, 3 escalated, 1 blocked by a guardrail. 12 of 12 logged, reconciled |
| Report | `metrics.md`, `metrics.json`, `outcomes.jsonl` and `decisions.db` all written. Every outcome row carried its routing rule |
| Local console | Started, served the form, answered a ticket with a resolving citation |

No step needed intervention beyond pasting an API key, which the README asks for.

## Two defects it found

Both would have affected the gate, and neither was visible from reading the repository.

**1. The knowledge base was not in the repository.** `data/documentation.json` had been gitignored alongside the course ticket sets. It is not test data: it is the corpus every answer is grounded in. Worse than a crash, the failure was silent — Chroma's `get_or_create_collection` returns an empty collection rather than complaining, so a fresh clone would have run all 120 tickets, escalated every one for want of a supporting passage, and reported a completed run. A failure that looks like success is the hardest kind to notice on someone else's machine.

Fixed three ways: the 40KB corpus is now committed, since the submission guide's constraint is on large files and this is the application's own data; the index builds itself on first search, so the one documented command is sufficient; and a genuinely missing corpus now raises `CorpusMissing` naming the file and where to get it.

**2. The setup instruction produced the wrong Python.** The README said `python3 -m venv .venv` and then asserted that `.venv/bin/python` was 3.11. A virtual environment runs whichever interpreter created it, so on a machine whose `python3` is 3.9.6 that instruction produces a 3.9.6 environment, below the project's floor. The reader's next sight would have been a dependency failure or a `TypeError` on a union annotation, neither of which says what to do.

Fixed by naming the version in the instruction, explaining why it matters, and saying how to check. `src/config.py` additionally raises on import below 3.10 with the same instruction, so getting it wrong produces a sentence rather than a stack trace.

## What this does not prove

The run was 12 tickets, not 120. The scale question is answered separately in `docs/run_cost.md`: the constraint is the provider's per-minute token bucket, which sets a floor on wall clock rather than a ceiling on volume, and the README states the expected 25 to 40 minutes so that a slow run is not mistaken for a hung one.

The machine was the author's, with the same operating system and a Python 3.11 already installed. A genuinely foreign machine could still differ in ways this cannot surface — most plausibly if no Python 3.10+ is present at all, which the version guard now reports clearly but cannot solve.

This rehearsal should be repeated once more immediately before submission, after the final commits.
