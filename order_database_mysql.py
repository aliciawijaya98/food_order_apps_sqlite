from database import get_connection
from mysql.connector import Error
from datetime import datetime

def init_order_tables():
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    
    #ORDERS TABLE (HEADER)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INT AUTO_INCREMENT PRIMARY KEY,
        invoice_code VARCHAR (30) UNIQUE NOT NULL,
        user_id VARCHAR(20) NOT NULL,
        order_type ENUM ('Dine-in', 'Takeaway') NOT NULL,
        reference_number INT NOT NULL,
        total_price DECIMAL(12,2) DEFAULT 0,
        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status ENUM ('pending', 'paid','cancelled') DEFAULT 'pending',
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON DELETE CASCADE
    )               
    """)
    
    #ORDER ITEM (DETAIL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items(
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        menu_id INT NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(12,2) NOT NULL,
        subtotal DECIMAL (10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id)
            ON DELETE CASCADE,
        FOREIGN KEY (menu_id) REFERENCES food_menu(id)
    )
    """)
    
    conn.commit()
    conn.close()

#Generate Daily Invoice
def generate_daily_invoice():
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE DATE (order_date) = CURDATE()               
    """)
    
    count_today = cursor.fetchone()[0] + 1
    
    today_str = datetime.now().strftime("%Y%m%d")
    invoice_code = f"{today_str}-{count_today:03d}"
    
    conn.close()
    return invoice_code

#CREATE ORDER (HEADER)
def create_order(user_id, order_type, reference_number):
    conn = get_connection()
    if not conn:
        return None, "Database connection failed."
    
    try:
        cursor = conn.cursor()
        
        invoice_code = generate_daily_invoice()
        
        if order_type not in ["Dine-in", "Takeaway"]:
            return None, "Invalid order type."
        
        cursor.execute("""
            INSERT INTO orders
            (invoice_code, user_id, order_type, reference_number)
            VALUES (%s, %s, %s, %s)                              
        """, (invoice_code, user_id, order_type, reference_number))
        
        conn.commit()
        
        order_id = cursor.lastrowid
        return order_id, invoice_code
    
    except Error as e:
        return None, f"Database error: {e}"
    
    finally:
        conn.close()
        
#ADD ORDER ITEM (DETAIL)
def add_order_item(order_id, menu_id, quantity, price):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed."
    
    try:
        cursor = conn.cursor()
        
        subtotal = quantity * price
        
        cursor.execute("""
            INSERT INTO order_items
            (order_id, menu_id, quantity, price, subtotal)
            VALUES (%s, %s, %s, %s, %s)               
        """, (order_id, menu_id, quantity, price, subtotal))
        
        conn.commit()
        update_order_total(order_id)
        return True, "Item added."
    
    except Error as e:
        return False, f"Database error: {e}"
    
    finally:
        conn.close()
        
#UPDATE TOTAL PRICE
def update_order_total(order_id):
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(subtotal)
        FROM order_items
        WHERE order_id = %s
    """, (order_id,))
    
    total = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        UPDATE orders
        SET total_price = %s
        WHERE id = %s                
    """, (total, order_id))
    
    conn.commit()
    conn.close()
    
    return True

#GET ORDER DETAIL
def get_order_detail(order_id):
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM orders
        WHERE id = %s
    """, (order_id,))
    order = cursor.fetchone()
    
    cursor.execute("""
        SELECT oi.quantity, oi.price, oi.subtotal, m.item
        FROM order_items oi
        JOIN food_menu m ON oi.menu_id = m.id
        WHERE oi.order_id = %s
    """, (order_id,))
    items = cursor.fetchall()
    
    conn.close()
    
    return{
        "order": order,
        "items": items
    }
    
#DAILY SALES REPORT
def get_daily_sales():
    conn = get_connection()
    
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*), SUM(total_price)
        FROM orders
        WHERE DATE(order_date) = CURDATE()
        AND status != 'cancelled'               
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    return{
        "total_orders": result[0] or 0,
        "total_revenue": result [1] or 0
    }