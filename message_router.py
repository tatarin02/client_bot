from telegram import Update
from telegram.ext import ContextTypes

from keyboards.support import receive_support_message
from keyboards.partnership import receive_partner_message

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    # print(f"📩 message_router: состояние = {state}")

    if state == "awaiting_support_message":
        # print("➡️ передаём в поддержку")
        await receive_support_message(update, context)
    elif state == "awaiting_partner_message":
        # print("➡️ передаём в партнёрство")
        await receive_partner_message(update, context)
    else:
        print("⚠️ неизвестное состояние — игнор")
        await update.message.reply_text("Неизвестная команда. Используйте кнопки меню 👇")
