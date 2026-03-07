import sqlite3
from datetime import datetime

DB_NAME = 'steps_tracker.db'

#Create Table
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS steps_tracker 
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        step_taken INTEGER, 
        weight REAL,
        date TEXT
        )
        """
    )
    conn.commit()
    conn.close()

create_table()


