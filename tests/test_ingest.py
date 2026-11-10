"""Tests for ingest (acceptance criterion A2).

The behaviour under test is that every one of the four channels produces the
same shape, and that malformed input is recorded rather than raised, because
the unattended run cannot stop on a bad ticket.
"""

import json
import os

import pytest

from src.ingest import (
    clean_text,
    load_labels,
    load_tickets,
    normalise_channel,
    normalise_ticket,
    parse_timestamp,
    summarise,
)
from src.models import CHANNELS

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "data", "sample_tickets.json")


def make_raw(**overrides):
    raw = {
        "ticket_id": "DEV-0001",
        "channel": "email",
        "subject": "Cannot log in to the console",
        "body": "I have been trying to sign in since this morning.",
        "received_at": "2026-03-14T09:22:00Z",
        "customer_id": "CUST-1042",
        "customer_name": "Priya Sharma",
        "customer_tier": "business",
        "customer_region": "europe",
        "language_fluency": "fluent",
        "labels": {"intent": "authentication_failure"},
        "history": {"csat_rating": 4},
    }
    raw.update(overrides)
    return raw


class TestAllFourChannels:
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_every_channel_normalises_to_the_same_shape(self, channel):
        ticket = normalise_ticket(make_raw(channel=channel))
        assert ticket.channel == channel
        assert ticket.ticket_id == "DEV-0001"
        assert ticket.text

    def test_chat_tickets_have_no_leading_separator(self):
        """Chat carries an empty subject; joining unconditionally would leave one."""
        ticket = normalise_ticket(make_raw(channel="chat", subject=""))
        assert not ticket.text.startswith("\n")
        assert ticket.text == "I have been trying to sign in since this morning."

    def test_channel_aliases_are_accepted(self):
        assert normalise_channel("Live Chat", []) == "chat"
        assert normalise_channel("e-mail", []) == "email"
        assert normalise_channel("community_forum", []) == "forum"

    def test_unknown_channel_is_recorded_not_rejected(self):
        issues = []
        assert normalise_channel("carrier_pigeon", issues) == "unknown"
        assert issues


class TestGroundTruthIsNotLeaked:
    """A component that can see the answer cannot be measured against it."""

    def test_labels_and_history_are_absent_from_the_ticket(self):
        ticket = normalise_ticket(make_raw())
        assert not hasattr(ticket, "labels")
        assert not hasattr(ticket, "history")
        assert "authentication_failure" not in ticket.text

    def test_customer_name_is_dropped_at_the_boundary(self):
        ticket = normalise_ticket(make_raw())
        assert not hasattr(ticket, "customer_name")
        assert "Priya" not in ticket.text
        assert "Priya" not in ticket.raw_text

    def test_labels_load_separately_for_the_harness(self, tmp_path):
        path = tmp_path / "tickets.json"
        path.write_text(json.dumps([make_raw()]))
        labels = load_labels(str(path))
        assert labels["DEV-0001"]["labels"]["intent"] == "authentication_failure"


class TestMalformedInputNeverRaises:
    def test_empty_body_is_flagged_not_rejected(self):
        ticket = normalise_ticket(make_raw(body=""))
        assert "empty body" in ticket.issues
        assert ticket.ticket_id == "DEV-0001"

    def test_a_ticket_with_no_text_at_all_is_marked_empty(self):
        ticket = normalise_ticket(make_raw(subject="", body=""))
        assert ticket.is_empty

    def test_missing_fields_fall_back_rather_than_raise(self):
        ticket = normalise_ticket({"channel": "email", "body": "help"})
        assert ticket.ticket_id == "UNKNOWN"
        assert ticket.customer_tier == "unknown"
        assert "missing ticket_id" in ticket.issues

    def test_completely_empty_record(self):
        ticket = normalise_ticket({})
        assert ticket.is_empty
        assert ticket.issues

    @pytest.mark.parametrize("record", [None, "a string", 42, []])
    def test_non_object_records_are_returned_with_an_issue(self, record):
        ticket = normalise_ticket(record)
        assert ticket.ticket_id == "UNKNOWN"
        assert ticket.issues

    def test_unparseable_timestamp_becomes_none_and_is_flagged(self):
        ticket = normalise_ticket(make_raw(received_at="not a date"))
        assert ticket.received_at is None
        assert any("received_at" in issue for issue in ticket.issues)

    def test_valid_timestamp_parses(self):
        assert parse_timestamp("2026-03-14T09:22:00Z").year == 2026
        assert parse_timestamp("") is None
        assert parse_timestamp(None) is None


class TestTextCleaning:
    def test_control_characters_are_stripped(self):
        """They break both the vector store and the JSON decision log."""
        assert clean_text("hello\x00\x07world") == "helloworld"

    def test_newlines_and_tabs_survive(self):
        """Stack traces and code blocks lose their meaning without them."""
        assert "\n" in clean_text("line one\nline two")

    def test_excess_blank_lines_collapse(self):
        assert clean_text("a\n\n\n\n\nb") == "a\n\nb"

    def test_unicode_is_folded_so_retrieval_compares_equal(self):
        assert clean_text("ﬁle") == "file"
        assert clean_text("ＡＢＣ") == "ABC"

    def test_none_and_non_strings_do_not_raise(self):
        assert clean_text(None) == ""
        assert clean_text(12345) == "12345"


class TestLoadingFiles:
    def test_sample_file_loads_with_all_four_channels(self):
        tickets = load_tickets(SAMPLE)
        assert len(tickets) == 12
        assert {t.channel for t in tickets} == set(CHANNELS)

    def test_summary_accounts_for_every_ticket(self):
        tickets = load_tickets(SAMPLE)
        summary = summarise(tickets)
        assert summary["tickets"] == len(tickets)
        assert sum(summary["by_channel"].values()) == len(tickets)

    def test_a_wrapped_list_is_accepted(self, tmp_path):
        """The hidden file is promised the same schema, not the same wrapper."""
        path = tmp_path / "wrapped.json"
        path.write_text(json.dumps({"tickets": [make_raw()]}))
        assert len(load_tickets(str(path))) == 1

    def test_a_file_that_is_not_a_list_raises_clearly(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text(json.dumps({"unexpected": "shape"}))
        with pytest.raises(ValueError, match="expected a list"):
            load_tickets(str(path))
