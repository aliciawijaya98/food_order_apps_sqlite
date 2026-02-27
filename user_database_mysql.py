from database import get_connection
from mysql.connector import Error
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
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(20) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        gender ENUM('male','female') NOT NULL,
        age INT NOT NULL,
        job VARCHAR(100),
        hobby TEXT,
        city VARCHAR(100),
        rt VARCHAR(5),
        rw VARCHAR(5),
        zip VARCHAR(5),
        latitude VARCHAR(20),
        longitude VARCHAR(20),
        phone VARCHAR(15)
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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

    except Error as e:
        if e.errno == 1062:
            return False, "UserID or Email already exists."
        return False, f"Database error: {e}"

    finally:
        conn.close()

# LOGIN USER
def login_user(user_id, password):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return False, "User not registered."

        if user["password"] != hash_password(password):
            return False, "Wrong password."

        return True, user

    finally:
        conn.close()


# GET USER BY USER_ID
def get_user_by_userid(user_id):
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user



# UPDATE USER

def update_user(user_id, updated_data):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE users
        SET name=%s, email=%s, job=%s, phone=%s,
            city=%s, rt=%s, rw=%s, zip=%s,
            latitude=%s, longitude=%s
        WHERE user_id=%s
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

    except Error as e:
        if e.errno == 1062:
            return False, "Email already in use."
        return False, f"Database error: {e}"

    finally:
        conn.close()



# DELETE USER

def delete_user(user_id):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return False, "User not found."

        return True, "Account deleted successfully."

    finally:
        conn.close()
        
#VIEW USER ALL

def get_all_users():
    conn = get_connection()
    if not conn:
        return[]
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name FROM users")
    users = cursor.fetchall()
    conn.close()
    return users