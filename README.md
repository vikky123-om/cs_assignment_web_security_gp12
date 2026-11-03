# Web Server Security – Exploitation & Mitigation

**Course:** Web Server Security  
**Instructor:** Dr. Soumyadev Maity  
**Assignment:** Exploitation and Mitigation of Web Server Vulnerabilities  
**Submission Deadline:** 03 November 2026, 23:59  

---

## Overview

This repository contains fully functional demonstrations of web server security vulnerabilities and their mitigations.
As per assignment specifications, each member implements one variant chosen from the options in Table 1.

Every variant is built as an **independent, self-contained web application** inside its own directory, featuring:
1. **(a) Vulnerable implementation:** Clearly marked vulnerable code path.
2. **(b) Working exploit:** Real, verifiable exploit payload.
3. **(c) Root cause analysis:** Technical explanation of the underlying security flaw.
4. **(d) Implemented mitigation:** One production-ready fix applied and demonstrated blocking the payload.
5. **(e) Alternative mitigations (theory):** Deep conceptual explanations of other mitigations covered in lecture slides.
6. **Dedicated README.md:** Complete documentation per variant for video demonstrations and the viva.

---

## Directory Structure

```
cs_assign/
├── README.md                      ← Master repository overview & ownership table
├── requirements.txt               ← Python dependencies (Flask, etc.)
│
├── sqli_auth_bypass/              ← SQL Injection: Authentication Bypass (Port 5001)
│   ├── app.py
│   ├── init_db.py
│   ├── templates/
│   └── README.md
│
├── cmdi_inband/                   ← OS Command Injection: In-band (Port 5002)
│   ├── app.py
│   ├── templates/
│   └── README.md
│
├── xss_reflected/                 ← Cross-Site Scripting (XSS): Reflected XSS (Port 5003)
│   ├── app.py
│   ├── templates/
│   └── README.md
│
├── csrf_get/                      ← CSRF: GET-based Forged Action (Port 5004)
│   ├── app.py
│   ├── init_db.py
│   ├── templates/
│   └── README.md
│
└── csrf_post/                     ← CSRF: POST-based Forged Action (Port 5005)
    ├── app.py
    ├── init_db.py
    ├── templates/
    └── README.md
```

---

## Summary of Implemented Variants

| # | Vulnerability Category | Variant Implemented | Port | Directory | Exploit Payload Sample | Implemented Mitigation |
|---|------------------------|---------------------|------|-----------|------------------------|------------------------|
| 1 | **SQL Injection** | Authentication Bypass | `5001` | [`sqli_auth_bypass/`](sqli_auth_bypass/) | `' OR '1'='1' --` | Parameterised queries with bound parameters |
| 2 | **OS Command Injection** | In-band (output returned) | `5002` | [`cmdi_inband/`](cmdi_inband/) | `127.0.0.1; whoami` | Regex allow-list + argument vector (`shell=False`) |
| 3 | **Cross-Site Scripting (XSS)** | Reflected XSS | `5003` | [`xss_reflected/`](xss_reflected/) | `<script>alert('Reflected XSS')</script>` | Context-aware HTML entity output encoding |
| 4 | **CSRF** | GET-based forged action | `5004` | [`csrf_get/`](csrf_get/) | `<img src="http://.../delete-account">` | Require HTTP POST + synchronizer CSRF token |
| 5 | **CSRF** | POST-based forged action | `5005` | [`csrf_post/`](csrf_post/) | Auto-submitting hidden `<form>` | Per-session synchronizer anti-CSRF token |

---

## Ownership Declaration (Table 3)

| Member Name | Roll Number | Category | Variant Implemented | Folder |
|---|---|---|---|---|
| ____________________ | ____________________ | SQL Injection | Authentication Bypass | [`sqli_auth_bypass/`](sqli_auth_bypass/) |
| ____________________ | ____________________ | OS Command Injection | In-band (output returned) | [`cmdi_inband/`](cmdi_inband/) |
| ____________________ | ____________________ | Cross-Site Scripting (XSS) | Reflected XSS | [`xss_reflected/`](xss_reflected/) |
| ____________________ | ____________________ | CSRF | GET-based forged action | [`csrf_get/`](csrf_get/) |
| ____________________ | ____________________ | CSRF | POST-based forged action | [`csrf_post/`](csrf_post/) |

---

## Setup & Execution Guide

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

### Running Individual Variants

Each variant runs on its own designated port so they can be demonstrated independently or concurrently without port conflicts:

```bash
# Variant 1: SQL Injection (Port 5001)
cd sqli_auth_bypass
python init_db.py
python app.py

# Variant 2: OS Command Injection (Port 5002)
cd cmdi_inband
python app.py

# Variant 3: Reflected XSS (Port 5003)
cd xss_reflected
python app.py

# Variant 4: GET-based CSRF (Port 5004)
cd csrf_get
python init_db.py
python app.py

# Variant 5: POST-based CSRF (Port 5005)
cd csrf_post
python init_db.py
python app.py
```

---

## Academic Integrity

All code implementations, exploit demonstrations, and mitigation defenses were independently authored by the group members for this assignment. Originality and technical mastery will be defended individually at the viva.
