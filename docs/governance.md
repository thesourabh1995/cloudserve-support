# Governance

Follows the structure of the Governance Framework. Its own test is applied throughout: for each way this system could harm a customer, the entry names a control that was built, not a property of the model that is hoped for. Where no control exists, the entry says so.

Owners are named by role. On an individual project all roles are the author; they are written as roles because the question governance asks is who would be accountable in the client's organisation, and a document that answers "me" for all eight is not usable by CloudServe.

---

## 1. Decision logging

Every ticket writes one row to `evaluation/results/<run>/decisions.db` before the next ticket is read, so an interrupted run keeps the history of what it had already decided. Written by `src/logging_store.py`.

The record carries the framework's minimum fields: ticket and run identifiers, the timestamp, the classification with its confidence and the alternatives considered, the retrieved sources with their scores, the threshold that was applied, the action, the rule that produced it, a reason in a support manager's language, the guardrail findings, and the prompt version. Requirement IDs are carried on the prompt rather than on each row, since every decision at a stage is produced by the same prompt version.

**Coverage.** The harness calls `reconcile(run_id, tickets_processed)` at the end of every run and writes the result into the report. The 80-ticket validation run logged 80 of 80 and reconciled. A ticket that throws is still logged, as an escalation carrying the exception as its reason, so a crash cannot create an unlogged decision.

**One deliberate omission.** `customer_name` is dropped at the ingest boundary and never reaches the log, a prompt, or an outbound response.

---

## 2. Risk register

| ID | Risk | Likelihood | Impact | Mitigation in the design | Owner |
|---|---|---|---|---|---|
| R-01 | The system answers confidently and incorrectly | Medium | High | Every factual claim must quote a verbatim span of a retrieved passage; `_unsupported` in `src/guardrails.py` blocks the reply otherwise. Fired twice in the validation run on fabricated citations. Confidence gating is explicitly *not* relied on for this, because measurement showed it is not calibrated (see R-09). | Support Operations Lead |
| R-02 | Private data appears in an outbound response | Low | High | `_private_data` blocks any reply containing an email address, a phone number or an API-key pattern, and escalates rather than redacting. `customer_name` never enters the system. Zero detections in validation. | Data Protection Officer |
| R-03 | A customer's input is treated as an instruction | Medium | High | Ticket text is delimited and declared untrusted in both prompts, with an explicit instruction not to act on embedded directions. **This is a mitigation without a detector**: nothing currently checks whether an injection succeeded. Recorded as an open finding, below. | AI Engineering Lead |
| R-04 | Some customer groups receive worse answers | Medium | Medium | Routing reads no customer attribute. Audited in `docs/fairness_audit.md` per stage, not just per outcome. One real signal found: the model is less confident on non-fluent English while being no less accurate. Mitigation is to stop treating confidence as a gate (R-09). | Support Operations Lead |
| R-05 | The documentation the system relies on goes stale | High | Medium | Citations resolve to a document and chunk, so every automated answer names the article it depended on and a stale answer is traceable to the article that caused it. **No freshness check or re-index schedule exists.** Open finding. | Technical Documentation Lead |
| R-06 | The model provider becomes unavailable | High | Medium | `ModelUnavailable` is raised after retries with exponential backoff and jitter, and every caller degrades to an escalation rather than propagating. Verified by running uncached tickets against an invalid key: all escalated, all logged, run completed. Retrieval also falls back to local weights so an offline Hugging Face Hub cannot break it. | AI Engineering Lead |
| R-07 | Latency degrades under load | Medium | Low | Measured p95 is 13.2s against a 3-second target, and the free tier's per-minute token bucket is the cause. Accepted as a declared tradeoff rather than mitigated: the business requirement it serves is under five minutes to first reply, which is met by a wide margin. Revisit on a paid tier. | AI Engineering Lead |
| R-08 | Costs rise unexpectedly with volume | Medium | Medium | Tokens and calls are counted per task and reported in every run. Per-ticket cost was measured and reduced 55% (`docs/run_cost.md`). Responses are cached by content so repeated runs do not re-spend. **No spend cap or alert exists**; the free tier is a hard ceiling rather than a chosen control. Open finding. | AI Engineering Lead |
| R-09 | Confidence is treated as calibrated when it is not | High | Medium | Found by measurement, not assumed: correctness is not monotonic in stated confidence (0.80 and 0.95 both scored 100%, 0.90 scored 87%), and all three sub-threshold tickets in the validation run were non-fluent. Mitigation is that the threshold is not load-bearing — it produced 2 of 23 escalations, while the protected-category rule and the grounding guardrail do the real work. Declared rather than papered over. | AI Engineering Lead |

Risks R-01 to R-08 are the framework's. R-09 was added because the validation run produced it and omitting it would have left the register describing a system we no longer believe in.

---

## 3. Fairness audit

Full audit in `docs/fairness_audit.md`, with tables regenerable by `analysis/fairness_audit.py`. In summary: the pipeline stages are flat across tier, region, fluency and ticket length once confidence intervals are read; the variation is at the routing decision; for tier, region and length that variation is explained by the groups sending different proportions of must-not-auto-respond tickets; for fluency it is not, and the mechanism is the confidence score rather than retrieval.

The framework predicted retrieval would degrade on non-fluent English. It did not — 100% against 98%. The likely reason is that indexed chunks carry their article title, a decision taken during retrieval tuning for an unrelated reason.

---

## 4. Guardrails

Two checks run on every response and can block it. Three of the framework's five are not implemented, which is stated here rather than left to be discovered.

| Guardrail | What it checks | What happens when it fires | Status |
|---|---|---|---|
| Private data | Email addresses, phone numbers, API-key and access-key patterns | Blocks and escalates. Never redacts and sends. | **Built**, blocking, tested |
| Grounding | Every citation resolves to a verbatim span of a passage that was actually retrieved | Blocks and escalates with the unsupported claim recorded | **Built**, blocking, tested. Fired twice in validation |
| Instruction integrity | That ticket content has not altered the system's instructions | — | **Not built.** Prompts delimit and declare ticket text untrusted, which is a mitigation, but nothing detects a successful injection |
| Tone and scope | That the reply makes no commitment about refunds or timelines | — | **Not built.** The grounding check constrains claims to the documentation, which indirectly limits commitments, but this is a side effect rather than a control |
| Confidence floor | That the routing threshold was applied | Escalates; a missing confidence is treated as low, not high | **Built** as a routing rule rather than a guardrail. See R-09 for why it is not relied on |

Neither built guardrail can be disabled by configuration. There is no flag that turns them off, which is deliberate: A7 fails outright for a guardrail that a run can switch off.

---

## 5. Incident response

Written to be followed by someone who did not build this.

| Step | What to do | Who | How long |
|---|---|---|---|
| **1. Detect** | A bad reply reaches a customer, or a run reports a guardrail activation count or escalation rate outside its usual range. Reports are written to `evaluation/results/<run>/metrics.md` after every run. Anyone in support who sees a wrong automated reply raises it; no triage judgement is needed to report. | Any support agent | Immediately on sight |
| **2. Contain** | Stop automatic answering before investigating. Create the file `storage/STOP_AUTOMATION`, writing the reason into it: `echo "ticket 4412 got a wrong refund promise" > storage/STOP_AUTOMATION`. From the next ticket onward every ticket is classified, logged and escalated to a person. **Do not redeploy, do not restart, and do not edit configuration.** | Duty support manager | Under 1 minute |
| **3. Assess** | Find the ticket in the decision log: `select * from decisions where ticket_id = ?`. The row carries the classification, the confidence, the retrieved sources with scores, the threshold, the rule, the reason, the guardrail findings and the prompt version. Determine whether the answer was ungrounded (a guardrail gap), grounded in stale documentation (a content problem), or correctly produced from a wrong classification. Then query the same run for other tickets sharing the rule or the cited document to size the blast radius. | AI Engineering Lead | Under 2 hours |
| **4. Notify** | Tell the affected customer first, with a correction, before any internal communication. Then the Head of Support with the count of affected tickets from step 3. If private data reached a customer, notify the Data Protection Officer immediately and treat statutory breach timelines as started at step 1, not at step 4. | Head of Support; DPO if R-02 | Customer within 4 hours; DPO within 1 hour |
| **5. Remediate** | Fix the cause, not the ticket: a guardrail gap gets a new blocking check with a test that fails before the fix; stale documentation gets corrected and the index rebuilt; a bad classification gets a routing rule or a prompt revision with its version bumped. Re-run the validation set and compare against `docs/validation_run.md` to confirm nothing else moved. Then delete `storage/STOP_AUTOMATION`. | AI Engineering Lead | Fix within 2 working days; switch stays on until then |
| **6. Review** | Within five working days, write up what happened, why the controls did not catch it, and what changed. Record the trigger in the PRD revision log if a requirement or assumption was wrong. The test written in step 5 is the real output; an incident that produces only a document will recur. | Head of Support, chaired | Within 5 working days |

---

## The kill switch

| Question | Answer |
|---|---|
| **What is the mechanism?** | The presence of a file, `storage/STOP_AUTOMATION`, whose contents are the reason for the stop. Checked once per ticket by `src/killswitch.py`, ahead of every routing rule. A file rather than an environment variable or a config flag, because a variable needs the process restarted — a deployment under another name — and because a file can be created by someone who has shell access but no ability to ship. |
| **Who is authorised to use it?** | Any duty support manager, unilaterally and without approval. Engaging it degrades the system to the behaviour it had before this project existed, so the cost of engaging it wrongly is a slower queue, while the cost of hesitating is more wrong answers to customers. It is deliberately not restricted to engineering. |
| **How long until it takes effect?** | The next ticket. The switch is read per ticket rather than at startup, so there is no restart and no deployment. Measured as under one second in the rehearsal below. |
| **What happens to tickets in flight?** | Nothing is dropped. A ticket already past the routing decision finishes and is logged. Every ticket after the switch is still ingested, still classified and still logged, then escalated with its classification and retrieved sources attached. The human queue receives the same context it would have had, so the switch costs throughput rather than information. Generation is skipped while halted, because the usual reason to stop is that the drafts are wrong and a bad suggestion in front of a stressed agent is worse than none. |
| **How is it tested?** | Two ways. `tests/test_killswitch.py` covers the mechanism, including that an empty file still halts, that releasing twice is safe, and that end to end a ticket the system would have answered is escalated instead, with no draft attempted and the stop reason on the log row. `tests/test_route.py` pins that the halt outranks every other rule. And it was rehearsed against the real harness: 12 tickets, all 12 escalated as `automation_halted`, 12 of 12 logged, reconciled, zero model calls. The switch was then released and the release verified. |

The switch file lives under `storage/`, which is excluded from version control, so a fresh clone can never arrive with automation already halted.

---

## 6. The declaration

| Statement | Position |
|---|---|
| **This system must never** | send a customer a factual claim that is not traceable to a specific passage of CloudServe's own documentation, and must never send one that contains another person's contact details. |
| **The mechanism that enforces that is** | two guardrails that block rather than warn, running on every response with no configuration that can disable them. Grounding requires each citation to quote a verbatim span of a passage that retrieval actually returned, so a fabricated reference fails even when the document exists. Four categories — security incidents, compliance requests, feature requests and unclear requests — are never answered automatically regardless of how confident the model is. Every decision, sent or blocked, is on a record that reconciles against the tickets processed. |
| **The most likely way it could still cause harm is** | a confidently wrong answer that is correctly grounded in documentation that has gone out of date. Every control here checks that a claim matches the corpus; none checks that the corpus matches reality, and there is no freshness check or re-index schedule (R-05). A customer following a correct citation to a stale article is the failure this design does not catch. Second to that is a successful prompt injection, which is mitigated by prompt structure but not detected (R-03). |
| **We would not deploy this without first** | a documentation freshness process with a named owner and a re-index trigger; a hallucination review of at least fifty replies by two independent assessors, which this project could not staff; a detector for instruction-integrity rather than only a mitigation; and a larger run to establish whether the non-fluent confidence gap is real, since 19 tickets cannot settle it. We would also not deploy while describing the confidence score as calibrated, because it is not. |
