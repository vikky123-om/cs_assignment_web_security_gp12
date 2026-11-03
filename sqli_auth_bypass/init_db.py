"""Initialise the SQLite database with sample users."""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def init():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)
    c.executemany("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)", [
        ("admin", "SuperSecret123", "admin@example.com", "admin"),
        ("alice", "alice_pass", "alice@example.com", "user"),
        ("bob", "bob_pass", "bob@example.com", "user"),
        ("charlie", "charlie_pass", "charlie@example.com", "user"),
    ])
    conn.commit()
    conn.close()
    print(f"[+] Database initialised at {DB_PATH}")

if __name__ == "__main__":
    init()
