"""Local console for trying one ticket.

    python -m src.api

Then open http://127.0.0.1:8000. This is the interactive way to see a
decision. The unattended run over a whole file is the harness, which is
separate and is what acceptance criterion A9 checks.
"""

import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from src import killswitch
from src.pipeline import Pipeline

app = FastAPI(title="CloudServe support console")
_pipeline: Pipeline | None = None


def get_pipeline() -> Pipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = Pipeline(run_id="local")
    return _pipeline


# Sample tickets from the validation set, so a demonstration does not depend on
# typing a ticket accurately. These only fill the form; the pipeline still runs.
SAMPLES = [
    {
        "key": "VAL-0001",
        "name": "API key returning 401",
        "note": "VAL-0001 · answerable from the documentation",
        "channel": "forum",
        "subject": "Need to rotate an exposed key",
        "body": (
            "One of our production keys started returning 401 at around yesterday "
            "morning without any change on our side. Other keys against the same "
            "account are still working."
        ),
    },
    {
        "key": "VAL-0043",
        "name": "Possible credential exposure",
        "note": "VAL-0043 · protected category",
        "channel": "forum",
        "subject": "Suspicious activity in audit log",
        "body": (
            "One of our engineers believes their credentials may have been exposed "
            "in a breach at another service. What should we be doing right now?"
        ),
    },
    {
        "key": "VAL-0002",
        "name": "Empty follow-up",
        "note": "VAL-0002 · unclear request, nothing retrieved",
        "channel": "chat",
        "subject": "",
        "body": "Following up on my previous message. Any update?",
    },
    {
        "key": "VAL-0011",
        "name": "Rollback after a bad release",
        "note": "VAL-0011 · exercises the grounding guardrail",
        "channel": "forum",
        "subject": "How do I revert to the previous revision",
        "body": (
            "We shipped a release yesterday morning that has broken checkout for a "
            "portion of our customers. We need to get back to the previous version "
            "quickly. What is the fastest safe route?"
        ),
    },
    {
        "key": "DEMO-VOCAB",
        "name": "The vocabulary gap",
        "note": "customer words, documentation title",
        "channel": "email",
        "subject": "Deployment health check failing",
        "body": (
            "My deployment keeps failing its health check after the last release. "
            "The container starts, then gets restarted. What should I look at?"
        ),
    },
]


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CloudServe support console</title>
<style>
  :root {
    /* shell */
    --shell: #171a21;
    --shell-2: #1e222b;
    --shell-3: #272c37;
    --shell-line: #333a47;
    --shell-ink: #eceef2;
    --shell-muted: #949cab;

    /* content */
    --bg: #f3f4f7;
    --surface: #ffffff;
    --surface-alt: #f8f9fb;
    --border: #e3e5ea;
    --border-strong: #cfd3db;
    --ink: #171a21;
    --muted: #596071;
    --faint: #878e9e;

    /* accent and status */
    --accent: #4338ca;
    --accent-bright: #5b52e0;
    --accent-soft: #eeeefc;
    --accent-line: #d7d6f6;
    --ok: #0b6b3f;
    --ok-soft: #e6f4ec;
    --warn: #8a5200;
    --warn-soft: #fbf1df;
    --stop: #a8182f;
    --stop-soft: #fbe9ec;

    --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  }

  * { box-sizing: border-box; }

  html, body { height: 100%; }
  body {
    margin: 0;
    display: flex;
    flex-direction: column;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.5;
    color: var(--ink);
    background: var(--bg);
    -webkit-font-smoothing: antialiased;
  }

  /* ---------- top bar ---------- */
  .topbar {
    flex: none;
    background: var(--shell);
    color: var(--shell-ink);
    border-bottom: 1px solid #000;
    padding: 0 1.5rem;
    height: 56px;
    display: flex;
    align-items: center;
    gap: 0.9rem;
  }
  .mark {
    width: 26px; height: 26px; border-radius: 6px;
    background: linear-gradient(135deg, var(--accent-bright), var(--accent));
    display: grid; place-items: center;
    font-size: 0.8rem; font-weight: 700; color: #fff;
  }
  .brand { font-size: 1rem; font-weight: 650; letter-spacing: -0.01em; }
  .brand span { font-weight: 400; color: var(--shell-muted); margin-left: 0.5rem; font-size: 0.9rem; }
  .grow { flex: 1; }
  .pill {
    display: inline-flex; align-items: center; gap: 0.45rem;
    font-size: 0.8rem; font-weight: 600;
    padding: 0.3rem 0.7rem; border-radius: 6px;
    border: 1px solid var(--shell-line);
    background: var(--shell-2);
    color: var(--shell-muted);
    white-space: nowrap;
  }
  .pill .led { width: 7px; height: 7px; border-radius: 50%; background: #33c27f; }
  .pill.halted { border-color: #7d1c2c; background: #3a1119; color: #ffc9d1; }
  .pill.halted .led { background: #ef4b63; }

  /* ---------- halt banner ---------- */
  #halt {
    display: none;
    flex: none;
    background: var(--stop-soft);
    border-bottom: 1px solid #f0c2ca;
    color: var(--stop);
    padding: 0.7rem 1.5rem;
    font-size: 0.93rem;
  }
  #halt.on { display: block; }

  /* ---------- shell ---------- */
  .shell {
    flex: 1;
    display: grid;
    grid-template-columns: 372px minmax(0, 1fr);
    min-height: 0;
  }

  /* ---------- sidebar ---------- */
  aside {
    background: var(--shell);
    border-right: 1px solid #000;
    color: var(--shell-ink);
    padding: 1.25rem 1.25rem 2rem;
    overflow-y: auto;
  }
  aside::-webkit-scrollbar { width: 10px; }
  aside::-webkit-scrollbar-thumb { background: #353b48; border-radius: 5px; border: 3px solid var(--shell); }

  .side-title {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.09em; color: var(--shell-muted);
    margin: 0 0 0.6rem;
  }
  .side-title:not(:first-child) { margin-top: 1.5rem; }

  .samples { display: flex; flex-direction: column; gap: 0.3rem; }
  .sample {
    display: block; width: 100%; text-align: left;
    font: inherit; cursor: pointer;
    padding: 0.5rem 0.65rem;
    border: 1px solid var(--shell-line);
    border-radius: 6px;
    background: var(--shell-2);
    color: var(--shell-ink);
    line-height: 1.3;
  }
  .sample b { display: block; font-size: 0.88rem; font-weight: 600; }
  .sample em {
    display: block; font-style: normal;
    font-family: var(--mono); font-size: 0.7rem;
    color: var(--shell-muted); margin-top: 0.1rem;
  }
  .sample:hover { background: var(--shell-3); border-color: #49506080; }
  .sample.on { border-color: var(--accent-bright); background: #262451; }
  .sample.on em { color: #b9b5f5; }

  .field { margin-bottom: 0.75rem; }
  label {
    display: block;
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; color: var(--shell-muted);
    margin-bottom: 0.3rem;
  }
  input, select, textarea {
    width: 100%; font: inherit; font-size: 0.92rem;
    padding: 0.5rem 0.6rem;
    border: 1px solid var(--shell-line);
    border-radius: 6px;
    background: var(--shell-2);
    color: var(--shell-ink);
  }
  textarea { min-height: 6.2rem; resize: vertical; line-height: 1.45; }
  input::placeholder, textarea::placeholder { color: #6b7280; }
  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--accent-bright);
    box-shadow: 0 0 0 3px rgba(91,82,224,0.25);
  }
  select { appearance: none; background-image: none; }

  button.primary {
    width: 100%; font: inherit; font-size: 0.95rem; font-weight: 600;
    padding: 0.62rem 1rem; margin-top: 0.3rem;
    border: none; border-radius: 6px;
    background: var(--accent-bright); color: #fff; cursor: pointer;
  }
  button.primary:hover { background: var(--accent); }
  button.primary:disabled { background: #3b4050; color: #8c93a3; cursor: progress; }
  .kbd { margin: 0.5rem 0 0; font-size: 0.72rem; color: var(--shell-muted); text-align: center; }
  .kbd b { font-family: var(--mono); font-weight: 500; color: #b6bcc9; }

  /* ---------- content ---------- */
  .content { overflow-y: auto; padding: 1.5rem; }
  .inner { max-width: 1040px; }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: 0 1px 2px rgba(23,26,33,0.04), 0 1px 1px rgba(23,26,33,0.03);
    overflow: hidden;
  }

  /* empty state */
  .empty { padding: 3rem 2rem; text-align: center; }
  .empty h2 { margin: 0 0 0.3rem; font-size: 1.1rem; font-weight: 600; }
  .empty p { margin: 0; color: var(--muted); font-size: 0.95rem; }
  .flow {
    display: flex; flex-wrap: wrap; justify-content: center; align-items: center;
    gap: 0.4rem; margin-top: 1.8rem;
  }
  .flow span {
    font-family: var(--mono); font-size: 0.76rem;
    padding: 0.3rem 0.6rem; border-radius: 5px;
    background: var(--surface-alt); border: 1px solid var(--border); color: var(--muted);
  }
  .flow i { color: var(--faint); font-style: normal; font-size: 0.8rem; }

  /* verdict */
  .verdict {
    display: flex; align-items: center; gap: 0.85rem;
    padding: 1.15rem 1.35rem;
    border-bottom: 1px solid var(--border);
  }
  .verdict .dot { width: 11px; height: 11px; border-radius: 50%; flex: none; }
  .verdict h3 { margin: 0; font-size: 1.3rem; font-weight: 650; letter-spacing: -0.015em; }
  .verdict p { margin: 0.1rem 0 0; font-size: 0.9rem; color: var(--muted); }
  .verdict.auto_respond { background: var(--ok-soft); border-bottom-color: #c9e5d6; }
  .verdict.auto_respond .dot { background: var(--ok); }
  .verdict.auto_respond h3 { color: var(--ok); }
  .verdict.escalate { background: var(--warn-soft); border-bottom-color: #ecd9b4; }
  .verdict.escalate .dot { background: var(--warn); }
  .verdict.escalate h3 { color: var(--warn); }
  .verdict.blocked { background: var(--stop-soft); border-bottom-color: #f0c2ca; }
  .verdict.blocked .dot { background: var(--stop); }
  .verdict.blocked h3 { color: var(--stop); }

  /* facts */
  .facts {
    display: grid; grid-template-columns: repeat(5, 1fr);
    margin: 0; border-bottom: 1px solid var(--border);
    background: var(--surface-alt);
  }
  @media (max-width: 1100px) { .facts { grid-template-columns: repeat(3, 1fr); } }
  .fact { padding: 0.75rem 1.35rem; border-right: 1px solid var(--border); }
  .fact:last-child { border-right: none; }
  .fact dt {
    margin: 0 0 0.15rem; font-size: 0.66rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em; color: var(--faint);
  }
  .fact dd { margin: 0; font-size: 1rem; font-weight: 600; }
  .fact dd.mono { font-family: var(--mono); font-size: 0.86rem; }
  .fact dd small { font-weight: 400; color: var(--faint); font-size: 0.78rem; }

  /* stages */
  .stage { padding: 1.1rem 1.35rem; border-bottom: 1px solid var(--border); }
  .stage:last-child { border-bottom: none; }
  .stage h4 {
    margin: 0 0 0.55rem; font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.09em; color: var(--faint);
  }
  .stage p { margin: 0.3rem 0; }
  .stage .lead { font-size: 0.97rem; }

  .chip {
    display: inline-block; font-family: var(--mono); font-size: 0.76rem;
    padding: 0.12rem 0.45rem; border-radius: 4px;
    background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent-line);
  }

  table.passages { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  table.passages td { padding: 0.38rem 0.6rem 0.38rem 0; vertical-align: middle; border-bottom: 1px solid var(--surface-alt); }
  table.passages tr:last-child td { border-bottom: none; }
  td.id { font-family: var(--mono); font-size: 0.79rem; white-space: nowrap; color: var(--accent); width: 1%; }
  td.score { width: 120px; }
  td.num { font-family: var(--mono); font-size: 0.79rem; color: var(--muted); text-align: right; width: 1%; white-space: nowrap; }
  .bar { height: 5px; border-radius: 3px; background: #e8e9f1; overflow: hidden; }
  .bar i { display: block; height: 100%; background: var(--accent); border-radius: 3px; }

  .answer {
    margin: 0; padding: 0.85rem 1rem;
    background: var(--surface-alt);
    border: 1px solid var(--border);
    border-left: 3px solid var(--ok);
    border-radius: 6px;
    font-family: inherit; font-size: 0.96rem; line-height: 1.55;
    white-space: pre-wrap;
  }
  .answer.withheld { border-left-color: var(--faint); color: var(--muted); }

  ul.clean { list-style: none; margin: 0; padding: 0; }
  ul.clean li { padding: 0.4rem 0; border-bottom: 1px solid var(--surface-alt); font-size: 0.92rem; }
  ul.clean li:last-child { border-bottom: none; }
  .cite-id { font-family: var(--mono); font-size: 0.79rem; color: var(--accent); }
  .cite-span { display: block; color: var(--muted); border-left: 2px solid var(--border-strong); padding-left: 0.6rem; margin-top: 0.2rem; }

  .check { display: flex; gap: 0.6rem; align-items: baseline; padding: 0.4rem 0; }
  .check .tag {
    flex: none; font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em;
    padding: 0.12rem 0.45rem; border-radius: 4px;
  }
  .check .tag.pass { background: var(--ok-soft); color: var(--ok); }
  .check .tag.block { background: var(--stop-soft); color: var(--stop); }
  .check .what { font-family: var(--mono); font-size: 0.83rem; }
  .check .detail { color: var(--muted); font-size: 0.9rem; }

  .muted { color: var(--muted); }
  .provenance {
    padding: 0.65rem 1.35rem;
    font-family: var(--mono); font-size: 0.73rem; color: var(--faint);
    background: var(--surface-alt); border-top: 1px solid var(--border);
  }
  .error { color: var(--stop); padding: 1.35rem; }

  .working { padding: 3rem 1.5rem; text-align: center; color: var(--muted); }
  .working .spin {
    width: 22px; height: 22px; margin: 0 auto 0.8rem;
    border: 3px solid var(--border-strong); border-top-color: var(--accent);
    border-radius: 50%; animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  @media (max-width: 900px) {
    .shell { grid-template-columns: 1fr; }
    aside { border-right: none; border-bottom: 1px solid #000; }
  }
</style>
</head>
<body>

<div class="topbar">
  <div class="mark">CS</div>
  <div class="brand">CloudServe<span>Support triage console</span></div>
  <div class="grow"></div>
  <div class="pill" id="state"><span class="led"></span><span id="statetext">Automatic answering active</span></div>
</div>

<div id="halt"><strong>Automatic answering is stopped.</strong> <span id="haltnote"></span> Every ticket is still classified, logged and escalated with its context attached.</div>

<div class="shell">
  <aside>
    <p class="side-title">Sample tickets</p>
    <div class="samples" id="samples"></div>

    <p class="side-title">Ticket</p>
    <form id="ticket">
      <div class="field">
        <label for="channel">Channel</label>
        <select id="channel" name="channel">
          <option>email</option>
          <option>chat</option>
          <option>docs_comment</option>
          <option>forum</option>
        </select>
      </div>
      <div class="field">
        <label for="subject">Subject</label>
        <input id="subject" name="subject" value="Deployment health check failing">
      </div>
      <div class="field">
        <label for="body">Message</label>
        <textarea id="body" name="body">My deployment keeps failing its health check after the last release. The container starts, then gets restarted. What should I look at?</textarea>
      </div>
      <button class="primary" type="submit">Run through the pipeline</button>
      <p class="kbd"><b>&#8984; &#9166;</b> to run &middot; classify and draft each call the model</p>
    </form>
  </aside>

  <div class="content">
    <div class="inner">
      <section class="card" id="result">
        <div class="empty">
          <h2>No ticket run yet</h2>
          <p>Pick a sample on the left, or write one, then run it to see the decision and why it was made.</p>
          <div class="flow">
            <span>ingest</span><i>&rarr;</i>
            <span>classify</span><i>&rarr;</i>
            <span>retrieve</span><i>&rarr;</i>
            <span>route</span><i>&rarr;</i>
            <span>generate</span><i>&rarr;</i>
            <span>guard</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</div>

<script>
const form = document.getElementById("ticket");
const result = document.getElementById("result");

const LABELS = {
  auto_respond: ["Answered automatically", "The reply below was released to the customer."],
  escalate: ["Escalated to a person", "Nothing was sent. The ticket goes to the queue with its context attached."],
  blocked: ["Blocked by a guardrail", "A reply was drafted and withheld. The ticket goes to a person."],
};

function esc(value) {
  return String(value ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

/* ---------- sample tickets ---------- */
fetch("/samples").then((r) => r.json()).then((samples) => {
  document.getElementById("samples").innerHTML = samples.map((s, i) =>
    `<button type="button" class="sample" data-i="${i}"><b>${esc(s.name)}</b><em>${esc(s.note)}</em></button>`
  ).join("");
  document.querySelectorAll(".sample").forEach((el) => {
    el.addEventListener("click", () => {
      const s = samples[el.dataset.i];
      document.getElementById("channel").value = s.channel;
      document.getElementById("subject").value = s.subject;
      document.getElementById("body").value = s.body;
      document.querySelectorAll(".sample").forEach((o) => o.classList.remove("on"));
      el.classList.add("on");
    });
  });
});

/* ---------- kill switch indicator ---------- */
async function pollState() {
  try {
    const s = await (await fetch("/status")).json();
    const banner = document.getElementById("halt");
    const pill = document.getElementById("state");
    banner.classList.toggle("on", s.engaged);
    pill.classList.toggle("halted", s.engaged);
    document.getElementById("statetext").textContent =
      s.engaged ? "Automatic answering STOPPED" : "Automatic answering active";
    if (s.engaged) {
      document.getElementById("haltnote").textContent = s.note ? "Reason given: " + s.note + "." : "";
    }
  } catch (e) { /* the console is still usable without the indicator */ }
}
pollState();
setInterval(pollState, 2000);

/* ---------- run a ticket ---------- */
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    channel: document.getElementById("channel").value,
    subject: document.getElementById("subject").value,
    body: document.getElementById("body").value,
  };
  const button = form.querySelector("button");
  button.disabled = true;
  result.innerHTML = '<div class="working"><div class="spin"></div>Running classify, retrieve, route, draft and the guardrails.</div>';
  const started = performance.now();
  try {
    const response = await fetch("/tickets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const outcome = await response.json();
    result.innerHTML = render(outcome, (performance.now() - started) / 1000);
  } catch (error) {
    result.innerHTML = '<p class="error">The request failed: ' + esc(error) + "</p>";
  } finally {
    button.disabled = false;
    pollState();
  }
});

document.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") form.requestSubmit();
});

/* ---------- rendering ---------- */
function render(o, seconds) {
  if (o.error) return '<p class="error">' + esc(o.error) + "</p>";

  const action = o.final_action;
  const [title, subtitle] = LABELS[action] || [action, ""];
  const cls = o.classification || {};
  const routing = o.routing || {};
  const draft = o.draft || {};
  const guard = o.guardrail || {};

  const verdict = `
    <div class="verdict ${esc(action)}">
      <span class="dot"></span>
      <div><h3>${esc(title)}</h3><p>${esc(subtitle)}</p></div>
    </div>`;

  const facts = `
    <dl class="facts">
      <div class="fact"><dt>Intent</dt><dd class="mono">${esc(cls.intent)}</dd></div>
      <div class="fact"><dt>Urgency</dt><dd>${esc(cls.urgency)}</dd></div>
      <div class="fact"><dt>Confidence</dt><dd>${esc(cls.confidence)} <small>/ ${esc(routing.threshold)}</small></dd></div>
      <div class="fact"><dt>Rule applied</dt><dd class="mono">${esc(routing.rule)}</dd></div>
      <div class="fact"><dt>Elapsed</dt><dd>${seconds.toFixed(2)}s</dd></div>
    </dl>`;

  const routingStage = `
    <div class="stage">
      <h4>Routing decision</h4>
      <p class="lead">${esc(routing.reason)}</p>
    </div>`;

  const alts = (cls.alternatives || []).map((a) =>
    `<span class="chip">${esc(a.intent ?? a)}${a.confidence === undefined ? "" : " " + Number(a.confidence).toFixed(2)}</span>`
  ).join(" ");
  const classification = `
    <div class="stage">
      <h4>Classification</h4>
      <p class="lead">${esc(cls.reason)}</p>
      ${alts ? `<p class="muted" style="font-size:0.88rem">Also considered: ${alts}</p>` : ""}
    </div>`;

  const passages = (o.passages || []);
  const retrieval = `
    <div class="stage">
      <h4>Retrieved passages</h4>
      ${passages.length ? `<table class="passages">${passages.map((p) => `
        <tr>
          <td class="id">${esc(p.doc_id)}</td>
          <td>${esc(p.title)}</td>
          <td class="score"><span class="bar"><i style="width:${Math.max(2, Math.min(100, (p.similarity || 0) * 100)).toFixed(0)}%"></i></span></td>
          <td class="num">${Number(p.similarity).toFixed(3)}</td>
        </tr>`).join("")}</table>`
        : '<p class="muted">Nothing cleared the relevance floor, so there was nothing to ground an answer in.</p>'}
    </div>`;

  const skipped = (draft.reason || "").startsWith("no draft attempted");
  const answerBlock = o.sent_answer
    ? `<pre class="answer">${esc(o.sent_answer)}</pre>`
    : skipped
      ? `<p class="muted">No draft was attempted, because this ticket can never be answered automatically. Spending a model call on text nobody should trust would also put a bad suggestion in front of the person handling it.</p>`
      : `<p class="muted" style="font-size:0.9rem;margin-top:0">Nothing was released to the customer. The draft is kept for the person who picks this up:</p>
         <pre class="answer withheld">${esc(draft.answer)}</pre>`;

  const reply = `
    <div class="stage">
      <h4>${o.sent_answer ? "Reply sent" : "Draft, not sent"}</h4>
      ${answerBlock}
    </div>`;

  const citations = (draft.citations || []);
  const citeStage = citations.length ? `
    <div class="stage">
      <h4>Citations</h4>
      <ul class="clean">${citations.map((c) => `
        <li><span class="cite-id">${esc(c.doc_id)}</span><span class="cite-span">${esc(c.supports)}</span></li>`).join("")}</ul>
    </div>` : "";

  const findings = (guard.findings || []);
  const guardStage = findings.length ? `
    <div class="stage">
      <h4>Guardrails</h4>
      ${findings.map((f) => `
        <div class="check">
          <span class="tag ${f.blocked ? "block" : "pass"}">${f.blocked ? "Blocked" : "Passed"}</span>
          <span><span class="what">${esc(f.check)}</span> <span class="detail">${esc(f.detail)}</span></span>
        </div>`).join("")}
    </div>` : "";

  const provenance = `<div class="provenance">ticket ${esc(o.ticket_id)} &middot; channel ${esc(o.channel)} &middot; prompts ${esc(cls.prompt_version)}${draft.prompt_version ? " / " + esc(draft.prompt_version) : ""} &middot; logged to the decision store</div>`;

  return verdict + facts + routingStage + classification + retrieval + reply + citeStage + guardStage + provenance;
}
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def console() -> str:
    return PAGE


@app.get("/samples")
def samples() -> JSONResponse:
    """Sample tickets for the form. Loading one does not pre-empt any decision."""
    return JSONResponse(SAMPLES)


@app.get("/status")
def status() -> JSONResponse:
    """The stop control, for the indicator. The same read routing makes."""
    halt = killswitch.status()
    return JSONResponse({"engaged": halt.engaged, "note": halt.note})


@app.post("/tickets")
async def tickets(request: Request) -> JSONResponse:
    try:
        raw = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Expected a JSON object."}, status_code=400)
    if not isinstance(raw, dict):
        return JSONResponse({"error": "Expected a JSON object."}, status_code=400)

    try:
        outcome = get_pipeline().handle(raw)
    except Exception as error:
        return JSONResponse(
            {"error": f"The ticket could not be processed: {error}", "final_action": "escalate"},
            status_code=500,
        )
    return JSONResponse(outcome.as_dict())


def main() -> None:
    import os

    import uvicorn

    # 8000 is the usual port. PORT overrides it when something else is already there.
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
