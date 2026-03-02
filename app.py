from flask import Flask, render_template, request, redirect, url_for, session, flash
from user_database_sqlite import (
    init_users_table,
    register_user,
    login_user,
    get_user_by_userid,
    update_user,
    delete_user,
    get_all_users
)

app = Flask(__name__)
app.secret_key = "dsdjsbjrerfnsakaleek"

# USER DATABASE
init_users_table()

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

    hosting, extension = domain_full.split(".")
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

# MAIN MENU
@app.route("/")
def index():
    if "user_id" in session:
        user = get_user_by_userid(session["user_id"])
        return render_template("index.html", user=user)
    return redirect(url_for("login"))

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
            "hobby": form.getlist("hobby"),
            "city": form["city"],
            "rt": form["rt"],
            "rw": form["rw"],
            "zip": form["zip"],
            "latitude": form["latitude"],
            "longitude": form["longitude"],
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
            flash("Login successful")
            return redirect(url_for("index"))
        else:
            flash(result)

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user_id", None)
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

# DELETE ACCOUNT
@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    success, message = delete_user(session["user_id"])
    session.clear()
    flash(message)
    return redirect(url_for("register"))

# ADMIN VIEW
@app.route("/users")
def users():
    all_users = get_all_users()
    return render_template("users.html", users=all_users)

# RUN
if __name__ == "__main__":
    app.run(debug=True)