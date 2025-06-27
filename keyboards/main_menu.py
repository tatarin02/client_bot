# keyboards/main_menu.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db import is_agreement_accepted, user_has_any_keys

def get_main_menu(user_choice, user_id):
    agreed = is_agreement_accepted(user_id)

    if not agreed:
        keyboard = [
            [InlineKeyboardButton("📜 Соглашение об использовании", callback_data="user_agreement")],
            [InlineKeyboardButton("💎 Поддержка", callback_data="support")]
        ]
        return InlineKeyboardMarkup(keyboard)

    if not user_has_any_keys(user_id):
        keyboard = [
            [InlineKeyboardButton("📋 Тарифный план", callback_data="tariff_plan")],
            [InlineKeyboardButton("🤝 Партнёрство", callback_data="partnership")],
            [InlineKeyboardButton("📜 Соглашение об использовании", callback_data="user_agreement")],
            [InlineKeyboardButton("💎 Поддержка", callback_data="support")]
        ]
    else:
        keyboard = [
     #      [InlineKeyboardButton("🔵 Проверить оплату", callback_data="check_payment")],
            [InlineKeyboardButton("🔵 Мои ключи", callback_data="my_keys")],
            [InlineKeyboardButton("🔵 Моя статистика", callback_data="my_stats")],
            [InlineKeyboardButton("📋 Тарифный план", callback_data="tariff_plan")],
            [InlineKeyboardButton("🤝 Партнёрство", callback_data="partnership")],
            [InlineKeyboardButton("📜 Соглашение об использовании", callback_data="user_agreement")],
            [InlineKeyboardButton("💎 Поддержка", callback_data="support")]
        ]

    return InlineKeyboardMarkup(keyboard)

