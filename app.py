from flask import Flask, render_template, request, redirect
import sqlite3
import string
import random

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS urls
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        short_url TEXT NOT NULL)"""
    )
    conn.commit()
    conn.close()


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = "".join(random.choice(characters) for _ in range(6))
    return short_url


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form["url"]
        short_url = generate_short_url()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO urls (original_url, short_url) VALUES (?, ?)",
            (original_url, short_url),
        )
        conn.commit()
        conn.close()

        return render_template("shortened.html", short_url=short_url)

    return render_template("index.html")


@app.route("/<short_url>")
def redirect_to_url(short_url):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_url = ?", (short_url,))
    original_url = c.fetchone()

    if original_url:
        return redirect(original_url[0])
    else:
        return "URL not found", 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
