from sqlalchemy import create_engine

Database_URL = "sqlite:///db/restaurant.db"
                
# engine untuk database restaurant
engine = create_engine(
    Database_URL,
    echo=True, 
    future=True,
    connect_args={"check_same_thread": False}
)

# Init all tables
def init_all_tables():
    from user_database_sqlite import init_users_table
    from menu_database_sqlite import init_menu_table
    from order_database_sqlite import init_order_tables

    print("Initializing database...")
    
    init_users_table()
    init_menu_table()
    init_order_tables()
    
    print("All tables created successfully!")

if __name__ == "__main__":
    init_all_tables()