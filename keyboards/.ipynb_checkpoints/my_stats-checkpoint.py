from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from outline.outline_script import get_all_keys_with_connections, get_data_usage
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from text_replies import *

async def handle_my_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        await query.answer()
    except:
        pass

    keys = get_all_keys_with_connections()
    traffic = get_data_usage()

    # Фильтруем ключи по user_id
    user_keys = [k for k in keys if str(k.get("user_id")) == str(user_id)]

    if not user_keys:
        await query.message.reply_text(my_stats_1)
        return

    total_traffic_mb = 0
    active_keys = []

    for key in user_keys:
        created_at_str = key["created_at"]
        days_valid = key.get("days_valid", 30)

        # Парсим дату создания
        try:
            created_at = datetime.fromisoformat(created_at_str)
        except Exception:
            created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")

        expires_at = created_at + timedelta(days=days_valid)
        if expires_at < datetime.utcnow():
            continue  # Пропускаем просроченные

        key["created_dt"] = created_at
        key["expires_dt"] = expires_at
        active_keys.append(key)

    if not active_keys:
        await query.message.reply_text(my_stats_2)
        return

    for key in active_keys:
        port = key["port"]
        devices = key["devices"]
        traffic_bytes = traffic.get(port, 0)
        traffic_mb = traffic_bytes / (1024 * 1024)
        total_traffic_mb += traffic_mb

        caption = (
            f"🛡 <b>Порт:</b> {port}\n"
            f"📱 <b>Подключений:</b> {devices}\n"
            f"📊 <b>Трафик:</b> {traffic_mb:.2f} MB\n"
            f"🕒 <b>Создан:</b> {key['created_dt'].strftime('%d.%m.%Y %H:%M')}\n"
            f"⏳ <b>Действует до:</b> {key['expires_dt'].strftime('%d.%m.%Y %H:%M')}"
        )

        await query.message.reply_text(caption, parse_mode="HTML")

    # Итоговая статистика
    await query.message.reply_text(f"📦 <b>Суммарный трафик:</b> {total_traffic_mb:.2f} MB", parse_mode="HTML")

    # Кнопка возврата
    back_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(my_stats_3, callback_data="back_to_main")]
    ])
    await query.message.reply_text(my_stats_4, reply_markup=back_markup)


def get_my_stats_handler():
    return CallbackQueryHandler(handle_my_stats_callback, pattern="^my_stats$")
