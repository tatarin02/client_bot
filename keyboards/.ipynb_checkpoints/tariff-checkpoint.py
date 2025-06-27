from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime, timedelta
from db import (
    has_used_trial,
    mark_trial_used,
    save_choice,
    save_mock_payment,
    get_and_mark_payment_as_used
)
from outline.outline_script import create_outline_key, generate_qr_image

# Тарифы
TARIFFS = {
    "monthly": {"days": 30, "price": "99₽"},
    "3months": {"days": 90, "price": "249₽"},
    "6months": {"days": 180, "price": "489₽"},
    "12months": {"days": 365, "price": "949₽"},
}


# Показ тарифов
async def show_tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    try: await query.answer()
    except: pass

    text = (
        "<b>📦 Тарифные планы:</b>\n\n"
        "📝 <b>Пробный (3 дня)</b>\n• Бесплатно\n\n"
        "📅 <b>1 месяц</b>\n• 99₽\n\n"
        "📦 <b>3 месяца</b>\n• 249₽\n\n"
        "💼 <b>6 месяцев</b>\n• 489₽\n\n"
        "🎯 <b>12 месяцев</b>\n• 949₽"
    )

    buttons = []
    if not has_used_trial(user_id):
        buttons.append([InlineKeyboardButton("✅ Выбрать 📝 Пробный", callback_data="select_plan_trial")])

    buttons += [
        [InlineKeyboardButton("✅ Выбрать 📅 1 месяц", callback_data="select_plan_monthly")],
        [InlineKeyboardButton("✅ Выбрать 📦 3 месяца", callback_data="select_plan_3months")],
        [InlineKeyboardButton("✅ Выбрать 💼 6 месяцев", callback_data="select_plan_6months")],
        [InlineKeyboardButton("✅ Выбрать 🎯 12 месяцев", callback_data="select_plan_12months")],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_main")]
    ]

    await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))


# Универсальный экран оплаты
async def send_payment_menu(update, context, label, price, plan_key):
    query = update.callback_query
    user_id = query.from_user.id
    try: await query.answer()
    except: pass

    save_choice(user_id, plan_key)

    text = f"<b>🧾 Вы выбрали тариф: {label}</b>\nСтоимость: <b>{price}</b>\n\nВыберите действие:"
    buttons = [
        [InlineKeyboardButton("💳 Оплатить", callback_data=f"pay_{plan_key}")],
        [InlineKeyboardButton("🔍 Проверка / Ключ", callback_data=f"check_payment_{plan_key}")],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_main")]
    ]
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))


# Выбор платных тарифов
async def select_plan_monthly(update, context): await send_payment_menu(update, context, "1 месяц", "99₽", "monthly")
async def select_plan_3months(update, context): await send_payment_menu(update, context, "3 месяца", "249₽", "3months")
async def select_plan_6months(update, context): await send_payment_menu(update, context, "6 месяцев", "489₽", "6months")
async def select_plan_12months(update, context): await send_payment_menu(update, context, "12 месяцев", "949₽", "12months")


# Пробный тариф
async def select_trial_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    try: await query.answer()
    except: pass

    if has_used_trial(user_id):
        await query.message.reply_text("❌ Ты уже использовал пробный доступ. Выбери другой тариф.")
        return

    save_choice(user_id, "trial")
    mark_trial_used(user_id)

    key = create_outline_key(user_id=user_id, days_valid=3, max_devices=3)
    if not key:
        await query.message.reply_text("⚠️ Не удалось создать пробный ключ. Попробуйте позже.")
        return

    qr_path = generate_qr_image(key["accessUrl"])
    expires_at = (datetime.utcnow() + timedelta(days=3)).strftime('%d.%m.%Y %H:%M')
    caption = (
        f"<b>🎉 Пробный доступ активирован!</b>\n"
        f"<b>🔗 Ссылка:</b> {key['accessUrl']}\n"
        f"<b>⏳ Действует до:</b> {expires_at}"
    )

    if qr_path:
        await query.message.reply_photo(photo=InputFile(qr_path), caption=caption, parse_mode="HTML")
    else:
        await query.message.reply_text(caption, parse_mode="HTML")

    await send_app_links(update)
    await query.message.reply_text("🔙 Нажми кнопку ниже, чтобы вернуться в меню:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_main")]]))


# Проверка оплаты и выдача ключа
async def check_payment_and_send_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    plan_key = query.data.replace("check_payment_", "")

    try: await query.answer()
    except: pass

    # Получить неиспользованную оплату
    payment = get_and_mark_payment_as_used(user_id, plan_key)
    if not payment:
        await query.message.reply_text("❌ Оплата не найдена или уже использована.")
        return

    days = TARIFFS.get(plan_key, {}).get("days", 30)
    key = create_outline_key(user_id=user_id, days_valid=days, max_devices=3)

    if not key:
        await query.message.reply_text("⚠️ Не удалось создать ключ. Попробуйте позже.")
        return

    qr_path = generate_qr_image(key["accessUrl"])
    expires_at = (datetime.utcnow() + timedelta(days=days)).strftime('%d.%m.%Y %H:%M')
    caption = (
        f"<b>✅ Оплата подтверждена!</b>\n"
        f"<b>🔗 Ссылка:</b> {key['accessUrl']}\n"
        f"<b>⏳ Действует до:</b> {expires_at}"
    )

    if qr_path:
        await query.message.reply_photo(photo=InputFile(qr_path), caption=caption, parse_mode="HTML")
    else:
        await query.message.reply_text(caption, parse_mode="HTML")

    await send_app_links(update)
    await query.message.reply_text("🔙 Нажми кнопку ниже, чтобы вернуться в меню:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_main")]]))


# Заглушка оплаты
async def show_payment_placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    plan_key = query.data.replace("pay_", "")

    try:
        await query.answer()
    except:
        pass

    save_mock_payment(user_id, plan_key)

    await query.message.reply_text("💳 <b>Тут должна быть ссылка на сервис оплаты</b>\nОплата добавлена как тестовая запись.", parse_mode="HTML")


# Ссылки на приложения
async def send_app_links(update: Update):
    await update.callback_query.message.reply_text(
        "<b>Для установки приложения перейдите по ссылкам:</b>\n\n"
        "📱 <b>iPhone</b>:\nhttps://apps.apple.com/ru/app/outline-app/id1356177741?l=en-GB\n\n"
        "🤖 <b>Android</b>:\nhttps://play.google.com/store/apps/details?id=org.outline.android.client\n\n"
        "💻 <b>Mac OS</b>:\nhttps://itunes.apple.com/us/app/outline-app/id1356178125\n\n"
        "🪟 <b>Windows</b>:\nhttps://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe\n\n"
        "⚙️ <b>Linux</b>:\nhttps://s3.amazonaws.com/outline-releases/client/linux/stable/Outline-Client.AppImage",
        parse_mode="HTML"
    )


# Регистрация хендлеров
def register_tariff_handlers(app):
    app.add_handler(CallbackQueryHandler(show_tariffs, pattern=r"^tariff_plan$"))
    app.add_handler(CallbackQueryHandler(select_trial_tariff, pattern=r"^select_plan_trial$"))
    app.add_handler(CallbackQueryHandler(select_plan_monthly, pattern=r"^select_plan_monthly$"))
    app.add_handler(CallbackQueryHandler(select_plan_3months, pattern=r"^select_plan_3months$"))
    app.add_handler(CallbackQueryHandler(select_plan_6months, pattern=r"^select_plan_6months$"))
    app.add_handler(CallbackQueryHandler(select_plan_12months, pattern=r"^select_plan_12months$"))
    app.add_handler(CallbackQueryHandler(show_payment_placeholder, pattern=r"^pay_"))
    app.add_handler(CallbackQueryHandler(check_payment_and_send_key, pattern=r"^check_payment_"))
