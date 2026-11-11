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
import re
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
    # Tokens the provider billed for this call. Zero for a cache hit, which is
    # the point of the cache. The free tier is capped per minute and per day in
    # tokens rather than in money, so this is the figure that decides whether a
    # full run finishes.
    tokens: int = 0


class ResponseCache:
    """Content-addressed cache of model responses, one JSON file per entry."""

    def __init__(self, directory: str = "./storage/llm_cache"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def _path(self, key: str) -> str:
        return os.path.join(self.directory, f"{key}.json")

    @staticmethod
    def key(model: str, system: str, prompt: str, temperature: float, *extra: str) -> str:
        digest = hashlib.sha256()
        for part in (model, system, prompt, str(temperature), *extra):
            digest.update(str(part).encode("utf-8"))
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
        max_backoff: float = 75.0,
    ):
        self.model = model or settings.model_name
        self.max_attempts = max_attempts
        self.timeout = timeout
        # A per-minute limit can ask for a wait approaching a minute, so the
        # ceiling has to exceed that or the run gives up on a limit that was
        # about to reset.
        self.max_backoff = max_backoff
        self.cache = ResponseCache() if cache is self._DEFAULT_CACHE else cache
        self._transport = transport
        self._sleep = sleep

        # Running totals for the cost section of the report. Cache hits are
        # excluded from both, so these are what the provider actually billed.
        self.tokens_used = 0
        self.calls_made = 0
        # Same totals split by caller, because the two calls cost very different
        # amounts and tuning the cheap one would be wasted effort.
        self.tokens_by_task: dict[str, int] = {}
        self.calls_by_task: dict[str, int] = {}

    def _post(
        self,
        system: str,
        prompt: str,
        temperature: float,
        reasoning_effort: Optional[str] = None,
    ) -> tuple[str, int]:
        """One HTTP attempt, returning the text and the tokens it cost.

        Raises on anything that is not a usable answer.
        """
        if self._transport is not None:
            result = self._transport(system=system, prompt=prompt, temperature=temperature)
            # An injected transport may return just the text; tests do.
            if isinstance(result, tuple):
                return result
            return result, 0

        body = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        if reasoning_effort and "gpt-oss" in self.model:
            body["reasoning_effort"] = reasoning_effort

        response = requests.post(
            f"{settings.api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.require_api_key()}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.timeout,
        )

        if response.status_code in self.RETRYABLE_STATUS:
            # The free tier is capped per minute. When it throttles, it says how
            # long to wait, and guessing shorter than that just wastes another
            # attempt against a limit that has not reset yet.
            raise _Retryable(
                f"provider returned {response.status_code}",
                retry_after=_retry_after_seconds(response.headers),
            )
        if response.status_code >= 400:
            raise ModelUnavailable(
                f"provider returned {response.status_code}: {response.text[:200]}"
            )

        try:
            payload = response.json()
            text = payload["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError) as error:
            raise _Retryable(f"unparseable response: {error}") from error

        return text, int((payload.get("usage") or {}).get("total_tokens", 0))

    def complete(
        self,
        prompt: str,
        system: str = "You are a precise assistant.",
        temperature: float = 0.0,
        use_cache: bool = True,
        reasoning_effort: Optional[str] = None,
        task: str = "other",
    ) -> Completion:
        """Return a completion, or raise ModelUnavailable having tried properly.

        Temperature defaults to zero. Routing has to be deterministic under A5,
        and a sampled classification would make the same ticket route two
        different ways on two runs.
        """
        key = None
        if use_cache and self.cache is not None:
            # The effort is part of the key: the same prompt at a different
            # effort is a different request and must not serve a stale answer.
            key = self.cache.key(
                self.model, system, prompt, temperature, reasoning_effort or ""
            )
            hit = self.cache.get(key)
            if hit is not None:
                return Completion(text=hit, cached=True, attempts=0)

        started = time.monotonic()
        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                text, tokens = self._post(system, prompt, temperature, reasoning_effort)
                if key is not None:
                    self.cache.put(key, text)
                self.tokens_used += tokens
                self.calls_made += 1
                self.tokens_by_task[task] = self.tokens_by_task.get(task, 0) + tokens
                self.calls_by_task[task] = self.calls_by_task.get(task, 0) + 1
                return Completion(
                    text=text,
                    cached=False,
                    attempts=attempt,
                    latency_seconds=round(time.monotonic() - started, 3),
                    tokens=tokens,
                )
            except ModelUnavailable:
                raise
            except (_Retryable, requests.RequestException) as error:
                last_error = error
                if attempt < self.max_attempts:
                    # Exponential backoff with jitter: a fixed delay would make
                    # concurrent workers retry in lockstep and throttle again.
                    delay = min(2.0 ** (attempt - 1), 8.0) + random.uniform(0, 0.4)
                    asked = getattr(error, "retry_after", None)
                    if asked:
                        delay = max(delay, min(float(asked) + 0.5, self.max_backoff))
                    self._sleep(delay)

        raise ModelUnavailable(
            f"giving up after {self.max_attempts} attempts: {last_error}"
        ) from last_error


class _Retryable(Exception):
    """Internal: a failure worth another attempt.

    `retry_after` is the provider's own instruction, in seconds, when it gave
    one. None means back off on our own schedule.
    """

    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


def _retry_after_seconds(headers) -> Optional[float]:
    """Read Retry-After, or the reset hint Groq sends with a 429.

    Values look like "2", "1m26.4s" or "547ms". An unreadable value returns
    None so the caller falls back to its own backoff rather than to zero.
    """
    for name in ("retry-after", "x-ratelimit-reset-tokens", "x-ratelimit-reset-requests"):
        raw = (headers or {}).get(name)
        if not raw:
            continue
        text = str(raw).strip()
        try:
            return float(text)
        except ValueError:
            pass
        match = re.fullmatch(
            r"(?:(\d+(?:\.\d+)?)m)?(?:(\d+(?:\.\d+)?)s)?|(\d+(?:\.\d+)?)ms", text
        )
        if match:
            minutes, seconds, millis = match.groups()
            if millis is not None:
                return float(millis) / 1000.0
            if minutes or seconds:
                return float(minutes or 0) * 60 + float(seconds or 0)
    return None


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
