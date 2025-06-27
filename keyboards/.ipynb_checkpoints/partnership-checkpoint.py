from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler
)

from db import get_choice, is_agreement_accepted
from keyboards.main_menu import get_main_menu
from text_replies import *

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from env import *

ADMIN_ID = ADMIN_ID_PARTNERSHIP  # Telegram ID администратора партнёрства


# Открытие партнёрского меню через callback
async def open_partnership_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Я хочу стать партнёром", callback_data="become_partner")],
        [InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_main")]
    ])
    await query.message.reply_text(
        "🤝 Партнёрская программа:\nНажмите кнопку ниже, если хотите стать партнёром.",
        reply_markup=keyboard
    )


# Обработка запроса стать партнёром — просим ввести сообщение
async def become_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["state"] = "awaiting_partner_message"

    await query.message.reply_text(
        "✉️ Пожалуйста, отправьте сообщение для администратора (например, как вы хотите сотрудничать):"
    )


# Принимаем текст от пользователя (через message_router)
async def receive_partner_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "awaiting_partner_message":
        return

    context.user_data.pop("state", None)

    user = update.effective_user
    text = update.message.text

    user_link = (
        f"https://t.me/{user.username}" if user.username
        else f"[Профиль](tg://user?id={user.id})"
    )

    await update.message.reply_text(
        "Спасибо! Мы с вами свяжемся.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_main")]
        ])
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"📞 Новый партнёр:\n"
            f"👤 Имя: {user.first_name}\n"
            f"🔗 Telegram: {user_link}\n"
            f"📝 Сообщение: {text}"
        ),
        parse_mode="Markdown"
    )


# Возврат в главное меню
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name

    if not is_agreement_accepted(user_id):
        await query.message.reply_text(declaration_if_not_excepted)
        return

    user_choice = get_choice(user_id)
    reply_markup = get_main_menu(user_choice, user_id)

    await query.message.reply_text(
        text_1_greating.format(user_first_name=user_first_name) +
        f"\nuser_id = {user_id}\nuser_choice = {user_choice}",
        reply_markup=reply_markup
    )


# Регистрация хендлеров
def register_partnership_handlers_ptb(app):
    app.add_handler(CallbackQueryHandler(open_partnership_menu, pattern="^partnership$"))
    app.add_handler(CallbackQueryHandler(become_partner, pattern="^become_partner$"))
    app.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^back_to_main$"))
