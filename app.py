import os

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Secret Key
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "starico-secret-key"
)


# Database configuration
# Vercel filesystem is read-only, so SQLite must use /tmp there.
if os.environ.get("VERCEL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/starico.db"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Initialize database
db = SQLAlchemy(app)


# =========================
# User Model
# =========================

class User(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        nullable=False,
        unique=True
    )

    email = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


# =========================
# Home
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# Login
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.password == password:

            session["user_id"] = user.id
            session["username"] = user.username

            return redirect("/dashboard")

        else:
            return "ایمیل یا رمز عبور اشتباه است"

    return render_template("login.html")


# =========================
# Register
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email already exists
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "این ایمیل قبلاً ثبت شده است"

        # Check if username already exists
        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:
            return "این نام کاربری قبلاً استفاده شده است"

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return "حسابت ساخته شد ✨"

    return render_template("register.html")


# =========================
# Products
# =========================

@app.route("/products")
def products():
    return render_template("products.html")


# =========================
# Dashboard
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "user/dashboard.html",
        username=session["username"]
    )


# =========================
# Logout
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# Create Database
# =========================

with app.app_context():
    db.create_all()


# =========================
# Run App Locally
# =========================

if __name__ == "__main__":
    app.run(
        debug=True
    )