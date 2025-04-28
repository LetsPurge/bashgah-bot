# db.py

import sqlite3
from datetime import datetime
from config import CHAT_ID

DB_NAME = "bot_database.db"

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        day TEXT,
        status TEXT,
        lottery TEXT,
        note TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    # اگر بار اول اجرا شد، روزهای هفته رو مقداردهی کن
    days = ["شنبه", "یک‌شنبه", "دو‌شنبه", "سه‌شنبه", "چهار‌شنبه", "پنج‌شنبه", "جمعه"]
    for day in days:
        cursor.execute('''
        INSERT OR IGNORE INTO records (chat_id, day, status, lottery, note)
        VALUES (?, ?, ?, ?, ?)
        ''', (CHAT_ID, day, "گزارش نشده😯", "", ""))

    conn.commit()
    conn.close()

def update_record(day, field, value):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE records
    SET {field} = ?
    WHERE chat_id = ? AND day = ?
    ''', (value, CHAT_ID, day))
    conn.commit()
    conn.close()

def get_all_records():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM records
    WHERE chat_id = ?
    ''', (CHAT_ID,))
    records = cursor.fetchall()
    conn.close()
    return records
