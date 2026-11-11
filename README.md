# cloudserve-support

Local console, one ticket at a time:

```bash
cp .env.example .env   # then set GROQ_API_KEY
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.api
```

**Create the environment with Python 3.11 or newer, naming the version explicitly.** A virtual environment runs whichever interpreter created it, so `python3 -m venv` gives you a 3.9 environment on a machine whose `python3` is 3.9, and this project needs 3.10 or above. Any of `python3.11`, `python3.12` or `python3.13` works. Check with `.venv/bin/python -V` before installing; if it reports anything below 3.10, delete `.venv` and create it again with a named version. The code checks this too and will tell you if it is wrong.

Every command below then uses `.venv/bin/python` rather than `python`, because on some systems there is no `python` on the path at all.

Open http://127.0.0.1:8000. If that port is already taken, start with `PORT=8010 .venv/bin/python -m src.api` and open http://127.0.0.1:8010.

The knowledge base is `data/documentation.json`, which is in the repository. It is indexed into a local vector store automatically the first time anything searches it, so there is no separate setup step. To rebuild it deliberately, run `.venv/bin/python -m src.retrieve`. The first run on a new machine downloads the embedding model, so it needs network access and takes a minute or two.

The unattended run over a whole file, which is the gate for the project:

```bash
.venv/bin/python -m evaluation.harness --input path/to/tickets.json --output evaluation/results/run1
```

Both paths are arguments; no filename is hardcoded. The report is written to the output directory as `metrics.md` and `metrics.json`, the per-ticket outcomes as `outcomes.jsonl`, and the decision log for that run as `decisions.db` in the same directory.

**Expect the run to take time, and let it.** Processing costs about 1,470 tokens per ticket, and free tiers cap tokens per minute rather than per request, so the run spends much of its time waiting out rate limits on purpose. A 120-ticket file takes roughly 25 to 40 minutes. The client retries with backoff and honours the provider's own `Retry-After`, so slow progress is the system working rather than hanging. It needs no attention while it runs: a ticket that fails entirely is logged as an escalation and the run continues.

## Stopping it

To halt automatic answering immediately, without a restart or a redeploy, create the switch file with your reason in it:

```bash
echo "wrong answers on billing tickets" > storage/STOP_AUTOMATION
```

From the next ticket onward, every ticket is still ingested, classified and logged, then escalated to a person with its context attached. Nothing is dropped. Delete the file to resume. The full procedure, including who is authorised and what happens to tickets in flight, is in `docs/governance.md`.

The tests, which do not call the model:

```bash
.venv/bin/python -m pytest tests/ -q
```