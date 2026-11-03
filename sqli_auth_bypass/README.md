# SQL Injection – Authentication Bypass

| **Category** | SQL Injection |
|---|---|
| **Variant** | Authentication Bypass (Variant 1) |
| **Port** | 5001 |

---

## Overview

This application demonstrates how **SQL Injection** can be exploited to **bypass login authentication**. When user-supplied input is concatenated directly into a SQL query string, an attacker can manipulate the query logic to authenticate as any user — or as the first user in the database (typically the admin) — without knowing a valid password.

---

## How to Run

```bash
# 1. Install dependencies
pip install flask

# 2. Initialise the database
python init_db.py

# 3. Start the application
python app.py

# 4. Open in your browser
open http://localhost:5001
```

---

## Vulnerable Implementation

The vulnerable login endpoint builds its SQL query by concatenating user input directly into the query string using an f-string:

```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
user = db.execute(query).fetchone()
```

This allows an attacker to inject arbitrary SQL into the `username` or `password` fields.

---

## Working Exploit

On the **Vulnerable Login** page (`/login`), use the following payload:

| Field | Value |
|---|---|
| **Username** | `' OR '1'='1' --` |
| **Password** | `anything` |

### What happens

The resulting SQL query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' --' AND password = 'anything'
```

- `' OR '1'='1'` — closes the original string and injects a condition that is always `TRUE`, so the `WHERE` clause matches **every** row.
- `--` — comments out the rest of the query (the password check), so the password value is ignored.
- The database returns the **first row** in the `users` table, which is typically the **admin** account.

---

## Root Cause

User input is concatenated into the SQL query via an **f-string**. The database cannot distinguish between the intended SQL logic and the attacker's injected SQL fragment. The attacker:

1. Closes the username string literal with `'`
2. Injects `OR '1'='1'` to make the `WHERE` clause always true
3. Uses `--` to comment out the remaining password check

---

## Mitigation Implemented

The **Secure Login** page (`/login-secure`) uses **parameterised queries** with `?` placeholders:

```python
user = db.execute(
    "SELECT * FROM users WHERE username = ? AND password = ?",
    (username, password)
).fetchone()
```

The database driver treats the parameters strictly as **data values**, never as executable SQL. Even if the input contains SQL syntax like `' OR '1'='1' --`, it is treated as a literal string and will not match any username.

---

## Other Mitigations (Theory)

| Mitigation | Description |
|---|---|
| **Parameterised Queries** ✅ | Use `?` placeholders so the DB driver separates SQL logic from data. Primary defence. |
| **Input Validation with Allow-Lists** | Restrict usernames to alphanumeric patterns. Reject special characters like `'`, `;`, `--`. |
| **Least-Privilege Database Accounts** | Run the app with minimal DB permissions (e.g., `SELECT` only). Limits damage even if injection succeeds. |
| **Safe Error Handling** | Never expose raw SQL errors to users. Log details server-side; show generic messages to clients. |







INTENDED LOGIC TREE:
         [WHERE]
            |
          [AND] <--- Both MUST be true!
         /     \
[user='alice']  [pass='secret']


HIJACKED LOGIC TREE (AFTER INJECTION):
         [WHERE]
            |
          [OR]  <--- Only ONE needs to be true!
         /    \
[user='']      ['1'='1'] (ALWAYS TRUE!)
(False)            |
                   +---> Result: TRUE for all rows!
( Everything after '--' was deleted by SQLite parser)
























---

## File Structure

```
sqli_auth_bypass/
├── app.py                  # Flask application (port 5001)
├── init_db.py              # Database initialisation script
├── app.db                  # SQLite database (auto-generated)
├── README.md               # This file
└── templates/
    ├── base.html           # Base template with navbar & styling
    ├── index.html          # Home page with overview & test accounts
    ├── login.html          # Vulnerable login page
    ├── login_secure.html   # Secure login page
    └── dashboard.html      # Post-login dashboard
```

---

## Ownership

| Member | Contribution |
|---|---|
| | |
| | |
| | |
