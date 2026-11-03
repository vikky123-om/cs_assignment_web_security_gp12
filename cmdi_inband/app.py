import os
import re
import subprocess
import secrets
from flask import Flask, request, render_template, flash

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ping", methods=["GET", "POST"])
def ping():
    output = ""
    command = ""
    target = ""
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        if not target:
            flash("Please enter a target host.", "warning")
        else:
            command = f"ping -c 2 {target}"
            try:
                result = os.popen(command).read()
                output = result if result else "(no output)"
            except Exception as e:
                output = f"Error: {e}"
    return render_template("ping.html", output=output, command=command, target=target)


@app.route("/ping-secure", methods=["GET", "POST"])
def ping_secure():
    output = ""
    command = ""
    target = ""
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        if not target:
            flash("Please enter a target host.", "warning")
        else:
            # Mitigation 1: Allow-list regex validation
            if not re.match(r"^[a-zA-Z0-9.\-]+$", target):
                flash(
                    "Invalid input! Only alphanumeric characters, dots, and hyphens are allowed.",
                    "danger",
                )
                return render_template(
                    "ping_secure.html", output="", command="", target=target
                )

            # Mitigation 2: Subprocess with argument vector (shell=False)
            cmd_list = ["ping", "-c", "2", target]
            command = str(cmd_list)
            try:
                result = subprocess.run(
                    cmd_list,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=False,
                )
                output = result.stdout if result.stdout else result.stderr
                if not output:
                    output = "(no output)"
            except subprocess.TimeoutExpired:
                output = "Error: Command timed out after 10 seconds."
            except Exception as e:
                output = f"Error: {e}"
    return render_template(
        "ping_secure.html", output=output, command=command, target=target
    )


if __name__ == "__main__":
    app.run(debug=True, port=5002)
