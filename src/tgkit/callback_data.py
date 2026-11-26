"""Compact, versioned callback data.

Telegram allows 1-64 **bytes** (not characters) in ``callback_data``. Exceeding it makes the
whole ``sendMessage`` call fail, so it is worth checking before you build the keyboard.
"""

from __future__ import annotations

MAX_CALLBACK_BYTES = 64
SEPARATOR = ":"


class CallbackDataTooLong(ValueError):
    """Raised when packed callback data would exceed Telegram's 64 byte limit."""


def pack_callback(action: str, *parts: object, version: int = 1) -> str:
    """Pack ``action`` and ``parts`` into ``v1:action:part:...``.

    Raises :class:`CallbackDataTooLong` if the UTF-8 encoding is over 64 bytes.
    """
    if not action or SEPARATOR in action:
        raise ValueError("action must be non-empty and must not contain ':'")
    if any(SEPARATOR in str(part) for part in parts):
        raise ValueError("parts must not contain ':'")
    data = SEPARATOR.join([f"v{version}", action, *(str(part) for part in parts)])
    if len(data.encode()) > MAX_CALLBACK_BYTES:
        raise CallbackDataTooLong(
            f"callback data is {len(data.encode())} bytes, limit is {MAX_CALLBACK_BYTES}"
        )
    return data


def unpack_callback(data: str) -> tuple[str, tuple[str, ...]]:
    """Return ``(action, parts)`` and reject anything that is not a versioned payload."""
    parts = data.split(SEPARATOR)
    if len(parts) < 2 or not parts[0].startswith("v"):
        raise ValueError("not a versioned callback payload")
    return parts[1], tuple(parts[2:])
