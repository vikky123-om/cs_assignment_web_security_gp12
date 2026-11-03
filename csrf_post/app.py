"""CSRF – POST-based Forged Action demo (Flask, port 5005)."""
from flask import (
    Flask, request, session, redirect, url_for,
    render_template, flash, abort, g
)
import sqlite3, os, secrets
from functools import wraps

app = Flask(__name__)
app.secret_key = "csrf-post-demo-secret-key"

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
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ---------------------------------------------------------------------------
# CSRF token helper
# ---------------------------------------------------------------------------

def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

app.jinja_env.globals["csrf_token"] = generate_csrf_token

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("index"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))

# ---- VULNERABLE profile endpoint (no CSRF token check) -------------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_vuln():
    db = get_db()
    if request.method == "POST":
        new_email = request.form.get("email", "")
        db.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, session["user"]))
        db.commit()
        flash(f"Email updated to {new_email}", "success")
        return redirect(url_for("profile_vuln"))
    user = db.execute("SELECT * FROM users WHERE username = ?", (session["user"],)).fetchone()
    return render_template("profile.html", user=user)

# ---- SECURE profile endpoint (validates CSRF token) ----------------------

@app.route("/profile-secure", methods=["GET", "POST"])
@login_required
def profile_secure():
    db = get_db()
    if request.method == "POST":
        token = request.form.get("_csrf_token", "")
        if not token or token != session.get("_csrf_token"):
            abort(403, "CSRF token missing or invalid.")
        new_email = request.form.get("email", "")
        db.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, session["user"]))
        db.commit()
        flash(f"Email updated to {new_email}", "success")
        return redirect(url_for("profile_secure"))
    user = db.execute("SELECT * FROM users WHERE username = ?", (session["user"],)).fetchone()
    return render_template("profile_secure.html", user=user)

# ---- Attacker page -------------------------------------------------------

@app.route("/evil")
def evil():
    return render_template("attack.html")

# ---------------------------------------------------------------------------
# Auto-create DB & run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        from init_db import init
        init()
    app.run(debug=True, port=5005)
