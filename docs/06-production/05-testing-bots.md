# Testing Bots

> **TL;DR:** Test pure logic directly, build the `Application` to catch wiring mistakes, and fake the network by replacing `bot` methods. Do not call the real Bot API in unit tests.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. Test pyramid

| Layer | What | Speed |
| :--- | :--- | :--- |
| Unit | validation, formatting, state transitions | ms |
| Wiring | build `Application`, register handlers | ms |
| Integration | handlers with a fake bot | tens of ms |
| End-to-end | a real bot against a test account | seconds, manual |

## 2. Pure logic first

```python
from tgkit.initdata import validate_init_data

def test_rejects_tampered_hash():
    with pytest.raises(InitDataError):
        validate_init_data(raw, token)
```

See `tests/test_initdata.py` for a complete example that signs its own data.

## 3. Wiring test

```python
import importlib

def test_example_builds():
    module = importlib.import_module("01_hello_polling")
    app = module.build_application("123456789:AAH...")
    assert app.handlers
```

This catches wrong filters, unknown handler arguments and missing extras without any network access.

## 4. Faking the bot

```python
class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, **kwargs):
        self.sent.append((chat_id, text))
        return None

async def test_handler_sends_greeting():
    bot = FakeBot()
    context = SimpleNamespace(bot=bot)
    await start(update_stub(), context)
    assert bot.sent == [(42, "Hello")]
```

You can also use `unittest.mock.AsyncMock` for `context.bot` methods.

## 5. Building an `Update` without Telegram

```python
from telegram import Chat, Message, Update, User

def text_update(text: str, user_id: int = 42) -> Update:
    user = User(id=user_id, first_name="Ada", is_bot=False)
    chat = Chat(id=user_id, type=Chat.PRIVATE)
    message = Message(message_id=1, date=None, chat=chat, from_user=user, text=text)
    return Update(update_id=1, message=message)
```

## 6. What to test in a bot

| Area | Example assertion |
| :--- | :--- |
| authorisation | non-admin gets nothing |
| idempotency | second `successful_payment` grants nothing |
| limits | long text is split, not rejected |
| callbacks | unknown/old callback data does not crash |
| payments | pre-checkout rejects unknown payloads |
| security | webhook secret mismatch returns 403 |

## 7. CI

```yaml
- run: ruff check .
- run: python scripts/check_docs.py
- run: pytest -q
```

Run against Python 3.11, 3.12 and 3.13. Do not put a real token in CI; if you need an end-to-end test, use a dedicated test bot and a repository secret, and never run it on pull requests from forks.

## 8. Pitfalls

- **Hitting the real API** — flaky and can get the test bot rate-limited.
- **Sleeping in tests** — inject `sleep` (as `tgkit` does) and assert on it.
- **Testing implementation details** — assert on sent messages, not on internal calls.
- **No test for restarts** — simulate a fresh store and replay the same update.

## Sources

- https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html
- https://docs.python-telegram-bot.org/en/stable/telegram.update.html
