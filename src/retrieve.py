"""Retrieval over the CloudServe knowledge base.

Acceptance criterion A4: search returns identifiable source passages that
resolve back to the real corpus, so that a citation can be followed and
checked rather than taken on trust.

Two behaviours here are deliberate and are the ones worth defending:

Every returned passage carries the `doc_id` it came from and the exact text
that was indexed. A citation is therefore verifiable by string comparison
against the corpus, not by believing the model.

When nothing clears the similarity threshold the result is empty. Ines
described agents being unable to find articles that existed; a retriever that
always returns its best guess reproduces that failure while hiding it, because
an irrelevant passage looks identical to a relevant one downstream.
"""

import json
import os
from dataclasses import dataclass
from typing import Optional

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from src.config import settings


@dataclass
class Passage:
    """One retrieved chunk, with everything needed to verify a citation."""

    doc_id: str
    title: str
    category: str
    text: str
    similarity: float
    chunk_index: int

    def citation(self) -> str:
        return f"[{self.doc_id}] {self.title}"


def load_documents(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                return value
    return payload


def chunk_documents(
    documents: list[dict],
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> tuple[list[str], list[dict]]:
    """Split articles into passages, keeping the source identity on each.

    The title is prepended to every chunk. Ines' example was a customer writing
    "my deployment keeps dying" against an article called "resolving container
    health check failures" — the title carries vocabulary the body often does
    not, and including it measurably improves retrieval on paraphrased queries.
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    texts: list[str] = []
    metadatas: list[dict] = []
    for document in documents:
        doc_id = document.get("doc_id") or document.get("id") or "UNKNOWN"
        title = document.get("title", "")
        category = document.get("category", "")
        for index, chunk in enumerate(splitter.split_text(document.get("content", ""))):
            texts.append(f"{title}\n\n{chunk}" if title else chunk)
            metadatas.append(
                {
                    "doc_id": doc_id,
                    "title": title,
                    "category": category,
                    "chunk_index": index,
                    "chunk_text": chunk,
                }
            )
    return texts, metadatas


class Retriever:
    """Chroma-backed vector search with a relevance floor.

    The embedding model is loaded lazily so that importing this module stays
    cheap for components that never search.
    """

    def __init__(
        self,
        chroma_path: str = None,
        collection_name: str = None,
        embedding_model: str = None,
        min_similarity: float = None,
    ):
        self.chroma_path = chroma_path or settings.chroma_path
        self.collection_name = collection_name or settings.collection_name
        self.embedding_model_name = embedding_model or settings.embedding_model
        self.min_similarity = (
            settings.retrieval_min_similarity if min_similarity is None else min_similarity
        )
        self._encoder: Optional[SentenceTransformer] = None
        self._client = None
        self._collection = None

    @property
    def encoder(self) -> SentenceTransformer:
        """Load the embedding model, falling back to the local cache.

        sentence-transformers contacts the HuggingFace Hub on construction to
        resolve the model revision, even when the weights are already cached.
        That turns an offline or rate-limited network into a hard failure of
        retrieval, so a failed lookup retries against the cache alone. The
        first run on a new machine still needs network access; the README says
        so and the setup step downloads it.
        """
        if self._encoder is None:
            try:
                self._encoder = SentenceTransformer(self.embedding_model_name)
            except Exception:
                self._encoder = SentenceTransformer(
                    self.embedding_model_name, local_files_only=True
                )
        return self._encoder

    @property
    def collection(self):
        if self._collection is None:
            os.makedirs(self.chroma_path, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.chroma_path)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                # Cosine rather than Chroma's default L2: these embeddings are
                # normalised, so cosine distance is the meaningful measure and
                # converts to a similarity we can threshold on.
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def index(self, documents: list[dict], reset: bool = True) -> int:
        """Embed and store the corpus. Returns the number of passages stored."""
        if reset and self.collection.count() > 0:
            self._client.delete_collection(self.collection_name)
            self._collection = None

        texts, metadatas = chunk_documents(documents)
        embeddings = self.encoder.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        ).tolist()

        self.collection.add(
            ids=[f"{m['doc_id']}::{m['chunk_index']}" for m in metadatas],
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(texts)

    def search(self, query: str, top_k: int = None) -> list[Passage]:
        """Return passages above the similarity floor, best first.

        An empty list is a legitimate and informative result.
        """
        if not query or not query.strip():
            return []

        top_k = top_k or settings.retrieval_top_k
        if self.collection.count() == 0:
            return []

        embedding = self.encoder.encode(
            [query], normalize_embeddings=True, show_progress_bar=False
        ).tolist()

        response = self.collection.query(
            query_embeddings=embedding,
            n_results=min(top_k, self.collection.count()),
            include=["metadatas", "documents", "distances"],
        )

        passages = []
        for metadata, distance in zip(
            response["metadatas"][0], response["distances"][0]
        ):
            similarity = 1.0 - float(distance)
            if similarity < self.min_similarity:
                continue
            passages.append(
                Passage(
                    doc_id=metadata["doc_id"],
                    title=metadata.get("title", ""),
                    category=metadata.get("category", ""),
                    text=metadata.get("chunk_text", ""),
                    similarity=round(similarity, 4),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                )
            )
        return passages


def build_index(docs_path: str = "data/documentation.json") -> int:
    """Entry point used by the README setup step and by the harness."""
    retriever = Retriever()
    count = retriever.index(load_documents(docs_path))
    print(f"indexed {count} passages from {docs_path} into {retriever.chroma_path}")
    return count


if __name__ == "__main__":
    build_index()
