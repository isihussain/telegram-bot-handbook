"""08 - Production template: webhook + rate limiter + idempotency + graceful errors.

This is the shape most real bots converge on. Read the comments; each line exists for a reason.

    BOT_TOKEN=... WEBHOOK_URL=https://bot.example.com/telegram \
    WEBHOOK_SECRET=... python examples/08_production_template.py
"""

from __future__ import annotations

import logging
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import Forbidden, TelegramError
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from tgkit.config import redact
from tgkit.idempotency import MemoryUpdateStore

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

seen = MemoryUpdateStore(max_items=50_000)


class SeenUpdates:
    """Middleware-ish guard: drop updates we already processed."""

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # A TypeHandler runs for every update; returning early is cheap.
        if not seen.claim(update.update_id):
            logger.info("duplicate update %s ignored", update.update_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_message is not None
    await update.effective_message.reply_text(
        "<b>Ready.</b>", parse_mode=ParseMode.HTML
    )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    error = context.error
    if isinstance(error, Forbidden):
        # The user blocked the bot: stop sending, do not retry.
        logger.info("forbidden: %s", redact(str(error)))
        return
    if isinstance(error, TelegramError):
        logger.warning("telegram error: %s", redact(str(error)))
        return
    logger.exception("unhandled error", exc_info=error)


def build_application(token: str) -> Application:
    from telegram.ext import TypeHandler

    app = (
        ApplicationBuilder()
        .token(token)
        # Respect per-chat limits instead of hammering the API and collecting 429s.
        .rate_limiter(AIORateLimiter(max_retries=2))
        # Concurrency: number of updates processed in parallel. 256 is a sane default.
        .concurrent_updates(256)
        .build()
    )
    app.add_handler(TypeHandler(Update, SeenUpdates()), group=-1)
    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(on_error)
    return app


def main() -> None:
    token = os.environ["BOT_TOKEN"]
    app = build_application(token)
    if url := os.environ.get("WEBHOOK_URL"):
        app.run_webhook(
            listen=os.environ.get("WEBHOOK_LISTEN", "0.0.0.0"),
            port=int(os.environ.get("WEBHOOK_PORT", "8443")),
            url_path=url.rsplit("/", 1)[-1],
            webhook_url=url,
            secret_token=os.environ.get("WEBHOOK_SECRET"),
        )
    else:
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
