# Stage 4 — Sprint plan

Written as a plan in `PROJECT_PLAN.md` before the build and recorded here with what actually happened against it. The delivery plan was triaged from the outset: the available time was roughly a third of what the pack is written for, so the plan protected the pass/fail gate and the highest-weight marks and deliberately made some sections thin.

## 1. Capacity

| Week | Hours realistically available | Other commitments | Days unavailable |
|---|---|---|---|
| Week one (6–8 Nov) | ~4/day planned | *to be completed from your own record* | — |
| Week two (9–15 Nov) | ~4/day planned, 6–8 on the final day | *to be completed* | — |
| Week three | Not available — the deadline falls on 15 November | — | — |

**Planned total: ~40 hours against a programme written for roughly three times that.** Actual hours belong in the effort log and only you can supply them; the commit history shows concentrated work on 8, 10 and 11 November rather than evenly spread, which is worth stating honestly rather than smoothing.

Working alone removes coordination overhead and replaces it with nobody noticing when you are stuck. The rule adopted was to write down anything blocking for more than an hour; in practice the blockers that cost most — the provider retiring its Llama models, and the response cache serving tests each other's answers — were recorded in `docs/report_notes.md` as they happened, which is why they could be written up accurately afterwards.

## 2. The backlog

Priority: **M** must, **S** should, **C** could.

| ID | Item | Est. | Pri | Depends on | Definition of done | Outcome |
|---|---|---:|:---:|---|---|---|
| B-01 | Environment and dependency setup | 1.5 | M | — | A real model call returns real text | Done. The pack's pins do not resolve at all; replaced and documented |
| B-02 | Data loading and normalisation | 2.5 | M | B-01 | One `Ticket` from all four channels, no failures across the supplied sets | Done. 580 tickets, zero parse issues |
| B-03 | Chunking and embedding | 1.0 | M | B-02 | Two configurations measured, choice recorded with the figure | Done. Five measured; 800/120 on recall@3 |
| B-04 | Vector store and retrieval | 1.0 | M | B-03 | Ranked passages with resolvable IDs; returns nothing when nothing is relevant | Done |
| B-05 | Evaluation harness | 2.5 | M | B-02 | One command taking `--input` and `--output`, producing a metrics report unaided | Done |
| B-06 | Intent and urgency classifier | 2.0 | M | B-02 | Intent, urgency, numeric confidence, alternatives, defined fallback | Done. 91.2% accuracy |
| B-07 | Routing and thresholds | 1.5 | M | B-06 | Deterministic; protected categories never auto-answered | Done. Pure function, seven ordered rules |
| B-08 | Generation with citations | 1.5 | M | B-04 | Every citation resolves to a retrieved passage | Done. 98.0% |
| B-09 | Guardrails that block | 1.5 | M | B-08 | At least one check that blocks and cannot be disabled | Done. Two, both blocking |
| B-10 | Decision log | 1.0 | M | B-07 | Every decision has a reason; counts reconcile | Done. 80 of 80 |
| B-11 | Resilience and degradation | 1.5 | M | B-05 | Provider disconnected entirely; run completes | Done. Verified on uncached tickets |
| B-12 | Tests and CI | 1.0 | M | B-09 | Green in CI from one documented command, no key required | Done. 148 tests |
| B-13 | Full unattended evaluation run | 1.0 | M | B-05, B-11 | Whole file processed, report produced, log reconciles | Done. 80 tickets, 9.4 min |
| B-14 | Fairness audit and calibration | 1.5 | M | B-13 | Segmented by tier, fluency, region, length, per stage | Done |
| B-15 | Governance: register, incident response, kill switch | 1.5 | M | B-10 | A stop control that works without a deployment | Done, and the kill switch was built rather than declared missing |
| B-16 | Clean-checkout rehearsal | 1.0 | M | B-12 | Fresh clone, README followed literally, run completes | Done early. Found two gate-breaking defects |
| B-17 | Hallucination review | 2.0 | M | B-13 | At least fifty replies scored against the rubric | **Sheet built, scoring outstanding** |
| B-18 | Workbooks and PRD revision | 4.0 | M | B-13 | All five stages complete; revision has a real trigger | Stages 1–5 drafted |
| B-19 | Report | 3.0 | M | B-18 | Ten prescribed sections, every figure referenced | **Outstanding** |
| B-20 | Video | 2.5 | M | B-19 | 20 minutes, 7+ of real demo, author on camera | **Outstanding** |
| B-21 | Packaging and submission | 1.0 | M | B-19, B-20 | Four top-level folders, history scanned for credentials | **Outstanding** |
| B-22 | Prometheus counters endpoint | 0.5 | C | B-10 | Endpoint serves counters | **Dropped.** No acceptance criterion needs it |
| B-23 | FR-17 documentation freshness check | 1.0 | S | B-04 | A cited article past its review window is flagged | **Not built.** Recorded as an open requirement and a governance precondition |
| B-24 | FR-15 automated-reply disclosure | 0.5 | S | B-08 | The customer is told the reply was drafted automatically | **Not built.** Requested directly by a customer in discovery |

## 3. Sequencing, and whether the three rules held

The pack's three rules were followed, and one of them mattered more than expected.

**Retrieval and the harness early.** Both were built before generation and guardrails. This was correct: the harness is what surfaced the token cost that would have failed the gate, and it could only do that because it existed before the expensive components did.

**Definition of done written before work starts.** Held for the build items. It did not hold for the documentation items, which is visible above in how vague B-18 and B-19 are compared with B-01 to B-16.

**The full unattended run in week two, not week three.** Held, and the plan's contingency named Thursday 12 November as the point to stop adding capability if the run was not working. The run worked on 11 November, a day early, which is the reason there was time to do the clean-checkout rehearsal properly instead of on the final afternoon.

## 4. What was dropped, and in what order

The plan fixed the drop order in advance so the decision would be made calmly rather than at midnight: intent breadth first, then the Prometheus endpoint, then report length toward the twenty-page floor. In the event only the Prometheus endpoint was dropped, plus two **Should** requirements (B-23, B-24) which are recorded as unbuilt requirements rather than silently abandoned.

The plan's instruction never to drop the video stands. It is 10% of the marks on its own and cannot be reconstructed afterwards.
