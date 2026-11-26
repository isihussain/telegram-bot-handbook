# Flood and Abuse Control

> **TL;DR:** Rate-limit per user and per chat, answer 429 with `retry_after`, and use Telegram's own tools (restrictions, reports) for persistent abusers. Never build a tool whose purpose is to evade Telegram's limits.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. Two different limits

| Limit | Who imposes it | What happens |
| :--- | :--- | :--- |
| Telegram → your bot | Telegram | HTTP 429, `retry_after` seconds |
| Your bot → one user | you | you decide the policy |

The first protects you from Telegram; the second protects your users and your wallet.

## 2. Per-user rate limiting

```python
import time
from collections import defaultdict, deque

WINDOW = 10          # seconds
MAX_CALLS = 5        # per window per user

hits: dict[int, deque[float]] = defaultdict(deque)

def allowed(user_id: int, now: float | None = None) -> bool:
    current = time.monotonic() if now is None else now
    bucket = hits[user_id]
    while bucket and current - bucket[0] > WINDOW:
        bucket.popleft()
    if len(bucket) >= MAX_CALLS:
        return False
    bucket.append(current)
    return True
```

For multiple workers, use Redis (`INCR` + `EXPIRE`) instead of a local dict.

## 3. Handling 429 properly

```python
from telegram.error import RetryAfter

try:
    await bot.send_message(chat_id, text)
except RetryAfter as exc:
    await asyncio.sleep(float(exc.retry_after) + 0.5)
```

`tgkit.call_with_retry` and `tgkit.broadcast` already do this. Never retry immediately in a tight loop: that turns a short wait into a longer ban.

## 4. Broadcast pacing

| Scope | Safe rate |
| :--- | :--- |
| One chat | ≤ 1 message/second |
| One group | ≤ 20 messages/minute |
| All users | ~25–30 messages/second |

```python
from tgkit.broadcast import broadcast

result = await broadcast(user_ids, lambda uid: bot.send_message(uid, text))
print(result.sent, len(result.blocked), len(result.failed))
```

`Forbidden` means the user blocked the bot: remove them from the list instead of retrying forever.

## 5. Telegram-side tools

| Tool | Use |
| :--- | :--- |
| `restrict_chat_member` | mute, with `until_date` |
| `ban_chat_member` | remove and block re-entry |
| `delete_message` | remove spam (needs delete rights) |
| `report` in the client | users report the account, not your bot |
| `setChatMemberTag` (9.5) | label members for moderation workflows |

## 6. Abuse patterns to design for

| Pattern | Control |
| :--- | :--- |
| Command spam | per-user rate limit, temporary mute |
| Invite-link farming | single-use links, join request approval |
| Forwarded spam | content checks, link allow-list |
| Payment fraud | idempotent delivery, refund audit |
| Scraping via inline mode | rate limit and `is_personal=True` |

## 7. What this handbook will not help with

Mass-messaging strangers, evading bans, or bypassing Telegram's limits. Those violate the platform terms, get bots removed, and are outside the scope of this repository.

## Sources

- https://core.telegram.org/bots/faq#broadcasting-to-users
- https://core.telegram.org/bots/api#restrictchatmember
- https://core.telegram.org/bots/api#banchatmember
