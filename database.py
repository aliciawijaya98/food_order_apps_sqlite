from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Mastiin folder db ada
os.makedirs("db", exist_ok=True)

DATABASE_URL = "sqlite:///db/restaurant.db"
                
# engine untuk database restaurant
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()