# What a run costs, and why the free tier can serve it

The system has to process a ticket set it has never seen, unattended, in one run, on whatever API key the assessor supplies. That key will be a free-tier key. So the cost of a run is an acceptance concern, not a finance one, and it was measured rather than estimated.

## The limits that actually apply

Groq publishes a daily token allowance per model, but the account does not expose one. The live response headers carry only two limits:

| Header | Value | Window |
|---|---:|---|
| `x-ratelimit-limit-requests` | 1,000 | per day |
| `x-ratelimit-limit-tokens` | 8,000 | per minute, continuously refilling |

There is no daily token header. The published figure for `openai/gpt-oss-20b` is 200,000 tokens per day, and the code is budgeted against it, but it could not be confirmed from the account and should be treated as unverified. A clarification question on this has gone to the course provider.

This changes which limit binds. Requests are not the constraint: a 120-ticket run makes roughly 200 calls against an allowance of 1,000. The per-minute token bucket is the constraint, and it sets a floor on wall clock rather than a ceiling on volume. At the measured cost, 120 tickets cannot complete in less than about 22 minutes however fast the machine is. The run is expected to spend much of its time being throttled, which is why the client honours `Retry-After` and allows a backoff ceiling above a full minute.

## Measured cost

From the 80-ticket validation run, uncached, on the real provider:

| | |
|---|---:|
| Tickets | 80 |
| Model calls billed | 130 |
| Tokens billed | 117,751 |
| Tokens per ticket | 1,472 |
| Wall clock | 9.4 minutes |

Split by call:

| Call | Tokens | Calls | Per call |
|---|---:|---:|---:|
| classify | 62,265 | 72 | 865 |
| generate | 55,486 | 58 | 957 |

Fewer than two calls per ticket because generation is skipped where a draft would be unusable, and fewer than 80 classifications because some tickets were already in the response cache.

Extrapolated to the 120-ticket hidden set: about 177,000 tokens and 200 calls. That fits inside the published daily allowance, but not with much room, which is the reason for the reductions below.

## What brought it down

An earlier measurement was 3,278 tokens per ticket, which would have put the hidden set at roughly 393,000 tokens and failed the run outright. Three changes, each measured:

1. **One passage per document.** Retrieval returns chunks, and the top five routinely contained two or three chunks of the same article. `distinct_sources` keeps the best chunk from each of the top three documents instead. Near-duplicate passages cost tokens without adding evidence.
2. **Reasoning effort set per task.** These models bill hidden reasoning as output tokens, and it was the larger half of the original figure. Classification runs at `medium` and generation at `low`. On 18 stratified tickets, classification at `low` scored 88.9% against 94.4% at `medium`, so classification pays for the reasoning; generation does not, because its output is checked by the citation guardrail regardless of how carefully it was produced.
3. **No draft where a draft cannot be sent.** A ticket escalated for a protected category, an unusable classification or an empty body is never drafted, because the answer would be discarded. This is what makes the call count 1.6 per ticket rather than 2.

Combined effect: 1,472 tokens per ticket, down 55%.

## The honest caveat

The second change trades a little accuracy for tokens, and the evidence for it is 18 tickets. One ticket moved. That is suggestive, not conclusive, and if the token budget were not binding the safer setting would be `medium` for both calls.
