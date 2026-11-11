# Evaluation run

Produced by the harness. Figures that need a labelled file are marked n/a when the input had no labels.

| Measure | Baseline | Target | Achieved | Notes |
|---|---|---|---|---|
| First contact resolution | 42% | 60% or better | 0.0% | Share of tickets answered with no person involved. |
| Mean time to first reply | 8 to 12 hours | Under 5 minutes | n/a | Processing time of the tickets that were answered. Median n/a. |
| Satisfaction proxy | 3.2 / 5 | 4.0 or better | n/a | Needs a human review of a sample. This run does not invent one. |
| Escalation rate | 58% | 30% or lower | 100.0% | Escalated and blocked tickets. Both leave the queue for a person. |
| Classification accuracy | — | 85% precision | 0.0% | Per-class precision and recall are in the JSON report. |
| Hallucination rate | — | 5% or lower | n/a | The framework requires two human reviewers of at least fifty replies. |
| Citation accuracy | — | 95% or better | n/a | 0 of 0 citations resolved to a retrieved passage. |
| Latency, 95th percentile | — | Under 3 seconds | 2.48s | End to end, including retrieval and both model calls. Mean 0.63s. |
| Private data in outbound replies | — | Zero | 0 | Guardrail activations: none. |
| Cross-group variation, by tier | — | Under 5 points | 0.0% | Spread in automatic-answer rate across customer tiers. |

## Volume

- Tickets processed: 6
- Answered automatically: 0
- Escalated: 6
- Blocked by guardrails: 0

## Governance

- Decisions logged: 6 of 6
- Log reconciles: True

Retrieval hit rate: 100.0% (3 of 3 tickets with an expected document).
