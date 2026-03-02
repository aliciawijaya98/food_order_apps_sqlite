from database import get_connection
import sqlite3
import hashlib

# PASSWORD HASHING
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# INIT USERS TABLE
def init_users_table():
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,        
        user_id TEXT NOT NULL UNIQUE,              
        password TEXT NOT NULL,                   
        email TEXT NOT NULL UNIQUE,                  
        name TEXT NOT NULL,                         
        gender TEXT CHECK(gender IN ('male','female')) NOT NULL, 
        age INTEGER NOT NULL,                        
        job TEXT,
        hobby TEXT,
        city TEXT,
        rt TEXT,
        rw TEXT,
        zip TEXT,
        latitude TEXT,
        longitude TEXT,
        phone TEXT
    )
    """)

    conn.commit()
    conn.close()

# REGISTER USER
def register_user(data):
    required_fields = [
    "user_id", "password", "email", "name",
    "gender", "age", "job", "hobby",
    "city", "rt", "rw", "zip",
    "latitude", "longitude", "phone"
]

    if not all(field in data for field in required_fields):
        return False, "Incomplete registration data."
    
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users 
        (user_id, password, email, name, gender, age, job, hobby, 
         city, rt, rw, zip, latitude, longitude, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["user_id"],
            hash_password(data["password"]),
            data["email"],
            data["name"],
            data["gender"],
            data["age"],
            data["job"],
            ",".join(data["hobby"]),
            data["city"],
            data["rt"],
            data["rw"],
            data["zip"],
            data["latitude"],
            data["longitude"],
            data["phone"]
        ))

        conn.commit()
        return True, "Registration successful."

    except sqlite3.IntegrityError:
        return False, "UserID or Email already exists."

    finally:
        conn.close()

# LOGIN USER
def login_user(user_id, password):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "User not registered."

    if user["password"] != hash_password(password):
        return False, "Wrong password."

    return True, dict(user)


# GET USER BY USER_ID
def get_user_by_userid(user_id):
    conn = get_connection()
    if not conn:
        return None

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None



# UPDATE USER
def update_user(user_id, updated_data):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE users
        SET name=?, email=?, job=?, phone=?,
            city=?, rt=?, rw=?, zip=?,
            latitude=?, longitude=?
        WHERE user_id=?
        """,
        (
            updated_data["name"],
            updated_data["email"],
            updated_data["job"],
            updated_data["phone"],
            updated_data["city"],
            updated_data["rt"],
            updated_data["rw"],
            updated_data["zip"],
            updated_data["latitude"],
            updated_data["longitude"],
            user_id
        ))

        conn.commit()

        if cursor.rowcount == 0:
            return False, "User not found."

        return True, "Profile updated successfully."

    finally:
        conn.close()



# DELETE USER
def delete_user(user_id):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()

    if cursor.rowcount == 0:
        return False, "User not found."
        
    conn.close()
    return True, "Account deleted successfully."

#VIEW USER ALL
def get_all_users():
    conn = get_connection()
    if not conn:
        return[]
    
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return [dict(u) for u in users]