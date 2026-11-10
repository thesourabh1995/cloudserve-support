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

## AI tool use — log as you go

Required by Project Instructions §09 and the final checklist. Keeping it here as it
happens means the declaration is accurate rather than reconstructed.

| Date | Tool | Used for | What I changed or overrode |
|---|---|---|---|
| 8 Nov | Cursor / Claude | Repository scaffold and the discovery analysis script | |
| 10 Nov | Cursor / Claude | Ingest, retrieval, config, test suites, tuning script | Chose cosine over default L2; added offline fallback for the encoder |
