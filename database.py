import sqlite3
import os

db_name = "restaurant.db"
base_dir = os.path.dirname(os.path.dirname(__file__), "restaurant.db")
db_path = os.path.join(base_dir, db_name)

def get_connection():
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        conn.commit()

        return conn
    
    except sqlite3.Error as e:
        print("[DB ERROR]", e)
        return None