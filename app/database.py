import logging
import sqlite3
from contextlib import contextmanager


DB_NAME = "giveaways.db"


@contextmanager
def get_db_connection():
    """Контекстный менеджер для работы с базой данных."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Инициализация базы данных."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
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
        except sqlite3.Error as e:
            logging.error(f"Ошибка инициализации базы данных: {e}")
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
    """
    Получение розыгрышей на сегодня и прошедшие.
    :param current_date: Текущая дата в формате "YYYY-MM-DD".
    :param current_time: Текущее время в формате "HH:MM".
    :return: Список кортежей с данными о розыгрышах.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, user_id, channel_name, channel_link 
        FROM giveaways
        WHERE (date < ?) OR (date = ? AND (time <= ? OR time = 'Не указано'))
        """, (current_date, current_date, current_time))
        return cursor.fetchall()


def delete_sendler_giveaways(giveaway_id):
    """
    Удаление отправленной записи о розыгрыше из базы данных.
    :param giveaway_id: ID записи для удаления.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            logging.info(f"Попытка удаления записи с ID {giveaway_id}")
            cursor.execute("""
            DELETE FROM giveaways
            WHERE id = ?
            """, (giveaway_id,))
            deleted_count = cursor.rowcount
            logging.info(f"Удалено записей: {deleted_count}")
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при удалении записи с ID {giveaway_id}: {e}")
