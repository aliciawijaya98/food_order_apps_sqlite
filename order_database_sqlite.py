from database import Base, SessionLocal
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from datetime import date, datetime
from menu_database_sqlite import FoodMenu

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    invoice_code = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    order_type = Column(String, nullable=False)
    reference_number = Column(Integer)
    total_price = Column(Float, default=0)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")

    items = relationship("OrderItem", back_populates="order", cascade="all, delete")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    menu_id = Column(Integer, ForeignKey("food_menu.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
            
# CREATE ORDER (HEADER)
def create_order(user_id, order_type, reference_number):
    if order_type not in ["Dine-in", "Takeaway"]:
        return None, "Invalid order type."
    
    if order_type == "Dine-in":
        if reference_number is None:
            return None, "Table number is required for Dine-in."
        active_order = check_active_table(reference_number)
        if active_order:
            return None, f"Table {reference_number} already has an active order."
    
    session = SessionLocal()

    try:
        new_order = Order(
            invoice_code="TEMP",
            user_id=user_id,
            order_type=order_type,
            reference_number=reference_number
        )

        session.add(new_order)
        session.flush()

        today_str = datetime.now().strftime("%Y%m%d")
        new_order.invoice_code = f"{today_str}-{new_order.id:04d}"

        session.commit()

        return new_order.id, new_order.invoice_code

    except Exception as e:
        session.rollback()
        return None, str(e)

    finally:
        session.close()
    
#ADD ORDER ITEM (DETAIL)
def add_order_item(order_id, menu_id, quantity, price):

    if quantity <= 0:
        return False, "Quantity must be greater than 0."

    session = SessionLocal()

    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False, "Order not found."

        if order.status != "pending":
            return False, "Cannot add item. Order already closed."

        menu = session.query(FoodMenu).filter(FoodMenu.id == menu_id).first()
        if not menu:
            return False, "Menu not found."

        subtotal = quantity * menu.price

        new_item = OrderItem(
            order_id=order_id,
            menu_id=menu_id,
            quantity=quantity,
            price=menu.price,
            subtotal=subtotal
        )

        session.add(new_item)
        order.total_price += subtotal

        session.commit()

        return True, "Item added."

    except Exception as e:
        session.rollback()
        return False, str(e)

    finally:
        session.close()
    
# GET ORDER DETAIL
def get_order_detail(order_id):
    session = SessionLocal()

    try:
        order = session.query(Order).filter(Order.id == order_id).first()

        if not order:
            return None

        items = []
        for item in order.items:  # <-- relationship magic
            items.append({
                "id": item.id,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": item.subtotal,
                "menu_name": item.menu.item if item.menu else None
            })

        order_data = {
            "id": order.id,
            "invoice_code": order.invoice_code,
            "total_price": order.total_price,
            "status": order.status
        }

        return {
            "order": order_data,
            "items": items
        }

    finally:
        session.close()

#DAILY SALES REPORT
def get_daily_sales():
    session = SessionLocal()

    try:
        result = session.query(
            func.count(Order.id),
            func.sum(Order.total_price)
        ).filter(
            func.date(Order.order_date) == date.today(),
            Order.status != "cancelled"
        ).first()

        return {
            "total_orders": result[0] or 0,
            "total_revenue": result[1] or 0
        }

    finally:
        session.close()

#Check Active table biar gak double
def check_active_table(table_number):
    session = SessionLocal()

    try:
        order = session.query(Order).filter(
            Order.reference_number == table_number,
            Order.order_type == "Dine-in",
            Order.status == "pending"
        ).first()

        return order.id if order else None

    finally:
        session.close()

#Payment System
def pay_order(order_id):
    session = SessionLocal()

    try:
        order = session.query(Order).filter(Order.id == order_id).first()

        if not order or order.status != "pending":
            return False, "Order cannot be paid"

        order.status = "paid"
        session.commit()

        return True, "Payment successful. Order closed."

    except Exception as e:
        session.rollback()
        return False, str(e)

    finally:
        session.close()

#Find order
def find_order_id(keyword):
    session = SessionLocal()

    try:
        order = session.query(Order).filter(
            Order.invoice_code == keyword
        ).first()

        if not order and keyword.isdigit():
            order = session.query(Order).filter(
                Order.reference_number == int(keyword)
            ).first()

        return order.id if order else None

    finally:
        session.close()