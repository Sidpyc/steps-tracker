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

    print("Table Created", DB_NAME)


def log_steps(user_id,steps_taken,weight):
    conn = sqlite3.connect(DB_NAME)
    cursor= conn.cursor()
    date_today = datetime.today().strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO steps_tracker  (user_id,step_taken,weight, date) VALUES (?,?,?,?)", (user_id,steps_taken,weight, date_today))
    conn.commit()
    conn.close()


def get_steps_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor= conn.cursor()
    cursor.execute("SELECT step_taken,weight date FROM steps_tracker WHERE user_id = ? ", (user_id,))
    records = cursor.fetchall()
    conn.commit()
    conn.close()

    return records


   

create_table()