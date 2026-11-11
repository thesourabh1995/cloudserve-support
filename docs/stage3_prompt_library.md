# Stage 3 — Prompt library

Prompts live as versioned files in `prompts/`, not as string literals, and the version travels into every decision row. `src/prompts.py` loads them and `register()` lists them, so this document and the running system cannot drift.

## 1. From requirement to specification

| FR | Specification | Inputs | Outputs | Acceptance |
|---|---|---|---|---|
| FR-01 | Normalise a ticket from any of the four channels into one `Ticket`, preserving original text and channel, tolerating missing fields, unusual characters and empty bodies. Drop `customer_name` at this boundary so personal data cannot reach a prompt or a reply | A raw record from any channel | `Ticket`, with `is_empty` set when there is no usable text | A2. Verified across all 580 supplied tickets: zero parse failures, zero unrecognised channels |
| FR-02 | Assign exactly one intent from the fixed 22-value taxonomy. Never invent a value; use `unclear_request` when the ticket does not carry enough information | Channel, subject, body | Intent string from the taxonomy | A3 |
| FR-03 | Assign urgency and a numeric confidence, record up to three alternatives considered, and return a defined fallback rather than raising when the response cannot be parsed | Same as FR-02 | Urgency, confidence 0–1, alternatives, reason in a support manager's language | A3 |
| FR-04 | Embed the 29 articles into a cosine-similarity store with the article title prepended to every chunk, and return nothing when nothing clears the relevance floor | Query text, top-k | Ranked passages with doc_id, title, text, similarity; possibly empty | A4. chunk_size 800 / overlap 120, chosen on recall@3 of 94.7% across five measured configurations |
| FR-05 | Draft a reply using only the supplied passages, with ticket text delimited and declared untrusted so customer text cannot restate the instructions | Ticket, up to three distinct-document passages | Structured reply with answer, citations, and a `known` flag | A6 |
| FR-06 | Each citation must carry a verbatim span of a passage that was actually retrieved, so a fabricated reference fails even when the document exists | Draft, retrieved passages | Resolved / unresolved per citation | A6, A7 |

Only FR-02, FR-03, FR-05 and FR-06 are implemented by prompts. FR-01, FR-04 and the rest are ordinary code, which is deliberate: a language model is used where judgement about language is required and nowhere else.

## 2. The prompt register

### PR-01 — classify

| Field | Value |
|---|---|
| Name and purpose | Assign an intent and urgency to a ticket, with a confidence and the alternatives considered |
| Category | Build |
| Serves requirement | FR-02, FR-03 |
| Version | 1.0 |
| Model used | `openai/gpt-oss-20b` via Groq, temperature 0, reasoning effort `medium` |
| Inputs | `channel`, `subject`, `body` |
| Output format | A single JSON object: `intent`, `urgency`, `confidence`, `alternatives[]`, `reason` |
| How we know it worked | 91.2% classification accuracy over the 80-ticket validation run against a target of 85%. Per-class precision and recall in `metrics.json` |
| Known weaknesses | **The purpose line claims a "calibrated confidence" and that is false.** Correctness is not monotonic in the number it returns: 0.80 and 0.95 both scored 100% while 0.90 scored 87%, and only 3 of 80 tickets fell below 0.80. It also reports lower confidence on non-fluent English while classifying it more accurately. Small models also wrap JSON in prose, handled by `extract_json` rather than by asking more firmly |
| Change history | 1.0 initial. No text change yet; the reasoning-effort setting moved from global to per-task on 11 Nov, which changes behaviour without changing the prompt and so did not bump the version |

Temperature is fixed at 0 by the caller. A sampled classification would route the same ticket two different ways on two runs, which fails A5.

### PR-02 — generate

| Field | Value |
|---|---|
| Name and purpose | Draft a reply grounded only in the retrieved passages, with a verbatim span for every citation |
| Category | Build |
| Serves requirement | FR-05, FR-06 |
| Version | 1.0 |
| Model used | `openai/gpt-oss-20b` via Groq, temperature 0, reasoning effort `low` |
| Inputs | Ticket text and up to three passages, one per distinct document |
| Output format | JSON: `answer`, `citations[{doc_id, supports}]`, `known` |
| How we know it worked | 98.0% citation accuracy over the validation run (100 of 102 citations resolved) against a 95% target. The two that did not resolve were blocked rather than sent |
| Known weaknesses | It will occasionally cite a real document with a quote that is not in the retrieved passage, which is why the guardrail checks the span rather than trusting the citation. Reasoning effort is set to `low` for cost, on the argument that the guardrail checks the output regardless — that tradeoff is declared in `docs/run_cost.md` and is not independently validated for generation quality |
| Change history | 1.0 initial |

### Categories not used

Specification, review and evaluation prompts were not used. Specifications were written directly, review was done by reading and by the test suite, and evaluation is measured by code against labels rather than judged by a model. Using a model to grade its own output would make the evaluation depend on the thing being evaluated; the one judgement that genuinely needs a human — hallucination rate — is done by hand in `docs/hallucination_review.md`.

## 3. Prompt text

Full text is in `prompts/build/classify.md` and `prompts/build/generate.md`, each with front matter carrying its ID, version, requirements and acceptance criteria. They are reproduced verbatim in the report appendix rather than duplicated here, so there is one copy to keep current.
