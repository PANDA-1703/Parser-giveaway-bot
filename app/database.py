import sqlite3
from contextlib import contextmanager

DB_NAME = "giveaways.db"


@contextmanager
def get_db_connection():
    """Контекстный менеджер для работы с базой данных."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Инициализация базы данных."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS giveaways (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_name TEXT,
            channel_link TEXT,
            date TEXT,
            time TEXT
        )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date_time ON giveaways (date, time)")
        conn.commit()


def add_giveaway(user_id, channel_name, channel_link, date, time):
    """Добавление розыгрыша в базу данных."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO giveaways (user_id, channel_name, channel_link, date, time)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, channel_name, channel_link, date, time))
        conn.commit()


def get_todays_giveaways(current_date, current_time):
    """Получение розыгрышей на сегодня."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT user_id, channel_name FROM giveaways
        WHERE date = ? AND (time = ? OR time = 'Не указано')
        """, (current_date, current_time))
        return cursor.fetchall()
