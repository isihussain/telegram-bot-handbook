"""10 - Scheduling with JobQueue: reminders, digests, cleanups.

Run:
    BOT_TOKEN=... python examples/10_job_queue.py
"""

from __future__ import annotations

import datetime as dt
import logging
import os

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat is None:
        return
    if not context.args:
        await update.effective_message.reply_text("Usage: /remind <seconds> <text>")
        return
    try:
        delay = int(context.args[0])
    except ValueError:
        await update.effective_message.reply_text("First argument must be a number of seconds.")
        return
    text = " ".join(context.args[1:]) or "Reminder"
    context.job_queue.run_once(
        _fire, when=delay, chat_id=chat.id, data=text, name=f"{chat.id}:{text}"
    )
    await update.effective_message.reply_text(f"Okay, in {delay}s.")


async def _fire(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(job.chat_id, f"Reminder: {job.data}")


async def daily(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id if context.job else None
    if chat_id is None:
        return
    await context.bot.send_message(chat_id, "Daily digest placeholder.")


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat is None:
        return
    # Run every day at 09:00 UTC. `first` avoids a burst of catch-up runs after downtime.
    context.job_queue.run_daily(
        daily,
        time=dt.time(hour=9, tzinfo=dt.UTC),
        chat_id=chat.id,
        name=f"digest:{chat.id}",
    )
    await update.effective_message.reply_text("Subscribed to the 09:00 UTC digest.")


def build_application(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("digest", subscribe))
    return app


def main() -> None:
    build_application(os.environ["BOT_TOKEN"]).run_polling()


if __name__ == "__main__":
    main()
