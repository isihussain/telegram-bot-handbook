# Troubleshooting

> **TL;DR:** Most "it does nothing" reports are one of five things: wrong token, no update subscription, privacy mode, a webhook still set, or a handler that raised before replying. Work through the table in order.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. Symptom → cause

| Symptom | Check first | Then |
| :--- | :--- | :--- |
| Bot does not respond at all | `getMe` works? | token, network, process running |
| Works in private, silent in groups | privacy mode | [../01-foundations/06-privacy-mode-in-groups.md](../01-foundations/06-privacy-mode-in-groups.md) |
| No updates arriving | `getWebhookInfo` | a webhook may still be set |
| Duplicate replies | two pollers or retries | idempotency, `Conflict` errors |
| Buttons spin forever | `answerCallbackQuery` missing | answer first |
| `400 can't parse entities` | unescaped input | [../02-interaction/01-formatting-parse-modes.md](../02-interaction/01-formatting-parse-modes.md) |
| `409 Conflict` | second poller | kill one process |
| 429 storms | broadcast too fast | pace + retry |
| Works locally, not in Docker | env vars missing | `.env` not loaded |
| Mini App says invalid hash | wrong token or `initDataUnsafe` | [../04-advanced/02-miniapp-initdata-validation.md](../04-advanced/02-miniapp-initdata-validation.md) |
| Payments never complete | pre-checkout not answered in 10 s | answer immediately |

## 2. The five-minute triage

```bash
# 1. Is the token valid?
curl "https://api.telegram.org/bot$BOT_TOKEN/getMe"

# 2. Is a webhook set?
curl "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"

# 3. Are updates waiting?
curl "https://api.telegram.org/bot$BOT_TOKEN/getUpdates?limit=1"
```

| Result | Meaning |
| :--- | :--- |
| `getMe` 401 | token wrong/revoked |
| `getWebhookInfo.url` not empty and you use polling | delete the webhook |
| `getUpdates` returns updates | your process is not consuming them |
| `getUpdates` empty but users message the bot | webhook set, or privacy mode |

## 3. Logging enough to see the problem

```python
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("telegram").setLevel(logging.DEBUG)   # temporary only
```

Turn DEBUG off afterwards: it logs full URLs, which contain the token.

## 4. Handler never runs

| Cause | Fix |
| :--- | :--- |
| Filter too narrow (`filters.TEXT` misses captions) | use `filters.TEXT | filters.CAPTION` |
| Command registered after a catch-all | reorder |
| Conversation state intercepts the message | check the conversation's states |
| `ApplicationHandlerStop` raised earlier | check group `-1` handlers |
| Update type not in `allowed_updates` | add it |

## 5. Works then stops

| Pattern | Likely cause |
| :--- | :--- |
| Stops after ~1 hour | webhook certificate or DNS issue |
| Stops after a deploy | two instances, or missing env |
| Stops at night | host sleep, quota, or a job that blocks |
| Stops after a burst | 429 not handled, process stuck sleeping |

## 6. Asking for help

Include: Bot API version, library version, the exact `error_code` and `description`, whether polling or webhook, and the `update_id` from your logs. Never include the token.

## Sources

- https://core.telegram.org/bots/api#getme
- https://core.telegram.org/bots/api#getwebhookinfo
- https://core.telegram.org/bots/api#getupdates
- https://core.telegram.org/bots/faq
