"""Start all 5 vulnerability variant servers simultaneously."""
import os
import sys
import time
import subprocess
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python")

APPS = [
    ("SQL Injection (Auth Bypass)", "sqli_auth_bypass", "app.py", 5001),
    ("OS Command Injection (In-band)", "cmdi_inband", "app.py", 5002),
    ("Reflected XSS", "xss_reflected", "app.py", 5003),
    ("CSRF (GET-based)", "csrf_get", "app.py", 5004),
    ("CSRF (POST-based)", "csrf_post", "app.py", 5005),
]


def main():
    # Make sure all databases exist
    for _, folder, _, _ in APPS:
        init_script = os.path.join(BASE_DIR, folder, "init_db.py")
        if os.path.exists(init_script):
            subprocess.run([PYTHON, "init_db.py"], cwd=os.path.join(BASE_DIR, folder), check=True)

    processes = []

    def shutdown(signum=None, frame=None):
        print("\nStopping all servers...")
        for name, p in processes:
            print(f"Stopping {name}...")
            p.terminate()
        for _, p in processes:
            p.wait()
        print("All servers stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("=" * 60)
    print("STARTING ALL 5 WEB SECURITY APPLICATIONS")
    print("=" * 60)

    for name, folder, script, port in APPS:
        app_dir = os.path.join(BASE_DIR, folder)
        p = subprocess.Popen(
            [PYTHON, script],
            cwd=app_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        processes.append((name, p))
        print(f"  [+] {name:<32} -> http://127.0.0.1:{port}")

    print("=" * 60)
    print("All servers are active! Press Ctrl+C to terminate all.")
    print("=" * 60)

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()

