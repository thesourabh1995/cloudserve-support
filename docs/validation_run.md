# Validation run: what the numbers say

80 validation tickets, one unattended run, real provider, no cached classifications for most of the set. Full output in `evaluation/results/validation_01/`.

These are validation figures, not hidden-set figures. The Dataset Guide is explicit that the validation set may be used as often as needed and that the report must say plainly where the numbers came from.

## Against the targets

| Measure | Target | Achieved | |
|---|---|---:|---|
| First contact resolution | 60% or better | 68.8% | pass |
| Mean time to first reply | under 5 minutes | 7.5s | pass |
| Classification accuracy | 85% precision | 91.2% | pass |
| Citation accuracy | 95% or better | 98.0% | pass |
| Private data in outbound replies | zero | 0 | pass |
| Escalation rate | 30% or lower | 31.2% | misses by 1.2 points |
| Latency, 95th percentile | under 3 seconds | 13.2s | misses |
| Cross-group variation by tier | under 5 points | 30.4% | misses |
| Satisfaction proxy | 4.0 or better | n/a | needs human review |
| Hallucination rate | 5% or lower | n/a | needs two human reviewers |

The two n/a figures are not omissions. The Evaluation Framework requires a human-scored sample of at least fifty responses with two independent assessors and a reported agreement rate. The harness does not invent a number it cannot measure.

## The tier variation is explained by content, not by tier

This is the figure that looks worst and matters most, so it was decomposed rather than reported raw.

| Tier | n | Answered automatically |
|---|---:|---:|
| enterprise | 8 | 87.5% |
| business | 30 | 80.0% |
| standard | 42 | 57.1% |

Standard-tier tickets are answered automatically 30 points less often than enterprise, which on its face is the system serving cheaper customers worse. The decision log says otherwise. Of the 23 escalations, 14 were `protected_category`, and 11 of those 14 were standard tier. The protected categories are `security_incident`, `compliance_request`, `feature_request` and `unclear_request`.

Those intents are not evenly distributed across tiers in the validation set:

| Tier | Tickets with a protected-category intent |
|---|---:|
| standard | 11 of 42 (26%) |
| business | 2 of 30 (7%) |
| enterprise | 1 of 8 (12%) |

So standard-tier tickets escalate more because more of them are security incidents and unclear requests, which the policy says must go to a human. `src/route.py` does not read `customer_tier`, `customer_region` or `language_fluency` at all; the routing rules are a pure function of the classification and the retrieved passages. The variation is attributable to the input distribution rather than to the protected attribute.

Two caveats that belong in the audit rather than being quietly dropped. The enterprise cell is 8 tickets, so a single ticket moves it by 12.5 points and the ranking between enterprise and business is not meaningful at this sample size. And "explained by content" is not the same as "harmless": if standard-tier customers genuinely send more unclear requests, they still wait longer for an answer, and whether that is acceptable is a policy question for the client, not an engineering one.

## Confidence is not doing the work it was designed to do

The confidence threshold was set to 0.80, the illustrative value in the brief. The distribution shows that choice barely matters:

| Reported confidence | Classification correct |
|---:|---|
| 0.70 | 2 of 3 (67%) |
| 0.80 | 8 of 8 (100%) |
| 0.85 | 1 of 1 (100%) |
| 0.90 | 34 of 39 (87%) |
| 0.92 | 9 of 10 (90%) |
| 0.95 | 19 of 19 (100%) |

Two things follow. The model emits a handful of coarse values clustered at the top, with a median of 0.90 and only 3 of 80 tickets below 0.80, so the threshold fires almost never: `below_threshold` accounted for 2 escalations out of 23. And the relationship with correctness is not monotonic — 0.80 and 0.95 both scored 100% while 0.90 scored 87% — so the number is not a calibrated probability and should not be described as one.

The practical consequence is that the safety of the system rests on the grounding checks and the protected-category rule, not on confidence gating. Raising the threshold would convert correctly-classified 0.90 tickets into escalations and push the escalation rate further above target without a matching accuracy gain. It is left at 0.80 deliberately, and the report should say that confidence is a weak signal rather than implying it is a calibrated one.

## Open items

- **Latency p95 of 13.2s against a 3-second target.** Two sequential model calls on a throttled free tier cannot meet 3 seconds. The target is reachable only by a faster provider or by dropping to one call, and the business target it serves — under 5 minutes to first reply — is met with four orders of magnitude to spare. This needs stating as a deliberate tradeoff rather than a defect.
- **Escalation rate 31.2% against 30%.** Within noise of the target at n=80. The cheapest honest reduction is the single `no_supporting_passage` escalation, not the protected-category rules, which should not be relaxed to hit a number.
- **The two fabricated citations.** The guardrail blocked 2 replies for `unsupported_claim`, which is the control working. Those two tickets are worth reading individually for the report.
