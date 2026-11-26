"""Splitting long text into Telegram-sized messages."""

from __future__ import annotations

from telegram.constants import MessageLimit

MAX_TEXT_LENGTH = MessageLimit.MAX_TEXT_LENGTH


def split_message(text: str, limit: int = MAX_TEXT_LENGTH) -> list[str]:
    """Split ``text`` into chunks of at most ``limit`` characters.

    Splits on paragraph breaks first, then newlines, then spaces, and only hard-cuts as a last
    resort. Empty input returns an empty list.

    Caveat: this works on plain text. If you send ``parse_mode`` HTML/MarkdownV2, a chunk can end
    inside an entity and Telegram will reject it. Split before formatting, or format each chunk
    separately.
    """
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        window = remaining[:limit]
        cut = _last_break(window)
        if cut <= 0:
            cut = limit
        chunks.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip("\n")
    if remaining:
        chunks.append(remaining)
    return [chunk for chunk in chunks if chunk]


def _last_break(window: str) -> int:
    for separator in ("\n\n", "\n", " "):
        index = window.rfind(separator)
        if index > 0:
            return index + len(separator)
    return -1
