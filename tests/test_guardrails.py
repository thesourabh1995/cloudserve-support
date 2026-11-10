"""Guardrails (A7). Each check can block, and a clean draft records a pass.

A6 is exercised here as well: a citation is followed to the passage and the
quoted span has to be in it.
"""

from src.generate import Citation, Draft
from src.guardrails import release, review
from src.retrieve import Passage


SPAN = "the container listens on the port named in the health check"


def passage(doc_id="DOC-DEPLOY-001", text=None):
    return Passage(
        doc_id=doc_id,
        title="Resolving container health check failures",
        category="deployment",
        text=text or f"Check that {SPAN}.",
        similarity=0.7,
        chunk_index=0,
    )


def draft(**overrides):
    values = dict(
        answer="Check that the container listens on the port named in the health check.",
        citations=[Citation("DOC-DEPLOY-001", SPAN)],
        known=True,
        prompt_version="PR-02 v1.0",
        degraded=False,
        reason="",
    )
    values.update(overrides)
    return Draft(**values)


class TestPrivateData:
    def test_an_email_address_blocks_the_reply(self):
        """The ticket an assessor submits to check A7."""
        report = review(draft(answer="Write to jane@example.com and we will reset it."), [passage()])
        assert report.blocked
        activation = report.activations()[0]
        assert activation.check == "private_data"

    def test_a_pasted_api_key_blocks_the_reply(self):
        report = review(draft(answer="Your key is gsk_live_abc123XYZ and it is active."), [passage()])
        assert report.blocked
        assert any(finding.check == "private_data" and finding.blocked for finding in report.findings)

    def test_a_phone_number_blocks_the_reply(self):
        report = review(draft(answer="Call us on +44 20 7946 0991."), [passage()])
        assert any(finding.check == "private_data" and finding.blocked for finding in report.findings)

    def test_a_clean_reply_records_the_check_as_a_pass(self):
        report = review(draft(), [passage()])
        privacy = next(finding for finding in report.findings if finding.check == "private_data")
        assert not privacy.blocked
        assert privacy.detail


class TestCitations:
    def test_a_verbatim_span_from_the_retrieved_passage_passes(self):
        report = review(draft(), [passage()])
        assert not report.blocked
        assert release(draft(), report) is not None

    def test_whitespace_and_case_do_not_invalidate_a_real_quote(self):
        quoted = "The   Container\nlistens on the port named in the health check"
        report = review(draft(citations=[Citation("DOC-DEPLOY-001", quoted)]), [passage()])
        citation = next(finding for finding in report.findings if finding.check == "unsupported_claim")
        assert not citation.blocked

    def test_a_doc_id_that_was_not_retrieved_blocks(self):
        report = review(draft(citations=[Citation("DOC-MADE-UP", SPAN)]), [passage()])
        assert report.blocked
        assert release(draft(citations=[Citation("DOC-MADE-UP", SPAN)]), report) is None

    def test_a_quote_that_is_not_in_the_passage_blocks(self):
        report = review(
            draft(citations=[Citation("DOC-DEPLOY-001", "the database fails over automatically within seconds")]),
            [passage()],
        )
        assert report.blocked

    def test_a_claim_with_no_citation_blocks(self):
        report = review(draft(citations=[]), [passage()])
        assert report.blocked

    def test_an_abstention_is_not_an_unsupported_claim(self):
        abstained = draft(known=False, citations=[], answer="The documentation does not cover this.")
        report = review(abstained, [passage()])
        citation = next(finding for finding in report.findings if finding.check == "unsupported_claim")
        assert not citation.blocked
        assert release(abstained, report) is None


class TestBothChecksRun:
    def test_a_blocked_reply_still_records_the_other_check(self):
        report = review(draft(answer="Email jane@example.com", citations=[]), [passage()])
        checks = {finding.check for finding in report.findings}
        assert checks == {"private_data", "unsupported_claim"}
        assert len(report.activations()) == 2
