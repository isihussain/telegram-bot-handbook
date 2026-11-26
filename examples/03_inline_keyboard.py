"""03 - Inline keyboards and callback queries, with compact versioned callback data.

Run:
    BOT_TOKEN=... python examples/03_inline_keyboard.py
"""

from __future__ import annotations

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from tgkit.callback_data import pack_callback, unpack_callback

logging.basicConfig(level=logging.INFO)

PAGES = {
    "1": "Page 1: polling vs webhooks -> docs/01-foundations/03-polling-vs-webhooks.md",
    "2": "Page 2: limits -> docs/01-foundations/05-limits-cheatsheet.md",
    "3": "Page 3: security -> docs/05-security/01-webhook-and-secrets.md",
}


def menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Page 1", callback_data=pack_callback("page", 1)),
                InlineKeyboardButton("Page 2", callback_data=pack_callback("page", 2)),
                InlineKeyboardButton("Page 3", callback_data=pack_callback("page", 3)),
            ],
            [InlineKeyboardButton("Docs", url="https://core.telegram.org/bots/api")],
        ]
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_message is not None
    await update.effective_message.reply_text("Pick a page:", reply_markup=menu_markup())


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    # Always answer: otherwise the client shows a loading spinner until it times out.
    await query.answer()
    try:
        action, parts = unpack_callback(query.data or "")
    except ValueError:
        await query.edit_message_text("This button is from an older version of the menu.")
        return

    if action != "page" or not parts:
        return
    page = parts[0]
    await query.edit_message_text(
        PAGES.get(page, "Unknown page"), reply_markup=menu_markup()
    )


def build_application(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(on_callback))
    return app


def main() -> None:
    build_application(os.environ["BOT_TOKEN"]).run_polling()


if __name__ == "__main__":
    main()
