"""07 - Admin-only commands, group moderation, and an inline mode handler.

Run:
    BOT_TOKEN=... ADMIN_IDS=11111111 python examples/07_admin_and_moderation.py
"""

from __future__ import annotations

import logging
import os
from collections.abc import Awaitable, Callable
from functools import wraps

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_IDS = {int(part) for part in os.environ.get("ADMIN_IDS", "").split(",") if part}


def admin_only(
    func: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]],
) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]:
    """Reject anyone not listed in ADMIN_IDS."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if user is None or user.id not in ADMIN_IDS:
            # Do not leak whether the command exists.
            if update.effective_message:
                await update.effective_message.reply_text("Not available.")
            return
        await func(update, context)

    return wrapper


@admin_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_message is not None
    await update.effective_message.reply_text(f"Known admins: {len(ADMIN_IDS)}")


async def on_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Restrict new members until an admin (or a captcha) releases them."""
    result = update.chat_member
    if result is None or result.new_chat_member.status != ChatMemberStatus.MEMBER:
        return
    chat = result.chat
    user = result.new_chat_member.user
    try:
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=user.id,
            permissions={"can_send_messages": False},
        )
        await context.bot.send_message(
            chat.id, f"Welcome {user.first_name}. Ask an admin to unlock you."
        )
    except Exception:
        logger.exception("Could not restrict %s in %s", user.id, chat.id)


async def inline_echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query
    if query is None:
        return
    text = (query.query or "").strip()[:200] or "type something"
    await query.answer(
        results=[
            InlineQueryResultArticle(
                id="echo",
                title="Send as a message",
                input_message_content=InputTextMessageContent(text),
            )
        ],
        cache_time=30,
        is_personal=True,
    )


def build_application(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(ChatMemberHandler(on_join, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(InlineQueryHandler(inline_echo))
    return app


def main() -> None:
    build_application(os.environ["BOT_TOKEN"]).run_polling()


if __name__ == "__main__":
    main()
