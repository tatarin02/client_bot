import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'bot.db'

# === Инициализация базы данных ===
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            agreement_accepted INTEGER DEFAULT 0,
            choice TEXT,
            trial_used INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if "trial_used" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN trial_used INTEGER DEFAULT 0")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_key TEXT,
            paid_at TEXT,
            used INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

# === Сохраняем или обновляем выбор пользователя ===
def save_choice(user_id, choice):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, choice)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET choice=excluded.choice
    ''', (user_id, choice))
    conn.commit()
    conn.close()

# === Получаем последний выбор пользователя ===
def get_choice(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT choice FROM users WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# === Проверяем, принял ли пользователь соглашение ===
def is_agreement_accepted(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT agreement_accepted FROM users WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

# === Сохраняем факт принятия соглашения ===
def accept_agreement(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, agreement_accepted)
        VALUES (?, 1)
        ON CONFLICT(user_id) DO UPDATE SET agreement_accepted=1
    ''', (user_id,))
    conn.commit()
    conn.close()

# === Отмечаем, что пользователь использовал пробный период ===
def mark_trial_used(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET trial_used = 1
        WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()

# === Проверяем, использовал ли пользователь пробный период ===
def has_used_trial(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT trial_used FROM users WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

# === Проверка: есть ли у пользователя ключи ===
def user_has_any_keys(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM outline_keys WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] > 0

# === Сохраняем "оплату" (заглушка) ===
def save_mock_payment(user_id, plan_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (user_id, plan_key, paid_at, used)
        VALUES (?, ?, ?, 0)
    ''', (user_id, plan_key, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

import sqlite3

import sqlite3

def get_and_mark_payment_by_email(email):
    """
    Находит неиспользованную оплату по email, определяет план по amount,
    помечает запись как использованную и возвращает plan_key.
    """
    conn = sqlite3.connect("/root/cloudpayments-server/payments.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, amount FROM emails
        WHERE email = ? AND used = 0
        LIMIT 1
    """, (email,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    entry_id, amount = row

    # Очистка значения amount (например, '11.00' → '11')
    amount_clean = str(amount).strip()
    if '.' in amount_clean:
        amount_clean = amount_clean.rstrip('0').rstrip('.')

    amount_to_plan = {
        "10": "monthly",
        "11": "3months",
        "12": "6months",
        "13": "12months"
    }

    plan_key = amount_to_plan.get(amount_clean)
    if not plan_key:
        conn.close()
        return None

    # Помечаем запись как использованную
    cursor.execute("UPDATE emails SET used = 1 WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

    return {"plan_key": plan_key}