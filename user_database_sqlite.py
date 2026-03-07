from database import engine
from sqlalchemy import text
import hashlib

# PASSWORD HASHING
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# INIT USERS TABLE
def init_users_table():
    
    with engine.begin() as conn:

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,          
            password TEXT NOT NULL,  
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
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
        """))

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
    
    try:
        if int(data["age"]) <= 0:
            return False, "Invalid age."
    except ValueError:
        return False, "Age must be a number."
    
    try:
        
        with engine.begin() as conn:

            conn.execute(
            text("""
            INSERT INTO users
            (user_id,password,email,name,gender,age,job,hobby,
            city,rt,rw,zip,latitude,longitude,phone)
            VALUES
            (:user_id,:password,:email,:name,:gender,:age,:job,:hobby,
             :city,:rt,:rw,:zip,:latitude,:longitude,:phone)
            """),
            {
                "user_id": data["user_id"],
                "password": hash_password(data["password"]),
                "email": data["email"],
                "name": data["name"],
                "gender": data["gender"],
                "age": data["age"],
                "job": data["job"],
                "hobby": ",".join(data["hobby"]) if isinstance(data["hobby"], list) else data["hobby"],
                "city": data["city"],
                "rt": data["rt"],
                "rw": data["rw"],
                "zip": data["zip"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "phone": data["phone"]
            }
        )
            
        return True, "Registration successful."

    except Exception as e:
        if "UNIQUE constraint" in str(e):
            return False, "UserID or Email already exists."
        return False, f"Database error: {e}"

# LOGIN USER
def login_user(user_id, password):
    
    with engine.connect() as conn:
        
        user = conn.execute(
            text("""
            SELECT * 
            FROM users 
            WHERE user_id=:user_id 
            """),
            {"user_id":user_id}
        ).mappings().first()

    if not user:
        return False, "User not registered."

    if user["password"] != hash_password(password):
        return False, "Wrong password."

    user_dict = dict(user)
    user_dict.pop("password", None)

    return True, user_dict

# GET USER BY USER_ID
def get_user_by_userid(user_id):
   
    with engine.connect() as conn:
        
        user = conn.execute(
            text("""
            SELECT * FROM users 
            WHERE user_id=:user_id
            """), 
            {"user_id":user_id}
        ).mappings().first()
        
    if user:
        user = dict(user)
        user.pop("password", None)

    return user

# UPDATE USER

def update_user(user_id, updated_data):

    try:
        
        with engine.begin() as conn:

            result = conn.execute(
                text("""
                UPDATE users
                SET name=:name,
                    email=:email,
                    job=:job,
                    phone=:phone,
                    city=:city,
                    rt=:rt,
                    rw=:rw,
                    zip=:zip,
                    latitude=:latitude,
                    longitude=:longitude
                WHERE user_id=:user_id
                """),
                {
                    "name":updated_data["name"],
                    "email":updated_data["email"],
                    "job":updated_data["job"],
                    "phone":updated_data["phone"],
                    "city":updated_data["city"],
                    "rt":updated_data["rt"],
                    "rw":updated_data["rw"],
                    "zip":updated_data["zip"],
                    "latitude":updated_data["latitude"],
                    "longitude":updated_data["longitude"],
                    "user_id":user_id
                }
            )

        if result.rowcount == 0:
            return False, "User not found."

        return True, "Profile updated successfully."

    except Exception as e:
        if "UNIQUE constraint" in str(e):
            return False, "Email already in use."
        return False, f"Database error: {e}"


# DELETE USER

def delete_user(user_id):
    
    try:
        
        with engine.begin() as conn:
            
            result = conn.execute(
                text("""
                DELETE FROM users 
                WHERE user_id=:user_id
                """), 
                {"user_id":user_id}
            )
       

        if result.rowcount == 0:
            return False, "User not found."

        return True, "Account deleted successfully."

    except Exception as e:
        return False,f"Database error: {e}"
        
#VIEW USER ALL

def get_all_users():
    
    with engine.connect() as conn:
    
        users = conn.execute(
        text("""
            SELECT user_id, name 
            FROM users
            """)
        ).mappings().all()
        
    return users