# Persistence: What Survives a Restart

> **TL;DR:** `user_data`, `chat_data` and `bot_data` are in-memory by default. Use `PicklePersistence` for single-process bots and a real database for anything else. Never pickle untrusted input.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. The three stores

| Store | Scope | Typical content |
| :--- | :--- | :--- |
| `context.user_data` | one user | conversation step, draft form |
| `context.chat_data` | one chat | group settings, game state |
| `context.bot_data` | whole bot | shared clients, caches, counters |

All three are plain dicts and are lost on restart unless persisted.

## 2. PicklePersistence

```python
from telegram.ext import ApplicationBuilder, PicklePersistence

persistence = PicklePersistence(filepath="bot.pickle", update_interval=60)
app = ApplicationBuilder().token(token).persistence(persistence).build()
```

| Property | Reality |
| :--- | :--- |
| Scope | single process, single machine |
| Format | Python pickle — arbitrary code execution if tampered with |
| Concurrency | not safe for multiple workers |
| Good for | prototypes, single-server hobby bots |

If you use it: keep the file outside the web root, back it up, and never load a file you did not create.

## 3. Database persistence

For production, store only the small state you need, keyed by ids:

```sql
CREATE TABLE user_state (
    user_id    BIGINT PRIMARY KEY,
    step       TEXT NOT NULL,
    data       JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```python
async def save(user_id: int, step: str, data: dict) -> None:
    await pool.execute(
        """
        INSERT INTO user_state (user_id, step, data)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id) DO UPDATE
        SET step = EXCLUDED.step, data = EXCLUDED.data, updated_at = now()
        """,
        user_id, step, json.dumps(data),
    )
```

| Do | Don't |
| :--- | :--- |
| Store ids, flags, small JSON | Store whole messages or files |
| Add `updated_at` and TTL cleanup | Let the table grow forever |
| Use JSONB/JSON with a schema version | Change the shape silently |
| Encrypt PII at rest if required | Store secrets in `user_data` |

## 4. What not to persist

- **Secrets** (tokens, API keys) — keep them in the secret manager.
- **Whole updates** — they are large and mostly useless after processing.
- **Derived data you can recompute** — cache it with a TTL instead.

## 5. Persistence and de-duplication

Persistence of conversation state and de-duplication of updates are different problems. Solve the second with [03-idempotent-updates.md](03-idempotent-updates.md): a durable `processed_updates` table or a Redis `SET NX` with a TTL.

## 6. Migration checklist

1. Add the table and indexes.
2. Read state at the start of each handler; write after each transition.
3. Make transitions atomic (`UPDATE ... WHERE step = 'expected'`).
4. Add a cleanup job for stale rows.
5. Test a restart mid-conversation.

## Sources

- https://docs.python-telegram-bot.org/en/stable/telegram.ext.picklepersistence.html
- https://docs.python-telegram-bot.org/en/stable/telegram.ext.basepersistence.html
