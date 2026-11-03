# Cross-Site Request Forgery (CSRF) – GET-based Forged Action

| **Property** | **Value** |
|---|---|
| **Category** | Cross-Site Request Forgery (CSRF) |
| **Variant** | GET-based forged action (Variant 1) |
| **Port** | 5004 |

---

## Overview

This application demonstrates a **GET-based Cross-Site Request Forgery (CSRF)** vulnerability in an account deletion feature. The application exposes an endpoint that executes a state-changing operation (deleting the user account) upon receiving an HTTP GET request without verifying origin or intent. An external attacker can embed this URL inside an HTML image tag or link on a third-party webpage, triggering unauthenticated account destruction whenever an authenticated victim visits the malicious page.

---

## How to Run

```bash
# From within the csrf_get directory:
python init_db.py
python app.py
```
Open **http://127.0.0.1:5004** in your browser.

---

## (a) Vulnerable Implementation

File: `csrf_get/app.py`  
Endpoint: `GET /delete-account`

```python
@app.route("/delete-account")
@login_required
def delete_account_vuln():
    db = get_db()
    # VULNERABLE: State mutation triggered by a GET request with no CSRF validation
    db.execute("DELETE FROM users WHERE username = ?", (session["user"],))
    db.commit()
    session.clear()
    flash("Account deleted!", "danger")
    return redirect(url_for("index"))
```

---

## (b) Working Exploit

1. Log into the application at `http://127.0.0.1:5004/login` using credentials `alice` / `alice_pass`.
2. Observe active account data on the profile page (`http://127.0.0.1:5004/profile`).
3. While remaining logged in, open the simulated attacker webpage in another tab (`http://127.0.0.1:5004/evil`).
4. The attacker page contains the following payload:

```html
<!-- Attacker payload embedding target state-changing GET URL -->
<img src="http://127.0.0.1:5004/delete-account" style="display:none;" />
```

**Observed Result:**  
The browser requests the image URL, automatically attaching Alice's session cookie. The server receives the GET request, validates the session cookie, and deletes Alice's account from the database without any confirmation or warning. When returning to the web application, Alice is logged out and the account is gone.

---

## (c) Root Cause

The application violates the HTTP specification (RFC 7231) by performing a state-changing mutation via an **HTTP GET request**. Furthermore, it assumes that the presence of an authenticated session cookie proves the user's deliberate intent. Because web browsers automatically attach stored session cookies to cross-origin requests for resources (such as `<img>`, `<iframe>`, and `<link>`), third-party websites can forge authenticated GET requests on behalf of the victim.

---

## (d) Mitigation Implemented

File: `csrf_get/app.py`  
Endpoint: `POST /delete-account-secure`

1. **Enforce POST Method:** State-changing operations cannot be triggered via GET.
2. **Synchronizer Token Pattern:** A unique, unpredictable, cryptographically random `_csrf_token` is generated per user session and included as a hidden form field. Upon submission, the server verifies that the submitted token matches the session token.

```python
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
```

**Testing the payload against mitigation:**  
Third-party sites attempting to issue GET requests against `/delete-account-secure` receive `405 Method Not Allowed`. If an attacker constructs a cross-site form, they cannot read or forge the required `_csrf_token` due to the Same-Origin Policy (SOP), resulting in `403 Forbidden`.

---

## (e) Other Mitigations (Theory)

1. **Anti-CSRF (Synchronizer) Tokens:**  
   Embed a server-generated, cryptographically strong random token in forms. Because the attacker's page cannot read the victim's DOM across origins, forged requests will omit or provide an invalid token and be rejected.
2. **SameSite Cookie Attribute:**  
   Configure session cookies with `SameSite=Strict` or `SameSite=Lax`. Browsers will not send `SameSite` cookies with cross-site resource requests or cross-origin POST requests, blocking CSRF at the browser level.
3. **Re-authentication for Sensitive Actions:**  
   Require the user to provide their current password or an MFA one-time passcode before completing sensitive actions like account deletion or password changes.
4. **Avoiding State-changing GET Requests:**  
   Ensure all state-altering operations use safe HTTP verbs (`POST`, `PUT`, `DELETE`). GET must remain safe and idempotent.

---

## Ownership Declaration

| Member Name | Roll Number | Category | Variant Implemented |
|---|---|---|---|
| ____________ | ____________ | Cross-Site Request Forgery (CSRF) | GET-based forged action |

