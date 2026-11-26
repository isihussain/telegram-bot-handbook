"""02 - Webhook deployment with a secret token and a minimal handler.

Run behind TLS (Caddy, nginx, Cloudflare Tunnel). Telegram only posts to ports 443, 80, 88, 8443
on a public IPv4 address, so terminating TLS in front of this process is the normal setup.

    BOT_TOKEN=... WEBHOOK_URL=https://bot.example.com/telegram \
    WEBHOOK_SECRET=$(python -c 'import secrets;print(secrets.token_urlsafe(48))') \
    WEBHOOK_PORT=8443 python examples/02_webhook.py
"""

from __future__ import annotations

import logging
import os

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_message is not None
    await update.effective_message.reply_text("Webhook mode is up.")


def build_application(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    return app


def main() -> None:
    token = os.environ["BOT_TOKEN"]
    url = os.environ["WEBHOOK_URL"]
    secret = os.environ["WEBHOOK_SECRET"]
    port = int(os.environ.get("WEBHOOK_PORT", "8443"))
    listen = os.environ.get("WEBHOOK_LISTEN", "0.0.0.0")
    url_path = url.rsplit("/", 1)[-1] or "telegram"

    app = build_application(token)
    # run_webhook registers the webhook (setWebhook) and starts an aiohttp server.
    # secret_token makes python-telegram-bot reject requests without the
    # X-Telegram-Bot-Api-Secret-Token header, and passes it to setWebhook for us.
    app.run_webhook(
        listen=listen,
        port=port,
        url_path=url_path,
        webhook_url=url,
        secret_token=secret,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=False,
        max_connections=40,
    )


if __name__ == "__main__":
    main()
