"""09 - Streaming a generated reply with sendMessageDraft (Bot API 9.3+).

Drafts are ephemeral: they are a ~30 second preview. When generation finishes you must call
sendMessage with the final text, otherwise the message disappears.

Run:
    BOT_TOKEN=... python examples/09_streaming_draft.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import random

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)


async def slow_answer(prompt: str) -> str:
    """Stand-in for your LLM call."""
    await asyncio.sleep(0.2)
    return f"You asked: {prompt}\n\n" + " ".join(["streaming"] * 40)


async def stream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    if message is None or chat is None or message.text is None:
        return

    answer = await slow_answer(message.text)
    draft_id = random.randint(1, 2**31 - 1)  # non-zero, stable for this generation
    shown = ""
    for word in answer.split(" "):
        shown = f"{shown} {word}".strip()
        # Same draft_id animates; different id replaces without animation.
        await context.bot.send_message_draft(
            chat_id=chat.id, draft_id=draft_id, text=shown
        )
    # Persist the final message. Without this the draft vanishes.
    await message.reply_text(answer)


def build_application(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        assert update.effective_message is not None
        await update.effective_message.reply_text("Ask me anything.")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, stream))
    return app


def main() -> None:
    build_application(os.environ["BOT_TOKEN"]).run_polling()


if __name__ == "__main__":
    main()
