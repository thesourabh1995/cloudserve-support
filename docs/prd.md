# Product requirements document — CloudServe intelligent support system

## 1. Document control

| Field | Value |
|---|---|
| Version | 1.0 |
| Written by | thesourabh1995 |
| Date | 11 November 2026 |
| Status | Draft for review |
| Approved by | — (individual project; no approver exists) |

**A note on when this was written, because it affects how it should be read.** The build ran ahead of the paperwork. This document states the requirements and assumptions as they were held *at the start of implementation*, reconstructed from `docs/report_notes.md`, which was written at the end of each working session while the decisions were being taken. It is not backdated: the date above is the date it was typed. Several assumptions in section 7 are already known to have failed, and they are recorded here in the form they were held rather than silently corrected, because the Stage 5 revision log is the place where a failed assumption is accounted for. Correcting them here would hide the reasoning the revision log exists to show.

## 2. The problem in one paragraph

> CloudServe's support team is not short of answers. It is short of a reliable path from what a customer wrote to the article that already answers them. Seven in ten tickets are answerable from twenty-nine knowledge base articles that are accurate and currently reviewed, yet agents reconstruct those answers from memory, because the internal search matches article titles and customers do not describe problems in the words the titles use. The cost is paid twice: as an eight-to-twelve-hour first response while known answers are rewritten by hand, and as a 56% escalation rate of which roughly half is not difficulty but an agent who could not find the page and would not send an answer they were not confident about.

Full statement, including the evidence and the two interview claims the ticket data contradicts, in `docs/problem_statement.md`. **Under review by the author; if the framing there changes, this paragraph changes with it.**

## 3. Who this is for

| User group | What they need | What they do instead now | How we will know it worked |
|---|---|---|---|
| **Customers raising tickets** | A correct answer quickly, or an honest statement of what is thought and who will confirm it. Ravi: acceptable *"provided it is honest"* — what it thinks, the page it came from, and that a person will confirm | Search the documentation themselves and find the answer about half the time, having burned two hours | Time to first reply falls from 8–12 hours to under five minutes. Every automatic answer names the article it came from |
| **Tier one support agents** | Not to be the person apologising for a wrong answer they did not write. Sofia: a ticket arriving *"with a draft and the relevant page attached"* would *"save me half of every ticket"* | Reconstruct known answers from memory, or copy from a personal file of past answers that nobody has reviewed | Volume reaching tier one that is already answered falls. No outbound reply contains a claim that is not traceable to an article |
| **Tier two and specialist agents** | Context, not correctness. Daniel: *"I do not need it to be right. I need it to show its working"* | Read the whole thread from a bare forwarded ticket and often re-ask the customer something already asked | Every escalation carries the classification, the retrieved documentation and an explicit statement of what was uncertain |
| **The head of support** | First contact resolution up without more headcount, and an explanation for the autumn compliance review. Marcus: *"I need to be able to say why it did what it did"* | Reports a red number to the executive team and has run out of ways to explain it | First contact resolution rises from 42% toward 60%. Every decision is on a record that reconciles exactly against tickets processed |

A deliberate omission: Ines, who owns the documentation, is a stakeholder but not a user of this system. Her requirement (EV-20) is that an answer names its source so a fault can be diagnosed as a wrong article or a misreading. That is served by FR-06 without her ever using the system.

## 4. Functional requirements

Evidence IDs refer to the register in `docs/traceability.md`. Priorities use the pack's scale: **Must** means unacceptable without it, **Should** means expected but deferrable with a stated consequence, **Could** means valuable if time allows, **Will not** means considered and excluded.

| ID | Requirement | Priority | Evidence | Acceptance |
|---|---|---|---|---|
| FR-01 | The system shall accept tickets from all four channels as one normalised representation, tolerating missing fields, unusual characters and empty bodies without failing | Must | EV-31 | A2 |
| FR-02 | The system shall assign each ticket an intent from the fixed 22-value taxonomy | Must | EV-30, EV-33 | A3 |
| FR-03 | The system shall assign an urgency and a numeric confidence expressing the probability that the intent is correct, record the alternatives considered, and fall back to a defined default rather than raising an exception | Must | EV-10, EV-22 | A3 |
| FR-04 | The system shall retrieve documentation passages by meaning rather than keyword, and shall return nothing when nothing clears the relevance floor | Must | EV-09, EV-19, EV-37 | A4 |
| FR-05 | The system shall draft answers grounded only in retrieved passages, with ticket text separated from system instructions so that customer text cannot redirect it | Must | EV-16, EV-21 | A6 |
| FR-06 | Every citation in an outbound answer shall resolve to a passage that was actually retrieved, and shall name the article | Must | EV-20, EV-23 | A6 |
| FR-07 | Routing shall be deterministic, and four intents — security_incident, compliance_request, feature_request, unclear_request — shall never be answered automatically regardless of confidence | Must | EV-03, EV-17, EV-33, EV-36 | A5 |
| FR-08 | Every decision shall be recorded with its reason, sources, applied threshold and prompt version, and the count shall reconcile exactly against tickets processed | Must | EV-05, EV-20 | A8 |
| FR-09 | The system shall block, not warn, when an outbound reply contains private data or a claim not traceable to a retrieved passage | Must | EV-03 | A7 |
| FR-10 | An escalation shall carry the classification, what the system was uncertain about, and the documentation that appeared relevant | Must | EV-11, EV-14, EV-15 | A5 |
| FR-11 | The system shall degrade to escalation rather than stopping when the model provider is unreachable, retrieval is empty, or input is malformed | Must | EV-01 | A11 |
| FR-12 | Automatic answering shall be stoppable immediately without a deployment, and the stop shall be recorded | Must | EV-03, EV-05 | — |
| FR-13 | The system shall report outcomes split by customer tier, region, language fluency and ticket length | Must | EV-06, EV-12, EV-25 | A10 |
| FR-14 | The system shall process an entire ticket file unattended from a single command and produce a metrics report without further instruction | Must | EV-01 | A9, A10 |
| FR-15 | An automatically drafted reply shall disclose to the customer that it was drafted automatically | Should | EV-24 | — |
| FR-16 | The system shall detect, not merely discourage, a successful prompt injection | Should | EV-16 | — |
| FR-17 | The system shall check that a cited article is still within its review cycle before relying on it | Should | EV-16, EV-35 | — |
| FR-18 | The system shall not learn from, or retrieve from, agents' private answer files | Will not | EV-16 | — |
| FR-19 | The system shall not make commitments about refunds, credits or delivery timelines | Will not | EV-17 | — |
| FR-20 | The system shall not present itself as a conversational assistant or chat interface for customers | Will not | EV-19, EV-30 | — |

FR-18 to FR-20 are recorded as deliberate exclusions rather than omissions. FR-20 in particular is the reframe: the client asked for a chatbot, and the evidence says a conversational front end would add a fifth place to ask without repairing the path from a question to its existing answer.

## 5. Non-functional requirements

| ID | Category | Requirement | How it will be verified |
|---|---|---|---|
| NFR-01 | Latency | 95th-percentile end-to-end processing under 3 seconds | Measured per ticket by the harness and reported in `metrics.md` |
| NFR-02 | Availability | 99.5% or better; a provider outage must degrade rather than stop the run | Induced outage against an invalid key on uncached tickets, confirming every ticket escalates and the run completes |
| NFR-03 | Accuracy | Classification precision 85% or better; citation accuracy 95% or better; hallucination rate 5% or lower | Classification and citations measured automatically against labels; hallucination rate requires human review of at least fifty replies by two independent assessors |
| NFR-04 | Privacy | Zero private data in outbound replies. `customer_name` shall not reach a prompt, a log or a reply | Blocking guardrail on every response, plus a test that the field is dropped at the ingest boundary |
| NFR-05 | Auditability | Every decision reconstructable months later by someone who was not there, including which prompt version produced it | Decision log reconciliation count, reported every run |
| NFR-06 | Fairness | Under five points of variation in outcome across customer tier, region and language fluency | Segmented audit per pipeline stage, not only on the final outcome |
| NFR-07 | Cost | A full run over the hidden ticket set shall complete within a free-tier allowance | Tokens and calls counted per task and reported every run |

## 6. Deliberately out of scope

| Not building | Why not | What would change this |
|---|---|---|
| A conversational chat interface for customers | The failure is the path from a question to its existing answer, not a shortage of places to ask. A chat front end reproduces the findability failure at higher volume | Evidence that customers cannot reach support at all, rather than cannot get a timely answer |
| LangGraph or any agent-orchestration framework | An explicit pipeline through six components is legible and testable at this scale. A framework earns its cost when branching becomes genuinely dynamic | Branching logic complex enough that the explicit pipeline becomes hard to follow — realistically, multi-turn conversations |
| Learning from historical agent replies | Daniel: answers in private files *"were correct two years ago and have not been right since"*, and a system learning from them *"will scale up a mistake"* | A reviewed, dated corpus of past replies with known provenance |
| Multi-turn conversation with the customer | Every requirement here concerns the first response. Follow-ups are a different problem with a different failure mode | First-response quality reaching target, making the next bottleneck the follow-up |
| PostgreSQL, Grafana, a production deployment | None of the twelve acceptance criteria require them, and the governance marks are for decision logging, risk and fairness rather than visualisation | A deployment beyond evaluation |
| Writing or correcting documentation | The corpus is accurate within its review cycle. Fixing articles is Ines's work and a different project | Evidence that article quality, rather than findability, is the constraint |

## 7. Assumptions and their consequences

Stated as held at the start of implementation. Where an assumption has since failed, that is recorded in the Stage 5 revision log with its trigger rather than corrected here.

| Assumption | Why believed | If false | How we would find out |
|---|---|---|---|
| A numeric confidence from the model reflects the real probability of being correct, so a threshold on it is a meaningful safety control | The Build Specification asks for a calibrated confidence and the architecture diagram routes on a 0.80 threshold | The threshold either escalates tickets that were correct or passes tickets that were wrong, and the system's safety rests on something that is not load-bearing | Bin outcomes by confidence band and compare stated confidence against observed accuracy |
| Retrieval will perform worse on tickets written in non-fluent English, because the phrasing stops matching the documentation | The Governance Framework states this as the variation most likely to be found, and Sofia describes those tickets as harder | Either the fairness risk is elsewhere, or a mitigation already in the design is absorbing it, and the audit must look at every stage rather than the expected one | Segment retrieval hit rate by language fluency |
| A free-tier API allowance is sufficient to process the hidden ticket set in one unattended run | The gate requires an unattended run on an assessor's machine, which implies a key they can obtain without payment | The gate run cannot complete, which caps implementation marks regardless of the rest | Measure tokens per ticket on a real run and extrapolate |
| 95th-percentile latency under 3 seconds is achievable | It is stated as a technical target in the pack | The target is unreachable by design rather than by implementation, and must be declared as a tradeoff against the business target it serves | Measure p95 on a real run |
| The published per-day token allowance for the chosen model is the binding cost constraint | It is documented by the provider | Cost planning is aimed at the wrong limit, and the real constraint is discovered during the gate run rather than before it | Read the rate-limit headers the provider actually returns |
| A capable free instruction-following model is available for both classification and generation | Several providers advertise free tiers with current open models | Model choice is constrained by availability rather than by measurement, and the comparison has to be rerun against whatever is actually served | Query the provider's model list and attempt a real call |
| Enterprise customers currently receive the best service, so the main fairness risk is degrading it | Marcus states this as his principal worry and Ravi corroborates it from the customer side | The system could be measured against the wrong fairness baseline, and protecting the status quo would protect the worst outcome in the business | Segment the historical baseline by tier |
| The 29 knowledge base articles are accurate and current | Ines reviews them on a rotation and states they are accurate within that cycle | Grounding answers in the corpus would propagate stale information with a citation attached, which is harder to detect than an ungrounded answer | Check the review age carried on each article |

## 8. Success measures

Baselines are the pack's published figures. Where the development set gives a different figure, both are shown, because the report has to state which it is quoting.

| Measure | Baseline | Target | Measured how | Reported by |
|---|---|---|---|---|
| First contact resolution | 42% (43.8% in the development set) | 60% or better | Share of tickets answered with no person involved | Harness, every run |
| Time to first reply | 8 to 12 hours | Under 5 minutes | Processing time of answered tickets | Harness, every run |
| Customer satisfaction | 3.2 / 5 (2.97 in the development set) | 4.0 or better | Human review of a sample against the published rubric; cannot be automated | Author, once, with the sample size declared |
| Escalation rate | 58% (56.2% in the development set) | 30% or lower | Escalated and blocked tickets together, since both leave the queue for a person | Harness, every run |
| Classification precision | — | 85% or better | Per-class precision and recall against labels | Harness, every run |
| Hallucination rate | — | 5% or lower | Human review of at least fifty replies, two independent assessors, agreement rate reported | Author, with the single-assessor limitation declared |
| Citation accuracy | — | 95% or better | Share of citations resolving to a retrieved passage | Harness, every run |
| Latency, 95th percentile | — | Under 3 seconds | End to end, including retrieval and both model calls | Harness, every run |
| Private data in outbound replies | — | Zero | Guardrail activations | Harness, every run |
| Cross-group variation | — | Under 5 points | Spread in automatic-answer rate across tier, region and fluency | Fairness audit |
| Confidence calibration | — | Within 5 points | Stated confidence against observed accuracy, by band | Fairness audit |

The client's own table states 65% first contact resolution while the targets table and Evaluation Framework state 60%. Reported against 60%, with Marcus's 65% recorded as the client aspiration.

## 9. Open questions

| Question | Why it matters | Owner | Resolve by |
|---|---|---|---|
| Is the hidden evaluation set 100 tickets or 120? The pack says both in different places | The report must state a figure. The harness counts whatever it is given, so the build is unaffected | Author | Before submission; the harness is deliberately count-agnostic in the meantime |
| May the validation set be used during development? The Project Brief forbids it; the Dataset Guide and Build Specification encourage it | Determines whether the reported figures are presented as validation results or as a single hold-out measurement | Author | Unresolved. Proceeding on the Dataset Guide's reading, with one run and no subsequent tuning, which satisfies the stricter reading as well |
| Is a single-assessor hallucination review acceptable on an individual project? | The framework asks for two independent assessors and an agreement rate, which an individual project cannot staff | Author | Before the report; proceeding with one assessor and declaring the limitation |
| Will the gate run use a free-tier key? | Determines whether per-ticket cost is an acceptance concern or merely an efficiency one | Author | Treated as yes, which is the conservative reading |
| Who owns documentation freshness once this is deployed? | FR-17 is unbuilt, and a correctly cited answer to a stale article is the most likely remaining way this system causes harm | Unassigned — this is a gap, not a decision | Named in the governance declaration as a precondition for deployment |

---

## The review check

The template asks whether an engineer who attended none of the interviews could build each requirement from what is written. Three do not pass that test as written, and are marked accordingly:

- **FR-03** says confidence must express the probability of being correct, but does not say how to calibrate it. As written an engineer would do what this build did, which is take the model's self-reported number at face value. Assumption one in section 7 is the reason.
- **FR-13** names the segments but not the metric to compare across them. This build compared the automatic-answer rate, and that choice is not in the requirement.
- **FR-15** cannot be built from this document at all, because it does not say where the disclosure goes or what it says. It is a requirement in name and a note in substance.
