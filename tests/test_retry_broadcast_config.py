from __future__ import annotations

from datetime import timedelta

import pytest
from telegram.error import BadRequest, Forbidden, NetworkError, RetryAfter, TimedOut

from tgkit.broadcast import broadcast
from tgkit.config import Settings, generate_webhook_secret, redact
from tgkit.retry import call_with_retry, retry_after_seconds

TOKEN = "123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"


async def test_retry_succeeds_after_retry_after() -> None:
    sleeps: list[float] = []
    calls = {"n": 0}

    async def flaky() -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RetryAfter(3)
        return "ok"

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    assert await call_with_retry(flaky, sleep=fake_sleep) == "ok"
    assert sleeps == [3.5]


async def test_retry_uses_exponential_backoff_for_timeouts() -> None:
    sleeps: list[float] = []
    calls = {"n": 0}

    async def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimedOut()
        return "ok"

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    await call_with_retry(flaky, base_delay=2.0, sleep=fake_sleep)
    assert sleeps == [2.0, 4.0]


async def test_retry_does_not_retry_bad_request() -> None:
    calls = {"n": 0}

    async def always_bad() -> str:
        calls["n"] += 1
        raise BadRequest("Bad Request: chat not found")

    with pytest.raises(BadRequest):
        await call_with_retry(always_bad, sleep=_no_sleep)
    assert calls["n"] == 1


async def test_retry_gives_up_after_max_attempts() -> None:
    calls = {"n": 0}

    async def always_network() -> str:
        calls["n"] += 1
        raise NetworkError("boom")

    with pytest.raises(NetworkError):
        await call_with_retry(always_network, max_attempts=3, sleep=_no_sleep)
    assert calls["n"] == 3


async def _no_sleep(_: float) -> None:
    return None


async def test_broadcast_records_blocked_users() -> None:
    async def send(chat_id: int) -> str:
        if chat_id == 2:
            raise Forbidden("bot was blocked by the user")
        return "sent"

    result = await broadcast([1, 2, 3], send, sleep=_no_sleep)
    assert result.sent == 2
    assert result.blocked == [2]
    assert 2 in result.failed


async def test_broadcast_retries_after_flood_wait() -> None:
    attempts = {"n": 0}

    async def send(chat_id: int) -> str:
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise RetryAfter(1)
        return "sent"

    result = await broadcast([1], send, sleep=_no_sleep)
    assert result.sent == 1


async def test_broadcast_rejects_too_fast_rate() -> None:
    with pytest.raises(ValueError):
        await broadcast([1], _send_ok, rate_per_second=50)


async def _send_ok(chat_id: int) -> str:
    return "sent"


def test_generate_webhook_secret_uses_allowed_alphabet() -> None:
    secret = generate_webhook_secret()
    assert len(secret) == 48
    assert all(char.isalnum() or char in "_-" for char in secret)


def test_generate_webhook_secret_length_bounds() -> None:
    with pytest.raises(ValueError):
        generate_webhook_secret(0)
    with pytest.raises(ValueError):
        generate_webhook_secret(257)


def test_redact_hides_bot_token() -> None:
    assert redact(f"GET /bot{TOKEN}/getMe") == "GET /bot<bot-token>/getMe"


def test_settings_from_env() -> None:
    settings = Settings.from_env(
        {
            "BOT_TOKEN": TOKEN,
            "ADMIN_IDS": "1, 2 ,3",
            "WEBHOOK_SECRET": "abc_DEF-123",
            "WEBHOOK_PORT": "8443",
        }
    )
    assert settings.admin_ids == (1, 2, 3)
    assert settings.port == 8443
    assert settings.webhook_secret == "abc_DEF-123"


def test_settings_rejects_missing_token() -> None:
    with pytest.raises(ValueError):
        Settings.from_env({})


def test_settings_rejects_bad_secret() -> None:
    with pytest.raises(ValueError):
        Settings.from_env({"BOT_TOKEN": TOKEN, "WEBHOOK_SECRET": "has space"})


def test_retry_after_seconds_accepts_int_and_timedelta() -> None:
    assert retry_after_seconds(7) == 7.0
    assert retry_after_seconds(timedelta(seconds=7, milliseconds=500)) == 7.5


async def test_retry_handles_timedelta_retry_after() -> None:
    sleeps: list[float] = []
    calls = {"n": 0}

    async def flaky() -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RetryAfter(timedelta(seconds=2))
        return "ok"

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    assert await call_with_retry(flaky, sleep=fake_sleep) == "ok"
    assert sleeps == [2.5]
