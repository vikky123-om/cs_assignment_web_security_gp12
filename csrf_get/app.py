"""CSRF – GET-based Forged Action demo (port 5004)."""
from flask import (
    Flask, request, session, redirect, url_for,
    render_template, flash, abort, g
)
import sqlite3, os, secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

# ── database helpers ────────────────────────────────────────────────
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

# ── CSRF token helper ──────────────────────────────────────────────
def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

app.jinja_env.globals["csrf_token"] = generate_csrf_token

# ── login decorator ────────────────────────────────────────────────
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── routes ──────────────────────────────────────────────────────────
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
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("profile"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))

@app.route("/profile")
@login_required
def profile():
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (session["user"],)
    ).fetchone()
    if not user:
        session.clear()
        flash("Account not found. It may have been deleted.", "danger")
        return redirect(url_for("index"))
    return render_template("profile.html", user=user)

# ── VULNERABLE: state-changing action via GET, no CSRF token ──────
@app.route("/delete-account")
@login_required
def delete_account_vuln():
    db = get_db()
    db.execute("DELETE FROM users WHERE username = ?", (session["user"],))
    db.commit()
    session.clear()
    flash("Account deleted!", "danger")
    return redirect(url_for("index"))

# ── SECURE: POST + CSRF token ────────────────────────────────────
@app.route("/delete-account-secure", methods=["POST"])
@login_required
def delete_account_secure():
    token = request.form.get("_csrf_token", "")
    if not token or token != session.get("_csrf_token"):
        abort(403, "CSRF token missing or invalid.")
    db = get_db()
    db.execute("DELETE FROM users WHERE username = ?", (session["user"],))
    db.commit()
    session.clear()
    flash("Account deleted securely.", "info")
    return redirect(url_for("index"))

# ── attacker page ─────────────────────────────────────────────────
@app.route("/evil")
def evil():
    return render_template("attack.html")

# ── reset DB ──────────────────────────────────────────────────────
@app.route("/reset")
def reset():
    from init_db import init
    init()
    flash("Database has been reset.", "info")
    return redirect(url_for("index"))

# ── auto-create DB if missing ─────────────────────────────────────
if not os.path.exists(DB_PATH):
    from init_db import init
    init()

if __name__ == "__main__":
    app.run(debug=True, port=5004)
