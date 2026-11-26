"""05 - Telegram Stars payments (digital goods).

Flow, per https://core.telegram.org/bots/payments-stars:
    sendInvoice (currency="XTR") -> pre_checkout_query -> answer within 10s ->
    successful_payment -> deliver goods and store telegram_payment_charge_id

Run:
    BOT_TOKEN=... python examples/05_stars_payment.py
"""

from __future__ import annotations

import logging
import os

from telegram import LabeledPrice, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRODUCT = {"title": "Premium month", "description": "30 days of premium features", "stars": 150}
# In production this belongs in your database, keyed by payload.
PAID_ORDERS: dict[str, str] = {}


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_message is not None
    payload = f"premium-30d-{update.effective_user.id if update.effective_user else 0}"
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id if update.effective_chat else 0,
        title=PRODUCT["title"],
        description=PRODUCT["description"],
        payload=payload,
        # Digital goods are sold in Telegram Stars: currency "XTR", no provider token.
        currency="XTR",
        prices=[LabeledPrice(PRODUCT["title"], PRODUCT["stars"])],
    )


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query is None:
        return
    # You must answer within 10 seconds or the payment is cancelled.
    if query.invoice_payload.startswith("premium-30d-"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Unknown product. Nothing was charged.")


async def on_paid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    payment = message.successful_payment if message else None
    if payment is None or message is None:
        return
    # Idempotency: Telegram can re-deliver. Charge id is unique per payment.
    if payment.telegram_payment_charge_id in PAID_ORDERS:
        return
    PAID_ORDERS[payment.telegram_payment_charge_id] = payment.invoice_payload
    logger.info(
        "Paid %s stars, charge %s, payload %s",
        payment.total_amount,
        payment.telegram_payment_charge_id,
        payment.invoice_payload,
    )
    await message.reply_text(
        f"Thanks! {payment.total_amount} Stars received. Premium is active.\n"
        f"Receipt: {payment.telegram_payment_charge_id}"
    )


def build_application(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    # successful_payment arrives as a message with a successful_payment field
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, on_paid))
    return app


def main() -> None:
    build_application(os.environ["BOT_TOKEN"]).run_polling()


if __name__ == "__main__":
    main()
