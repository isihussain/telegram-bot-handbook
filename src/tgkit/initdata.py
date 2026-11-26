"""Telegram Mini App `initData` validation.

Two schemes are supported by Telegram:

1. **Bot-side (HMAC-SHA256)** - the bot checks the `hash` field with its own token.
2. **Third-party (Ed25519)** - someone who does not have the bot token checks the
   `signature` field with Telegram's public key.

Both follow https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
and https://core.telegram.org/bots/webapps#validating-data-for-third-party-use

The data-check-string is every received field except ``hash`` and ``signature``,
sorted alphabetically, formatted ``key=value`` and joined with ``\\n``.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import time
from collections.abc import Mapping
from urllib.parse import parse_qsl

PRODUCTION_PUBLIC_KEY = "e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d"
TEST_PUBLIC_KEY = "40055058a4ee38156a06562e52eece92a771bcd8346a8c4615cb7376eddf72ec"


class InitDataError(ValueError):
    """Raised when init data is malformed, unsigned or stale."""


def _parse(init_data: str) -> dict[str, str]:
    if not init_data:
        raise InitDataError("initData is empty")
    pairs = parse_qsl(init_data, keep_blank_values=True, strict_parsing=False)
    fields: dict[str, str] = {}
    for key, value in pairs:
        if key in fields:
            raise InitDataError(f"duplicate field: {key}")
        fields[key] = value
    return fields


def _data_check_string(fields: Mapping[str, str], *, prefix: str | None = None) -> str:
    lines = [
        f"{key}={fields[key]}"
        for key in sorted(fields)
        if key not in ("hash", "signature")
    ]
    if prefix is not None:
        lines.insert(0, prefix)
    return "\n".join(lines)


def validate_init_data(
    init_data: str,
    bot_token: str,
    *,
    max_age_seconds: int = 3600,
    now: float | None = None,
) -> dict[str, object]:
    """Validate Mini App init data with the bot token.

    Returns the parsed fields, with ``user`` and ``chat`` decoded from JSON.
    Raises :class:`InitDataError` when anything is off.
    """
    fields = _parse(init_data)
    received_hash = fields.get("hash")
    if not received_hash:
        raise InitDataError("missing hash")

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    check_string = _data_check_string(fields)
    expected = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received_hash):
        raise InitDataError("hash mismatch")

    return _finish(fields, max_age_seconds=max_age_seconds, now=now)


def validate_init_data_ed25519(
    init_data: str,
    bot_id: int,
    *,
    public_key_hex: str = PRODUCTION_PUBLIC_KEY,
    max_age_seconds: int = 3600,
    now: float | None = None,
) -> dict[str, object]:
    """Validate init data without the bot token, using Telegram's Ed25519 signature."""
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:  # pragma: no cover - depends on optional dependency
        raise InitDataError("cryptography is required for Ed25519 validation") from exc

    fields = _parse(init_data)
    signature_b64 = fields.get("signature")
    if not signature_b64:
        raise InitDataError("missing signature")

    try:
        signature = base64.urlsafe_b64decode(signature_b64 + "=" * (-len(signature_b64) % 4))
        public_key = Ed25519PublicKey.from_public_bytes(binascii.unhexlify(public_key_hex))
    except (binascii.Error, ValueError) as exc:
        raise InitDataError("malformed signature or public key") from exc

    check_string = _data_check_string(fields, prefix=f"{bot_id}:WebAppData")
    try:
        public_key.verify(signature, check_string.encode())
    except InvalidSignature as exc:
        raise InitDataError("signature mismatch") from exc

    return _finish(fields, max_age_seconds=max_age_seconds, now=now)


def _finish(
    fields: dict[str, str], *, max_age_seconds: int, now: float | None
) -> dict[str, object]:
    try:
        auth_date = int(fields["auth_date"])
    except (KeyError, ValueError) as exc:
        raise InitDataError("missing or invalid auth_date") from exc

    current = time.time() if now is None else now
    if max_age_seconds > 0 and current - auth_date > max_age_seconds:
        raise InitDataError("initData is too old")

    result: dict[str, object] = dict(fields)
    for key in ("user", "chat", "receiver", "chat_join_request"):
        if key in result and isinstance(result[key], str):
            try:
                result[key] = json.loads(result[key])
            except json.JSONDecodeError as exc:
                raise InitDataError(f"invalid JSON in {key}") from exc
    result["auth_date"] = auth_date
    return result
