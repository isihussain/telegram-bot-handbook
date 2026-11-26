"""01 - Hello bot: long polling, the smallest correct starting point.

Run:
    BOT_TOKEN=123456:ABC... python examples/01_hello_polling.py

Teaches: Application lifecycle, a CommandHandler, an echo MessageHandler, and the difference
between "handler returns" and "bot replies".
"""

from __future__ import annotations

import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    assert update.effective_message is not None
    await update.effective_message.reply_text(
        f"Hi {user.first_name if user else 'there'}! Send me any text and I will echo it."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None or message.text is None:
        return
    # quote=True makes it a reply, which is easier to follow in group chats
    await message.reply_text(message.text, quote=True)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Never let an exception disappear: log it with the update that caused it.
    logger.exception("Unhandled error while processing %s", update, exc_info=context.error)


def build_application(token: str) -> Application:
    app = (
        ApplicationBuilder()
        .token(token)
        # Only subscribe to the update types you handle. This reduces traffic and noise.
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(on_error)
    return app


def main() -> None:
    token = os.environ["BOT_TOKEN"]
    app = build_application(token)
    # run_polling installs signal handlers and calls initialize/start/stop/shutdown for you.
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)


if __name__ == "__main__":
    main()
