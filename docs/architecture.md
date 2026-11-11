# Architecture notes

Orientation for someone reading the code. The reasoning behind each choice, and the
alternatives that were rejected, is in section 5 of `docs/report.md`; this file says what
is where and which invariants must not be broken.

Diagrams are in `docs/figures/`: `fig1_architecture.svg` is the processing path for one
ticket, `fig2_routing.svg` is the routing order with the outcome of each rule.

## The path a ticket takes

```
ingest -> classify -> retrieve -> route -+-> generate -> guardrails -> answer
                                         |
                                         +-> human queue
```

Every stage writes to one decision row, which is committed before the next ticket is read.

| Module | Responsibility | Criterion |
|---|---|---|
| `src/ingest.py` | Four channel formats into one `Ticket`. Drops `customer_name` | A2 |
| `src/classify.py` | Intent, urgency, confidence and alternatives, via PR-01 | A3 |
| `src/retrieve.py` | Chroma search over the indexed corpus; builds the index on first use | A4 |
| `src/route.py` | Seven ordered rules, first match wins | A5 |
| `src/generate.py` | A reply grounded only in the retrieved passages, via PR-02 | A6 |
| `src/guardrails.py` | Private data and grounding; both block rather than warn | A7 |
| `src/logging_store.py` | One SQLite row per ticket per run, and the reconciliation | A8 |
| `src/killswitch.py` | Presence of a file halts automatic answering | — |
| `src/pipeline.py` | Orchestration, and what to skip when a draft could not be sent | — |
| `evaluation/harness.py` | The unattended run; takes `--input` and `--output` | A9 |
| `evaluation/metrics.py` | The report the run produces by itself | A10 |

## Four invariants worth knowing before you change anything

**`route()` is pure.** It takes a ticket, a classification, passages, a threshold and a
halt status, and returns an action and a reason. It performs no IO and reads no clock. A5
is checked by running the same ticket twice, so anything that makes the result depend on
the moment it ran breaks the acceptance criterion. This is why the kill switch file is read
once per ticket in `pipeline.py` and passed in as an argument rather than read inside
`route()`.

**`route()` reads no customer attribute.** Not tier, not region, not language fluency. The
fairness argument in the report rests on that being structurally true rather than
statistically likely, so adding one would invalidate the audit as well as the behaviour.

**The guardrails cannot be switched off.** There is no flag, no environment variable and no
config key that disables either check. A7 fails outright for a guardrail a run can turn off.

**A missing confidence is low, never high.** When the provider is unreachable or the
response cannot be parsed, classification returns intent `unclear_request` with confidence
`0.0` rather than raising or returning nothing. A missing confidence read downstream as a
high one is the failure that would send unreviewed answers during an outage.

## Where state lives

| Path | Contents | In git |
|---|---|---|
| `data/documentation.json` | The 29-article corpus every answer is grounded in | yes, it is the application's own data |
| `data/sample_tickets.json` | Twelve tickets, three per channel, for the smoke test | yes |
| `data/*_tickets.json`, `ground_truth_responses.json` | Course datasets | no |
| `storage/chroma/` | The vector index, rebuilt from the corpus on demand | no |
| `storage/cache/` | Model responses keyed by content, model and prompt version | no |
| `storage/STOP_AUTOMATION` | The kill switch, when engaged | no, so a clone never arrives halted |
| `evaluation/results/<run>/` | `decisions.db`, `outcomes.jsonl`, `metrics.md`, `metrics.json` | the validation and outage runs only |

The index is built by `ensure_index()` on first search, so the single command in the README
is sufficient on a clean checkout. A genuinely missing corpus raises `CorpusMissing` naming
the file and where to get it, rather than returning an empty collection — which is what it
did before the clean-checkout rehearsal, and which made a failed run look like a completed
one.

## Prompts

`prompts/build/classify.md` (PR-01) and `prompts/build/generate.md` (PR-02) are files
rather than string literals, and the version travels onto every decision row, so "was this
behaviour intended" has an answer after the fact. Both delimit ticket text and declare it
untrusted. Nothing detects a successful injection; that is FR-16, and it is not built.
