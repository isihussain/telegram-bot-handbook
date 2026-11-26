# Telegram Bot Handbook

**Practical, tested cheat sheets for building, securing and scaling Telegram bots.**

[![Bot API](https://img.shields.io/badge/Bot%20API-10.5-2CA5E0)](https://core.telegram.org/bots/api-changelog)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-22.8-2CA5E0)](https://github.com/python-telegram-bot/python-telegram-bot)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/isihussain/telegram-bot-handbook/actions/workflows/ci.yml/badge.svg)](https://github.com/isihussain/telegram-bot-handbook/actions/workflows/ci.yml)

39 focused pages. Every limit, parameter and behaviour is checked against the official Telegram
docs and pinned to a version, so you can tell whether a page is still true. Runnable examples and a
small tested helper library (`tgkit`) are included — no bot token needed to run the test suite.

> **New here?** Read [Bot API Overview](docs/01-foundations/01-bot-api-overview.md), then
> [Limits Cheatsheet](docs/01-foundations/05-limits-cheatsheet.md), then run
> `python examples/01_hello_polling.py`.

---

## Why this exists

Most Telegram bot bugs are not exotic. They are one of these:

| Symptom | Real cause | Page |
| :--- | :--- | :--- |
| `400 Bad Request: message is too long` | text over **4096** characters | [Limits](docs/01-foundations/05-limits-cheatsheet.md) |
| `400 BUTTON_DATA_INVALID` | `callback_data` over **64 bytes** | [Callbacks](docs/02-interaction/03-callback-queries.md) |
| Bot silent in groups | privacy mode is on by default | [Privacy mode](docs/01-foundations/06-privacy-mode-in-groups.md) |
| Buttons spin forever | `answerCallbackQuery` never called | [Callbacks](docs/02-interaction/03-callback-queries.md) |
| Users charged twice | no idempotency on `successful_payment` | [Idempotency](docs/03-state/03-idempotent-updates.md) |
| `429 Too Many Requests` storms | broadcast faster than ~30/s | [Flood control](docs/05-security/04-flood-and-abuse-control.md) |
| Mini App rejects every login | wrong `initData` HMAC | [initData validation](docs/04-advanced/02-miniapp-initdata-validation.md) |
| Webhook silently stops | no `secret_token`, or a stale URL | [Webhook hardening](docs/05-security/01-webhook-and-secrets.md) |

This handbook covers each of them once, properly, with the exact numbers and a fix you can paste.

---

## Contents

### 1. Foundations — how the platform works

| Page | What you get |
| :--- | :--- |
| [Bot API Overview](docs/01-foundations/01-bot-api-overview.md) | The update/method model, raw `curl` calls, what a handler really is, version reality check |
| [BotFather and Tokens](docs/01-foundations/02-botfather-and-tokens.md) | Creating a bot, every useful BotFather command, token hygiene, what a leak allows |
| [Polling vs Webhooks](docs/01-foundations/03-polling-vs-webhooks.md) | Side-by-side table, required ports/subnets, migration checklist |
| [Update Types](docs/01-foundations/04-update-types-and-subscriptions.md) | Every `Update` field, `allowed_updates`, handler matching, group order |
| [Limits Cheatsheet](docs/01-foundations/05-limits-cheatsheet.md) | Every number that matters: text, files, callbacks, polls, flood limits |
| [Privacy Mode](docs/01-foundations/06-privacy-mode-in-groups.md) | Why a bot ignores group messages and how to change it correctly |

### 2. Interaction — messages, buttons, media

| Page | What you get |
| :--- | :--- |
| [Formatting and Parse Modes](docs/02-interaction/01-formatting-parse-modes.md) | HTML vs MarkdownV2 vs entities, escaping user input, UTF-16 offsets |
| [Keyboards](docs/02-interaction/02-keyboards-inline-vs-reply.md) | Inline vs reply, editing buttons, when buttons are the wrong tool |
| [Callback Queries](docs/02-interaction/03-callback-queries.md) | Answer-first pattern, safe edits, versioned callback data, state placement |
| [Inline Mode](docs/02-interaction/04-inline-mode.md) | `@bot query`, 50-result pages, caching rules, result types |
| [Deep Links](docs/02-interaction/05-deep-links.md) | `?start=` payloads, `startapp`, validation, attribution without trust |
| [Media and Files](docs/02-interaction/06-media-and-files.md) | `file_id` reuse, 20/50 MB limits, downloads, albums, upload validation |
| [Commands and Menu](docs/02-interaction/07-commands-and-menu.md) | `setMyCommands`, scopes, localisation, menu button, unknown commands |
| [Polls and Quizzes](docs/02-interaction/08-polls-and-quizzes.md) | `sendPoll`, `correct_option_ids`, `poll_answer`, anonymous semantics |

### 3. State — conversations that survive reality

| Page | What you get |
| :--- | :--- |
| [Conversations and FSM](docs/03-state/01-conversations-and-fsm.md) | `ConversationHandler` vs explicit state machine, timeouts, concurrency traps |
| [Persistence](docs/03-state/02-persistence-and-storage.md) | `user_data` vs database, `PicklePersistence` risks, schema, migrations |
| [Idempotent Updates](docs/03-state/03-idempotent-updates.md) | Why duplicates happen, claim-by-`update_id`, Redis/SQLite/Postgres |
| [JobQueue](docs/03-state/04-job-queue.md) | `run_once`/`run_daily`/`run_repeating`, time zones, restart behaviour |

### 4. Advanced — Mini Apps, payments, new Bot API

| Page | What you get |
| :--- | :--- |
| [Mini Apps Overview](docs/04-advanced/01-mini-apps-overview.md) | The seven launch modes, minimal frontend and backend, security rules |
| [initData Validation](docs/04-advanced/02-miniapp-initdata-validation.md) | HMAC-SHA256 and Ed25519, the exact data-check-string, failure modes, test signing |
| [Telegram Stars](docs/04-advanced/03-stars-payments.md) | `XTR` invoices, the 10-second pre-checkout deadline, delivery, refunds |
| [Streaming Replies](docs/04-advanced/04-streaming-ai-replies.md) | `sendMessageDraft`, the 30-second preview rule, stop handling, throttling |
| [Groups and Channels](docs/04-advanced/05-groups-channels-permissions.md) | Admin rights, restrict/promote/ban, join requests, guard bots |
| [Local Bot API Server](docs/04-advanced/06-local-bot-api-server.md) | Lifting 20/50 MB limits, any webhook port, moving a bot between servers |
| [Bot API 10.x Changes](docs/04-advanced/07-bot-api-10-changes.md) | What changed in 2026, and how to call methods the library has not wrapped |

### 5. Security — defensive, not clever

| Page | What you get |
| :--- | :--- |
| [Webhook and Secrets](docs/05-security/01-webhook-and-secrets.md) | `secret_token`, subnet allow-list, nginx check, fast-200 pattern |
| [Token Leak Response](docs/05-security/02-token-leak-response.md) | First 10 minutes, what the attacker could do, git history, post-incident list |
| [Input Validation](docs/05-security/03-input-validation.md) | Trust boundaries, allow-lists, injection classes, file uploads, authorisation |
| [Flood and Abuse Control](docs/05-security/04-flood-and-abuse-control.md) | Per-user limits, 429 handling, broadcast pacing, Telegram moderation tools |

### 6. Production — running it for real

| Page | What you get |
| :--- | :--- |
| [Deployment](docs/06-production/01-deployment-docker-systemd.md) | Dockerfile, Compose, systemd unit, config rules, health checks |
| [Scaling](docs/06-production/02-scaling-queues-workers.md) | Growth stages, ingress → queue → workers, per-chat ordering, sharding |
| [Errors, 429s and Retries](docs/06-production/03-errors-429-and-retries.md) | Retry vs never-retry classes, duplicate-send problem, `ChatMigrated`, `Conflict` |
| [Logging and Observability](docs/06-production/04-logging-and-observability.md) | Structured logs, handler timing, metrics, alerts, privacy |
| [Testing Bots](docs/06-production/05-testing-bots.md) | Test pyramid, wiring tests, fake bots, building `Update` objects, CI |
| [Troubleshooting](docs/06-production/06-troubleshooting.md) | Symptom → cause table, five-minute triage, "works then stops" |

### 7. Reference

| Page | What you get |
| :--- | :--- |
| [Library Comparison](docs/07-libraries/01-comparison.md) | python-telegram-bot, aiogram, grammY, Telegraf and friends, with real numbers |
| [Error Reference](docs/08-reference/01-error-reference.md) | The `description` strings you will actually see, and the fix for each |
| [API Method Cheatsheet](docs/08-reference/03-api-cheatsheet.md) | Every method grouped by job, with the limit or permission that bites |
| [Glossary](docs/08-reference/02-glossary.md) | Every term used in the Bot API and in this handbook |

---

## Start in five minutes

```bash
git clone https://github.com/isihussain/telegram-bot-handbook.git
cd telegram-bot-handbook
python -m venv .venv && source .venv/bin/activate   # Python 3.11+
pip install -e ".[dev]"

export BOT_TOKEN="123456789:AAH..."   # from @BotFather
python examples/01_hello_polling.py
```

Send `/start`, then any text. The bot echoes it.

Check your own code without a token:

```bash
ruff check .
python scripts/check_docs.py
pytest -q
```

---

## The 12 rules this handbook keeps repeating

| # | Rule | Why |
| :-: | :--- | :--- |
| 1 | Never commit the token | It is a password; anyone with it *is* your bot |
| 2 | One poller per token | Two pollers split updates unpredictably (`409 Conflict`) |
| 3 | Subscribe only to the update types you handle | Less traffic, fewer surprises |
| 4 | Answer every callback query immediately | Otherwise the client spins until timeout |
| 5 | Treat `callback_data` as 64 bytes, not a database | Over the limit the whole send fails |
| 6 | Escape user text for the parse mode you chose | One `<` breaks the whole message |
| 7 | Split text at 4096 characters before sending | Telegram rejects, it does not truncate |
| 8 | Make payments idempotent on the charge id | Telegram may deliver `successful_payment` twice |
| 9 | Honour `retry_after` exactly | Tight retry loops turn a wait into a ban |
| 10 | Validate `initData` on the server, every request | It is the only proof of who opened the Mini App |
| 11 | Set a webhook `secret_token` and check the header | A public URL is not an authentication mechanism |
| 12 | Log ids, not message content | Privacy, retention and incident response all get easier |

---

## Limits at a glance

Verified against Bot API 10.5 on 2026-11-26. Sources and context: [Limits Cheatsheet](docs/01-foundations/05-limits-cheatsheet.md).

| Thing | Limit |
| :--- | :--- |
| Message text | 1–4096 characters after entity parsing |
| Caption | 0–1024 characters |
| Entities per message | 100 |
| `callback_data` | 1–64 **bytes** |
| Bot command | 1–32 characters |
| Commands per scope | 100 |
| Deep-link `start` payload | 64 characters |
| Inline results per answer | 50 |
| Media group | 2–10 items |
| Upload (bot) | 50 MB (photos 10 MB) |
| Download (`getFile`) | 20 MB |
| Upload (local Bot API server) | 2000 MB |
| Webhook ports | 443, 80, 88, 8443 |
| Webhook `secret_token` | 1–256 chars, `[A-Za-z0-9_-]` |
| `max_connections` | 1–100, default 40 |
| Pre-checkout answer deadline | 10 seconds |
| Broadcast | ~30 messages/s free, 1000/s with paid broadcasts |

---

## Runnable examples

Every example builds its `Application` in a `build_application(token)` function, so it can be
imported and tested without network access.

| File | Shows |
| :--- | :--- |
| [`01_hello_polling.py`](examples/01_hello_polling.py) | Smallest correct bot: commands, echo, error handler |
| [`02_webhook.py`](examples/02_webhook.py) | Webhook with `secret_token` and `allowed_updates` |
| [`03_inline_keyboard.py`](examples/03_inline_keyboard.py) | Inline keyboard + versioned callback data |
| [`04_conversation_form.py`](examples/04_conversation_form.py) | Multi-step form with timeout and `/cancel` |
| [`05_stars_payment.py`](examples/05_stars_payment.py) | Telegram Stars invoice, pre-checkout, idempotent delivery |
| [`06_miniapp_backend.py`](examples/06_miniapp_backend.py) | `initData` validation helpers for any web framework |
| [`07_admin_and_moderation.py`](examples/07_admin_and_moderation.py) | Admin-only commands, join restrictions, inline mode |
| [`08_production_template.py`](examples/08_production_template.py) | Rate limiter, de-duplication, graceful errors |
| [`09_streaming_draft.py`](examples/09_streaming_draft.py) | Streaming a generated reply with `sendMessageDraft` |
| [`10_job_queue.py`](examples/10_job_queue.py) | Reminders and daily digests with `JobQueue` |

---

## `tgkit` — the small library behind the examples

Copy-paste sized helpers, each with tests. Import them, or read them as reference implementations.

| Module | Function |
| :--- | :--- |
| [`tgkit.initdata`](src/tgkit/initdata.py) | `validate_init_data` (HMAC), `validate_init_data_ed25519` (third-party), `InitDataError` |
| [`tgkit.callback_data`](src/tgkit/callback_data.py) | `pack_callback` / `unpack_callback` with a hard 64-byte check |
| [`tgkit.idempotency`](src/tgkit/idempotency.py) | `MemoryUpdateStore`, `SQLiteUpdateStore` — claim an `update_id` once |
| [`tgkit.retry`](src/tgkit/retry.py) | `call_with_retry` — honours `RetryAfter`, skips permanent errors |
| [`tgkit.ratelimit`](src/tgkit/ratelimit.py) | `TokenBucket` — per-key bursts, refill and a `retry_after` hint |
| [`tgkit.broadcast`](src/tgkit/broadcast.py) | `broadcast` — paced sending, records blocked users |
| [`tgkit.text`](src/tgkit/text.py) | `split_message` — 4096-character safe splitting |
| [`tgkit.config`](src/tgkit/config.py) | `Settings.from_env`, `generate_webhook_secret`, `redact` |

```python
from tgkit.config import Settings
from tgkit.initdata import validate_init_data
from tgkit.callback_data import pack_callback

settings = Settings.from_env()                      # fails fast on a bad token
data = validate_init_data(raw_init_data, settings.bot_token, max_age_seconds=3600)
button = pack_callback("page", 2)                   # raises before Telegram does
```

---

## How this handbook stays correct

Every page starts with the same header:

```markdown
> **TL;DR:** The answer in two sentences.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26
```

and ends with a **Sources** section linking the official docs or library source. CI enforces the
structure, checks that every relative link resolves, and compiles every Python file. Nothing here
is written from memory without a source.

| Check | Command |
| :--- | :--- |
| Structure, links, code fences | `python scripts/check_docs.py` |
| Lint | `ruff check .` |
| Tests (no network) | `pytest -q` |

---

## Using this with an AI assistant

- [`llms.txt`](llms.txt) is a compact, machine-readable index of every page.
- Point an assistant at the specific page, not the whole repo: pages are self-contained.
- The `Applies to` line tells the model which Bot API version the advice assumes.
- For anything newer than the library, the answer is usually `bot.do_api_request(...)` — see
  [Bot API 10.x Changes](docs/04-advanced/07-bot-api-10-changes.md).

Suggested prompt:

```text
Use the Telegram Bot Handbook page docs/02-interaction/03-callback-queries.md as the source of
truth. Follow its answer-first pattern and 64-byte callback data rule. If the page does not cover
something, say so instead of guessing.
```

---

## FAQ

**Why python-telegram-bot and not aiogram?**
It has the largest community and the most examples, and every concept maps cleanly to the other
frameworks. See the [comparison](docs/07-libraries/01-comparison.md) for the trade-offs.

**Does this work with Bot API 10.5?**
The library wraps the 10.0 surface; newer methods are reachable via `do_api_request`. Every page
states its version, and [Bot API 10.x Changes](docs/04-advanced/07-bot-api-10-changes.md) lists
what is and is not wrapped.

**Can I use this for a business or a large bot?**
Yes. Start with [Deployment](docs/06-production/01-deployment-docker-systemd.md) and
[Scaling](docs/06-production/02-scaling-queues-workers.md); the patterns are the ones large bots
converge on.

**Is there exploit or spam tooling here?**
No. The security pages are defensive only, and the handbook deliberately does not help with
evading Telegram's limits or bans.

**Something is outdated.**
Open a [doc correction](https://github.com/isihussain/telegram-bot-handbook/issues/new?template=doc-correction.yml) with the official source.
Corrections with a link get merged quickly.

---

## Contributing

Corrections, new pages and better examples are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md)
first: every fact needs a source, every Python block must parse, and secrets never go in a commit.

- [Report a security issue](SECURITY.md) privately, not in a public issue.
- One topic per pull request.
- Update the `Applies to` line when behaviour changes.

## 9. Cookbook

A collection of practical, standalone recipes for real-world bot scenarios. Each recipe
contains a self-contained problem, a solution with copy-paste code, and a link to the
corresponding documentation page. See \`docs/09-cookbook/\` for the current recipes.

- [Recipe: Support Inbox with Forum Topics](docs/09-cookbook/01-support-inbox.md)

## License

MIT. Use the pages and the code however you like; attribution is appreciated.
