import sqlite3
import os
import datetime

DB_FILE = "chatty.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS conversazioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user TEXT,
    user_id TEXT,
    channel TEXT,
    message TEXT,
    response TEXT
)''')
conn.commit()

def log_to_sqlite(user_obj, channel_obj, message, response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO conversazioni (timestamp, user, user_id, channel, message, response)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (timestamp, user_obj.name, str(user_obj.id),
                    channel_obj.name if hasattr(channel_obj, 'name') else "DM",
                    message, response))
    conn.commit()
