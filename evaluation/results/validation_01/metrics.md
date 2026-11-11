# Evaluation run

Produced by the harness. Figures that need a labelled file are marked n/a when the input had no labels.

| Measure | Baseline | Target | Achieved | Notes |
|---|---|---|---|---|
| First contact resolution | 42% | 60% or better | 68.8% | Share of tickets answered with no person involved. |
| Mean time to first reply | 8 to 12 hours | Under 5 minutes | 7.47s | Processing time of the tickets that were answered. Median 8.36s. |
| Satisfaction proxy | 3.2 / 5 | 4.0 or better | n/a | Needs a human review of a sample. This run does not invent one. |
| Escalation rate | 58% | 30% or lower | 31.2% | Escalated and blocked tickets. Both leave the queue for a person. |
| Classification accuracy | — | 85% precision | 91.2% | Per-class precision and recall are in the JSON report. |
| Hallucination rate | — | 5% or lower | n/a | The framework requires two human reviewers of at least fifty replies. |
| Citation accuracy | — | 95% or better | 98.0% | 100 of 102 citations resolved to a retrieved passage. |
| Latency, 95th percentile | — | Under 3 seconds | 13.20s | End to end, including retrieval and both model calls. Mean 7.04s. |
| Private data in outbound replies | — | Zero | 0 | Guardrail activations: {'unsupported_claim': 2}. |
| Cross-group variation, by tier | — | Under 5 points | 30.4% | Spread in automatic-answer rate across customer tiers. |

## Volume

- Tickets processed: 80
- Answered automatically: 55
- Escalated: 23
- Blocked by guardrails: 2

## Governance

- Decisions logged: 80 of 80
- Log reconciles: True

## Cost of the run

- Model calls billed: 130
- Tokens billed: 117,751 (1471.9 per ticket)
- Wall clock: 9.4 minutes
  - classify: 62,265 tokens over 72 calls
  - generate: 55,486 tokens over 58 calls

Cache hits are excluded, so these are what the provider actually charged.

Retrieval hit rate: 98.1% (52 of 53 tickets with an expected document).
