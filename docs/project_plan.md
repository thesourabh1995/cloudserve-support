# FDE Capstone — Delivery Plan (40-hour triaged)

CloudServe Solutions intelligent support system. Individual project, six stages in sequence.

**Deadline: Sunday 15 November 2026, 23:59 IST.**
**Runway: Friday 6 – Sunday 15 November. Ten days at ~4 focused hours = ~40 hours.**

## Read this before the schedule

Forty hours is roughly a third of what this pack is written for. The full programme is not
achievable in it, and pretending otherwise would just mean discovering the shortfall on the
final afternoon. So this plan is triaged: it protects the pass/fail gate and the highest-weight
marks, and it deliberately makes some sections thin. Every thinness is listed below so you can
declare it in the report rather than have an assessor find it as an absence — the pack
repeatedly rewards naming your own limits.

**Two things would change this materially, and both are worth doing today:**

1. **Find extra hours on the two weekends.** Sat 7, Sun 8, Sat 14 and Sun 15 at 7–8 hours
   instead of 4 would add ~15 hours and move this from "tight" to "workable". Sunday 15 in
   particular needs 6–8 hours no matter what — the report and video cannot both fit in four.
2. **Ask about an extension now, not later.** The Project Instructions say requests must come
   *before* the deadline with a reason, and the course email asks you to raise things early.
   Even three extra days changes the quality of what you submit substantially.

| Day | Date | Focus | Hrs |
|---|---|---|---|
| 1 | Fri 6 Nov | Setup, environment proven, repo scaffolded | 4 |
| 2 | Sat 7 Nov | Discovery: transcripts and ticket data | 4 |
| 3 | Sun 8 Nov | Problem statement, PRD v1, architecture | 4 |
| 4 | Mon 9 Nov | Specs and prompts, then ingest | 4 |
| 5 | Tue 10 Nov | Retrieval and classification | 4 |
| 6 | Wed 11 Nov | Routing, decision log, generation | 4 |
| 7 | Thu 12 Nov | Guardrails, harness, **first full run** | 4 |
| 8 | Fri 13 Nov | Resilience, tests, CI, final run | 4 |
| 9 | Sat 14 Nov | Governance, fairness, PRD revision | 4 |
| 10 | Sun 15 Nov | Report, video, package, submit | 6–8 |

---

## The scope cuts, decided now

**Architecture simplifications** (the Project Brief permits departures that you justify, and
explicitly says following it without explaining why is "not really designing anything"):

- **No LangGraph.** A plain explicit pipeline function through the six components. LangGraph
  is the right tool at scale and the wrong one when you have fourteen hours of build time.
  Justify this in the report as a deliberate trade-off.
- **Minimal FastAPI** — one `POST /ticket` endpoint. Enough for the live demo and A1.
- **Monitoring reduced to a Prometheus counters endpoint.** No Grafana. None of the twelve
  acceptance criteria require dashboards, and the governance marks are for decision logging,
  risk and fairness, not visualisation.
- **SQLite only.** No PostgreSQL.

**Method simplifications, each to be declared in the report:**

- Classification via one LLM call over the fixed list of 22 intent labels, plus rule-based
  overrides for the `must_not_auto_respond` classes. No per-class engineering.
- Hallucination rate from a self-assessed sample of ~20 responses rather than fifty reviewed by
  two independent assessors. State the sample size and the single-assessor limitation openly.
- Report written to the 20-page floor, with workbooks carrying weight as appendices.

**Never cut, because each is a gate or a whole marking category:** the unattended run, a
guardrail that genuinely blocks, the complete decision log, the compulsory PRD revision, the
clean-checkout rehearsal, the fairness audit, and the video.

**Cache every model response from the first call.** You will run the full set three times in
ten days on a free tier. Without a cache you will lose hours to rate limits you cannot afford.

**Keep `docs/report_notes.md` open and spend the last 15 minutes of every build day writing
down what you did and why you chose it.** This is the single highest-leverage habit in the
plan. It turns Sunday's report from writing-from-scratch into assembly, and it is where the
"explain every decision" marks come from.

---

## The three things that decide the grade

**1. The gate.** Before anything is marked, the repo is cloned onto a machine that is not
yours, your README is followed literally, and the harness must process the full ticket set in
one unattended run. Runs cleanly means marked in full; needs intervention caps implementation
marks; will not start gets one 48-hour repair window for setup and docs only.

**2. The reframe.** The client asked for a chatbot. Building a chatbot is defined as failing.
357 of the 500 development tickets (71%) are already answerable from the 29 documentation
articles; historical first contact resolution is 43.8%, escalation 56.2%, mean CSAT 2.97. The
problem is answer *delivery*, not answer *availability*. Evidence it from the transcripts and
the data — do not assert it.

**3. Traceability.** An assessor picks a requirement and asks which evidence produced it, then
picks a prompt and asks which requirement it serves. Carry IDs (`EV-xx` → `FR-xx` → `PR-xx` →
module) as you write.

---

## Day 1 — Fri 6 Nov: setup and reading (4h)

The course email's own advice, and the thing that protects every later day.

- **(1h)** Read Start Here and the Build Specification. Leave the Project Brief for tomorrow
  morning; the Build Spec is what you need first because it defines the twelve criteria.
- **(1.5h)** Environment: `python3 -m venv .venv`, activate, confirm `which python` points
  inside it. `echo ".env" >> .gitignore` **before** `cp .env.example .env` — a key in git
  history is a serious finding even after deletion. OpenRouter or Groq free-tier key in. Make a
  real call and get real text back; do not stop until this works. The supplied pins are an old
  stack (`langchain==0.1.0`, `chromadb==0.3.21`, `sentence-transformers==2.2.2`) and may not
  resolve on current Python — if you re-pin, document what and why.
- **(1h)** `git init`, scaffold `src/`, `prompts/`, `tests/`, `evaluation/`, `docs/`, `data/`,
  `.github/workflows/ci.yml`. First commit, push. Commit daily from here; history is reviewed.
- **(0.5h)** Pull the embedding model down now so the first-run download does not eat build
  time later. Start the effort log and `docs/report_notes.md`.

## Day 2 — Sat 7 Nov: discovery evidence (4h)

- **(1.5h)** Project Brief, then all five transcripts — Marcus Adeyemi (Head of Support), Sofia
  Restrepo (tier one), Daniel Okonkwo (tier two), Ines Varga (technical writer), Ravi Menon
  (customer). Fill Stage 1 section one as you read, recording which line each point came from.
  They contradict each other on a point of fact the ticket data can settle; find it.
- **(2.5h)** Ticket data analysis, Stage 1 sections two and three. Write scripts and keep them —
  they become appendices. Establish: channel volumes (email 212, chat 155, docs_comment 78,
  forum 55) and the answerable-from-docs share within each; intent distribution across the 22
  classes; the `must_not_auto_respond` classes that become hard escalation rules; the historical
  baseline; and the segment cuts you need later for fairness (tier 253/164/83, region, fluency
  380 fluent / 120 non-fluent).

## Day 3 — Sun 8 Nov: problem statement and PRD v1 (4h)

- **(1h)** Stage 1 sections four to six, including the problem statement. Test it against a
  transcript — would Marcus recognise this as his problem?
- **(2h)** PRD v1, all nine sections of the Stage 2 template. Every functional requirement cites
  its evidence ID. Write assumptions down explicitly — you cannot show one failed next week if
  you never recorded it. Run the template's read-back check: could someone who attended none of
  your interviews build from this?
- **(1h)** Short `docs/architecture.md` with the alternatives you rejected and why, including
  the LangGraph decision. Fix the decision-log schema now from the Governance Framework's
  minimum record, including `prompt_version` and `requirement_ids`.

## Day 4 — Mon 9 Nov: prompts, sprint plan, ingest *(A2)* (4h)

- **(1.5h)** Stage 3 prompt library and Stage 4 sprint plan, kept tight. Requirement →
  specification → versioned prompt, each carrying its requirement ID. Fill sprint plan section
  five (what you drop if short) while the decision is calm.
- **(2.5h)** Ingest: one normalised representation from all four channels, preserving original
  text and channel, handling missing fields, odd characters and empty bodies without failing.
  Check by printing the normalised object for one ticket per channel.
- **Then clone your own repo into a fresh directory and follow your own README** — tonight,
  while it is small and the fix takes two minutes.

## Day 5 — Tue 10 Nov: retrieval and classification *(A4, A3)* (4h)

- **(2h)** Retrieval: embed the 29-article corpus into Chroma, return ranked passages with
  scores and IDs that resolve to the real corpus. Apply a relevance threshold and return
  **nothing** when nothing is relevant — always returning something is explicitly listed as not
  working. Try two chunk configurations and measure; `expected_doc_ids` makes hit rate directly
  measurable. Record which you chose and why.
- **(2h)** Classification: intent and urgency with a numeric confidence that reflects real
  probability of correctness. Record the alternatives considered. Defined fallback, never an
  exception.

## Day 6 — Wed 11 Nov: routing, log, generation *(A5, A8, A6)* (4h)

- **(1.5h)** Routing: deterministic, same input same decision every time. Set the threshold from
  your data rather than taking 0.80 from the diagram. Record the reason in language a support
  manager could read; escalations carry the drafted summary and retrieved sources.
- **(1h)** Decision log to SQLite. Check: run twenty tickets, read the log, confirm every
  decision has a reason and counts reconcile against tickets processed.
- **(1.5h)** Generation: grounded in retrieved passages, citations resolving to the passage
  actually retrieved, structured parseable output, ticket content separated from system
  instructions so customer text cannot redirect the system.

## Day 7 — Thu 12 Nov: guardrails and the first full run *(A7, A9, A10)* (4h)

**The most important day in the plan.**

- **(1.5h)** At least one guardrail that genuinely blocks. A guardrail that only warns is not a
  guardrail, and one disabled by a flag during the run fails A7 outright. Private data and
  grounding at minimum. Build the deliberately-crafted trigger ticket and keep it — you need it
  for the video demo.
- **(2.5h)** Harness and the first unattended run. One command taking `--input` and `--output`
  as arguments — never a hardcoded filename, since it will be pointed at a file you have never
  seen. The run must produce a metrics report by itself: volume, business (FCR, mean and median
  response time, escalation rate), technical (precision and recall per class, retrieval hit
  rate, latency median and p95), governance (decisions logged, guardrail activations, private
  data detections).

Expect tonight to surface a rate limit, an encoding problem or an empty retrieval result.
That is what tonight is for. **If the run is not working by the end of tonight, stop adding
capability tomorrow and spend the whole of Friday making the run complete with what exists.**

## Day 8 — Fri 13 Nov: resilience, tests, final run *(A11, A12)* (4h)

- **(1.5h)** Induce each failure and confirm the system degrades rather than stops: empty
  retrieval, provider timeout, rate limiting, malformed input, provider disconnected entirely.
- **(1h)** Test suite running from one documented command, green in CI. Keys from GitHub
  encrypted secrets or recorded responses, never the workflow file.
- **(1.5h)** Fix what yesterday exposed, then the final clean evaluation run. Record the date
  and the run count — the report must state both. Do not tune afterwards; the set you can see is
  not the set that decides the grade.

## Day 9 — Sat 14 Nov: governance, fairness, revision (4h)

- **(1.5h)** Fairness audit: segment by tier, fluency and ticket length. The Governance
  Framework warns you will probably find retrieval doing worse on non-fluent English because the
  phrasing stops matching the documentation. **Finding and reporting that honestly scores far
  better than a table showing no variation.** Then the calibration check: bin by confidence
  band, compare stated against observed.
- **(1h)** Governance Framework: risk register with named mitigations and owners, incident
  response across all six steps written so a stranger could follow it at 2am, and the kill
  switch — mechanism, who operates it, how long, tickets in flight, how it is tested.
- **(1h)** Stage 5 revision log, all five sections. At least one substantive change with its
  trigger, which assumptions failed, what you chose not to change and why. Compulsory and
  assessed directly.
- **(0.5h)** Prometheus counters endpoint. Screenshot it.

**If at all possible, record video take one tonight.** It will overrun to twenty-eight minutes
and expose what you cannot yet explain cleanly, and knowing that tonight is worth a great deal
tomorrow.

## Day 10 — Sun 15 Nov: report, video, submit (6–8h, not 4)

- **(3h)** Report: single PDF, the prescribed ten-section order — executive summary, the
  problem, discovery findings, requirements, architecture and design, implementation,
  evaluation, governance and risk, the requirements revision, conclusions, appendices. Assemble
  from `report_notes.md` and the workbooks. Continuous prose, every figure numbered and
  referenced, business outcomes before technical. Include the sentence beginning *"the figures
  above should be treated with caution because…"* and the half-page AI tool use declaration.
- **(2.5h)** Video: problem (0–2), discovery (2–5), system (5–7), **live demo (7–14)**, numbers
  (14–17), governance (17–18), next steps (18–20). You on camera at open and close. At least
  seven minutes of real demo showing a success, an escalation, a guardrail firing, and the
  unattended run. Increase font sizes before recording.
- **(1h)** Final clean-checkout rehearsal from a fresh clone following your own README. Scan the
  repository and its full history for credentials. Confirm all five workbooks are genuinely
  completed. Work the Submission Guide checklist.
- Package as `FirstnameLastname_Capstone_Submission.zip`, exactly four top-level folders
  (`01_Video`, `02_Report`, `03_Workbooks`, `04_Source_Code`), nothing nested in an extra
  wrapper folder. **Target submitting by 17:00 IST, not 23:59.**

---

## Acceptance criteria coverage

| # | Criterion | Day |
|---|---|---|
| A1 | Runs from clean checkout via README | Mon 9, rehearsed Sun 15 |
| A2 | Four channels normalised | Mon 9 |
| A3 | Intent + urgency + numeric confidence | Tue 10 |
| A4 | Retrieval returns resolvable passages | Tue 10 |
| A5 | Deterministic threshold routing | Wed 11 |
| A6 | Citations resolve to retrieved passages | Wed 11 |
| A7 | A guardrail that actually blocks | Thu 12 |
| A8 | Complete decision log that reconciles | Wed 11 |
| A9 | Full set, single unattended run | Thu 12 |
| A10 | Metrics report produced automatically | Thu 12 |
| A11 | Degrades under failure, no crash | Fri 13 |
| A12 | Tests from one documented command | Fri 13 |

## Targets to report against

Business: first contact resolution 42% → 60%+, time to first reply 8–12 hrs → under 5 min,
satisfaction proxy 3.2 → 4.0+, escalation 58% → 30% or lower, repeat contacts halved. *(The
Project Brief's client table says 65% FCR while the targets table and Evaluation Framework say
60%; report against 60% and note the client's aspiration.)*

Technical: classification precision 85%+, hallucination rate ≤5%, citation accuracy 95%+, p95
latency under 3s, availability 99.5%+.

Governance conditions (pass/fail): zero private data in outbound responses, under five points
cross-group variation, complete decision log coverage, confidence calibrated within five points.

## Contingency

There are no slack days. The decision point is **Thursday 12 November**: if the full unattended
run is not working by the end of that evening, abandon new capability and spend Friday making
the run complete with whatever already works. Two intent classes handled properly with a clean
unattended run passes the gate; eight handled beautifully with no run does not.

Drop in this order if needed: intent breadth, then the Prometheus endpoint, then report length
toward the twenty-page floor. Do not drop the video — it is 10% of the marks on its own and
cannot be reconstructed afterwards.

## Questions to send today

The course email asks you to raise questions early rather than in the final week.

- **An extension**, given your available hours. Ask before the deadline, with a reason.
- **Hidden set size:** 120 tickets in the README, Project Instructions §05 and Build
  Specification §04; 100 in Start Here, Project Instructions §10, Build Specification §08 and
  the Evaluation Framework. (Make the harness count-agnostic regardless.)
- **Validation set usage:** the Project Brief says "do not look at these while building, do not
  tune against them"; the README and Build Specification say check yourself against them freely,
  and the gate itself runs the validation set. Confirm which applies.
- **Hallucination review:** the framework asks for fifty responses assessed by two independent
  people. Confirm a single-assessor sample with a declared limitation is acceptable on an
  individual project.
- **Whether the pack's archive naming and four-folder layout still apply**, since the
  announcement mentions only "complete project files plus a 20-minute video".
