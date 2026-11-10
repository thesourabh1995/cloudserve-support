# cloudserve-support

Local console, one ticket at a time:

```bash
cp .env.example .env   # then set GROQ_API_KEY
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.api
```

There is no `python` command on this machine. Use `.venv/bin/python`, which is Python 3.11. The system `python3` is older than the project allows.

Open http://127.0.0.1:8000. If that port is already taken, start with `PORT=8010 .venv/bin/python -m src.api` and open http://127.0.0.1:8010. The knowledge base index is built with `.venv/bin/python -m src.retrieve` if `storage/chroma` is empty.

The unattended run over a whole file, which is the gate for the project:

```bash
.venv/bin/python -m evaluation.harness --input path/to/tickets.json --output evaluation/results/run1
```

Both paths are arguments. The report is written to the output directory as `metrics.md` and `metrics.json`, and the decision log for that run is `decisions.db` in the same directory.

The tests, which do not call the model:

```bash
.venv/bin/python -m pytest tests/ -q
```