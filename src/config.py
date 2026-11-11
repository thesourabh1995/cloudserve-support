"""Configuration, read once from the environment.

Every tunable the system has lives here rather than as a literal in the code,
because the routing threshold and the retrieval cut-off are decisions the
report has to defend, and they need to be visible in one place to be defended.

Reading a missing API key is deliberately deferred until something tries to
call the model. Importing this module must not fail, or the test suite and the
discovery analysis stop working on a machine with no key configured.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# Both providers named in the project brief speak the OpenAI chat-completions
# format, so the difference between them is a base URL, a key and a model name.
# Groq is the default because its free tier allows 1,000 requests a day against
# OpenRouter's 50, and a full pass over the 500-ticket set needs roughly 800
# calls. The choice is recorded here rather than inline so the evaluation can be
# re-run against either provider and the comparison defended.
#
# The default model is the measured winner in analysis/compare_models.py, not
# the obvious pick: see docs/model_choice.md. Note that Groq's catalogue no
# longer carries the Llama models most write-ups assume.
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_var": "GROQ_API_KEY",
        "model": "openai/gpt-oss-20b",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "key_var": "OPENROUTER_API_KEY",
        "model": "meta-llama/llama-3.1-8b-instruct:free",
    },
}


def _provider() -> str:
    name = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    return name if name in PROVIDERS else "groq"


@dataclass(frozen=True)
class Settings:
    # Model access
    provider: str = _provider()
    api_key: str = os.getenv(PROVIDERS[_provider()]["key_var"], "")
    api_base: str = os.getenv("LLM_BASE_URL", PROVIDERS[_provider()]["base_url"])
    model_name: str = os.getenv("MODEL_NAME", PROVIDERS[_provider()]["model"])

    # Retrieval
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    chroma_path: str = os.getenv("CHROMA_PATH", "./storage/chroma")
    collection_name: str = os.getenv("CHROMA_COLLECTION", "cloudserve_docs")
    retrieval_top_k: int = _int("RETRIEVAL_TOP_K", 5)

    # Below this cosine similarity a passage is treated as irrelevant and is not
    # returned. Returning nothing is a valid answer; returning something
    # irrelevant hides the failure and is worse than silence.
    retrieval_min_similarity: float = _float("RETRIEVAL_MIN_SIMILARITY", 0.30)

    # Chunking. Both values are design decisions measured in
    # analysis/tune_retrieval.py rather than accepted as defaults.
    chunk_size: int = _int("CHUNK_SIZE", 800)
    chunk_overlap: int = _int("CHUNK_OVERLAP", 120)

    # How many distinct documents are put in front of the generator. Retrieval
    # returns chunks, and several of the top five are often from one article;
    # sending near-duplicates spends tokens without adding evidence.
    generation_docs: int = _int("GENERATION_DOCS", 3)

    # Reasoning models bill their hidden reasoning as output tokens, and that
    # reasoning was two thirds of the cost of a run. The setting differs by
    # task rather than globally: classification is a short prompt whose
    # accuracy decides every downstream step, so it pays for more reasoning,
    # while generation is the token-heavy call and its output is checked by
    # the citation guardrail regardless. Measured in docs/run_cost.md.
    # Empty disables the parameter.
    classify_reasoning_effort: str = os.getenv("CLASSIFY_REASONING_EFFORT", "medium")
    generate_reasoning_effort: str = os.getenv("GENERATE_REASONING_EFFORT", "low")

    # Routing. The pack's diagram shows 0.80 and says the number is illustrative.
    # It stays at 0.80 until a full classification pass produces a confidence
    # distribution to calibrate against. See docs/routing_rules.md.
    confidence_threshold: float = _float("CONFIDENCE_THRESHOLD", 0.80)

    # The stop control. Creating this file halts automatic answering from the
    # next ticket onward, with no restart and no deployment. See src/killswitch.py.
    kill_switch_file: str = os.getenv("KILL_SWITCH_FILE", "./storage/STOP_AUTOMATION")

    # Persistence
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./storage/decisions.db")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def decision_db_path(self) -> str:
        """Strip the SQLAlchemy-style prefix; we use sqlite3 directly."""
        url = self.database_url
        for prefix in ("sqlite:///", "sqlite://"):
            if url.startswith(prefix):
                return url[len(prefix):]
        return url

    def require_api_key(self) -> str:
        """Fail loudly, and only at the point of use."""
        if not self.api_key:
            key_var = PROVIDERS[self.provider]["key_var"]
            raise RuntimeError(
                f"{key_var} is not set. Copy .env.example to .env and add your "
                f"{self.provider} key, or set LLM_PROVIDER to another supported "
                f"provider ({', '.join(sorted(PROVIDERS))})."
            )
        return self.api_key


settings = Settings()
