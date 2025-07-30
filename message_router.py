from telegram import Update
from telegram.ext import ContextTypes

from keyboards.support import receive_support_message
from keyboards.partnership import receive_partner_message

from text_replies import *

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
        print(text_message_router_1)
        await update.message.reply_text(text_message_router_2)
