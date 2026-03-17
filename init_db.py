from database import engine, Base
import menu_database_sqlite
import user_database_sqlite
import order_database_sqlite

from menu_database_sqlite import seed_initial_menu

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    seed_initial_menu()