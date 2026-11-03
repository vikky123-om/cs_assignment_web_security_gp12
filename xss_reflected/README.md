# Cross-Site Scripting (XSS) – Reflected XSS

| **Property** | **Value** |
|---|---|
| **Category** | Cross-Site Scripting (XSS) |
| **Variant** | Reflected XSS (Variant 2) |
| **Port** | 5003 |

---

## Overview

This application demonstrates **Reflected Cross-Site Scripting (XSS)** in an e-commerce product search feature. When a user submits a search query via the URL parameter `q`, the search string is immediately included in the HTTP response page. Because the vulnerable implementation renders this parameter without output encoding, an attacker can craft a malicious URL containing JavaScript. When an unsuspecting user clicks the link, the script executes immediately within the user's browser in the application's security context.

---

## How to Run

```bash
# From within the xss_reflected directory:
python app.py
```
Open **http://127.0.0.1:5003** in your browser.

---

## (a) Vulnerable Implementation

File: `xss_reflected/templates/search.html`  
Endpoint: `GET /search?q=...`

In `xss_reflected/app.py`:
```python
@app.route("/search")
def search_vuln():
    query = request.args.get("q", "")
    results = []
    if query:
        results = [p for p in PRODUCTS if query.lower() in p["name"].lower() or query.lower() in p["category"].lower()]
    return render_template("search.html", query=query, results=results)
```

In `xss_reflected/templates/search.html`:
```html
<!-- VULNERABLE: | safe filter instructs Jinja2 not to escape HTML/JS -->
<h3>Search results for: {{ query | safe }}</h3>
```

---

## (b) Working Exploit

Submit the following payload into the search bar at `/search` or load the URL directly:

```
http://127.0.0.1:5003/search?q=%3Cscript%3Ealert('Reflected+XSS+Executed!')%3C%2Fscript%3E
```
Or with an image error event payload:
```html
<img src=x onerror="alert('Reflected XSS on ' + document.domain)">
```

**Observed Result:**  
The browser immediately executes the embedded JavaScript alert dialog demonstrating arbitrary script execution in the user's session context.

---

## (c) Root Cause

The server takes untrusted data directly from the HTTP request query string (`q`) and embeds it into the HTML document response without **context-aware output encoding**. By bypassing Jinja2's default escaping using the `| safe` template filter, raw HTML tags and JavaScript are passed unaltered to the browser's HTML parser, leading to script injection and execution.

---

## (d) Mitigation Implemented

File: `xss_reflected/app.py` and `xss_reflected/templates/search_secure.html`  
Endpoint: `GET /search-secure?q=...`

1. **Context-aware Output Encoding:**  
   The application encodes untrusted input with `html.escape()` and renders it using standard Jinja2 template interpolation without any `| safe` bypass filter.
2. **HTML Entity Replacement:**  
   Characters with syntactic meaning in HTML are converted to their corresponding safe character entities:
   - `<` becomes `&lt;`
   - `>` becomes `&gt;`
   - `&` becomes `&amp;`
   - `"` becomes `&quot;`
   - `'` becomes `&#x27;`

```html
<!-- SECURE: Output is HTML-encoded and auto-escaped -->
<h3>Search results for: {{ query }}</h3>
```

**Testing the payload against mitigation:**  
When visiting:
```
http://127.0.0.1:5003/search-secure?q=%3Cscript%3Ealert('Reflected+XSS')%3C%2Fscript%3E
```
The browser receives `&lt;script&gt;alert(&#x27;Reflected XSS&#x27;)&lt;/script&gt;`. The script is displayed harmlessly on the webpage as plain text, completely preventing code execution.

---

## (e) Other Mitigations (Theory)

1. **Context-aware Output Encoding (applied above):**  
   Ensure all dynamically rendered user data is encoded specifically for the destination context (e.g., HTML body, HTML attribute, JavaScript variable, or URL query parameter).
2. **Framework Auto-Escaping:**  
   Modern templating frameworks (Jinja2, Django, React, Angular) automatically escape expressions by default. Developers must enforce strict coding guidelines forbidding bypasses like `| safe` or `dangerouslySetInnerHTML`.
3. **HTML Sanitiser for Rich Text:**  
   When formatted HTML must be supported (such as user comments with bold/italics), run user input through an allow-list HTML sanitiser (e.g., Bleach or DOMPurify) to remove executable elements and event attributes.
4. **Content Security Policy (CSP):**  
   Configure HTTP headers such as `Content-Security-Policy: default-src 'self'; script-src 'self'`. A strict CSP blocks inline script execution and unauthorized remote scripts, providing defence-in-depth even if an output-encoding oversight occurs.
5. **HttpOnly Session Cookies:**  
   Set the `HttpOnly` flag on sensitive authentication cookies. This prevents malicious scripts executed via XSS from reading the cookies through `document.cookie`, mitigating session theft.
6. **Safe DOM Sinks:**  
   In client-side JavaScript, use secure DOM manipulation properties such as `element.textContent` or `element.innerText` instead of dangerous sinks like `innerHTML`, `outerHTML`, or `document.write()`.

---

## Ownership Declaration

| Member Name | Roll Number | Category | Variant Implemented |
|---|---|---|---|
| ____________ | ____________ | Cross-Site Scripting (XSS) | Reflected XSS |

