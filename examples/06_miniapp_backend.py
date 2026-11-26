"""06 - Mini App backend: validate initData, then trust the user id.

Serve this with any HTTP framework. The important part is `tgkit.validate_init_data`.

Run (Flask not required for the example; the function is framework agnostic):
    BOT_TOKEN=... python -c "from examples.06_miniapp_backend import check"
"""

from __future__ import annotations

import hmac
import os

from tgkit.initdata import InitDataError, validate_init_data


def check(init_data: str, token: str) -> int:
    """Return the authenticated Telegram user id, or raise."""
    data = validate_init_data(init_data, token, max_age_seconds=3600)
    user = data.get("user")
    if not isinstance(user, dict) or "id" not in user:
        raise InitDataError("no user in initData")
    return int(user["id"])


def secret_ok(received: str | None, expected: str) -> bool:
    """Constant-time comparison for webhook secret tokens."""
    if received is None:
        return False
    return hmac.compare_digest(received, expected)


def main() -> None:
    os.environ.get("BOT_TOKEN", "")
    print("POST initData to your endpoint, then call check(init_data, token).")


if __name__ == "__main__":
    main()
