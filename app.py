from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import Base, engine
from user_database_sqlite import (
    register_user,
    login_user,
    get_user_by_userid,
    update_user,
    delete_user,
    get_all_users
)
from menu_database_sqlite import(
    get_menu,
    add_menu_item,
    update_menu_item,
    delete_menu_item,
    get_menu_by_id,
)

from order_database_sqlite import (
    create_order,
    add_order_item,
    get_order_detail,
    get_daily_sales,
    pay_order,
    find_order_id,
    delete_order_item
)

app = Flask(__name__)
app.secret_key = "dsdjsbjrerfnsakaleek"

# CREATE TABLES
Base.metadata.create_all(bind=engine)

# VALIDATION
def validate_email(email):
    if email.count("@") != 1:
        return False

    user, domain_full = email.split("@")
    if not user or "." not in domain_full:
        return False
    if not user[0].isalnum():
        return False

    for char in user:
        if not (char.isalnum() or char in "._"):
            return False

    hosting, extension = domain_full.rsplit(".",1)
    if not hosting.isalnum():
        return False
    if not extension.isalpha() or len(extension) > 5:
        return False

    return True

def validate_userid(uid):
    uid = uid.strip()
    if len(uid) < 6 or len(uid) > 20:
        return False

    has_letter = has_digit = False
    for char in uid:
        if not (char.isalnum() or char in "._"):
            return False
        if char.isalpha():
            has_letter = True
        if char.isdigit():
            has_digit = True

    return has_letter and has_digit

def validate_password(pw):
    if len(pw) < 8:
        return False

    special = "/.,@#$%"
    up = low = digit = spec = False

    for char in pw:
        if char.isupper():
            up = True
        if char.islower():
            low = True
        if char.isdigit():
            digit = True
        if char in special:
            spec = True

    return up and low and digit and spec

#Dashboard
@app.route("/")
def index():
    if"user_id" not in session:
        return redirect(url_for("login"))
    
    user = get_user_by_userid(session["user_id"])
    
    return render_template("index.html", user=user)  


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form

        if not validate_userid(form["user_id"]):
            flash("Invalid User ID format")
            return render_template("register.html")

        if not validate_password(form["password"]):
            flash("Invalid password format")
            return render_template("register.html")

        if not validate_email(form["email"]):
            flash("Invalid email format")
            return render_template("register.html")

        data = {
            "user_id": form["user_id"],
            "password": form["password"],
            "email": form["email"],
            "name": form["name"],
            "gender": form["gender"],
            "age": form["age"],
            "job": form["job"],
            "hobby": [h.strip() for h in form["hobby"].split(",")],
            "city": form["city"],
            "rt": form["rt"],
            "rw": form["rw"],
            "zip": form["zip"],
            "latitude": float(form["latitude"]),
            "longitude": float(form["longitude"]),
            "phone": form["phone"]
        }

        success, message = register_user(data)
        flash(message)

        if success:
            return redirect(url_for("login"))

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]

        success, result = login_user(user_id, password)

        if success:
            session["user_id"] = user_id
            flash("Login successful.")
            return redirect(url_for("index"))
        else:
            flash(result)

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for("login"))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        updated_data = {
            "name": request.form["name"],
            "email": request.form["email"],
            "job": request.form["job"],
            "hobby": ",".join([h.strip() for h in request.form["hobby"].split(",")]),
            "phone": request.form["phone"],
            "city": request.form["city"],
            "rt": request.form["rt"],
            "rw": request.form["rw"],
            "zip": request.form["zip"],
            "latitude": request.form["latitude"],
            "longitude": request.form["longitude"]
        }

        success, message = update_user(user_id, updated_data)
        flash(message)

    user = get_user_by_userid(user_id)
    return render_template("profile.html", user=user)

# EDIT PROFILE
@app.route("/edit_profile", methods=["GET","POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = get_user_by_userid(user_id)

    msg = None
    if request.method == "POST":
        hobby_input = request.form.get("hobby", "")
        updated_data = {
            "name": request.form.get("name", user.get("name", "")),
            "email": request.form.get("email", user.get("email", "")),
            "job": request.form.get("job", user.get("job", "")),
            "hobby": ",".join([h.strip() for h in hobby_input.split(",")]),
            "phone": request.form.get("phone", user.get("phone", "")),
            "city": request.form.get("city", user.get("city", "")),
            "rt": request.form.get("rt", user.get("rt", "")),
            "rw": request.form.get("rw", user.get("rw", "")),
            "zip": request.form.get("zip", user.get("zip", "")),
            "latitude": request.form.get("latitude", user.get("latitude", "")),
            "longitude": request.form.get("longitude", user.get("longitude", ""))
        }

        success, message = update_user(user_id, updated_data)
        msg = message
        user = get_user_by_userid(user_id)  # refresh data
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=user, msg=msg)

# DELETE ACCOUNT
@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    msg = None
    if request.method == "POST":
        # baru hapus user ketika klik tombol Yes
        success, message = delete_user(session["user_id"])
        session.clear()
        msg = message
        return render_template("delete_account.html", msg=msg)

    return render_template("delete_account.html")

# VIEW MENU
@app.route("/menu")
def menu():
    
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    menus = get_menu()
    
    return render_template("menu.html",menus=menus)

# ADD MENU
@app.route("/menu/add", methods = ["GET","POST"])
def add_menu():
    
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
    
        new_item = {
            "category": request.form["category"],
            "item": request.form["item"],
            "price": int(request.form["price"])
        }
    
        success, message = add_menu_item(new_item)
    
        flash(message)
    
        if success:
            return redirect(url_for("menu"))
    
    return render_template("add_menu.html")

# EDIT MENU
@app.route("/menu/edit/<int:menu_id>", methods=["GET","POST"])
def edit_menu(menu_id):
    
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        
        category = request.form["category"]
        item = request.form["item"]
        price = int(request.form["price"])
        
        success, message = update_menu_item(menu_id, category, item, price)

        flash(message)
        
        if success:
            return redirect(url_for("menu"))

    menu = get_menu_by_id(menu_id)
    
    return render_template("edit_menu.html", menu=menu)

# DELETE MENU
@app.route("/menu/delete/<int:menu_id>")
def delete_menu(menu_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    success, message = delete_menu_item(menu_id)

    flash(message)

    return redirect(url_for("menu"))

# ORDER DASHBOARD
@app.route("/orders", methods=["GET","POST"])
def orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    sales = get_daily_sales()
    
    if request.method == "POST":
        
        keyword = request.form.get("keyword", "").strip()

        order_id = find_order_id(keyword)

        if order_id:
            return redirect(url_for("order_detail", order_id=order_id))

        # kalau tidak ketemu
        flash("Order not found")

    return render_template("orders.html", sales=sales)

# CREATE ORDER
@app.route("/orders/create", methods=["GET","POST"])
def create_order_page():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        order_type = request.form["order_type"]
        reference_number = request.form["reference_number"]

        order_id, invoice = create_order(
            session["user_id"],
            order_type,
            reference_number
        )

        if order_id:
            return redirect(url_for("order_detail", order_id=order_id, editable=1))

        flash(invoice)

    return render_template("create_order.html")

# ORDER DETAIL
@app.route("/orders/<int:order_id>")
def order_detail(order_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    order_data = get_order_detail(order_id)

    if order_data is None:
        flash("Order not found")
        return redirect(url_for("orders"))

    menus = get_menu()

    editable = request.args.get("editable", default=1, type=int)
    editable = bool(editable)

    return render_template(
        "order_detail.html",
        order=order_data["order"],
        items=order_data["items"],
        menus=menus,
        editable=editable
    )

# ADD ITEM TO ORDER
@app.route("/orders/<int:order_id>/add", methods=["POST"])
def add_item(order_id):
    
    if "user_id" not in session:
        return redirect(url_for("login"))

    menu_id = int(request.form["menu_id"])
    quantity = int(request.form["quantity"])
    price = float(request.form["price"])

    success, message = add_order_item(order_id, menu_id, quantity, price)

    flash(message)

    return redirect(url_for("order_detail", order_id=order_id))

# PAY ORDER
@app.route("/orders/pay/<int:order_id>", methods=["POST"])
def pay_order_route(order_id):

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    success, message = pay_order(order_id)

    flash(message)

    return redirect(url_for("order_detail", order_id=order_id)) 

# DELETE ITEM ON ORDER
@app.route("/orders/<int:order_id>/delete_item/<int:item_id>")
def delete_order_item_route(order_id, item_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    success, message = delete_order_item(order_id, item_id)

    flash(message)

    return redirect(url_for("order_detail", order_id=order_id))


# RUN
if __name__ == "__main__":
    app.run(debug=True)