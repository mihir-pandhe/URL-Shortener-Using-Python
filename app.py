from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, URL
import string
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret"
db.init_app(app)


def generate_short_url():
    return "".join(random.choices(string.ascii_letters + string.digits, k=6))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form["url"]
        custom_short_url = request.form["custom_short_url"]

        if custom_short_url:
            short_url = custom_short_url
        else:
            short_url = generate_short_url()

        if URL.query.filter_by(short_url=short_url).first():
            flash("Short URL already exists! Try another one.")
            return redirect(url_for("index"))

        new_url = URL(
            original_url=original_url,
            short_url=short_url,
            user_id=session.get("user_id"),
        )
        db.session.add(new_url)
        db.session.commit()

        return render_template("shortened.html", short_url=short_url)

    return render_template("index.html")


@app.route("/<short_url>")
def redirect_to_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    url.clicks += 1
    db.session.commit()
    return redirect(url.original_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists! Try another one.")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Login successful!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    urls = URL.query.filter_by(user_id=user_id).all()
    return render_template("dashboard.html", urls=urls)


if __name__ == "__main__":
    app.run(debug=True)
