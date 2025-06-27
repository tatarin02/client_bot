import sqlite3
from datetime import datetime, timedelta
import requests
from env import BOT_TOKEN


# Конфигурация
DB_PATH = "bot.db"
BOT_TOKEN = BOT_TOKEN

# Отправка уведомления в Telegram
def send_telegram_message(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    )

# Проверка ключей и уведомление пользователей
def notify_expiring_keys():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        tomorrow = datetime.utcnow() + timedelta(days=1)
        cursor.execute("SELECT user_id, port, expires_at FROM outline_keys")
        keys = cursor.fetchall()
        
        for user_id, port, expires_at in keys:
            expires_dt = datetime.fromisoformat(expires_at)
            if 0 <= (expires_dt - datetime.utcnow()).total_seconds() <= 86400:
                message = (
                    f"⚠️ <b>Внимание!</b>\n"
                    f"Ваш ключ на порту <b>{port}</b> истекает через 1 день (до {expires_dt.strftime('%d.%m.%Y %H:%M UTC')}).\n"
                    f"Продлите или выберите новый тариф."
                )
                send_telegram_message(user_id, message)

if __name__ == "__main__":
    notify_expiring_keys()