from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import accept_agreement, get_choice, is_agreement_accepted
from keyboards.main_menu import get_main_menu
from text_replies import USER_AGREEMENT_TEXT


# Функция показать текст соглашения с кнопками
async def show_user_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE, show_full=True):
    if show_full:
        keyboard = [
            [InlineKeyboardButton("✅ Ознакомился", callback_data="accept_agreement")],
            [InlineKeyboardButton("💎 Поддержка", callback_data="support")],
            [InlineKeyboardButton("❌ Отказаться", callback_data="decline_agreement")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_main")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (USER_AGREEMENT_TEXT)

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")



async def agreement_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if query.data == "accept_agreement":
        accept_agreement(user_id)
        await query.edit_message_text("✅ Спасибо за принятие соглашения!")

        user_choice = get_choice(user_id)
        reply_markup = get_main_menu(user_choice, user_id)

        await query.message.reply_text(
            "🏠 Добро пожаловать в главное меню!",
            reply_markup=reply_markup
        )

    elif query.data == "decline_agreement":
        # Завершаем сессию — больше ничего не показываем
        await query.edit_message_text(
            "❌ Вы отказались от соглашения.\n\n"
            "Чтобы начать заново — введите /start.",
            reply_markup=None
        )

    elif query.data == "back_to_main":
        user_id = query.from_user.id
        user_choice = get_choice(user_id)
        reply_markup = get_main_menu(user_choice, user_id)
    
        await query.message.reply_text("🏠 Главное меню", reply_markup=reply_markup)
    

from telegram.ext import CallbackQueryHandler

def get_agreement_handler():
    return CallbackQueryHandler(
        agreement_button_handler,
        pattern=r"^(accept_agreement|decline_agreement|back_to_main)$"
    )

async def user_agreement_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_agreement_accepted(user_id):
        await show_user_agreement(update, context, show_full=True)
    else:
        await show_user_agreement(update, context, show_full=False)
