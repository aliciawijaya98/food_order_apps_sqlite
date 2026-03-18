from database import Base, SessionLocal
from sqlalchemy import Column, Integer, String
import hashlib

# PASSWORD HASHING
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# INIT USERS TABLE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    job = Column(String)
    hobby = Column(String)
    city = Column(String)
    rt = Column(String)
    rw = Column(String)
    zip = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    phone = Column(String)

# REGISTER USER
def register_user(data):
    session = SessionLocal()

    try:
        new_user = User(
            user_id=data["user_id"],
            password=hash_password(data["password"]),
            email=data["email"],
            name=data["name"],
            gender=data["gender"],
            age=data["age"],
            job=data["job"],
            hobby=",".join(data["hobby"]) if isinstance(data["hobby"], list) else data["hobby"],
            city=data["city"],
            rt=data["rt"],
            rw=data["rw"],
            zip=data["zip"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            phone=data["phone"]
        )

        session.add(new_user)
        session.commit()

        return True, "Registration successful."

    except Exception as e:
        session.rollback()
        if "UNIQUE constraint" in str(e):
            return False, "UserID or Email already exists."
        return False, f"Database error: {e}"

    finally:
        session.close()

# LOGIN USER
def login_user(user_id, password):
    session = SessionLocal()

    user = session.query(User).filter(User.user_id == user_id).first()

    session.close()

    if not user:
        return False, "User not registered."

    if user.password != hash_password(password):
        return False, "Wrong password."

    user_dict = user.__dict__.copy()
    user_dict.pop("_sa_instance_state", None)
    user_dict.pop("password", None)

    return True, user_dict

# GET USER BY USER_ID
def get_user_by_userid(user_id):
    session = SessionLocal()

    user = session.query(User).filter(User.user_id == user_id).first()

    session.close()

    if not user:
        return None

    user_dict = user.__dict__.copy()
    user_dict.pop("_sa_instance_state", None)
    user_dict.pop("password", None)

    return user_dict

# UPDATE USER

def update_user(user_id, updated_data):
    session = SessionLocal()

    user = session.query(User).filter(User.user_id == user_id).first()

    if not user:
        session.close()
        return False, "User not found."

    try:
        for key, value in updated_data.items():
            if hasattr(user, key):
                if key == "password":
                    value = hash_password(value)
                setattr(user, key, value)

        session.commit()
        return True, "Profile updated successfully."

    except Exception as e:
        session.rollback()
        return False, f"Database error: {e}"

    finally:
        session.close()


# DELETE USER

def delete_user(user_id):
    session = SessionLocal()

    user = session.query(User).filter(User.user_id == user_id).first()

    if not user:
        session.close()
        return False, "User not found."

    session.delete(user)
    session.commit()
    session.close()

    return True, "Account deleted successfully."
        
#VIEW USER ALL

def get_all_users():
    session = SessionLocal()

    users = session.query(User.user_id, User.name).all()

    session.close()

    return users