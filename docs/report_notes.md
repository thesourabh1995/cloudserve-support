# Running notes for the report

Fifteen minutes at the end of each working session. Record what was built, what was
decided, and what was rejected. The report is assembled from this rather than written
from memory, and the "explain every decision" marks come from here.

Format: what I did / what I chose / what I rejected and why / what surprised me.

---

## Sun 8 Nov — Day 1: setup and discovery analysis

**Built.** Repository scaffold matching the structure the submission guide requires.
`analysis/discovery_analysis.py`, standard library only so it runs before dependencies
are installed, producing `docs/discovery_findings.md` from the 500 development tickets
and the 29 knowledge base articles.

**Decided.** Course-supplied datasets are kept out of version control, with a committed
12-ticket sample (three per channel) for the smoke test, because the submission guide
asks for small sample data only.

**Surprised by.** Two interview claims do not survive contact with the data — see the
findings file, section six. Both are recorded as discovery findings because the workbook
asks for disagreements resolved with evidence rather than by judgement.

**Still to decide.** The problem statement itself (Stage 1 section six).

---

## Tue 10 Nov — Day 2: environment, ingest, retrieval

**Found.** The dependency list supplied in the pack cannot be installed at all. It pins
`openai==1.0.0` while `langchain-openai==0.0.7` requires `openai>=1.10.0`; pip reports
`ResolutionImpossible`. Replaced with pins frozen from a verified install on Python 3.11.
The machine's default `python3` was 3.9.6, below the 3.10 floor the pack requires.

**Built.** Ingest (A2): all four channels into one `Ticket`. Verified against all 580
tickets in both supplied files — zero parse issues, zero empty bodies, no unrecognised
channels. Retrieval (A4): 29 articles into 59 passages in Chroma, cosine similarity,
with a relevance floor below which nothing is returned.

**Decided — chunking, from measurement.** Five configurations measured against the 357
development tickets carrying `expected_doc_ids` (`docs/retrieval_tuning.md`).
chunk_size=800 / overlap=120 wins on recall@3 at 94.7%. Recall@3 is the figure that
matters because generation receives the top passages, not only the first. Notably the
pack's suggested default was best, but it is now a measured choice rather than an
inherited one.

**Decided — the title is prepended to every indexed chunk.** Ines described a customer
writing "my deployment keeps dying" against an article titled "resolving container
health check failures". Titles carry vocabulary the body lacks. Verified: that exact
query now surfaces DOC-DEPLOY-001.

**Decided — retrieval returns nothing rather than its best guess.** An irrelevant
passage is indistinguishable from a relevant one downstream, so a retriever that always
answers reproduces the findability failure while concealing it. Cost measured: 0.6% of
answerable tickets return nothing at the chosen configuration and will escalate. Revisit
if the escalation rate lands above target.

**Decided — no label leakage.** `labels` and `history` load through a separate function
used only by the harness. `customer_name` is dropped at the ingest boundary so personal
data cannot reach a prompt or an outbound response. Both are covered by tests.

**Resilience fix.** sentence-transformers contacts the HuggingFace Hub on construction
even when weights are cached, turning an offline network into a hard retrieval failure.
Now falls back to `local_files_only=True`. Relevant to A11.

**Surprised by.** Smaller chunks (400) never returned nothing, but scored lower on
recall@3 than 800 did. More passages means more chances to clear the floor, but
individually weaker matches.

**Still to decide.** The problem statement. The routing threshold, which needs
calibration data that does not exist until classification runs.

---

## Wed 11 Nov — Day 3: routing, generation, guardrails, the harness, and the first real evaluation

**Built.** Routing (A5) as a pure function with seven ordered rules, first match wins, so
the same ticket routes identically every time. SQLite decision log (A8), one row per
ticket per run, committed per ticket so a crash cannot lose the history. Grounded
generation (A6) and two blocking guardrails (A7). The unattended harness (A9, A10)
taking `--input` and `--output`, and a local console for the demo. Provider-outage test
for A11: six uncached tickets against an invalid key, all six escalated and logged, run
completed. CI green (A12), including a step that scans for credentials.

**Found — the run did not fit the free tier.** First measurement was 3,278 tokens per
ticket. The 120-ticket hidden set would have needed about 393,000 tokens against a
published daily allowance of 200,000, so the gate itself would have failed on an
assessor's fresh key. Decomposing the figure showed roughly half was hidden reasoning
tokens, which these models bill as output. Three fixes took it to 1,472 (`docs/run_cost.md`):
one passage per document instead of per chunk, reasoning effort set per task, and no
draft attempted where a draft could never be sent.

**Found — the account exposes no daily token limit.** Only 1,000 requests per day and a
continuously refilling 8,000 per minute. So the per-minute bucket sets a floor on wall
clock rather than a ceiling on volume: 120 tickets cannot finish in under about 22
minutes however fast the machine is. The 200,000 daily figure is published but
unverifiable from the account, and the report should say so rather than cite it as fact.

**Decided — reasoning effort per task, not globally.** Classification at `medium`,
generation at `low`. On 18 stratified tickets classification scored 94.4% at medium
against 88.9% at low. Generation does not pay for the reasoning because its output is
checked by the citation guardrail regardless. The evidence is 18 tickets and one ticket
moved, which is suggestive rather than conclusive, and is declared as such.

**Ran.** The full 80-ticket validation set, unattended, one run: 130 calls, 117,751
tokens, 9.4 minutes, 80 of 80 decisions logged and reconciling (`docs/validation_run.md`).
Five of eight measurable targets met. Deliberately did not tune anything afterwards.

**Surprised by — the tier gap is not what it looks like.** Standard-tier tickets are
answered automatically 30 points less often than enterprise, which reads as the system
serving cheaper customers worse. It decomposes entirely to ticket content: 26% of
standard-tier tickets carry a protected-category intent against 7% of business, and
`src/route.py` reads no customer attribute at all. Worth keeping the raw figure in the
report next to the decomposition rather than only the reassuring version.

**Surprised by — confidence is not calibrated.** Correctness is not monotonic in
confidence: 0.80 and 0.95 both scored 100% while 0.90 scored 87%, and only 3 of 80
tickets fall below the 0.80 threshold. The threshold is therefore doing almost no work,
and the real safety comes from the grounding checks and the protected-category rule.
Left at 0.80 on purpose; raising it would buy escalations without accuracy. This also
means the governance condition "confidence calibrated within five points" cannot honestly
be claimed as met.

**Fixed.** `outcomes.jsonl` recorded the action but not the rule, so the reason a ticket
left the queue existed only in the database. Now carries both, with a test.

**Still to decide.** The problem statement, still. Whether to report the latency target
as missed or as a declared tradeoff. Whether the single `no_supporting_passage`
escalation is worth relaxing to bring escalation from 31.2% to under 30%.

---

## AI tool use — log as you go

Required by Project Instructions §09 and the final checklist. Keeping it here as it
happens means the declaration is accurate rather than reconstructed.

| Date | Tool | Used for | What I changed or overrode |
|---|---|---|---|
| 8 Nov | Cursor / Claude | Repository scaffold and the discovery analysis script | |
| 10 Nov | Cursor / Claude | Ingest, retrieval, config, test suites, tuning script | Chose cosine over default L2; added offline fallback for the encoder |
| 10 Nov | Cursor / Claude | Model client, classifier, prompt PR-01, model comparison script | Rejected the suggested OpenRouter default after checking its 50/day free limit against our ~800-call run; picked gpt-oss-20b on measured accuracy rather than model size |
| 10 Nov | Cursor / Claude | Routing and the SQLite decision log | Kept the confidence threshold at the brief's 0.80 until a full classification pass exists to calibrate it; the other branches follow the development labels |
| 10 Nov | Cursor / Claude | Grounded generation (PR-02) and the blocking guardrails | Citations must be a verbatim span of a retrieved passage; a reply with an email, phone or key is blocked rather than warned |
| 10 Nov | Cursor / Claude | Local console and the unattended harness | Satisfaction and hallucination stay blank in the report, because those need a human review and the run must not invent them |
| 10 Nov | Cursor / Claude | CI workflow and the provider-outage run | Ran the outage test on uncached tickets so the response cache could not hide the failure |
| 11 Nov | Cursor / Claude | Token-cost reduction and the per-task reasoning split | Checked the published daily token limit against the account's own headers and found it is not exposed; recorded it as unverified rather than citing it |
| 11 Nov | Cursor / Claude | Validation run and the analysis of its results | Declined to tune the confidence threshold or relax the protected-category rules to hit the escalation target; decomposed the tier gap rather than reporting the raw 30-point spread alone |
