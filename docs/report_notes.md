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

## AI tool use — log as you go

Required by Project Instructions §09 and the final checklist. Keeping it here as it
happens means the declaration is accurate rather than reconstructed.

| Date | Tool | Used for | What I changed or overrode |
|---|---|---|---|
| 8 Nov | Cursor / Claude | Repository scaffold and the discovery analysis script | |
