import sqlite3
import socket
import requests
from datetime import datetime, timedelta
from io import BytesIO
import subprocess
import re
import os
import pandas as pd

try:
    import qrcode
except ImportError:
    qrcode = None

# === Конфигурация ===
# API_URL = "https://193.187.174.24:22902/enA3_WAoRxhA5qdYe_KEsQ"
API_URL = "https://194.36.170.95:22902/enA3_WAoRxhA5qdYe_KEsQ/"



VERIFY_SSL = False
START_PORT = 30000
END_PORT = 40000
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "bot.db")
DB_PATH = os.path.abspath(DB_PATH)

def init_outline_keys_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS outline_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                port INTEGER UNIQUE,
                password TEXT,
                access_url TEXT,
                created_at TEXT,
                expires_at TEXT,
                max_devices INTEGER,
                valid INTEGER DEFAULT 1,
                notified INTEGER DEFAULT 0
            )
        """)
        # Попробовать добавить вручную, если таблица уже существует
        for column in ["valid", "notified"]:
            try:
                conn.execute(f"ALTER TABLE outline_keys ADD COLUMN {column} INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass


# === Обновление флагов valid ===
def update_valid_flags_in_db():
    import telegram
    from env import BOT_TOKEN
    bot = telegram.Bot(token=BOT_TOKEN)
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Получаем все просроченные ключи
        cursor.execute("SELECT port FROM outline_keys WHERE expires_at <= ? AND valid = 1", (now,))
        expired_ports = [row[0] for row in cursor.fetchall()]

        # Обновляем флаг valid в БД
        cursor.execute("""
            UPDATE outline_keys
            SET valid = 0
            WHERE expires_at <= ?
        """, (now,))
        cursor.execute("""
            UPDATE outline_keys
            SET valid = 1
            WHERE expires_at > ?
        """, (now,))
        conn.commit()

    # Уведомление за 1 день до истечения срока
    notify_time = (datetime.utcnow() + timedelta(days=1)).date().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, port, expires_at FROM outline_keys
            WHERE date(expires_at) = date(?) AND valid = 1 AND notified = 0
        """, (notify_time,))
        for user_id, port, expires_at in cursor.fetchall():
            try:
                bot.send_message(chat_id=user_id, text=f"⚠️ Ваш ключ на порту {port} истекает {expires_at[:16]} (UTC)")
                cursor.execute("UPDATE outline_keys SET notified = 1 WHERE port = ?", (port,))
            except Exception as e:
                print(f"[!] Ошибка при отправке уведомления пользователю {user_id}: {e}")

    # Удаляем просроченные ключи из API
    for port in expired_ports:
        delete_outline_key_by_port(port)

# === Проверка доступности порта ===
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0

# === Проверка: порт уже в базе ===
def port_exists_in_db(port):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM outline_keys WHERE port = ? AND valid = 1", (port,))
        return c.fetchone() is not None

# === Сохранение ключа в базу данных ===
def save_key_to_db(user_id, port, password, access_url, days_valid, max_devices):
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(days=days_valid)
    is_valid = int(expires_at > created_at)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO outline_keys (
                user_id, port, password, access_url,
                created_at, expires_at, max_devices, valid
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, port, password, access_url,
            created_at.isoformat(), expires_at.isoformat(), max_devices, is_valid
        ))

# === Создание ключа Outline ===
def create_outline_key(user_id, days_valid, max_devices):
    for port in range(START_PORT, END_PORT + 1):
        if is_port_available(port) and not port_exists_in_db(port):
            try:
                response = requests.post(
                    f"{API_URL}/access-keys",
                    json={"port": port},
                    verify=VERIFY_SSL,
                    timeout=5
                )
                if response.status_code == 201:
                    key = response.json()
                    save_key_to_db(user_id, key["port"], key["password"], key["accessUrl"], days_valid, max_devices)
                    return key
            except Exception as e:
                print(f"[!] Ошибка при создании ключа: {e}")
                return None
    return None

# === Генерация QR-кода как изображения ===
def generate_qr_image(url):
    if not qrcode:
        return None
    img = qrcode.make(url)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# === Получение информации о порте ===
def get_unique_clients(port: str):
    try:
        output = subprocess.check_output(["ss", "-ntu"], text=True)
        pattern = re.compile(rf'\[?::ffff:(\d+\.\d+\.\d+\.\d+)\]?:(\d+)\s+.*:{port}')
        connections = pattern.findall(output)
        unique_sessions = set(connections)
        client_summary = {}
        for ip, _ in unique_sessions:
            client_summary.setdefault(ip, 0)
            client_summary[ip] += 1
        return client_summary
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды: {e}")
        return {}

# === Получение уникальных IP по каждому порту ===
def get_unique_ips_by_port(ports_set):
    try:
        ports_set = set(map(str, ports_set))
        dict_port = {}
        for port in ports_set:
            ips = len(get_unique_clients(port))
            dict_port[port] = ips
        return dict_port
    except Exception as e:
        print(f"[!] Ошибка: {e}")
        return {}

# === Вывод только действующих ключей (с подключениями) ===
def get_all_keys_with_connections():
    update_valid_flags_in_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, port, password, access_url, created_at, expires_at, valid FROM outline_keys WHERE valid = 1 ORDER BY id")
    rows = c.fetchall()
    conn.close()
    ports = set(int(row[1]) for row in rows)
    active_conns = get_unique_ips_by_port(ports)
    result = []
    for row in rows:
        user_id = row[0]
        port = int(row[1])
        devices = active_conns.get(str(port), 0)
        result.append({
            "user_id": user_id,
            "port": port,
            "devices": devices,
            "password": row[2],
            "access_url": row[3],
            "created_at": row[4],
            "expires_at": row[5],
            "valid": bool(row[6])
        })
    return result

# === Удаление ключа по порту из API и БД ===
def delete_outline_key_by_port(port):
    try:
        response = requests.get(f"{API_URL}/access-keys", verify=VERIFY_SSL)
        if response.status_code == 200:
            for key in response.json().get("accessKeys", []):
                if key["port"] == port:
                    key_id = key["id"]
                    delete_url = f"{API_URL}/access-keys/{key_id}"
                    delete_response = requests.delete(delete_url, verify=VERIFY_SSL)
                    if delete_response.status_code == 204:
                        with sqlite3.connect(DB_PATH) as conn:
                            conn.execute("UPDATE outline_keys SET valid = 0 WHERE port = ?", (port,))
                            conn.commit()
                        return True
        print(f"❌ Ключ с портом {port} не найден в API")
    except Exception as e:
        print(f"[!] Ошибка при удалении ключа: {e}")
    return False

# === Получение трафика по ключам ===
def get_data_usage():
    try:
        response = requests.get(f"{API_URL}/metrics/transfer", verify=VERIFY_SSL)
        if response.status_code == 200:
            usage = response.json().get("bytesTransferredByUserId", {})
            return {int(k): v for k, v in usage.items()}
        print("❌ Не удалось получить данные о трафике")
    except Exception as e:
        print(f"[!] Ошибка при получении трафика: {e}")
    return {}

def get_outline_keys_by_user_id(user_id: int, db_path=DB_PATH) -> pd.DataFrame:
    """Возвращает все строки из outline_keys по заданному user_id."""
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM outline_keys WHERE user_id = ?"
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def get_existing_valid_key_by_user_id_and_plan(user_id: int, plan_key: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT access_url, expires_at
        FROM outline_keys
        WHERE user_id = ?
          AND plan_key = ?
          AND expires_at > ?
        ORDER BY expires_at DESC
        LIMIT 1
    """, (user_id, plan_key, now))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {"access_url": row[0], "expires_at": row[1]}
    else:
        return None