from __future__ import annotations

import pytest

from tgkit import callback_data, text
from tgkit.callback_data import CallbackDataTooLong, pack_callback, unpack_callback
from tgkit.text import split_message


def test_pack_and_unpack_roundtrip() -> None:
    data = pack_callback("page", 2, "books")
    assert data == "v1:page:2:books"
    assert unpack_callback(data) == ("page", ("2", "books"))


def test_pack_rejects_separator_inside_parts() -> None:
    with pytest.raises(ValueError):
        pack_callback("page", "a:b")


def test_pack_rejects_over_64_bytes() -> None:
    with pytest.raises(CallbackDataTooLong):
        pack_callback("page", "x" * 60)


def test_64_bytes_is_exactly_allowed() -> None:
    data = pack_callback("p", "y" * 59)
    assert len(data.encode()) == callback_data.MAX_CALLBACK_BYTES


def test_unpack_rejects_legacy_payload() -> None:
    with pytest.raises(ValueError):
        unpack_callback("page:2")


def test_split_short_text_returns_one_chunk() -> None:
    assert split_message("hello") == ["hello"]


def test_split_empty_returns_empty_list() -> None:
    assert split_message("") == []


def test_split_respects_limit_and_keeps_all_text() -> None:
    paragraph = " ".join(["word"] * 100)
    original = "\n\n".join([paragraph] * 12)
    chunks = split_message(original, limit=200)
    assert all(len(chunk) <= 200 for chunk in chunks)
    assert "".join(chunks).replace("\n", "").replace(" ", "") == original.replace(
        "\n", ""
    ).replace(" ", "")


def test_split_hard_cuts_when_no_break_exists() -> None:
    chunks = split_message("a" * 25, limit=10)
    assert [len(chunk) for chunk in chunks] == [10, 10, 5]


def test_split_prefers_paragraph_breaks() -> None:
    chunks = split_message("first part.\n\nsecond part.", limit=15)
    assert chunks == ["first part.", "second part."]


def test_split_rejects_bad_limit() -> None:
    with pytest.raises(ValueError):
        split_message("x", limit=0)


def test_default_limit_is_message_limit() -> None:
    assert text.MAX_TEXT_LENGTH == 4096
