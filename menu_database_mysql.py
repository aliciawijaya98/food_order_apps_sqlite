from database import get_connection
from mysql.connector import Error

# Initialize Menu_database_table
def init_db():
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Create the food_menu table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_menu (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category VARCHAR(50) NOT NULL,
        item VARCHAR(200) NOT NULL,
        price INT UNSIGNED NOT NULL,
        CONSTRAINT unique_category_item UNIQUE  (category, item)
    )
    ''')
    
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
        cursor.executemany('''
        INSERT INTO food_menu (category, item, price)
        VALUES (%s, %s, %s)
        ''', food_menu) 

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
    menus = cursor.fetchall()
    conn.close()
    return menus

# Adding new item to the menu
def add_menu_item(new_item):
    if "category" in new_item and "item" in new_item and "price" in new_item:
        conn = get_connection()
        if not conn:
            return False, "Database connection failed."
        
        try: 
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO food_menu (category, item, price) 
                VALUES (%s, %s, %s)
                """,
                (new_item["category"], new_item["item"], new_item["price"])
            )    
            conn.commit()
            return True,"Item added successfully"
        
        except Error as e:
            if e.errno == 1062:
                 return False, "Menu already exists in this category."
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
        SET category = %s, item = %s, price = %s 
        WHERE id = %s
        """,
        (category, item, price, menu_id)
        )
        conn.commit()
        return True, "Item updated successfully."
    
    except Error as e:
        if e.errno == 1062:
            return False, "Duplicate item in this category."
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
        cursor.execute("DELETE FROM food_menu WHERE id = %s", (menu_id,))
        conn.commit()
        return True, "Item deleted successfully."
    except Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()