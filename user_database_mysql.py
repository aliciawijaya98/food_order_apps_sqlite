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
                "hobby": ",".join(data["hobby"]),
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
        if "Duplicate" in str(e):
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

    return True, user

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
        if "Duplicate" in str(e):
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