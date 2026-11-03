"""Cross-Site Scripting (XSS) – Reflected XSS demo (Flask, port 5003)."""
import html
import secrets
from flask import Flask, request, render_template

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Sample mock product catalog
PRODUCTS = [
    {"id": 1, "name": "Wireless Mechanical Keyboard", "category": "Electronics", "price": 89.99},
    {"id": 2, "name": "Ergonomic Vertical Mouse", "category": "Electronics", "price": 49.50},
    {"id": 3, "name": "Noise Cancelling Headphones", "category": "Audio", "price": 149.00},
    {"id": 4, "name": "USB-C Multiport Adapter", "category": "Accessories", "price": 29.99},
    {"id": 5, "name": "Laptop Stand Aluminum", "category": "Accessories", "price": 39.00},
]


@app.route("/")
def index():
    return render_template("index.html")


# ── VULNERABLE: Reflects user input into HTML using | safe in template ──
@app.route("/search")
def search_vuln():
    query = request.args.get("q", "")
    results = []
    if query:
        # Simple case-insensitive search
        results = [p for p in PRODUCTS if query.lower() in p["name"].lower() or query.lower() in p["category"].lower()]
    return render_template("search.html", query=query, results=results)


# ── SECURE: Context-aware HTML entity encoding / auto-escaping ──
@app.route("/search-secure")
def search_secure():
    query = request.args.get("q", "")
    results = []
    if query:
        results = [p for p in PRODUCTS if query.lower() in p["name"].lower() or query.lower() in p["category"].lower()]
    # Mitigation: html.escape ensures special characters (<, >, &, ", ') are escaped
    safe_query = html.escape(query)
    return render_template("search_secure.html", query=safe_query, raw_query=query, results=results)


if __name__ == "__main__":
    app.run(debug=True, port=5003)

