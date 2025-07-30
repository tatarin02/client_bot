from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from datetime import datetime, timedelta
from db import (
    has_used_trial,
    mark_trial_used,
    save_choice,
    save_mock_payment,
    get_and_mark_payment_by_email
)
from outline.outline_script import create_outline_key, generate_qr_image

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from text_replies import *

TARIFFS = tariff_1

async def show_tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    try:
        await query.answer()
    except:
        pass

    text = tariff_2

    buttons = []
    if not has_used_trial(user_id):
        buttons.append([InlineKeyboardButton("✅ Выбрать 📜 Пробный период", callback_data="select_plan_trial")])

    buttons += [
        [InlineKeyboardButton(tariff_3, url="http://3avpn.ru/#rec1109268861")],
        [InlineKeyboardButton(tariff_4, callback_data="check_payment_request_email")],
        [InlineKeyboardButton(tariff_5, callback_data="back_to_main")]
    ]

    await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def select_trial_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        await query.answer()
    except:
        pass

    if has_used_trial(user_id):
        await query.message.reply_text(tariff_6)
        return

    save_choice(user_id, "trial")
    mark_trial_used(user_id)

    key = create_outline_key(user_id=user_id, days_valid=3, max_devices=3)
    if not key:
        await query.message.reply_text(tariff_8)
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
    await query.message.reply_text(tariff_9,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(tariff_10, callback_data="back_to_main")]]))

async def request_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(tariff_11)
    context.user_data["awaiting_email"] = True

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_email"):
        return

    email = update.message.text.strip().lower()
    context.user_data["awaiting_email"] = False

    payment = get_and_mark_payment_by_email(email)
    if not payment:
        await update.message.reply_text(
            tariff_12,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(tariff_13, callback_data="back_to_main")]]
            )
        )
        return

    plan_key = payment['plan_key']
    days = TARIFFS.get(plan_key, {}).get("days", 30)
    key = create_outline_key(user_id=update.effective_user.id, days_valid=days, max_devices=3)

    if not key:
        await update.message.reply_text(tariff_14)
        return

    qr_path = generate_qr_image(key["accessUrl"])
    expires_at = (datetime.utcnow() + timedelta(days=days)).strftime('%d.%m.%Y %H:%M')
    caption = (
        f"<b>✅ Оплата подтверждена!</b>\n"
        f"<b>🔗 Ссылка:</b> {key['accessUrl']}\n"
        f"<b>⏳ Действует до:</b> {expires_at}"
    )

    if qr_path:
        await update.message.reply_photo(photo=InputFile(qr_path), caption=caption, parse_mode="HTML")
    else:
        await update.message.reply_text(caption, parse_mode="HTML")

    await send_app_links(update)
    await update.message.reply_text(tariff_15,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(tariff_16, callback_data="back_to_main")]]))

async def send_app_links(update: Update):
    if update.message:
        send = update.message.reply_text
    elif update.callback_query:
        send = update.callback_query.message.reply_text
    else:
        return

    await send(
        tariff_17
        tariff_18
        tariff_19
        tariff_20
        tariff_21
        tariff_22,
        parse_mode="HTML"
    )

def register_tariff_handlers(app):
    app.add_handler(CallbackQueryHandler(show_tariffs, pattern=r"^tariff_plan$"))
    app.add_handler(CallbackQueryHandler(select_trial_tariff, pattern=r"^select_plan_trial$"))
    app.add_handler(CallbackQueryHandler(request_email, pattern=r"^check_payment_request_email$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email))
