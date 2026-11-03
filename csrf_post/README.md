# CSRF – POST-based Forged Action (Auto-submitting Form)

| Property     | Value                                        |
|-------------|----------------------------------------------|
| **Category** | Cross-Site Request Forgery (CSRF)            |
| **Variant**  | POST-based forged action (Variant 2)         |
| **Port**     | 5005                                         |

---

## Overview

The **email-change form** on the vulnerable endpoint (`/profile`) accepts any POST request carrying a valid session cookie — **without verifying a CSRF token**. An attacker can craft a malicious page that auto-submits a hidden form, silently changing the victim's email address while they are logged in.

---

## How to Run

```bash
# 1. Install dependencies
pip install flask

# 2. Initialise the database
python init_db.py

# 3. Start the server
python app.py

# 4. Open in browser
open http://localhost:5005
```

---

## Vulnerable Implementation

The `/profile` endpoint blindly processes any POST request without CSRF verification:

```python
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_vuln():
    db = get_db()
    if request.method == "POST":
        new_email = request.form.get("email", "")
        # ❌ No CSRF token check — any POST with a valid session is accepted
        db.execute("UPDATE users SET email = ? WHERE username = ?",
                   (new_email, session["user"]))
        db.commit()
        flash(f"Email updated to {new_email}", "success")
        return redirect(url_for("profile_vuln"))
    user = db.execute("SELECT * FROM users WHERE username = ?",
                      (session["user"],)).fetchone()
    return render_template("profile.html", user=user)
```

---

## Working Exploit

The attacker hosts a page with a **hidden auto-submitting form**:

```html
<form id="csrf-form" method="POST"
      action="http://127.0.0.1:5005/profile" style="display:none;">
  <input type="hidden" name="email" value="hacked@evil.com">
</form>
<script>document.getElementById('csrf-form').submit();</script>
```

When a logged-in user visits this page, the browser:

1. Builds a POST request to `http://127.0.0.1:5005/profile`
2. Automatically attaches the session cookie
3. The server sees a valid session → updates the email

The victim's email is changed to `hacked@evil.com` without their knowledge.

---

## Root Cause

| Factor | Detail |
|--------|--------|
| **No proof of intent** | The server accepts any POST with form data and a valid session cookie — it never verifies that the request originated from its own page. |
| **Cookie auto-attachment** | Browsers automatically include cookies for matching domains, regardless of which site initiated the request. |

---

## Mitigation Implemented

### Synchronizer CSRF Token Pattern

The `/profile-secure` endpoint validates a unique, per-session CSRF token:

```python
@app.route("/profile-secure", methods=["GET", "POST"])
@login_required
def profile_secure():
    db = get_db()
    if request.method == "POST":
        token = request.form.get("_csrf_token", "")
        if not token or token != session.get("_csrf_token"):
            abort(403, "CSRF token missing or invalid.")
        # ✅ Token valid — proceed with the update
        new_email = request.form.get("email", "")
        db.execute("UPDATE users SET email = ? WHERE username = ?",
                   (new_email, session["user"]))
        db.commit()
        flash(f"Email updated to {new_email}", "success")
        return redirect(url_for("profile_secure"))
    user = db.execute("SELECT * FROM users WHERE username = ?",
                      (session["user"],)).fetchone()
    return render_template("profile_secure.html", user=user)
```

The token is embedded in the form via a hidden field:

```html
<input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
```

---

## Other Mitigations (Theory)

| Technique | Description |
|-----------|-------------|
| **SameSite Cookies** | Set `SameSite=Lax` or `Strict` on session cookies so the browser refuses to send them with cross-origin requests. |
| **Re-authentication for Sensitive Actions** | Require the user to re-enter their password before critical operations like email or password changes. |
| **Avoid State-changing GET Requests** | Never use GET for operations that modify data. Always use POST/PUT/DELETE with proper token validation. |

---

## File Structure

```
csrf_post/
├── app.py                  # Flask application (port 5005)
├── init_db.py              # Database initialisation script
├── app.db                  # SQLite database (auto-created)
├── README.md               # This file
└── templates/
    ├── base.html           # Base layout template
    ├── index.html          # Home / overview page
    ├── login.html          # Login form
    ├── profile.html        # ⚠ Vulnerable profile (no CSRF)
    ├── profile_secure.html # ✓ Secure profile (CSRF token)
    └── attack.html         # 🎣 Attacker auto-submit page
```

---

## Ownership

| Field           | Value              |
|-----------------|--------------------|
| **Author**      |                    |
| **Date**        |                    |
| **Course**      |                    |
| **Assignment**  |                    |
