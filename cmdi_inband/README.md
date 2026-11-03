# OS Command Injection – In-band (Command Output Returned)

| **Property** | **Value** |
|---|---|
| **Category** | OS Command Injection |
| **Variant** | In-band / Output returned (Variant 1) |
| **Port** | 5002 |

---

## Overview

This application demonstrates **in-band OS Command Injection** inside a network diagnostic ping utility. The server executes an operating system ping command using user-supplied input. In the vulnerable implementation, the input is passed directly to the system shell, enabling an attacker to chain arbitrary shell commands whose output is directly reflected back in the HTTP response.

---

## How to Run

```bash
# From within the cmdi_inband directory:
python app.py
```
Open **http://127.0.0.1:5002** in your browser.

---

## (a) Vulnerable Implementation

File: `cmdi_inband/app.py`  
Endpoint: `POST /ping`

```python
@app.route("/ping", methods=["GET", "POST"])
def ping():
    output = ""
    command = ""
    target = ""
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        if target:
            # VULNERABLE: Direct string interpolation into shell command
            command = f"ping -c 2 {target}"
            result = os.popen(command).read()
            output = result if result else "(no output)"
    return render_template("ping.html", output=output, command=command, target=target)
```

---

## (b) Working Exploit

Submit the following in the target host field at `/ping`:

```bash
127.0.0.1; whoami
```
Or to read system configuration:
```bash
127.0.0.1; id
127.0.0.1; uname -a
```

**Observed Result:**  
The server executes `ping -c 2 127.0.0.1` followed immediately by `whoami`, returning the active user context (e.g. `varshith`) directly inside the webpage's output block.

---

## (c) Root Cause

User input (`target`) is directly concatenated into a shell command string and executed via `os.popen()`. Because a shell is spawned, shell metacharacters such as `;`, `&`, `&&`, and `|` act as command separators, allowing an attacker to append arbitrary OS commands with the permissions of the web server process.

---

## (d) Mitigation Implemented

File: `cmdi_inband/app.py`  
Endpoint: `POST /ping-secure`

1. **Allow-list Regex Validation:**  
   The input is validated against `^[a-zA-Z0-9.\-]+$`. If any unexpected characters (including `;`, `&`, `|`, spaces, quotes) are detected, the request is rejected immediately with an error flash message.
2. **Avoid the Shell via Argument Vector:**  
   The application uses `subprocess.run(["ping", "-c", "2", target], shell=False)`. Bypassing the shell ensures that even if a metacharacter reached the subprocess call, it would be treated strictly as an argument value rather than shell command syntax.

**Testing the payload against mitigation:**  
Entering `127.0.0.1; whoami` at `/ping-secure` triggers:
> *"Invalid input! Only alphanumeric characters, dots, and hyphens are allowed."*

No shell command is executed.

---

## (e) Other Mitigations (Theory)

1. **Avoid the shell entirely:**  
   Replace OS command invocations with native programming language APIs. For example, instead of running the `ping` or `curl` binary via shell, use Python's built-in `socket` or HTTP libraries (`urllib` / `requests`).
2. **Parameterised execution with argument vector:**  
   When invoking external programs cannot be avoided, pass commands and arguments as discrete array elements (e.g. `execve` or `subprocess.run([...], shell=False)`), preventing the invocation of a command-line interpreter (`/bin/sh`).
3. **Allow-list validation:**  
   Strictly constrain acceptable user input according to an allow-list schema (e.g., verifying that the input is a valid IPv4/IPv6 address or standard hostname) and reject non-conforming input.
4. **Least privilege:**  
   Execute the web application and worker processes using a dedicated user account with the minimal set of privileges required (e.g. read-only file permissions, restricted shell capabilities, and containerisation).

---

## Ownership Declaration

| Member Name | Roll Number | Category | Variant Implemented |
|---|---|---|---|
| ____________ | ____________ | OS Command Injection | In-band (output returned) |

