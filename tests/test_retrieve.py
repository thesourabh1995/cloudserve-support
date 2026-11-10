"""Tests for retrieval (acceptance criteria A4, and the basis of A6).

Two properties matter beyond "it returns something". Citations must resolve to
text that genuinely exists in the corpus, which is what A6 is checked against.
And an irrelevant query must return nothing, because a retriever that always
answers hides its own failures.
"""

import json
import os

import pytest

from src.retrieve import Passage, Retriever, chunk_documents, load_documents

DOCS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "documentation.json")
pytestmark = pytest.mark.skipif(
    not os.path.exists(DOCS_PATH), reason="documentation.json not present"
)


@pytest.fixture(scope="module")
def documents():
    return load_documents(DOCS_PATH)


@pytest.fixture(scope="module")
def retriever(documents, tmp_path_factory):
    """One index for the module: loading the encoder is the slow part."""
    workspace = tmp_path_factory.mktemp("chroma")
    instance = Retriever(chroma_path=str(workspace), collection_name="test_docs")
    instance.index(documents)
    return instance


class TestChunking:
    """Pure logic, no model required."""

    def test_every_chunk_keeps_its_source_identity(self, documents):
        _, metadatas = chunk_documents(documents)
        assert metadatas
        for metadata in metadatas:
            assert metadata["doc_id"]
            assert "chunk_text" in metadata
            assert isinstance(metadata["chunk_index"], int)

    def test_title_is_prepended_to_the_indexed_text(self, documents):
        """Titles carry vocabulary the body often lacks, which is the
        paraphrase problem the technical writer described."""
        texts, metadatas = chunk_documents(documents)
        assert texts[0].startswith(metadatas[0]["title"])

    def test_chunk_text_is_stored_without_the_title(self, documents):
        """The citation must quote the article, not our indexing artefact."""
        texts, metadatas = chunk_documents(documents)
        assert metadatas[0]["chunk_text"] in texts[0]
        assert not metadatas[0]["chunk_text"].startswith(metadatas[0]["title"])

    def test_smaller_chunks_produce_more_passages(self, documents):
        small, _ = chunk_documents(documents, chunk_size=400, chunk_overlap=80)
        large, _ = chunk_documents(documents, chunk_size=1600, chunk_overlap=240)
        assert len(small) > len(large)

    def test_a_document_with_no_content_is_skipped_cleanly(self):
        texts, metadatas = chunk_documents([{"doc_id": "X", "title": "T", "content": ""}])
        assert texts == [] and metadatas == []

    def test_a_document_missing_an_id_does_not_raise(self):
        texts, _ = chunk_documents([{"title": "T", "content": "some body text"}])
        assert texts


class TestCitationsResolve:
    """A6 is checked by following a citation to the passage it claims."""

    def test_returned_doc_ids_exist_in_the_corpus(self, retriever, documents):
        corpus_ids = {d["doc_id"] for d in documents}
        results = retriever.search("why is my invoice higher than last month", top_k=5)
        assert results
        for passage in results:
            assert passage.doc_id in corpus_ids

    def test_returned_text_appears_verbatim_in_its_source_article(
        self, retriever, documents
    ):
        """This is the property that makes a citation checkable rather than
        plausible: the quoted text is a substring of the real article."""
        by_id = {d["doc_id"]: d["content"] for d in documents}
        for query in ("how do I rotate an api key", "data residency", "invoice breakdown"):
            for passage in retriever.search(query, top_k=3):
                assert passage.text in by_id[passage.doc_id], (
                    f"{passage.doc_id} chunk is not present in the source article"
                )

    def test_citation_is_human_readable(self):
        passage = Passage("DOC-API-001", "Rate limits", "api", "body", 0.9, 0)
        assert passage.citation() == "[DOC-API-001] Rate limits"


class TestRelevanceFloor:
    def test_an_irrelevant_query_returns_nothing(self, retriever):
        """Returning nothing is a valid answer. Always returning the best
        available guess hides failure from every component downstream."""
        assert retriever.search("the airspeed velocity of an unladen swallow") == []

    def test_an_empty_query_returns_nothing(self, retriever):
        assert retriever.search("") == []
        assert retriever.search("   ") == []

    def test_a_lower_floor_admits_more(self, documents, tmp_path):
        permissive = Retriever(
            chroma_path=str(tmp_path), collection_name="permissive", min_similarity=-1.0
        )
        permissive.index(documents)
        assert permissive.search("the airspeed velocity of an unladen swallow")


class TestRanking:
    def test_results_are_ordered_best_first(self, retriever):
        results = retriever.search("how do I roll back a failed release", top_k=5)
        scores = [p.similarity for p in results]
        assert scores == sorted(scores, reverse=True)

    def test_similarity_is_a_fraction(self, retriever):
        for passage in retriever.search("multi factor authentication", top_k=5):
            assert 0.0 <= passage.similarity <= 1.0

    def test_top_k_is_respected(self, retriever):
        assert len(retriever.search("api", top_k=2)) <= 2

    def test_known_question_finds_the_right_article(self, retriever):
        """The paraphrase case: the customer's words are not the title's."""
        results = retriever.search("my deployment keeps dying", top_k=5)
        assert "DOC-DEPLOY-001" in {p.doc_id for p in results}


class TestIndexing:
    def test_indexing_reports_what_it_stored(self, documents, tmp_path):
        instance = Retriever(chroma_path=str(tmp_path), collection_name="count_check")
        stored = instance.index(documents)
        assert stored == instance.collection.count()

    def test_reindexing_does_not_duplicate(self, documents, tmp_path):
        instance = Retriever(chroma_path=str(tmp_path), collection_name="reindex_check")
        first = instance.index(documents)
        second = instance.index(documents, reset=True)
        assert first == second == instance.collection.count()
