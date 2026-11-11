# Fairness audit

Every figure carries a 95% confidence interval, because several of these groups are small enough that a point estimate on its own would overstate what the run shows.

## Customer tier

| Group | n | Answered automatically | Classification accuracy | Retrieval hit rate | Citations resolved |
|---|---:|---|---|---|---|
| standard | 42 | 57% (42%–71%) | 93% (81%–98%) | 96% (80%–99%) | 95% (84%–99%) |
| business | 30 | 80% (63%–90%) | 90% (74%–97%) | 100% (85%–100%) | 100% (93%–100%) |
| enterprise * | 8 | 88% (53%–98%) | 88% (53%–98%) | 100% (61%–100%) | 100% (74%–100%) |

Spread in automatic-answer rate: **30.4 points** (condition: under 5).

\* Fewer than 15 tickets. Reported for completeness, not relied on.

## Language fluency

| Group | n | Answered automatically | Classification accuracy | Retrieval hit rate | Citations resolved |
|---|---:|---|---|---|---|
| fluent | 61 | 72% (60%–82%) | 90% (80%–95%) | 98% (88%–100%) | 97% (91%–99%) |
| non_fluent | 19 | 58% (36%–77%) | 95% (75%–99%) | 100% (70%–100%) | 100% (87%–100%) |

Spread in automatic-answer rate: **14.2 points** (condition: under 5).

## Region

| Group | n | Answered automatically | Classification accuracy | Retrieval hit rate | Citations resolved |
|---|---:|---|---|---|---|
| north_america | 27 | 74% (55%–87%) | 89% (72%–96%) | 93% (69%–99%) | 100% (90%–100%) |
| europe | 25 | 68% (48%–83%) | 92% (75%–98%) | 100% (83%–100%) | 97% (86%–100%) |
| asia_pacific | 21 | 71% (50%–86%) | 90% (71%–97%) | 100% (82%–100%) | 97% (83%–99%) |
| latin_america * | 7 | 43% (16%–75%) | 100% (65%–100%) | 100% (44%–100%) | 100% (51%–100%) |

Spread in automatic-answer rate: **31.2 points** (condition: under 5).

\* Fewer than 15 tickets. Reported for completeness, not relied on.

## Ticket length

| Group | n | Answered automatically | Classification accuracy | Retrieval hit rate | Citations resolved |
|---|---:|---|---|---|---|
| medium (20 to 39 words) | 56 | 73% (60%–83%) | 95% (85%–98%) | 98% (87%–100%) | 97% (91%–99%) |
| short (under 20 words) | 22 | 55% (35%–73%) | 86% (67%–95%) | 100% (74%–100%) | 100% (86%–100%) |
| long (40 words or more) * | 2 | 100% (34%–100%) | 50% (9%–91%) | 100% (34%–100%) | 100% (61%–100%) |

Spread in automatic-answer rate: **45.5 points** (condition: under 5).

\* Fewer than 15 tickets. Reported for completeness, not relied on.

## Mechanism: which rule escalated whom

### Language fluency

| Group | n | Must-not-auto-respond by label | Escalations by rule | Mean stated confidence | Classification accuracy |
|---|---:|---:|---|---:|---:|
| fluent | 61 | 18% | live_incident 3, no_supporting_passage 1, protected_category 11 | 0.907 | 90% |
| non_fluent | 19 | 16% | below_threshold 2, live_incident 1, protected_category 3 | 0.863 | 95% |

### Ticket length

| Group | n | Must-not-auto-respond by label | Escalations by rule | Mean stated confidence | Classification accuracy |
|---|---:|---:|---|---:|---:|
| medium (20 to 39 words) | 56 | 11% | below_threshold 1, live_incident 3, no_supporting_passage 1, protected_category 6 | 0.908 | 95% |
| short (under 20 words) | 22 | 36% | below_threshold 1, live_incident 1, protected_category 8 | 0.866 | 86% |
| long (40 words or more) | 2 | 0% | none | 0.900 | 50% |
