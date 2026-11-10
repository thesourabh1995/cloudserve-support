# What happens when the model provider fails

Acceptance criterion A11 is checked by disconnecting the provider and running
the system anyway. This is the record of that run.

## The test

Six tickets the system had not seen before, so the response cache could not
mask the outage, with a deliberately invalid API key:

```bash
GROQ_API_KEY=invalid .venv/bin/python -m evaluation.harness \
  --input storage/outage_six.json \
  --output evaluation/results/outage
```

## The result

```
1/6 DEV-0401 escalate
...
6/6 DEV-0406 escalate
processed 6, logged 6, reconciles True
```

Every ticket was escalated, every decision was logged, and the run finished on
its own. No ticket was dropped and nothing had to be restarted, which is what
A9 requires of any run, including a failing one.

Each row in the decision log carries the reason:

| Field | Value |
|---|---|
| intent | `unclear_request` |
| confidence | `0.0` |
| action | `escalate` |
| rule | `classification_unusable` |
| reason | `Classification could not be trusted (model unavailable: provider returned 401 ...)` |

The confidence is zero rather than absent. A missing confidence read as a high
one is the failure that would send unreviewed answers during an outage, so the
fallback states it explicitly and routing escalates on it.

The metrics report for that run records first contact resolution at 0% and the
escalation rate at 100%, which is the honest description of a system with no
model behind it. It does not record an error rate of zero and quietly carry on.

## Why it behaves this way

The model client treats an unreachable provider as an expected condition. It
retries with exponential backoff and jitter, then raises `ModelUnavailable`
rather than an arbitrary exception. Classification and generation both catch
it: classification returns its defined fallback, generation abstains. Routing
sees a degraded classification and escalates with a reason a support manager
can read.

The consequence worth stating in the report is that an outage turns the system
into a well-organised intake queue rather than an answering service. Tickets
still arrive, are still logged, and reach a person with their context attached.
Availability of the answering function depends on the provider; availability of
the intake and logging functions does not.

## What this does not cover

A provider that is reachable but returning nonsense is a different failure, and
a harder one. The guardrails catch unsupported claims, so a fabricated answer is
blocked rather than sent, but a plausible and wrong answer with a real citation
would pass. That is a known limit, not a solved problem.
