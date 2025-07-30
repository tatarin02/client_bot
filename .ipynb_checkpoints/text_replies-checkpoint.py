#Текст первого приветствия
text_1_greating = """
Привет👋, {user_first_name}!
Чем сегодня займемся?😉
"""
# Если отказ принять пользовательское соглашение:
if_otkaz_polz = "✋ Пожалуйста, сначала ознакомьтесь с соглашением об использовании!"



# Кнопки главного меню
button_check_payment = "🔵 Проверить оплату"
button_my_key = "🔵 Мой ключ"
button_my_stats = "🔵 Моя статистика"
button_tariff_plan = "📋 Тарифный план"
button_partnership = "🤝 Партнерство"
button_user_agreement = "📜 Соглашение об использовании"
button_support = "💎 Поддержка"

# Другие тексты (если нужны)
text_about = "Этот бот создан для демонстрации красивой структуры кода! 🚀"
text_settings = "Здесь будут настройки пользователя! ⚙️"

text_message_router_1 = "⚠️ неизвестное состояние — игнор"
text_message_router_2 = "Неизвестная команда. Используйте кнопки меню 👇"

key_expiry_notifier_1 = (
                    f"⚠️ <b>Внимание!</b>\n"
                    f"Ваш ключ на порту <b>{port}</b> истекает через 1 день (до {expires_dt.strftime('%d.%m.%Y %H:%M UTC')}).\n"
                    f"Продлите или выберите новый тариф."
                )

bot_1 = "^(📋 Тарифный план|📜 Соглашение об использовании|💎 Поддержка|🔵 Проверить оплату|🔵 Мои ключи|🔵 Моя статистика|🤝 Партнёрство)$"

main_menu_1 = "📜 Соглашение об использовании"
main_menu_2 = "💎 Поддержка"
main_menu_3 = "🤝 Партнёрство"
main_menu_4 = "📋 Тарифный план"
main_menu_5 = "🔵 Моя статистика"
main_menu_6 = "🔵 Мои ключи"

my_keys_1 = "❌ У тебя пока нет действующих ключей."
my_keys_2 = (
    """<b>📲 Как пользоваться Outline VPN:</b>
1. Скачайте и установите на устройство приложение Outline:
iOS: https://itunes.apple.com/app/outline-app/id1356177741
macOS: https://itunes.apple.com/app/outline-app/id1356178125
Windows: https://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe
Linux: https://s3.amazonaws.com/outline-releases/client/linux/stable/Outline-Client.AppImage
Android: https://play.google.com/store/apps/details?id=org.outline.android.client
Дополнительная ссылка для Android: https://s3.amazonaws.com/outline-releases/client/android/stable/Outline-Client.apk

2. Нажми «Добавить ключ» → «Вставить из буфера» или отсканируй QR-код.
3. Подключись к VPN одним нажатием.

⬇️ Твои ключи:"""
)
my_keys_3 = "🔙 В главное меню"
my_keys_4 = "⬆️ Выше — твои ключи.\nНажми кнопку ниже, чтобы вернуться в меню:"

my_stats_1 = "❌ У тебя пока нет созданных ключей."
my_stats_2 = "❌ У тебя есть ключи, но все они просрочены."
my_stats_3 = "🔙 В главное меню"
my_stats_4 = "⬆️ Выше — твоя статистика по ключам:"

partnership_1 = """🤝 Партнёрская программа:
Напишите нам на почту с темой "Партнер" и вашим сообщением, если хотите стать партнером.
Почта:
3avpn.project@gmail.com."""
partnership_2 = "✉️ Пожалуйста, отправьте сообщение для администратора (например, как вы хотите сотрудничать):"
partnership_3 = "Спасибо! Мы с вами свяжемся."
partnership_4 = "⬅️ В главное меню"

support_1 = """🆘 Служба поддержки:
Если у вас возникли вопросы или проблемы, напишите нам на почту с темой "Проблема".
Почта:
3avpn.project@gmail.com"""
support_2 = "⬅️ В главное меню"
support_3 = "✉️ Пожалуйста, опишите вашу проблему, и мы передадим её администратору:"
support_4 = "Пожалуйста, отправьте текстовое сообщение."
support_5 = "✅ Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время."
support_6 = "⬅️ В главное меню"

tariff_1 = {
    "monthly": {"days": 30, "price": "99₽"},
    "3months": {"days": 90, "price": "249₽"},
    "6months": {"days": 180, "price": "489₽"},
    "12months": {"days": 365, "price": "949₽"},
}
tariff_2 = (
        "<b>📦 Тарифные планы:</b>\n\n"
        "📜 <b>Пробный (3 дня)</b>\n• Бесплатно (1 раз)\n\n"
        "🗕️ <b>1 месяц</b>\n• <s>259₽</s> → <b>99₽</b>\n\n"
        "📦 <b>3 месяца</b>\n• <s>659₽</s> → <b>249₽</b>\n\n"
        "💼 <b>6 месяцев</b>\n• <s>989₽</s> → <b>489₽</b>\n\n"
        "🎯 <b>12 месяцев</b>\n• <s>1590₽</s> → <b>949₽</b>"
    )
tariff_3 = "🗓️ Выбрать другой период и оплатить"
tariff_4 = "🔑 Ключ после оплаты"
tariff_5 = "🔙 В главное меню"
tariff_6 = "❌ Ты уже использовал пробный доступ. Выбери другой тариф."
tariff_8 = "⚠️ Не удалось создать пробный ключ. Попробуй позже."
tariff_9 = "🔙 Нажми кнопку ниже, чтобы вернуться в меню:"
tariff_10 = "🔙 В главное меню"
tariff_11 = "📧 Введите email, указанный при оплате:"
tariff_12 = "❌ Платёж не найден."
tariff_13 = "🔙 В главное меню"
tariff_14 = "⚠️ Не удалось создать ключ."
tariff_15 = "🔙 Нажми кнопку ниже, чтобы вернуться в меню:"
tariff_16 = "🔙 В главное меню"
tariff_17 = "<b>Для установки приложения Outline перейдите по ссылкам:</b>\n\n"
tariff_18 = "📱 <b>iPhone</b>:\nhttps://apps.apple.com/ru/app/outline-app/id1356177741\n\n"
tariff_19 = "🧐 <b>Android</b>:\nhttps://play.google.com/store/apps/details?id=org.outline.android.client\n\n"
tariff_20 = "💻 <b>Mac OS</b>:\nhttps://itunes.apple.com/us/app/outline-app/id1356178125\n\n"
tariff_21 = "🪠 <b>Windows</b>:\nhttps://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe\n\n"
tariff_22 = "⚙️ <b>Linux</b>:\nhttps://s3.amazonaws.com/outline-releases/client/linux/stable/Outline-Client.AppImage"

user_agreement_1 = "✅ Ознакомиться"
user_agreement_2 = "💎 Поддержка"
user_agreement_3 = "❌ Отказаться"
user_agreement_4 = "⬅️ В главное меню"
user_agreement_5 = "✅ Спасибо за принятие соглашения!"
user_agreement_6 = "🏠 Добро пожаловать в главное меню!"
user_agreement_7 = "❌ Вы отказались от соглашения.\n\n"
user_agreement_8 = "Чтобы начать заново — введите /start."
user_agreement_9 = "🏠 Главное меню"

# Пользовательское соглашение
USER_AGREEMENT_TEXT = """
<b>Соглашение перед использованием</b>

Перед использованием ознакомьтесь со слудующими документами:

1) Положение об обработке персональных данных:
   http://3avpn.ru/personal_data

2) Договор оферты:
   http://3avpn.ru/offer_agreement

Нажимая "Ознакомиться", вы подтверждаете принятие условий.
"""[1:]
declaration_if_not_excepted = "✋ Для доступа к полному функционалу бота, пожалуйста, сначала ознакомьтесь с вышеперечисленными документами!"