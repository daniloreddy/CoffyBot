# utils/db_utils.py

import sqlite3
import datetime

from utils.config import DB_FILE

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()


def initialize_db():
    """
    Create the conversations table if it does not exist.
    Should be called once at startup.
    """
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user TEXT,
            user_id TEXT,
            channel TEXT,
            message TEXT,
            response TEXT
        )"""
    )
    conn.commit()


def log_to_sqlite(user_obj, channel_obj, message, response):
    """
    Insert a conversation entry into the SQLite database.

    Args:
        user_obj: The Discord user object.
        channel_obj: The Discord channel object (or DM).
        message (str): User message.
        response (str): Bot response.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """INSERT INTO conversations (timestamp, user, user_id, channel, message, response)
                      VALUES (?, ?, ?, ?, ?, ?)""",
        (
            timestamp,
            user_obj.name,
            str(user_obj.id),
            channel_obj.name if hasattr(channel_obj, "name") else "DM",
            message,
            response,
        ),
    )
    conn.commit()


def close_db():
    """
    Close the SQLite database connection.
    """
    conn.close()
