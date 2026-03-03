from user_database_sqlite import init_users_table
from menu_database_sqlite import init_food_menu_table
from order_database_sqlite import init_order_tables

def init_all_tables():
    print("Initializing database...")

    init_users_table()
    print("Users Table Ready")

    init_food_menu_table()
    print("Menu Table Ready")

    init_order_tables()
    print("Order Table Ready")

    print("All tables initialized successfully.")

if __name__ == "__main__":
    init_all_tables()