import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",  #IP lebih stabil
            user="root",
            password="admin",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS restaurant")
        conn.database = "restaurant"
        return conn

    except Error as e:
        print("[DB ERROR]", e)
        return None