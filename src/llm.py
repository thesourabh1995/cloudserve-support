"""The single place the system talks to a language model.

Every component that needs a model goes through this client, which exists so
that three concerns are solved once rather than in five places:

Rate limits are a design problem, not an obstacle. The free tiers throttle, so
retries use exponential backoff with jitter and give up cleanly rather than
hanging the unattended run.

Responses are cached on disk, keyed by model and prompt. This keeps the free
allowance usable across the repeated full runs the project needs, and makes a
run reproducible, which matters when the evaluation has to be defensible.

Failure is expected, not exceptional. When the provider is unreachable the
client raises ModelUnavailable, and callers are required to degrade rather
than crash. Acceptance criterion A11 is tested by disconnecting the provider
entirely, so this path gets exercised for real.
"""

import hashlib
import json
import os
import random
import time
from dataclasses import dataclass
from typing import Callable, Optional

import requests

from src.config import settings


class ModelUnavailable(RuntimeError):
    """The provider could not be reached, or refused, after every retry.

    Callers catch this and degrade. They must not let it propagate into the
    unattended run, because one unreachable provider would end the whole run.
    """


@dataclass
class Completion:
    text: str
    cached: bool = False
    attempts: int = 1
    latency_seconds: float = 0.0


class ResponseCache:
    """Content-addressed cache of model responses, one JSON file per entry."""

    def __init__(self, directory: str = "./storage/llm_cache"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def _path(self, key: str) -> str:
        return os.path.join(self.directory, f"{key}.json")

    @staticmethod
    def key(model: str, system: str, prompt: str, temperature: float) -> str:
        digest = hashlib.sha256()
        for part in (model, system, prompt, str(temperature)):
            digest.update(part.encode("utf-8"))
            digest.update(b"\x00")
        return digest.hexdigest()[:32]

    def get(self, key: str) -> Optional[str]:
        try:
            with open(self._path(key), encoding="utf-8") as handle:
                return json.load(handle)["text"]
        except (OSError, ValueError, KeyError):
            return None

    def put(self, key: str, text: str) -> None:
        try:
            with open(self._path(key), "w", encoding="utf-8") as handle:
                json.dump({"text": text}, handle)
        except OSError:
            # A cache that cannot be written is a performance problem, never a
            # correctness one. Carry on.
            pass


class LLMClient:
    """Chat completions with retry, backoff and caching.

    `transport` is injectable so the test suite can drive every branch,
    including provider outage, without a network or an API key.
    """

    RETRYABLE_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}

    # Distinguishes "no cache argument given, use the default" from an explicit
    # cache=None meaning "do not cache at all".
    _DEFAULT_CACHE = object()

    def __init__(
        self,
        model: str = None,
        max_attempts: int = 4,
        timeout: float = 45.0,
        cache=_DEFAULT_CACHE,
        transport: Optional[Callable] = None,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.model = model or settings.model_name
        self.max_attempts = max_attempts
        self.timeout = timeout
        self.cache = ResponseCache() if cache is self._DEFAULT_CACHE else cache
        self._transport = transport
        self._sleep = sleep

    def _post(self, system: str, prompt: str, temperature: float) -> str:
        """One HTTP attempt. Raises on anything that is not a usable answer."""
        if self._transport is not None:
            return self._transport(system=system, prompt=prompt, temperature=temperature)

        response = requests.post(
            f"{settings.api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.require_api_key()}",
                "Content-Type": "application/json",
            },
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

        if response.status_code in self.RETRYABLE_STATUS:
            raise _Retryable(f"provider returned {response.status_code}")
        if response.status_code >= 400:
            raise ModelUnavailable(
                f"provider returned {response.status_code}: {response.text[:200]}"
            )

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError) as error:
            raise _Retryable(f"unparseable response: {error}") from error

    def complete(
        self,
        prompt: str,
        system: str = "You are a precise assistant.",
        temperature: float = 0.0,
        use_cache: bool = True,
    ) -> Completion:
        """Return a completion, or raise ModelUnavailable having tried properly.

        Temperature defaults to zero. Routing has to be deterministic under A5,
        and a sampled classification would make the same ticket route two
        different ways on two runs.
        """
        key = None
        if use_cache and self.cache is not None:
            key = self.cache.key(self.model, system, prompt, temperature)
            hit = self.cache.get(key)
            if hit is not None:
                return Completion(text=hit, cached=True, attempts=0)

        started = time.monotonic()
        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                text = self._post(system, prompt, temperature)
                if key is not None:
                    self.cache.put(key, text)
                return Completion(
                    text=text,
                    cached=False,
                    attempts=attempt,
                    latency_seconds=round(time.monotonic() - started, 3),
                )
            except ModelUnavailable:
                raise
            except (_Retryable, requests.RequestException) as error:
                last_error = error
                if attempt < self.max_attempts:
                    # Exponential backoff with jitter: a fixed delay would make
                    # concurrent workers retry in lockstep and throttle again.
                    delay = min(2.0 ** (attempt - 1), 8.0) + random.uniform(0, 0.4)
                    self._sleep(delay)

        raise ModelUnavailable(
            f"giving up after {self.max_attempts} attempts: {last_error}"
        ) from last_error


class _Retryable(Exception):
    """Internal: a failure worth another attempt."""


def extract_json(text: str) -> Optional[dict]:
    """Pull the first JSON object out of a model response.

    Small instruction-following models wrap JSON in prose or fences however
    firmly they are asked not to. Returning None rather than raising lets the
    caller fall back to its defined default, which is what A3 requires.
    """
    if not text:
        return None

    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.split("```")[1] if "```" in candidate[3:] else candidate[3:]
        if candidate.lstrip().lower().startswith("json"):
            candidate = candidate.lstrip()[4:]

    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else None
    except ValueError:
        pass

    # Fall back to the outermost braces in the response.
    start, end = candidate.find("{"), candidate.rfind("}")
    if start != -1 and end > start:
        try:
            parsed = json.loads(candidate[start : end + 1])
            return parsed if isinstance(parsed, dict) else None
        except ValueError:
            return None
    return None
