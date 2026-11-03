"""SQL Injection – Authentication Bypass demo (Flask, port 5001)."""
from flask import Flask, request, render_template, redirect, url_for, session, flash, g
from functools import wraps
import sqlite3, os

app = Flask(__name__)
app.secret_key = "sqli-auth-bypass-demo-key"

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ---------------------------------------------------------------------------
# Auth decorator
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

# ---- VULNERABLE login ----
@app.route("/login", methods=["GET", "POST"])
def login():
    query_executed = None
    user_row = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        db = get_db()
        # ⚠️  VULNERABLE: f-string concatenation — allows SQL injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        query_executed = query

        try:
            user = db.execute(query).fetchone()
        except Exception as e:
            flash(f"SQL Error: {e}", "danger")
            return render_template("login.html", query_executed=query_executed, user_row=None)

        if user:
            user_row = {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
            }
            session["user"] = user_row
            flash(f"Logged in as {user['username']} ({user['role']})", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html", query_executed=query_executed, user_row=user_row)

# ---- SECURE login ----
@app.route("/login-secure", methods=["GET", "POST"])
def login_secure():
    query_executed = None
    query_params = None
    user_row = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        db = get_db()
        # ✅ SECURE: parameterised query — immune to SQL injection
        query_executed = "SELECT * FROM users WHERE username = ? AND password = ?"
        query_params = (username, password)
        user = db.execute(query_executed, query_params).fetchone()

        if user:
            user_row = {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
            }
            session["user"] = user_row
            flash(f"Logged in as {user['username']} ({user['role']})", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login_secure.html",
                           query_executed=query_executed,
                           query_params=query_params,
                           user_row=user_row)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))

# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        from init_db import init
        init()
    app.run(debug=True, port=5001)
