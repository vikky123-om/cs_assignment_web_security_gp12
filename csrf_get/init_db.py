"""Initialise the SQLite database with users."""
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
            balance REAL NOT NULL DEFAULT 1000.00
        )
    """)
    c.executemany("INSERT INTO users (username, password, email, balance) VALUES (?, ?, ?, ?)", [
        ("alice", "alice_pass", "alice@example.com", 1000.00),
        ("bob", "bob_pass", "bob@example.com", 1000.00),
        ("charlie", "charlie_pass", "charlie@example.com", 1000.00),
    ])
    conn.commit()
    conn.close()
    print(f"[+] Database initialised at {DB_PATH}")

if __name__ == "__main__":
    init()
