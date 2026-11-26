"""Configuration and secret hygiene."""

from __future__ import annotations

import os
import re
import secrets
from dataclasses import dataclass

# BotFather tokens are <bot id>:<35 url-safe characters>, e.g. 123456789:AAH...
# No leading \b: in "bot<token>" the digit is already preceded by a word character.
TOKEN_PATTERN = re.compile(r"\d{6,12}:[A-Za-z0-9_-]{30,40}")
SECRET_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"


def generate_webhook_secret(length: int = 48) -> str:
    """Return a webhook secret token using only the characters Telegram allows."""
    if not 1 <= length <= 256:
        raise ValueError("webhook secret must be 1-256 characters")
    return "".join(secrets.choice(SECRET_ALPHABET) for _ in range(length))


def redact(text: str) -> str:
    """Remove anything that looks like a bot token, e.g. before logging."""
    return TOKEN_PATTERN.sub("<bot-token>", text)


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    webhook_url: str | None = None
    webhook_secret: str | None = None
    listen: str = "127.0.0.1"
    port: int = 8443
    admin_ids: tuple[int, ...] = ()

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        values = os.environ if env is None else env
        token = values.get("BOT_TOKEN", "").strip()
        if not TOKEN_PATTERN.fullmatch(token):
            raise ValueError("BOT_TOKEN is missing or does not look like a bot token")
        admins = tuple(
            int(part) for part in values.get("ADMIN_IDS", "").replace(" ", "").split(",") if part
        )
        secret = values.get("WEBHOOK_SECRET") or None
        if secret is not None and not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", secret):
            raise ValueError("WEBHOOK_SECRET must match [A-Za-z0-9_-]{1,256}")
        return cls(
            bot_token=token,
            webhook_url=values.get("WEBHOOK_URL") or None,
            webhook_secret=secret,
            listen=values.get("WEBHOOK_LISTEN", "127.0.0.1"),
            port=int(values.get("WEBHOOK_PORT", "8443")),
            admin_ids=admins,
        )
