from database import engine
from sqlalchemy import text

# Initialize Menu_database_table
def init_menu_table():
    with engine.begin() as conn: 
    
        # Create the food_menu table if it doesn't exist
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS food_menu (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            item VARCHAR(200) NOT NULL,
            price INT UNSIGNED NOT NULL,
            CONSTRAINT unique_category_item UNIQUE  (category, item)
        )
        '''))
    
        # Check if table is empty
        result = conn.execute(text("SELECT COUNT(*) FROM food_menu"))
        count = result.scalar()

        # Define initial menu data
        if count == 0:
            food_menu = [
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

            # Insert the menu data into the table
            conn.execute(
                text('''
                INSERT INTO food_menu (category, item, price)
                VALUES (:category, :item, :price)
                '''),
                [{"category": c, "item": i, "price": p} for c, i, p in food_menu] 
            ) 

# Get the database
def get_menu():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM food_menu")) 
        return result.mappings().all()
    

# Adding new item to the menu
def add_menu_item(new_item):
    
    if not all(k in new_item for k in ("category","item","price")):
        return False, "Invalid menu data."
        
    try: 
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO food_menu (category, item, price) 
                    VALUES (:category, :item, :price)
                """),
                {
                    "category": new_item["category"],
                    "item": new_item["item"],
                    "price": new_item["price"]
                } 
            )    
                
        return True,"Item added successfully"
        
    except Exception as e:
        if "Duplicate" in str(e):
            return False, "Menu already exists in this category."
        return False, f"Database error: {e}"

# Update menu item
def update_menu_item(menu_id, category, item, price):

    try:     
        with engine.begin() as conn:
            
            conn.execute(
            text("""
                UPDATE food_menu 
                SET category = :category, 
                    item = :item, 
                    price = :price 
                WHERE id = :id
            """),
            {
                "category": category, 
                "item": item, 
                "price": price, 
                "id": menu_id
            }
        )

        return True,"Item updated successfully"
        
    except Exception as e:
        if "Duplicate" in str(e):
            return False, "Duplicate item in this category."
        return False, f"Database error: {e}"


# Delete menu item
def delete_menu_item(menu_id):

    try:
        with engine.begin() as conn:
        
            conn.execute(
                text("DELETE FROM food_menu WHERE id = :id"),
                {"id": menu_id}
            )    
            
            return True, "Item deleted successfully."
    
    except Exception as e:
        return False, f"Database error: {e}"