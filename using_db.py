import sqlite3
import pandas as pd

DB_PATH = 'bot.db'

def show_tables_df(db_path=DB_PATH) -> dict:
    """Возвращает содержимое всех таблиц как словарь {table_name: DataFrame}."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    dataframes = {}
    for (table_name,) in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
        dataframes[table_name] = df

    conn.close()
    return dataframes


def print_all_dataframes(dataframes: dict):
    """Выводит все DataFrame из словаря на экран."""
    for table_name, df in dataframes.items():
        print(f"\n🗂 Таблица: {table_name}")
        if df.empty:
            print("Таблица пуста.")
        else:
            print(df)


def clean_tables(db_path=DB_PATH):
    """Очищает все пользовательские таблицы."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверим, существует ли sqlite_sequence
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='sqlite_sequence';
    """)
    has_sequence_table = cursor.fetchone() is not None

    # Получим список пользовательских таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        cursor.execute(f"DELETE FROM {table_name};")
        if has_sequence_table:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
        print(f"Таблица {table_name} очищена.")

    conn.commit()
    conn.close()
    print("✅ Очистка завершена.")

def get_outline_keys_by_user_id(user_id: int, db_path=DB_PATH) -> pd.DataFrame:
    """Возвращает все строки из outline_keys по заданному user_id."""
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM outline_keys WHERE user_id = ?"
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df


# Примеры использования:
# dataframes = show_tables_df()
# print_all_dataframes(dataframes)
# clean_tables()
