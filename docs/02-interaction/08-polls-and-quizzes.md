# Polls and Quizzes

> **TL;DR:** `sendPoll` creates polls; `quiz=True` makes a quiz with a correct answer. Poll answers arrive as `poll_answer` updates. Stop or close with `stopPoll`, and remember that anonymous polls do not reveal who voted.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. Sending

```python
await context.bot.send_poll(
    chat_id=chat_id,
    question="Deploy on Friday?",
    options=["Yes", "No", "Only with a rollback plan"],
    is_anonymous=False,
    allows_multiple_answers=False,
    open_period=600,          # auto-close after 10 minutes
)
```

Quiz:

```python
await context.bot.send_poll(
    chat_id=chat_id,
    question="Which HTTP status means 'too many requests'?",
    options=["400", "403", "429"],
    type="quiz",
    correct_option_ids=[2],   # Bot API 9.6+: list, supports multiple correct answers
    explanation="429 Too Many Requests.",
)
```

## 2. Limits

| Field | Limit |
| :--- | :--- |
| Question | 1–300 characters |
| Option | 1–100 characters |
| Options | 1–12 |
| Explanation | 200 characters |
| `open_period` | 5 – 2,628,000 seconds |

## 3. Receiving answers

```python
from telegram import Update
from telegram.ext import ContextTypes

async def on_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = update.poll_answer
    if answer is None:
        return
    user_id = answer.user.id
    chosen = answer.option_ids          # zero-based indexes
    poll_id = answer.poll_id
    # Persist (poll_id, user_id, chosen). Users can retract (empty option_ids).
```

```python
from telegram.ext import PollAnswerHandler
app.add_handler(PollAnswerHandler(on_poll_answer))
```

## 4. Anonymous vs not

| `is_anonymous` | What other members see | What your bot gets in `poll_answer` |
| :--- | :--- | :--- |
| `False` | who voted for what | `user` and `option_ids` |
| `True` | only totals | `user` and `option_ids` — the bot always learns the voter |

Anonymity is a promise to the **group**, not to the bot. Still, do not display or store that attribution where other members can see it: that would break the promise the poll made.

For votes you must attribute reliably, use `is_anonymous=False` **and** your own button-based UI when identity is critical.

## 5. Closing and reading results

```python
poll_message = await context.bot.send_poll(...)
await context.bot.stop_poll(chat_id=chat_id, message_id=poll_message.message_id)
```

To read current results, use the `poll` object on the message (`get_updates` will not resend it): store the `message_id` and call `forward_message` or rely on `poll_answer` updates.

## 6. Pitfalls

- **`correct_option_id` is gone** in recent API versions; use `correct_option_ids` (a list).
- **One option is allowed** since Bot API 10.0, so a "poll" with a single choice is valid.
- **Members-only polls** require the voter to be a member of the channel for a minimum period (`members_only`, `country_codes` in Bot API 10.0).
- **Editing options** changes the poll; options added later have `added_by_user`/`added_by_chat`.

## Sources

- https://core.telegram.org/bots/api#sendpoll
- https://core.telegram.org/bots/api#poll
- https://core.telegram.org/bots/api#pollanswer
- https://core.telegram.org/bots/api-changelog (9.6, 10.0 poll changes)
