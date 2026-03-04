from sqlalchemy import create_engine

db_user = "root"
db_pass = "admin"
db_host = "127.0.0.1"
db_port = 3306
db_name = "restaurant"
        
Database_URL = (
    f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)
                
# engine untuk database restaurant
engine_db = create_engine(
    Database_URL,
    pool_pre_ping=True
)