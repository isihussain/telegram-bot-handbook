"""Import every example and build its Application.

This catches wrong handler signatures, unknown filters, missing extras and typos without
touching the network: building an Application does not call the Bot API.
"""

from __future__ import annotations

import importlib

import pytest
from telegram.ext import Application

TOKEN = "123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"

MODULES = [
    "01_hello_polling",
    "02_webhook",
    "03_inline_keyboard",
    "04_conversation_form",
    "05_stars_payment",
    "07_admin_and_moderation",
    "08_production_template",
    "09_streaming_draft",
    "10_job_queue",
]


@pytest.mark.parametrize("name", MODULES)
def test_example_builds(name: str) -> None:
    module = importlib.import_module(name)
    app = module.build_application(TOKEN)
    assert isinstance(app, Application)
    assert app.handlers, f"{name} registered no handlers"


def test_miniapp_helpers_roundtrip() -> None:
    module = importlib.import_module("06_miniapp_backend")
    assert module.secret_ok("abc", "abc") is True
    assert module.secret_ok(None, "abc") is False
    assert module.secret_ok("abc", "abd") is False


def test_conversation_has_cancel_fallback() -> None:
    module = importlib.import_module("04_conversation_form")
    app = module.build_application(TOKEN)
    conversation = app.handlers[0][0]
    assert conversation.fallbacks, "a conversation must always be escapable"
