# keyboards/main_menu.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db import is_agreement_accepted, user_has_any_keys


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from text_replies import *

def get_main_menu(user_choice, user_id):
    agreed = is_agreement_accepted(user_id)

    if not agreed:
        keyboard = [
            [InlineKeyboardButton(main_menu_1, callback_data="user_agreement")],
            [InlineKeyboardButton(main_menu_2, callback_data="support")]
        ]
        return InlineKeyboardMarkup(keyboard)

    if not user_has_any_keys(user_id):
        keyboard = [
            [InlineKeyboardButton(main_menu_4, callback_data="tariff_plan")],
            [InlineKeyboardButton(main_menu_3, callback_data="partnership")],
            [InlineKeyboardButton(main_menu_1, callback_data="user_agreement")],
            [InlineKeyboardButton(main_menu_2, callback_data="support")]
        ]
    else:
        keyboard = [
     #      [InlineKeyboardButton("🔵 Проверить оплату", callback_data="check_payment")],
            [InlineKeyboardButton(main_menu_6, callback_data="my_keys")],
            [InlineKeyboardButton(main_menu_5, callback_data="my_stats")],
            [InlineKeyboardButton(main_menu_4, callback_data="tariff_plan")],
            [InlineKeyboardButton(main_menu_3, callback_data="partnership")],
            [InlineKeyboardButton(main_menu_1, callback_data="user_agreement")],
            [InlineKeyboardButton(main_menu_2, callback_data="support")]
        ]

    return InlineKeyboardMarkup(keyboard)

