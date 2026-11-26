# Logging and Observability

> **TL;DR:** Log updates by id and type, never by content by default; redact tokens; emit metrics for errors, latency and queue depth; alert on `401`, `409` and sustained `429`.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. What to log

| Event | Fields |
| :--- | :--- |
| update received | `update_id`, type, `chat_id`, `user_id` |
| handler finished | handler name, duration, result |
| API error | method, error class, `error_code`, `retry_after` |
| payment | charge id, amount, payload (no PII) |
| startup | bot username, version, polling/webhook mode |

Do **not** log: message text, file URLs with tokens, full init data, phone numbers.

## 2. Structured logging

```python
import logging, json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("update_id", "chat_id", "user_id", "handler", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
```

## 3. Timing handlers

Wrap the handlers you care about; there is no per-update "after" hook in the library, and a
`group=-1` handler cannot see when later handlers finish.

```python
import functools
import logging
import time

logger = logging.getLogger("bot")

def timed(name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(update, context):
            start = time.perf_counter()
            try:
                return await func(update, context)
            finally:
                logger.info(
                    "handler",
                    extra={
                        "handler": name,
                        "duration_ms": round((time.perf_counter() - start) * 1000, 1),
                        "update_id": update.update_id,
                        "user_id": getattr(update.effective_user, "id", None),
                    },
                )
        return wrapper
    return decorator

@timed("start")
async def start(update, context):
    ...
```

## 4. Metrics that matter

| Metric | Why |
| :--- | :--- |
| updates/sec | capacity planning |
| handler latency p50/p95/p99 | user experience |
| API error rate by class | detect 401 (bad token), 409 (double poller) |
| 429 rate and total sleep | pacing too aggressive |
| webhook `pending_update_count` | endpoint too slow |
| queue depth/age | workers falling behind |
| payment success rate | revenue |

## 5. Alerts

| Condition | Severity |
| :--- | :--- |
| `InvalidToken` once | page |
| `Conflict` once | page (two pollers) |
| 5xx rate > 1% for 5 min | page |
| sustained 429 for 10 min | warn |
| no updates for 30 min during expected traffic | warn |
| `pending_update_count` > 1000 | warn |

## 6. Trace correlation

Generate a short id per update and include it in every log line for that update, including downstream calls:

```python
trace = f"{update.update_id:x}"
logger.info("handling", extra={"update_id": update.update_id})
```

When a user reports a problem, the `update_id` from your logs is the fastest way to find it.

## 7. Privacy

- Set a retention window (e.g. 30 days) for logs that contain identifiers.
- Hash or truncate user ids where full ids are not needed.
- Never log `initData`, tokens or webhook secrets.

## Sources

- https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html#telegram.ext.Application.add_error_handler
- https://core.telegram.org/bots/api#getwebhookinfo (`pending_update_count`, `last_error_message`)
