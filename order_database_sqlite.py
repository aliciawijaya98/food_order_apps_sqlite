from database import engine
from sqlalchemy import text
from datetime import datetime

def init_order_tables():
    with engine.begin() as conn:
        
    #ORDERS TABLE (HEADER)
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS orders(
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoice_code VARCHAR (30) UNIQUE NOT NULL,
            user_id VARCHAR(20) NOT NULL,
            order_type ENUM ('Dine-in', 'Takeaway') NOT NULL,
            reference_number INT NULL,
            total_price DECIMAL(12,2) DEFAULT 0,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status ENUM ('pending', 'paid','cancelled') DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
                ON DELETE CASCADE
        )               
        """))
    
        #ORDER ITEM (DETAIL)
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS order_items(
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            menu_id INT NOT NULL,
            quantity INT NOT NULL,
            price DECIMAL(12,2) NOT NULL,
            subtotal DECIMAL (12,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
                ON DELETE CASCADE,
            FOREIGN KEY (menu_id) REFERENCES food_menu(id)
        )
        """))

#Generate Daily Invoice
def generate_daily_invoice():
    
    with engine.connect() as conn:
            
        count = conn.execute(text("""
            SELECT COUNT(*)
            FROM orders
            WHERE DATE (order_date) = CURDATE()               
        """)).scalar()
    
        count_today = count + 1
        today_str = datetime.now().strftime("%Y%m%d")
    
        invoice_code = f"{today_str}-{count_today:03d}"
    
        return invoice_code

#CREATE ORDER (HEADER)
def create_order(user_id, order_type, reference_number):
    if order_type not in ["Dine-in", "Takeaway"]:
        return None, "Invalid order type."
    
    try:
        
        with engine.begin() as conn:
            
            result = conn.execute(
                text("""
                INSERT INTO orders (invoice_code, user_id, order_type, reference_number)
                VALUES ('TEMP',:user_id,:order_type,:reference_number)
                """),
                {
                    "user_id": user_id,
                    "order_type": order_type,
                    "reference_number": reference_number
                }
            )
            
            order_id = result.lastrowid

            today_str = datetime.now().strftime("%Y%m%d")
            invoice_code = f"{today_str}-{order_id:04d}"

            conn.execute(
                text("""
                UPDATE orders
                SET invoice_code=:invoice
                WHERE id=:id
                """), 
                {"invoice":invoice_code,"id":order_id}    
            )

        return order_id, invoice_code

    except Exception as e:
        return None, f"Database error: {e}"
    
#ADD ORDER ITEM (DETAIL)
def add_order_item(order_id, menu_id, quantity, price):
    
    try:
        with engine.begin() as conn:
        
            subtotal = quantity * price
        
            conn.execute(
                text("""
                INSERT INTO order_items
                (order_id, menu_id, quantity, price, subtotal)
                VALUES (:order_id,:menu_id,:quantity,:price,:subtotal)
                """),
                { 
                    "order_id":order_id, 
                    "menu_id":menu_id, 
                    "quantity":quantity, 
                    "price":price, 
                    "subtotal":subtotal
                }    
            )
        
            # update total in SAME transaction
            total = conn.execute(
                text("""
                SELECT SUM(subtotal)
                FROM order_items
                WHERE order_id=:order_id
                """), 
                {"order_id":order_id}
            ).scalar()
    
            conn.execute(
            text("""
                UPDATE orders
                SET total_price=:total_price
                WHERE id=:id
                """),
                {"total_price":total or 0,"id":order_id}
            )
    
        return True, "Item added."
    
    except Exception as e:
        return False, f"Database error: {e}"
    
   
        
#GET ORDER DETAIL
def get_order_detail(order_id):

    with engine.connect() as conn:
        order = conn.execute(
            text("""
            SELECT * FROM orders
            WHERE id=:id
            """), 
            {"id":order_id}
        ).mappings().first()
    
        items = conn.execute(
            text("""
            SELECT oi.quantity, oi.price, oi.subtotal, m.item
            FROM order_items oi
            JOIN food_menu m ON oi.menu_id=m.id
            WHERE oi.order_id=:id
            """), 
            {"id":order_id}
        ).mappings().all()
    
    return {
        "order":order,
        "items":items
    }

#DAILY SALES REPORT
def get_daily_sales():
    
    with engine.connect() as conn:
    
        result = conn.execute(
            text("""
            SELECT COUNT(*) as total_orders, 
                SUM(total_price) as total_revenue
            FROM orders
            WHERE DATE(order_date) = CURDATE()
            AND status != 'cancelled'               
            """)
        ).mappings().first()

    return{
        "total_orders": result["total_orders"] or 0,
        "total_revenue": result ["total_revenue"] or 0
    }

#Check Active table biar gak double
def check_active_table(table_number):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
            SELECT id 
            FROM orders
            WHERE reference_number=:table
            AND order_type='Dine-in'
            AND status='pending'
            LIMIT 1
            """), 
            {"table":table_number}
        ).first()
    
    return result [0] if result else None

#Payment System
def pay_order(order_id):
    
    try:
    
        with engine.begin() as conn:
        
            result = conn.execute(
                text("""
                UPDATE orders
                SET STATUS = 'paid'
                WHERE id=:id 
                AND STATUS = 'pending'
                """), 
                {"id":order_id}
            )
        
            if result.rowcount == 0:
                return False, "Order cannot be paid"
        
        
        return True, "Payment successful. Order closed."
    
    except Exception as e:
        return False, f"Database error: {e}"
      
#Find order
def find_order_id(keyword):
    
    with engine.connect() as conn:

        # Cek invoice_code dulu
        result = conn.execute(
            text("""
            SELECT id FROM orders
            WHERE invoice_code=:code
            """), 
            {"code":keyword}
        ).first()
        
        # Kalau tidak ketemu dan input angka → cek sebagai table number
        if not result and keyword.isdigit():
        
            result = conn.execute(
            text("""
                SELECT id FROM orders
                WHERE reference_number=:table
                AND status = 'pending'
                """), 
                {"table":int(keyword)}
            ).first()
        
    return result[0] if result else None