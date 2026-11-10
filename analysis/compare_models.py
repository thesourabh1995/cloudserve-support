"""Choose the classification model on measured evidence rather than reputation.

The project brief names Groq and OpenRouter as the free options and asks for
the model choice to be justified. Groq's catalogue no longer carries the Llama
models most write-ups assume, so the candidates here are what the account can
actually reach, confirmed by calling the models list endpoint.

Three things decide the choice, and only the first is about quality:

Accuracy against the labelled intent, on a stratified sample of the
development set.

Tokens per ticket. The free tier allows 8,000 tokens a minute and 1,000
requests a day. A full run is roughly 800 calls, so a model that spends twice
as many tokens per ticket does not cost twice as much money, it costs twice as
much wall-clock time in an unattended run and risks not finishing. The
reasoning-style models bill their hidden reasoning as output tokens, which is
easy to miss until a run stalls.

Format compliance. A classifier that returns prose instead of JSON falls back
to escalation, so an articulate model that ignores the schema is worse here
than a blunt one that obeys it.

Run with:  python -m analysis.compare_models
"""

import collections
import json
import random
import time

from src.classify import Classifier
from src.ingest import load_labels, load_tickets
from src.llm import LLMClient

TICKETS = "../Capstone_Pack/05_Datasets/development_tickets.json"
LABELS = "../Capstone_Pack/05_Datasets/development_tickets.json"

CANDIDATES = [
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
]

SAMPLE_SIZE = 18
SEED = 7

# Stay under the 8,000 tokens-per-minute ceiling. Measured rather than
# guessed: the pause is recalculated from what the last call actually spent.
TPM_LIMIT = 8000


class MeteredClient(LLMClient):
    """An LLMClient that records token usage and paces itself under the TPM cap."""

    def __init__(self, model):
        super().__init__(model=model, cache=None)
        self.total_tokens = 0
        self.calls = 0
        self._window_start = time.monotonic()
        self._window_tokens = 0

    def _post(self, system, prompt, temperature):
        self._throttle()
        import requests

        from src.config import settings

        response = requests.post(
            f"{settings.api_base}/chat/completions",
            headers={"Authorization": f"Bearer {settings.require_api_key()}"},
            json={
                "model": self.model,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            from src.llm import ModelUnavailable, _Retryable

            if response.status_code in self.RETRYABLE_STATUS:
                raise _Retryable(f"provider returned {response.status_code}")
            raise ModelUnavailable(f"{response.status_code}: {response.text[:200]}")

        payload = response.json()
        used = payload.get("usage", {}).get("total_tokens", 0)
        self.total_tokens += used
        self._window_tokens += used
        self.calls += 1
        return payload["choices"][0]["message"]["content"]

    def _throttle(self):
        elapsed = time.monotonic() - self._window_start
        if elapsed >= 60:
            self._window_start = time.monotonic()
            self._window_tokens = 0
        elif self._window_tokens > TPM_LIMIT * 0.8:
            time.sleep(max(0.0, 60 - elapsed) + 1)
            self._window_start = time.monotonic()
            self._window_tokens = 0


def intent_of(labels, ticket_id):
    """Ground-truth intent. The datasets nest it under a `labels` object."""
    return (labels.get(ticket_id) or {}).get("labels", {}).get("intent")


def stratified_sample(tickets, labels, size, seed):
    """Spread the sample across intents so accuracy is not dominated by one class."""
    by_intent = collections.defaultdict(list)
    for ticket in tickets:
        intent = intent_of(labels, ticket.ticket_id)
        if intent:
            by_intent[intent].append(ticket)

    rng = random.Random(seed)
    chosen, intents = [], sorted(by_intent)
    while len(chosen) < size and intents:
        for intent in list(intents):
            if by_intent[intent]:
                chosen.append(by_intent[intent].pop(rng.randrange(len(by_intent[intent]))))
            else:
                intents.remove(intent)
            if len(chosen) >= size:
                break
    return chosen


def evaluate(model, sample, labels):
    client = MeteredClient(model)
    classifier = Classifier(client=client)

    correct = malformed = 0
    started = time.monotonic()

    for ticket in sample:
        result = classifier.classify(ticket)
        expected = intent_of(labels, ticket.ticket_id)
        if result.intent == expected:
            correct += 1
        if result.degraded or result.confidence == 0.0:
            malformed += 1

    elapsed = time.monotonic() - started
    n = len(sample)
    per_ticket = client.total_tokens / n if n else 0

    return {
        "model": model,
        "accuracy": correct / n if n else 0,
        "malformed": malformed,
        "tokens_total": client.total_tokens,
        "tokens_per_ticket": per_ticket,
        "seconds": elapsed,
        # What a full 500-ticket classification pass would cost.
        "full_run_tokens": per_ticket * 500,
        "full_run_minutes": (per_ticket * 500) / TPM_LIMIT,
    }


def main():
    tickets = load_tickets(TICKETS)
    labels = load_labels(LABELS)
    sample = stratified_sample(tickets, labels, SAMPLE_SIZE, SEED)

    print(f"Sample: {len(sample)} tickets across "
          f"{len({intent_of(labels, t.ticket_id) for t in sample})} intents\n")

    results = []
    for model in CANDIDATES:
        print(f"-- {model}")
        try:
            result = evaluate(model, sample, labels)
        except Exception as error:
            print(f"   failed: {error}\n")
            continue
        results.append(result)
        print(f"   accuracy {result['accuracy']:.1%}  "
              f"tokens/ticket {result['tokens_per_ticket']:.0f}  "
              f"malformed {result['malformed']}  "
              f"{result['seconds']:.0f}s\n")

    print("\n| Model | Accuracy | Malformed | Tokens/ticket | 500-ticket pass | Est. minutes |")
    print("|---|---|---|---|---|---|")
    for r in sorted(results, key=lambda r: -r["accuracy"]):
        print(f"| `{r['model']}` | {r['accuracy']:.1%} | {r['malformed']} | "
              f"{r['tokens_per_ticket']:.0f} | {r['full_run_tokens']:,.0f} | "
              f"{r['full_run_minutes']:.0f} |")

    with open("docs/model_comparison.json", "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)


if __name__ == "__main__":
    main()
