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


@dataclass(frozen=True)
class Settings:
    # Model access
    api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    api_base: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    model_name: str = os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct")

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

    # Routing. The pack's diagram shows 0.80 and says explicitly that the number
    # is illustrative; the value used here is set from the calibration data.
    confidence_threshold: float = _float("CONFIDENCE_THRESHOLD", 0.80)

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
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        return self.api_key


settings = Settings()
