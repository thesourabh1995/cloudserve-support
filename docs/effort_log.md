# Effort log — CloudServe intelligent support system

## How this record was compiled, and what that means for reading it

This log was assembled on 20 November from evidence rather than kept live: the commit timestamps
in this repository, the modification times of the run artefacts in `storage/` and
`evaluation/results/`, and the dated session entries in `docs/report_notes.md`, written at the
end of each session while the work was fresh.

The Submission Guide asks for entries at least every second day and says a log written from
memory in the final week is obvious. This one is neither continuous nor written from memory:
every row is anchored to a timestamp checkable against `git log`, and the four rows that are not
are marked **estimated** in the hours column. Stating which is which is more useful than
presenting the whole as a contemporaneous record it is not.

The shape of the work deserves the same treatment. The commit history runs from 10 November
15:14 to 11 November 16:00, with a discovery session on 8 November recorded in the notes but
not committed until the 10th, so the project was built in three concentrated sessions rather
than across three weeks. Smoothing these entries over the intended calendar would contradict
the commit history sitting beside them in the same submission.

---

## 1. Your details

| Field | Value |
|---|---|
| Full name | Sourabh Mishra |
| Contact | sourabhmishra2708@gmail.com |
| Project start date | 8 November 2026 |
| Target submission date | 22 November 2026, extended from 15 November |
| Hours available per week | ~4 per day planned; see the capacity table in Stage 4 |

The extension was requested before the original deadline rather than after it, which is what the
Project Instructions require and what `docs/project_plan.md` recommended doing on day one. It moved
the submission date by a week and did not change the shape of the build, which was already
complete on 11 November; what it bought was the time for the video, the packaging and this
record.

---

## 2. Summary of hours by stage

Planned hours are taken from the backlog estimates in `docs/stage4_sprint_plan.md`, which were
written before the build. Actual hours are derived as described above.

| Stage | Planned hours | Actual hours | Difference | Why the difference |
|---|---:|---:|---:|---|
| 1. Discovery | 3.0 | 3.25 | +0.25 | The only stage that landed on estimate. Reading five transcripts against 500 tickets takes the time it takes, and the script that computed the interview verdicts was written once and not revised |
| 2. Requirements | 2.0 | 0.20 | −1.80 | The PRD and the traceability chain were assembled from material that already existed in the running notes and the evidence register, so the writing was transcription rather than thinking. The thinking had happened during the build and was charged to stage 5 |
| 3. Prompt library | 1.0 | 0.20 | −0.80 | The prompts were written as versioned files during the build itself, so the workbook recorded them rather than producing them |
| 4. Sprint plan | 0.5 | 0.15 | −0.35 | Written against `docs/project_plan.md`, which already existed |
| 5. Build and revision | 25.5 | 7.75 | −17.75 | The single largest divergence, and the one worth examining. See the note below |
| 6. Report, video, packaging | 6.5 | 4.70 | −1.80 | Incomplete rather than fast: the video and packaging are not yet done and account for 3.5 of the planned hours |
| **Total** | **38.5** | **16.25** | **−22.25** | |

**On stage 5.** Twenty-three and a half planned hours became under eight. The cause is not that
the work was smaller than estimated; it is that the estimates were written for hand-written code
and the code was written with AI assistance, which is declared in section 10 of the report and
logged per task in `docs/report_notes.md`. The estimates in the backlog were never revised to
account for it, which is itself an estimation failure worth recording: the plan measured the
wrong quantity for the whole of the build.

The hours that did not shrink are the ones that required judgement rather than typing — the
discovery reading, the report, and the measurement work on 11 November where the token cost had
to be decomposed before it could be reduced.

**Outstanding at the time of writing.** Hallucination scoring (B-17, 2.0 planned), the video
(B-20, 2.5 planned) and packaging (B-21, 1.0 planned). These are not included in the actual
totals above because they have not been done.

---

## 3. Week one: daily entries

| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|---|---|:---:|---:|---|---|
| Sun&nbsp;8&nbsp;Nov | Read the five stakeholder transcripts against the development ticket set | 1 | 1.5 *(estimated)* | The interview half of the Stage 1 workbook; four claims marked for verification against the data | No |
| Sun&nbsp;8&nbsp;Nov | Write `analysis/discovery_analysis.py`, standard library only | 1 | 1.0 *(estimated)* | `docs/discovery_findings.md`, regenerated from the 500 tickets and 29 articles | No |
| Sun&nbsp;8&nbsp;Nov | Repository scaffold to the structure the submission guide requires | 5 | 0.5 *(estimated)* | Directory layout, `.env.example`, running-notes file | No |

Committed 10 Nov 15:52 in `Scaffold repository and add Stage 1 discovery analysis`. The session
itself is recorded in the running notes under 8 November; the two-day gap between working and
committing is why these three rows are marked estimated.

Two interview claims did not survive contact with the data. Both became discovery findings
rather than being quietly dropped, which is what the workbook asks for.

---

## 4. Week two: daily entries

### Tuesday 10 November — afternoon (15:14 to 17:12, timestamped)

| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|---|---|:---:|---:|---|---|
| Tue&nbsp;10&nbsp;Nov | Environment, dependency pins, first real model call | 5 | 0.5 | Working `requirements.txt` | **Yes.** The pack's own pins do not resolve: `openai==1.0.0` against `langchain-openai==0.0.7` needing `openai>=1.10.0`. Re-pinned from a verified install. The machine's default `python3` was 3.9.6, below the project floor |
| Tue&nbsp;10&nbsp;Nov | Ingest: four channels into one `Ticket` shape | 5 | 0.3 | 580 tickets parsed, zero failures; `customer_name` dropped at the boundary | No |
| Tue&nbsp;10&nbsp;Nov | Retrieval, with five chunk configurations measured | 5 | 0.4 | 800/120 chosen on recall@3 at 94.7%; titles prepended to every chunk | No |
| Tue&nbsp;10&nbsp;Nov | Model client with a typed failure, then classification | 5 | 0.3 | Intent, urgency, confidence, defined fallback | No |
| Tue&nbsp;10&nbsp;Nov | Provider made a configuration choice, defaulting to Groq | 5 | 0.1 | `src/config.py` | **Yes.** OpenRouter's free tier is 50 requests a day against a run needing ~800. Checked before committing to it rather than after |
| Tue&nbsp;10&nbsp;Nov | Model comparison on a stratified sample | 5 | 0.4 | `docs/model_choice.md`; gpt-oss-20b chosen on measured accuracy | No |

### Tuesday 10 November — evening (ends 22:44, start estimated)

| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|---|---|:---:|---:|---|---|
| Tue&nbsp;10&nbsp;Nov | Routing as a pure function, seven ordered rules | 5 | 0.5 *(estimated)* | Deterministic routing reading no customer attribute | No |
| Tue&nbsp;10&nbsp;Nov | SQLite decision log, committed per ticket | 5 | 0.4 *(estimated)* | One row per ticket per run, with the reason | No |
| Tue&nbsp;10&nbsp;Nov | Grounded generation with resolving citations | 5 | 0.6 *(estimated)* | Citations must quote a verbatim span of a retrieved passage | No |
| Tue&nbsp;10&nbsp;Nov | Two guardrails that block rather than warn | 5 | 0.5 *(estimated)* | No off switch, no config key | No |
| Tue&nbsp;10&nbsp;Nov | Unattended harness and metrics report | 5 | 0.8 *(estimated)* | `--input` and `--output`, no hardcoded filename | No |
| Tue&nbsp;10&nbsp;Nov | Test suite and CI, including a credential scan | 5 | 0.45 *(estimated)* | Green from one documented command | No |

Only the closing commit of this session carries a timestamp, so the split across the six rows is
apportioned by the size of each change rather than observed. The session total of 3.25 hours is
itself an estimate.

### Wednesday 11 November — morning (10:00 to 11:18; artefact times from 10:29)

| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|---|---|:---:|---:|---|---|
| Wed&nbsp;11&nbsp;Nov | Measure and reduce token cost per ticket | 5 | 0.8 | 3,278 down to 1,472 tokens per ticket, a 55% reduction across four measured runs (`storage/cost_twelve*.json`, 10:29 to 10:50) | **Yes, and it would have failed the gate.** The first measurement projected roughly twice the published daily allowance for the hidden set, so the run would not have completed on an assessor's free-tier key |
| Wed&nbsp;11&nbsp;Nov | Full validation run, unattended, once | 5 | 0.5 | 80 tickets, 130 calls, 117,751 tokens, 9.4 minutes, 80 of 80 decisions logged (`storage/validation_01.log`, 10:57) | No. Deliberately nothing was tuned afterwards |

### Wednesday 11 November — midday (11:18 to 13:19, timestamped)

| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|---|---|:---:|---:|---|---|
| Wed&nbsp;11&nbsp;Nov | Fairness audit, segmented per pipeline stage | 5 | 0.25 | The tier gap decomposed to ticket content; the confidence gap on non-fluent tickets found at a stage nobody predicted | No |
| Wed&nbsp;11&nbsp;Nov | Kill switch and the governance framework | 5 | 0.25 | A file whose presence halts automatic answering, built rather than declared missing | No |
| Wed&nbsp;11&nbsp;Nov | Commit the documentation corpus; fix the Python version instruction | 5 | 0.35 | Two gate-breaking defects closed | **Yes.** Both found by the rehearsal below, neither visible from reading the repository |
| Wed&nbsp;11&nbsp;Nov | Clean-checkout rehearsal | 5 | 0.25 | `docs/clean_checkout_rehearsal.md` | The corpus had been gitignored with the course ticket sets, and Chroma returns an empty collection rather than an error, so a fresh clone would have escalated all 120 hidden tickets and reported a completed run |
| Wed&nbsp;11&nbsp;Nov | Hallucination review sheet | 5 | 0.10 | 59 replies placed beside the full text of the articles they cite | **Scoring still outstanding.** The framework asks for two independent assessors and an individual project has one |
| Wed&nbsp;11&nbsp;Nov | Evidence-to-requirement traceability chain | 2 | 0.10 | `docs/traceability.md`, EV to FR to PR to module | No |
| Wed&nbsp;11&nbsp;Nov | Problem statement | 1 | 0.05 | `docs/problem_statement.md` | No |
| Wed&nbsp;11&nbsp;Nov | PRD version 1.0 and the revision log to 2.0 | 2 | 0.10 | Three requirements added, each with its trigger | No |
| Wed&nbsp;11&nbsp;Nov | Stage workbooks 1, 3 and 4 | 1, 3, 4 | 0.55 | Discovery, prompt library, sprint plan | No |

### Wednesday 11 November — afternoon (13:19 to 16:00, timestamped)

| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|---|---|:---:|---:|---|---|
| Wed&nbsp;11&nbsp;Nov | Write the report, build the four figures, PDF toolchain | 6 | 2.7 | 27 pages against a 20–30 limit; `docs/report.pdf` built at 15:59 | **Yes, and it was a finding.** Tallying the routing figure from the decision log did not reconcile with the metrics report. The two missing tickets were a third abstention path — the model declining to answer — that had never been designed |

### Thursday 12 November — evening (ends 22:15, start estimated)

| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|---|---|:---:|---:|---|---|
| Thu&nbsp;12&nbsp;Nov | Retrospective write-up of the build order and the traps | 6 | 1.5 *(estimated)* | `DEVELOPMENT_PLAN.md` | No |

---

## 5. Week three: daily entries

A third week exists only because the deadline moved to 22 November. Nothing was worked between
13 and 19 November.

| Date | Task | Stage | Hours | What it produced | Blocked by anything? |
|---|---|:---:|---:|---|---|
| Fri&nbsp;20&nbsp;Nov | Compile this effort log from commit timestamps, run-artefact times and the running notes | 6 | 0.3 | `docs/effort_log.md` | **Yes, and it is the cost of not keeping one.** The log had to be reconstructed from evidence because it was never kept live, which is the trap the Submission Guide names and section 7 answers honestly |
| Fri&nbsp;20&nbsp;Nov | Convert the five stage workbooks and the effort log to PDF for `03_Workbooks` | 6 | 0.2 | Six PDFs, 28 pages, typeset with the report's stylesheet (`docs/workbooks/`) | No |
| Fri&nbsp;20&nbsp;Nov | Fix two stale cells and one stale status row in the Stage 4 sprint plan | 4 | — | Capacity table completed from the record; B-19 corrected from Outstanding to Done | The capacity table still carried two *to be completed* placeholders, which would have read as a skeleton workbook |

Timestamps for these rows are the file modification times of the built PDFs, 23:27 to 23:39 on
20 November. The PDFs themselves are not committed — they are typeset output, and they ship in
`02_Report` and `03_Workbooks` rather than being kept in two places that can drift apart. The third row is charged at zero because it was a correction made during the
second, not separate work.

**Still to do, with the backlog estimates against them:** score the hallucination review (B-17,
2.0), record the video (B-20, 2.5), and package the archive (B-21, 1.0, now partly done). Two
days remain against 5.5 planned hours, which is the first point in this project where the
remaining estimate fits comfortably inside the remaining time.

---

## 6. Estimates against reality

The five largest items from the sprint plan backlog.

| Item | Estimated hours | Actual hours | Why the difference |
|---|---:|---:|---|
| B-18 Workbooks and PRD revision | 4.0 | 0.85 | The material already existed in the running notes and the evidence register. The estimate priced writing from a blank page, and the habit of writing session notes meant the page was never blank |
| B-19 Report | 3.0 | 2.70 | The closest estimate in the backlog, and the only large item that did not shrink. Assembly from notes was fast; reconciling the routing counts against the decision log was not, and that is where the time went |
| B-02 Data loading and normalisation | 2.5 | 0.30 | Four channels into one shape is a well-understood problem with an unambiguous definition of done. Over-estimated because it was listed early and early items attract caution |
| B-05 Evaluation harness | 2.5 | 0.80 | Over-estimated for the same reason, though the harness earned its place: it is what surfaced the token cost that would otherwise have failed the gate |
| B-06 Intent and urgency classifier | 2.0 | 0.30 | The estimate assumed prompt iteration that did not prove necessary. What did take time was not in this item at all — choosing the model by measurement, and later splitting reasoning effort per task |

---

## 7. Where the time went unexpectedly

**Which task took far longer than you expected, and why?** Reducing the token cost. It was not a
backlog item at all, because the plan treated cost as a budget concern rather than an acceptance
concern. It became the longest single task of 11 November once the first measurement showed the
run projecting to roughly twice the published daily allowance for the hidden set, which would
have failed the gate for reasons unrelated to whether the system works. The time went on
decomposing the figure rather than on the fixes: finding that hidden reasoning tokens were the
larger half of it took longer than removing them.

**Which task was easier than you expected, and why?** Almost the entire build, for a reason that
is uncomfortable rather than flattering: the backlog estimates were written for hand-written code
and the code was written with AI assistance, so stage 5 came in at under a third of its estimate.
Nobody revised the estimates once that was obvious, so the plan measured the wrong quantity for
two days.

**What would you allocate differently if you started again on Monday?** Spread the work across
the calendar instead of compressing it into three sessions; the compression is visible in the
commit history and no amount of good work inside those sessions repairs it. Start this log on day
one, because reconstructing it from timestamps costs more than fifteen minutes a day would have
and produces a weaker record. And move the clean-checkout rehearsal to the first day, repeating
it daily — doing it four days early was the best decision of the project and it was nearly the
last one.

**What did you spend time on that turned out not to matter?** Designing around the confidence
threshold as the control that stops wrong answers reaching customers. It fired on three tickets
in eighty with no monotonic relationship to correctness. The right controls were built — the
citation check and the protected-category rule — but the wrong one was credited, which is worse
than building the wrong thing, because the quantity being monitored is then not the quantity
doing the work.

---

## 8. Declaration

This record is an accurate account of my own work on this project, compiled from the evidence
described at the head of this document. Rows marked *(estimated)* are apportioned from session
boundaries rather than observed directly, and the log was assembled on 20 November rather than
maintained daily.

| Field | Value |
|---|---|
| Full name | Sourabh Mishra |
| Signature | |
| Date | |
| Total hours recorded | 16.25 |
