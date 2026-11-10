"""Local console for trying one ticket.

    python -m src.api

Then open http://127.0.0.1:8000. This is the interactive way to see a
decision. The unattended run over a whole file is the harness, which is
separate and is what acceptance criterion A9 checks.
"""

import json

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from src.pipeline import Pipeline

app = FastAPI(title="CloudServe support console")
_pipeline: Pipeline | None = None


def get_pipeline() -> Pipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = Pipeline(run_id="local")
    return _pipeline


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CloudServe support console</title>
<style>
  body { font-family: Georgia, serif; max-width: 760px; margin: 2rem auto; padding: 0 1rem; color: #1c1c1c; background: #f7f5f2; }
  h1 { font-size: 1.4rem; font-weight: normal; }
  label { display: block; margin-top: 0.8rem; font-size: 0.85rem; }
  input, select, textarea { width: 100%; box-sizing: border-box; font: inherit; padding: 0.4rem; }
  textarea { min-height: 9rem; }
  button { margin-top: 1rem; font: inherit; padding: 0.4rem 1rem; cursor: pointer; }
  .status { font-size: 1.3rem; margin-top: 1.5rem; }
  .escalate { color: #8a4b08; }
  .blocked { color: #8b1e1e; }
  .auto_respond { color: #1d5c32; }
  section { margin-top: 1.2rem; }
  h2 { font-size: 1rem; font-weight: normal; border-bottom: 1px solid #ccc; }
  pre { white-space: pre-wrap; font-family: inherit; }
  .muted { color: #555; font-size: 0.9rem; }
  .error { color: #8b1e1e; }
</style>
</head>
<body>
<h1>CloudServe support console</h1>
<p class="muted">One ticket through classify, retrieve, route, draft and the guardrails. Nothing is sent anywhere except the model provider.</p>
<form id="ticket">
  <label>Channel
    <select name="channel">
      <option>email</option>
      <option>chat</option>
      <option>docs_comment</option>
      <option>forum</option>
    </select>
  </label>
  <label>Subject <input name="subject" value="Deployment health check failing"></label>
  <label>Message
    <textarea name="body">My deployment keeps failing its health check after the last release. The container starts, then gets restarted. What should I look at?</textarea>
  </label>
  <button type="submit">Run this ticket</button>
</form>
<p id="waiting" class="muted" hidden>Running. Classification and the draft each call the model, so this usually takes under a minute.</p>
<div id="result"></div>
<script>
const form = document.getElementById("ticket");
const waiting = document.getElementById("waiting");
const result = document.getElementById("result");
const labels = { auto_respond: "Answered automatically", escalate: "Escalated to a person", blocked: "Blocked by a guardrail" };

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form).entries());
  waiting.hidden = false;
  result.innerHTML = "";
  form.querySelector("button").disabled = true;
  try {
    const response = await fetch("/tickets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const outcome = await response.json();
    result.innerHTML = render(outcome);
  } catch (error) {
    result.innerHTML = '<p class="error">The request failed: ' + error + "</p>";
  } finally {
    waiting.hidden = true;
    form.querySelector("button").disabled = false;
  }
});

function esc(value) {
  return String(value ?? "").replace(/[&<>]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]));
}

function render(outcome) {
  if (outcome.error) return '<p class="error">' + esc(outcome.error) + "</p>";
  const action = outcome.final_action;
  const passages = (outcome.passages || []).map((p) =>
    "<li>" + esc(p.citation) + " <span class=muted>(" + esc(p.similarity) + ")</span></li>").join("") || "<li>Nothing cleared the relevance floor.</li>";
  const findings = (outcome.guardrail.findings || []).map((f) =>
    "<li>" + (f.blocked ? "Blocked" : "Passed") + " — " + esc(f.check) + ". " + esc(f.detail) + "</li>").join("");
  const citations = (outcome.draft.citations || []).map((c) =>
    "<li>" + esc(c.doc_id) + ": " + esc(c.supports) + "</li>").join("") || "<li>None.</li>";
  const sent = outcome.sent_answer
    ? "<pre>" + esc(outcome.sent_answer) + "</pre>"
    : "<p class=muted>Nothing was released to the customer.</p><pre>" + esc(outcome.draft.answer) + "</pre>";
  return [
    '<p class="status ' + esc(action) + '">' + esc(labels[action] || action) + "</p>",
    "<section><h2>Classification</h2><p>",
    esc(outcome.classification.intent), ", ", esc(outcome.classification.urgency),
    ", confidence ", esc(outcome.classification.confidence), "</p><p>",
    esc(outcome.classification.reason), "</p></section>",
    "<section><h2>Retrieved</h2><ul>", passages, "</ul></section>",
    "<section><h2>Routing</h2><p>", esc(outcome.routing.rule), "</p><p>", esc(outcome.routing.reason), "</p></section>",
    "<section><h2>" + (outcome.sent_answer ? "Reply" : "Draft, not sent") + "</h2>", sent, "</section>",
    "<section><h2>Citations</h2><ul>", citations, "</ul></section>",
    "<section><h2>Guardrails</h2><ul>", findings, "</ul></section>",
  ].join("");
}
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def console() -> str:
    return PAGE


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
