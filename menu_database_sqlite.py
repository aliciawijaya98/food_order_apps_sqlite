from database import get_connection
import sqlite3

# Initialize Menu_database_table
def init_db():
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Create the food_menu table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        item TEXT NOT NULL,
        price INTEGER NOT NULL CHECK (price >= 0),
        UNIQUE (category, item)
    )
    """)
    
    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM food_menu")
    count = cursor.fetchone()[0]

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
        cursor.executemany("""
        INSERT INTO food_menu (category, item, price)
        VALUES (?, ?, ?)
        """, food_menu) 

        # Commit the transaction and close the connection
        conn.commit()
    
    conn.close()

# Get the database
def get_menu():
    conn = get_connection()
    if not conn:
        return[]
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM food_menu")
    menus = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return menus

# Adding new item to the menu
def add_menu_item(new_item):
    if not all(k in new_item for k in ("category", "item", "price")):
        return False, "Invalid input data."
    
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."
    
    try: 
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO food_menu (category, item, price) 
            VALUES (?, ?, ?)
            """,
            (new_item["category"], new_item["item"], new_item["price"])
        )    
        conn.commit()
        return True,"Item added successfully"
    
    except sqlite3.IntegrityError:
        return False, "Menu already exists in this category."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()
        

# Update menu item
def update_menu_item(menu_id, category, item, price):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE food_menu
        SET category = ?, item = ?, price = ?
        WHERE id = ?
        """, (category, item, price, menu_id))

        if cursor.rowcount == 0:
            return False, "Menu item not found."
        
        conn.commit()
        return True, "Item updated successfully."
    
    except sqlite3.IntegrityError:
        return False, "Duplicate item in this category."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()
    


# Delete menu item
def delete_menu_item(menu_id):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM food_menu WHERE id = ?", (menu_id,))

        if cursor.rowcount == 0:
            return False, "Menu item not found."

        conn.commit()
        return True, "Item deleted successfully."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()