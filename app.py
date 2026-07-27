from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "starico-secret-key"
)

# Database configuration
if os.environ.get("VERCEL"):
    # Vercel filesystem is read-only.
    # Temporary SQLite database for deployment testing.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/starico.db"
else:
    # Local development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:

            session["user_id"] = user.id
            session["username"] = user.username

            return redirect("/dashboard")

        else:
            return "ایمیل یا رمز عبور اشتباه است"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return "حسابت ساخته شد ✨"

    return render_template("register.html")


@app.route("/products")
def products():
    return render_template("products.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "user/dashboard.html",
        username=session["username"]
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# Create database tables when running locally
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)