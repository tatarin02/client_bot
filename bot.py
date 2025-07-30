from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    PicklePersistence,
    filters
)

from db import init_db, get_choice, is_agreement_accepted
from env import BOT_TOKEN
from text_replies import *
from outline.outline_script import init_outline_keys_table, update_valid_flags_in_db

from keyboards.main_menu import get_main_menu
from keyboards.user_agreement import (
    show_user_agreement,
    agreement_button_handler,
    get_agreement_handler,
    user_agreement_text_handler
)
from keyboards.tariff import register_tariff_handlers
from keyboards.partnership import register_partnership_handlers_ptb
from keyboards.support import register_support_handlers_ptb
from keyboards.my_keys import get_my_key_handler
from keyboards.my_stats import get_my_stats_handler
from message_router import message_router

# ✅ Инициализация БД и ключей
init_db()
init_outline_keys_table()

# ✅ Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_agreement_accepted(user_id):
        await update.message.reply_text(declaration_if_not_excepted)
        await show_user_agreement(update, context)
        return

    user_choice = get_choice(user_id)
    user_first_name = update.effective_user.first_name
    reply_markup = get_main_menu(user_choice, user_id)

    await update.message.reply_text(
        text_1_greating.format(user_first_name=user_first_name), 
        # +
        # f"\nuser_id = {user_id}\nuser_choice = {user_choice}",
        reply_markup=reply_markup
    )

# ✅ Persistence
persistence = PicklePersistence(filepath="bot_data")
app = ApplicationBuilder().token(BOT_TOKEN).persistence(persistence).build()

# ✅ Обновление valid-флагов
async def periodic_update_valid(context):
    update_valid_flags_in_db()

app.job_queue.run_repeating(periodic_update_valid, interval=300, first=15)

# ✅ Хендлеры
app.add_handler(CommandHandler("start", start))
app.add_handler(get_agreement_handler())
app.add_handler(CallbackQueryHandler(user_agreement_text_handler, pattern=r"^user_agreement$"))
app.add_handler(CallbackQueryHandler(agreement_button_handler, pattern=r"^back_to_main$"))

register_support_handlers_ptb(app)
register_partnership_handlers_ptb(app)
register_tariff_handlers(app)

app.add_handler(get_my_key_handler())
app.add_handler(get_my_stats_handler())

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.Regex(bot_1 ),
        message_router
    )
)

if __name__ == '__main__':
    app.run_polling()
