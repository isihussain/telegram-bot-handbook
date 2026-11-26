# Limits Cheatsheet

> **TL;DR:** Most "the bot is broken" reports are limit violations. Know the numbers below, and when you see HTTP 429, wait exactly `retry_after` seconds.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. Message and text limits

| Limit | Value | Source |
| :--- | :--- | :--- |
| Message text | **1–4096** characters after entity parsing | `sendMessage` |
| Caption (photo, video, document…) | **0–1024** characters | `sendPhoto` etc. |
| Entities per message | **100** | Bot API formatting |
| Callback data | **1–64 bytes** (bytes, not characters) | `InlineKeyboardButton` |
| `callback_query` copy text | 1–256 characters | Bot API |
| Bot command | **1–32** characters | `BotCommand` |
| Command description | 1–256 characters | `setMyCommands` |
| Commands per scope | 100 | `setMyCommands` |
| Deep-link `start` payload | **up to 64** characters | `create_deep_linked_url` |

```python
from telegram.constants import MessageLimit

print(MessageLimit.MAX_TEXT_LENGTH)   # 4096
print(MessageLimit.CAPTION_LENGTH)    # 1024
```

## 2. Files

| Limit | Value |
| :--- | :--- |
| Upload via bot | **50 MB** (photos: 10 MB) |
| Download via `getFile` | **20 MB** |
| Upload with a local Bot API server (`--local`) | **2000 MB** |
| Download with a local Bot API server | no limit |
| Media group | 2–10 items |
| Voice message | 50 MB |

Longer text → split it ([`tgkit.split_message`](../../src/tgkit/text.py)) or send a document.

## 3. Flood control

| Situation | Guidance |
| :--- | :--- |
| Single chat | avoid more than **1 message/second** |
| Group | max **20 messages/minute** |
| Bulk broadcast | about **30 messages/second** overall |
| Paid broadcasts enabled | up to **1000 messages/second**, 0.1 Stars per message above the free 30/s; requires ≥100,000 Stars and ≥100,000 monthly active users |

The limits are not exact contracts: short bursts may pass, then you get 429 with `retry_after`. Design for the limit, not the burst.

```python
from telegram.error import RetryAfter

try:
    await bot.send_message(chat_id, text)
except RetryAfter as exc:
    await asyncio.sleep(float(exc.retry_after) + 0.5)
    await bot.send_message(chat_id, text)
```

`tgkit.call_with_retry` and `tgkit.broadcast` implement this pattern.

> In python-telegram-bot 22.8 `retry_after` is an `int`; with `PTB_TIMEDELTA=1` (and in a future
> major version) it is a `datetime.timedelta`. Use `retry_after_seconds()` from `tgkit.retry` to
> support both.

## 4. Inline mode and queries

| Limit | Value |
| :--- | :--- |
| Results per `answerInlineQuery` | **50** |
| `next_offset` | up to 64 characters |
| Inline query text | up to 256 characters |
| `answerCallbackQuery` | call it for **every** callback query |

## 5. Polls

| Limit | Value |
| :--- | :--- |
| Question | 1–300 characters |
| Option text | 1–100 characters |
| Options | 1–12 (minimum lowered to 1 in Bot API 10.0) |
| Explanation | 200 characters |
| Open period | 5 s – 2,628,000 s (~30 days) |

## 6. Webhooks and payments

| Limit | Value |
| :--- | :--- |
| `max_connections` | 1–100, default 40 |
| `secret_token` | 1–256 chars, `[A-Za-z0-9_-]` |
| Ports | 443, 80, 88, 8443 |
| `answerPreCheckoutQuery` | within **10 seconds** or the payment is cancelled |
| Stars invoice | currency `XTR`, empty `provider_token`, exactly one `prices` item |

## 7. Where limits bite in practice

| Symptom | Likely cause | Fix |
| :--- | :--- | :--- |
| `400 Bad Request: message is too long` | text > 4096 | split |
| `400 ... BUTTON_DATA_INVALID` | callback data > 64 bytes | shorten, use an index into a cache |
| `429 Too Many Requests` | broadcast too fast | pace + `RetryAfter` |
| `400 ... can't parse entities` | unescaped user text | escape per parse mode |
| Nothing arrives in a group | privacy mode | see [06-privacy-mode-in-groups.md](06-privacy-mode-in-groups.md) |

## Sources

- https://core.telegram.org/bots/api (method parameter tables)
- https://core.telegram.org/bots/faq#broadcasting-to-users
- https://core.telegram.org/bots/webhooks
- https://core.telegram.org/bots/payments-stars
- `telegram.constants` in python-telegram-bot 22.8
