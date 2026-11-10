# Choosing the classification model

Reproduce with `python -m analysis.compare_models`.
Raw results in `docs/model_comparison.json`.

## The constraint that shaped the choice

The project brief names Groq and OpenRouter as the free options. The decision
between them is not about quality, it is about whether a full run can finish.

| | OpenRouter (free) | Groq (free) |
|---|---|---|
| Requests/day | 50, until the account buys $10 of credits | 1,000 |
| Requests/minute | 20 | 30 |
| Tokens/minute | — | 8,000 |

A full pass over the 500-ticket development set needs one classification call
per ticket plus one generation call for every ticket that routes to
auto-respond, so roughly 800 calls. OpenRouter's 50/day makes that impossible
without paying, and the project instructions rule paying out explicitly:

> If you find yourself unable to finish a run within a free allowance, raise it
> rather than paying; it almost always indicates a design problem worth fixing.

So Groq, with OpenRouter retained as a configured fallback.

The Groq limits above are read from the `x-ratelimit-*` response headers on
this account, not from documentation. Worth doing: most published summaries
list `llama-3.1-8b-instant` at 14,400 requests/day, but the Llama models are no
longer in Groq's catalogue at all. The candidates below are what the account
can actually reach, confirmed against the models endpoint.

## Candidates measured

18 development tickets, one per intent, stratified so no single class
dominates. Temperature 0. Accuracy is against `labels.intent`.

| Model | Accuracy | Malformed JSON | Tokens/ticket | 500-ticket pass | Est. minutes |
|---|---|---|---|---|---|
| `openai/gpt-oss-20b` | **94.4%** | 0 | 863 | 431,472 | 54 |
| `qwen/qwen3.8-27b` | 88.9% | 0 | 656 | 328,083 | 41 |
| `openai/gpt-oss-120b` | 88.9% | 0 | 799 | 399,611 | 50 |

## Decision

`openai/gpt-oss-20b`. Most accurate, and the token premium over the cheaper
Qwen model costs 13 extra minutes on a full pass rather than money.

Two results are worth noting beyond the ranking.

**The largest model was not the most accurate.** `gpt-oss-120b` scored the same
as the 27B Qwen and below the 20B, while costing more tokens than either. On a
short, heavily constrained classification task there is nothing for the extra
capacity to do, and this is direct evidence for the brief's claim that a
well-built system on a small model beats a thin one on an expensive model.

**Zero malformed responses across all three models and 54 calls.** The
delimiting and schema instructions in prompt PR-01 are holding. The fallback
path still exists and is tested, but it is not currently load-bearing — which
is the right way round.

## What this does not yet tell us

Accuracy on 18 tickets has a wide confidence interval; this sizes the field, it
does not settle performance. The headline accuracy number for the report comes
from the full evaluation run on the validation set.

The estimate of 54 minutes covers classification only. Generation carries
retrieved article text and will cost substantially more per call, so the
end-to-end run time is not yet known.

## The open risk

Classification alone is 500 of the 1,000 daily requests. Adding generation puts
a full end-to-end run at roughly 800, leaving little room to re-run after a
failure on the same day. Two things mitigate it: responses are cached on disk
and keyed by model and prompt, so a repeat run costs nothing, and the harness
can be pointed at a subset. It remains the main scheduling risk for the final
week, and it bears on the A9 gate, where an assessor runs the harness on their
own key.
