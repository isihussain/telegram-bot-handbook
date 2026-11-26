from __future__ import annotations

import hashlib
import hmac
import json
from urllib.parse import urlencode

import pytest

from tgkit.initdata import InitDataError, validate_init_data

TOKEN = "123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"


def sign(fields: dict[str, str], token: str = TOKEN) -> str:
    check = "\n".join(f"{key}={fields[key]}" for key in sorted(fields))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    return hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()


def build(fields: dict[str, str], token: str = TOKEN) -> str:
    data = dict(fields)
    data["hash"] = sign(fields, token)
    return urlencode(data)


def test_valid_init_data_is_parsed() -> None:
    fields = {
        "auth_date": "1764000000",
        "query_id": "AAHdF6IQAAAAAN0XohDhrOrc",
        "user": json.dumps({"id": 42, "first_name": "Ada"}, separators=(",", ":")),
    }
    result = validate_init_data(build(fields), TOKEN, max_age_seconds=0)
    assert result["auth_date"] == 1764000000
    assert result["user"] == {"id": 42, "first_name": "Ada"}
    assert result["query_id"] == "AAHdF6IQAAAAAN0XohDhrOrc"


def test_wrong_token_is_rejected() -> None:
    fields = {"auth_date": "1764000000", "user": '{"id":1}'}
    with pytest.raises(InitDataError, match="hash mismatch"):
        validate_init_data(build(fields), "999:other-token", max_age_seconds=0)


def test_tampered_field_is_rejected() -> None:
    fields = {"auth_date": "1764000000", "user": '{"id":1}'}
    data = build(fields).replace("user=", "user=2", 1)
    with pytest.raises(InitDataError, match="hash mismatch"):
        validate_init_data(data, TOKEN, max_age_seconds=0)


def test_missing_hash_is_rejected() -> None:
    with pytest.raises(InitDataError, match="missing hash"):
        validate_init_data("auth_date=1764000000&user=%7B%7D", TOKEN)


def test_stale_data_is_rejected() -> None:
    fields = {"auth_date": "1764000000", "user": '{"id":1}'}
    with pytest.raises(InitDataError, match="too old"):
        validate_init_data(build(fields), TOKEN, max_age_seconds=60, now=1764000000 + 61)


def test_fresh_data_within_window_passes() -> None:
    fields = {"auth_date": "1764000000", "user": '{"id":1}'}
    result = validate_init_data(build(fields), TOKEN, max_age_seconds=60, now=1764000000 + 59)
    assert result["user"] == {"id": 1}
