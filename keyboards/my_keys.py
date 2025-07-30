from telegram import (
    Update,
    InputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler
)
from datetime import datetime
import sys
import os

# Добавляем путь к outline/ для импорта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outline')))

from outline_script import generate_qr_image, get_outline_keys_by_user_id

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from text_replies import *


async def handle_my_key_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        await query.answer()
    except Exception as e:
        print(f"⚠️ Ошибка при query.answer(): {e}")

    df = get_outline_keys_by_user_id(user_id)

    # Фильтрация по дате истечения (оставляем только действующие ключи)
    now = datetime.utcnow()
    df["expires_at"] = df["expires_at"].apply(lambda x: datetime.fromisoformat(x))
    df = df[df["expires_at"] > now]

    if df.empty:
        await query.message.reply_text(my_keys_1)
        return

    instruction = my_keys_2

    await query.message.reply_text(instruction, parse_mode="HTML", disable_web_page_preview=True)

    for _, row in df.iterrows():
        link = row["access_url"]
        max_devices = row["max_devices"]
        expires_at = row["expires_at"].strftime('%d.%m.%Y %H:%M')

        qr_path = generate_qr_image(link)

        caption = (
            f"<b>🔗 Ссылка:</b> {link}\n"
            f"<b>⏳ Действует до:</b> {expires_at}"
        )

        if qr_path:
            await query.message.reply_photo(photo=InputFile(qr_path), caption=caption, parse_mode="HTML")
        else:
            await query.message.reply_text(caption, parse_mode="HTML")

    back_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(my_keys_3, callback_data="back_to_main")]
    ])

    await query.message.reply_text(
        my_keys_4,
        reply_markup=back_markup
    )


def get_my_key_handler():
    return CallbackQueryHandler(handle_my_key_callback, pattern="^my_keys$")
