# PRD revision log — version 1.0 to 2.0

## 1. Revision summary

| Field | Value |
|---|---|
| New version number | 2.0 |
| Date of revision | 11 November 2026 |
| Carried out by | thesourabh1995 |
| Reviewed and agreed by | No second party exists on an individual project. Each change below is justified by a measurement or a run that can be reproduced, which is the substitute for an approver |
| Requirements changed | 6 |
| Requirements added | 3 |
| Requirements removed | 0 |

Every trigger below is a specific thing that happened during the build, with the artefact it is recorded in. Nothing here is a wording change.

## 2. The changes

| ID | Version 1.0 | Version 2.0 | What prompted the change |
|---|---|---|---|
| FR-03 | Confidence shall express the probability that the intent is correct, and routing shall gate on a 0.80 threshold as a safety control | Confidence is recorded and the threshold retained, but it is **not** a safety control and the PRD no longer describes it as one. Safety rests on the protected-category rule and the grounding guardrail | The validation run's calibration table. Correctness is not monotonic in confidence: 0.80 and 0.95 both scored 100% while 0.90 scored 87%, and only 3 of 80 tickets fell below the threshold at all, producing 2 of 23 escalations. A control that fires twice in eighty tickets is not what is keeping customers safe. `docs/validation_run.md` |
| FR-04 | Retrieval shall return the top passages above the relevance floor | Retrieval returns the best passage from each of the top *distinct documents*, not the top chunks | Token measurement. The top five chunks routinely contained two or three chunks of the same article, costing tokens without adding evidence. `docs/run_cost.md` |
| FR-05 | The system shall draft an answer for every ticket not excluded by a protected category | Generation is skipped wherever a draft could not be sent — protected category, unusable classification, empty ticket, or automation halted | Cost decomposition. Drafting a reply that is discarded by policy spends tokens on text nobody reads, and took the call count from 2.0 per ticket to 1.6 |
| FR-13 | The system shall report outcomes split by customer tier and language fluency | Outcomes are split by tier, region, fluency **and ticket length**, and reported per pipeline stage rather than only on the final outcome | The raw outcome spread failed the five-point condition on every dimension while every pipeline stage was flat. Reporting only the outcome would have described discrimination the system does not perform; reporting only the stages would have hidden a real disparity in confidence. Both are needed. `docs/fairness_audit.md` |
| NFR-01 | 95th-percentile latency under 3 seconds | Target recorded as **not met and not reachable** on this architecture, declared as a tradeoff against the business requirement it serves | Measured 13.2s p95. Two sequential model calls on a rate-limited free tier cannot reach 3 seconds. The business target behind it — under five minutes to first reply — is met at 7.5s with four orders of magnitude to spare, so the architecture is not wrong, the technical target was |
| NFR-07 | A full run shall complete within a free-tier allowance | Restated with a measured per-ticket token budget, and the binding limit identified as tokens per minute rather than per day | First measurement was 3,278 tokens per ticket, projecting to roughly 393,000 tokens for the hidden set against a published daily allowance of 200,000. The gate run would have failed on an assessor's key. Reduced to 1,472 |

### Requirements added

| ID | Requirement | Why it was not in version 1.0 |
|---|---|---|
| FR-12 | Automatic answering shall be stoppable immediately without a deployment, and the stop shall be recorded | The Governance Framework states that a system of this kind needs a stop control and that not having one is itself the first governance finding. Version 1.0 had treated governance as logging and guardrails, and had no answer to "how do you turn it off at 2am" |
| FR-16 | The system shall detect, not merely discourage, a successful prompt injection | Version 1.0 treated delimiting and declaring ticket text untrusted as sufficient. It is a mitigation with no detector, which became clear when the risk register asked what in the design would stop the harm |
| FR-17 | The system shall check that a cited article is still within its review cycle | Discovered while building the hallucination review sheet: the corpus carries `last_reviewed_days_ago` and nothing reads it. Every control in the system checks that a claim matches the corpus; none checks that the corpus matches reality |

All three additions are **Should**, and FR-16 and FR-17 are **not built**. They are recorded as requirements rather than as ideas because an assessor comparing the evidence to the system will find the gap either way.

## 3. Assumptions that turned out to be wrong

| Assumption from version 1.0 | Held? | What was found instead | What changed because of it |
|---|---|---|---|
| A numeric confidence from the model reflects the real probability of being correct | **No** | Correctness is not monotonic in stated confidence, and the distribution is clustered at the top: median 0.90, only 3 of 80 below 0.80 | FR-03 rewritten. The threshold stays at 0.80 but is no longer described as a safety control, and the report is required to say confidence is a weak signal rather than a calibrated probability |
| Retrieval will perform worse on non-fluent English | **No — and this is the useful one** | Retrieval hit rate was 100% on non-fluent tickets against 98% on fluent. The most likely reason is that every indexed chunk carries its article title, a decision taken during retrieval tuning for an unrelated reason. What *did* appear is that the model reports lower confidence on non-fluent tickets while classifying them more accurately | FR-13 changed to audit every stage rather than the expected one. The fairness audit would have found nothing had it only looked where the framework predicted |
| A free-tier allowance is sufficient for one unattended run over the hidden set | **Only after work** | At the original cost it was not. 3,278 tokens per ticket projected to roughly twice the published daily allowance | NFR-07 restated with a measured budget. Three changes to the pipeline brought per-ticket cost down 55% |
| 95th-percentile latency under 3 seconds is achievable | **No** | 13.2s measured, caused by two sequential calls against a per-minute token bucket | NFR-01 restated as a declared tradeoff rather than a defect |
| The published per-day token allowance is the binding cost constraint | **No** | The account exposes no daily token limit at all: only 1,000 requests per day and a continuously refilling 8,000 per minute. The per-minute bucket sets a floor on wall clock rather than a ceiling on volume | The README now states an expected 25–40 minute runtime for 120 tickets, so a throttled run is not mistaken for a hung one. The 200,000 figure is cited as published but unverified |
| A capable free instruction-following model is available for both calls | **Partly** | The provider had retired the Llama models; `llama-3.1-8b-instant` returns 404. Model choice was constrained by what is actually served rather than by what is documented | Model comparison rerun against the provider's live model list, selecting `openai/gpt-oss-20b` on measured classification accuracy. `docs/model_choice.md` |
| Enterprise customers currently receive the best service, so the fairness risk is degrading it | **No — inverted** | Enterprise is the worst-served tier: 369 minutes median against business's 141, lowest first contact resolution at 37.3%, only 37% resolved within an hour | The fairness baseline was wrong, and protecting the status quo for enterprise would have protected the worst outcome in the business. Recorded in the problem statement as a finding, since Marcus's principal stated worry points the wrong way |
| The 29 knowledge base articles are accurate and current | **Yes** | Every article was reviewed within the current cycle | No change to the grounding decision. It does mean the staleness Daniel warned about lives in the agents' private files, which FR-18 excludes — so the assumption holding is itself the evidence for that exclusion |

Two further things were wrong in the repository rather than in the requirements, and both were found by the clean-checkout rehearsal rather than by reading: the knowledge base was not committed, and the setup instruction produced a Python below the project floor. Recorded in `docs/clean_checkout_rehearsal.md` because they would have failed the gate.

## 4. What was decided not to change

| What looked wrong | Why it was left | What changing it would have cost | Revisit when |
|---|---|---|---|
| Escalation rate of 31.2% against a 30% target | It misses by 1.2 points at n=80, which is inside noise. The only cheap reduction is relaxing a protected-category rule or the grounding floor, and both exist to prevent the failure Marcus called disqualifying | Relaxing `no_supporting_passage` would answer roughly one more ticket in eighty and remove the guarantee that every answer is grounded | On a larger run, if the gap persists and is driven by something other than policy |
| The 0.80 confidence threshold, once it was shown not to be calibrated | The reflex is to raise it. That would convert correctly-classified 0.90 tickets into escalations, push escalation further above target, and — because all three sub-threshold tickets were non-fluent — widen the one real fairness disparity while appearing more cautious | Recalibration needs a confidence distribution large enough to fit bands to, which the token budget did not allow | When a run of several hundred tickets is affordable |
| Classification at `medium` reasoning effort, costing 865 tokens per call | Dropping to `low` saves about 200 tokens a ticket and cost 5.5 points of accuracy on an 18-ticket comparison. Classification decides every downstream step; generation's output is checked by a guardrail regardless | Roughly 25,000 tokens across the hidden set, which the reduced budget can absorb | If the token budget tightens again |
| No LangGraph, against the architecture the brief illustrates | An explicit pipeline through six components is legible and testable at this scale, and the Project Brief says following it without explaining why is "not really designing anything" | Rebuilding the pipeline and retesting, for no change in behaviour | Multi-turn conversation, where branching becomes genuinely dynamic |
| Satisfaction and hallucination rate left as `n/a` in every automated report | Both need human judgement. A harness that invents them produces a number that looks like a measurement and is not | Nothing — the cost is that two cells in the results table are blank until scored by hand | Scored manually before submission, with the sample size and assessor count declared |

## 5. Reflection

**Drafted for your review.** These answers are reconstructed from `docs/report_notes.md` and are accurate as to what happened, but the judgements in them are yours to own — an assessor may well ask you about this section on camera.

**What did you most misunderstand about the problem when you wrote version one?**

That safety came from the confidence threshold. Version one treated the 0.80 gate as the control that stopped wrong answers reaching customers, and arranged the rest of the system around it. The measurement showed it firing on three tickets in eighty and bearing almost no relationship to correctness. What is actually protecting customers is the pair of rules that never consult confidence at all: four intents that are never answered automatically whatever the model thinks, and a guardrail that blocks any claim not quoting a retrieved passage. I had built the right controls and credited the wrong one, which is a worse error than building the wrong thing, because it meant the thing I was monitoring was not the thing doing the work.

**Which piece of discovery work would have caught it earlier?**

Binning the classifier's confidence against observed accuracy on a few dozen development tickets, which would have taken under an hour and needed no new code. I deferred it because the plan said the threshold needed "calibration data that does not exist until classification runs" — and then ran classification over hundreds of tickets without going back to do the calibration. The data existed from the first batch; I had written down the dependency and not the follow-up.

**What would you do differently if you started this project again on Monday?**

Do the clean-checkout rehearsal on day one and repeat it daily. It was scheduled for the final afternoon and, done early, it found two defects that would have failed the pass/fail gate — a missing knowledge base and a setup instruction that produced the wrong Python version. Neither was visible from reading the repository, because both lived in the gap between what the repository contained and what the README claimed about it. Everything else I would keep, including writing the running notes at the end of each session, which is the only reason this log could be written honestly rather than reconstructed from memory.

**What is still uncertain, and what would you need to resolve it?**

Three things. Whether the confidence gap on non-fluent English is real: it rests on two tickets out of nineteen, and resolving it needs a run of several hundred tickets segmented by fluency, which the free-tier budget does not allow. Whether the system hallucinates at an acceptable rate: the framework asks for fifty replies assessed by two independent people, and an individual project can supply one assessor and no agreement rate. And whether a correctly cited answer to a stale article would be caught at all — it would not, because nothing reads the review age the corpus already carries, and that is the most likely remaining way this system causes harm to a customer.
