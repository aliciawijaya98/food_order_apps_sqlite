from database import Base, SessionLocal
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError

# Initialize Menu_database_table
class FoodMenu(Base):
    __tablename__ = "food_menu"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    item = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

def seed_initial_menu():
    session = SessionLocal()
    try:
        # Prevent duplicate seeding 
        if session.query(FoodMenu).count() > 0:
            return "Menu already seeded."

        initial_data = [
            ("Appetizers", "Spring Rolls", 30000),
            ("Appetizers", "Garlic Bread", 25000),
            ("Appetizers", "Chicken Wings", 40000),
            ("Main Courses", "Grilled Chicken with Rice", 65000),
            ("Main Courses", "Beef Steak", 120000),
            ("Main Courses", "Fried Rice", 45000),
            ("Drinks", "Mineral Water", 10000),
            ("Drinks", "Iced Tea", 15000),
            ("Drinks", "Coffee", 20000),
            ("Desserts", "Ice Cream", 20000),
            ("Desserts", "Chocolate Cake", 30000),
            ("Desserts", "Vanilla Panna Cotta", 40000)
        ]

        objects = [
            FoodMenu(category=c, item=i, price=p)
            for c, i, p in initial_data
        ]

        session.add_all(objects)
        session.commit()

        return "Initial menu inserted successfully."

    except IntegrityError:
        session.rollback()
        return "Data already exists."

    except Exception as e:
        session.rollback()
        return f"Error: {e}"

    finally:
        session.close()

# Get the menu table
def get_menu():
    session = SessionLocal()
    try:
        return session.query(FoodMenu).order_by(FoodMenu.category.asc(),
                                                FoodMenu.item.asc()).all()
    finally:
        session.close()

#Get 1 menu aja
def get_menu_by_id(menu_id):
    session = SessionLocal()
    try:
        return session.query(FoodMenu).filter(FoodMenu.id == menu_id).first()
    finally:
        session.close()
    
# Adding new item to the menu
def add_menu_item(new_item):
    
    if not all(k in new_item for k in ("category","item","price")):
        return False, "Invalid menu data."
    
    # Price validation
    if new_item["price"] <= 0:
        return False, "Price must be greater than 0."
        
    session = SessionLocal()
    try:
        item = FoodMenu(
            category=new_item["category"],
            item=new_item["item"],
            price=new_item["price"]
        )

        session.add(item)
        session.commit()

        return True, "Item added successfully"

    except IntegrityError:
        session.rollback()
        return "Data already exists."
    
    except Exception as e:
        session.rollback()
        return False, str(e)

    finally:
        session.close()

# Update menu item
def update_menu_item(menu_id, category, item, price):
    
    if price <= 0:
        return False, "Price must be greater than 0."

    session = SessionLocal()
    try:
        menu = session.query(FoodMenu).filter(FoodMenu.id == menu_id).first()

        if not menu:
            return False, "Menu item not found."

        menu.category = category
        menu.item = item
        menu.price = price

        session.commit()

        return True, "Item updated successfully"

    except Exception as e:
        session.rollback()
        return False, str(e)

    finally:
        session.close()


# Delete menu item
def delete_menu_item(menu_id):
    session = SessionLocal()

    try:
        menu = session.query(FoodMenu).filter(FoodMenu.id == menu_id).first()

        if not menu:
            return False, "Menu item not found."

        session.delete(menu)
        session.commit()

        return True, "Item deleted successfully."

    except Exception as e:
        session.rollback()
        return False, str(e)

    finally:
        session.close()