# Scheduling with JobQueue

> **TL;DR:** `JobQueue` runs coroutines on a schedule inside your bot process. It is in-memory: jobs are lost on restart unless you re-create them. For durable schedules, use an external scheduler.
> **Applies to:** Bot API 10.5 · python-telegram-bot 22.8 · Last verified 2026-11-26

## 1. The three job kinds

| Call | Runs |
| :--- | :--- |
| `run_once(callback, when=...)` | once, after a delay or at a datetime |
| `run_daily(callback, time=...)` | every day at a time |
| `run_repeating(callback, interval=...)` | every N seconds |

```python
context.job_queue.run_once(remind, when=60, chat_id=chat.id, data="drink water")
context.job_queue.run_daily(digest, time=dt.time(9, 0, tzinfo=dt.timezone.utc), chat_id=chat.id)
context.job_queue.run_repeating(cleanup, interval=3600, first=10)
```

## 2. The job callback

```python
async def remind(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(job.chat_id, f"Reminder: {job.data}")
```

| Attribute | Meaning |
| :--- | :--- |
| `job.chat_id` | the chat passed when scheduling |
| `job.data` | any object you passed |
| `job.name` | unique name; scheduling the same name twice replaces the job |
| `job.remove()` | cancel it |

## 3. Time zones

`run_daily` interprets `time` in the time zone of the `time` object. Always pass an aware `datetime.time` with `tzinfo`, or you will get "runs at 09:00 in whatever the server thinks local time is".

## 4. Restart behaviour

`JobQueue` lives in memory. After a restart:

- one-off jobs are gone,
- repeating jobs are gone,
- daily jobs are gone.

Pattern: store schedules in your database and re-create jobs in `post_init`.

```python
async def post_init(app):
    for row in await db.list_schedules():
        app.job_queue.run_daily(digest, time=row.time, chat_id=row.chat_id, name=f"s:{row.id}")

app = ApplicationBuilder().token(token).post_init(post_init).build()
```

## 5. Concurrency and mistakes

| Mistake | Consequence |
| :--- | :--- |
| Scheduling the same `name` per chat with a global name | one chat silently replaces another |
| Long job body | blocks the event loop and delays other jobs; offload heavy work |
| Job that throws | logged; the job is not retried automatically |
| Huge number of jobs | memory grows; batch instead |

```python
# unique per chat
context.job_queue.run_daily(digest, time=t, chat_id=chat.id, name=f"digest:{chat.id}")
```

## 6. When not to use JobQueue

| Need | Use instead |
| :--- | :--- |
| Survives restarts, runs once across replicas | Celery / RQ / Temporal / cloud scheduler |
| Exactly-once delivery | external queue with visibility timeout |
| More than a few thousand schedules | database + a scheduler service |

## Sources

- https://docs.python-telegram-bot.org/en/stable/telegram.ext.jobqueue.html
- https://docs.python-telegram-bot.org/en/stable/telegram.ext.applicationbuilder.html (`post_init`)
