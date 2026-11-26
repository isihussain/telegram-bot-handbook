"""04 - A multi-step form with ConversationHandler and per-user state.

Run:
    BOT_TOKEN=... python examples/04_conversation_form.py

Teaches: explicit states, fallbacks (so a user can always cancel), and why you should not keep
state in module-level variables.
"""

from __future__ import annotations

import logging
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)

NAME, EMAIL, CONFIRM = range(3)


async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.effective_message is not None
    context.user_data.clear()
    await update.effective_message.reply_text(
        "Let's sign you up. What is your name? (/cancel to stop)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.effective_message is not None
    context.user_data["name"] = (update.effective_message.text or "").strip()
    await update.effective_message.reply_text("Email address?")
    return EMAIL


async def got_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.effective_message is not None
    text = (update.effective_message.text or "").strip()
    if "@" not in text:
        await update.effective_message.reply_text("That does not look like an email. Try again.")
        return EMAIL
    context.user_data["email"] = text
    markup = ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True, resize_keyboard=True)
    await update.effective_message.reply_text(
        f"Name: {context.user_data['name']}\nEmail: {text}\nIs that correct?",
        reply_markup=markup,
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.effective_message is not None
    answer = (update.effective_message.text or "").strip().lower()
    if answer != "yes":
        await update.effective_message.reply_text(
            "Discarded. Send /signup to start again.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    # Persist here: write to your database, not to memory.
    await update.effective_message.reply_text(
        f"Saved {context.user_data['name']} <{context.user_data['email']}>.",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.effective_message is not None
    context.user_data.clear()
    await update.effective_message.reply_text(
        "Cancelled.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def build_application(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()
    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("signup", begin)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_email)],
                CONFIRM: [MessageHandler(filters.Regex(r"^(?i:yes|no)$"), confirm)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            # Do not let a conversation hang forever in a forgotten state.
            conversation_timeout=600,
        )
    )
    return app


def main() -> None:
    build_application(os.environ["BOT_TOKEN"]).run_polling()


if __name__ == "__main__":
    main()
