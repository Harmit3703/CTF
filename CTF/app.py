from flask import Flask, request, redirect, url_for, make_response, render_template, session
import re
import os
import secrets
import netifaces

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, 'posts')

# Dynamically determine the server's IP address using hostname
def get_ip_address(interface="enp0s3"):
    try:
        # Get all addresses for the specified interface
        addresses = netifaces.ifaddresses(interface)
        # Check for IPv4 address (AF_INET)
        if netifaces.AF_INET in addresses:
            print("The IP addr for Host:",addresses[netifaces.AF_INET][0]['addr'] )
            return addresses[netifaces.AF_INET][0]['addr']
        else:
            return f"No IPv4 address found for {interface}"
    except ValueError:
        return f"Interface {interface} not found"
    except Exception as e:
        return f"Error: {str(e)}"

SERVER_IP = get_ip_address()

# Simulated OAuth IdP URL and Redirect URI using dynamic IP
IDP_AUTH_URL = f"http://{SERVER_IP}:5001/auth"
REDIRECT_URI = f"http://{SERVER_IP}:5000/callback"  # Dynamic redirect URI
CLIENT_ID = "blogsphere_client"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/view')
def view_page():
    page = request.args.get('page')
    if not page:
        return "Page not specified", 400

    try:
        requested_file = os.path.abspath(os.path.join(POSTS_DIR, page))

        if not os.path.isfile(requested_file):
            return f"File not found: {requested_file}", 404

        if not os.access(requested_file, os.R_OK):
            return f"File not readable: {requested_file}", 403

        with open(requested_file, 'r') as file:
            content = file.read()

     

        if page.endswith('.html'):
            return f"""
            <html>
            <head>
                <title>BlogSphere - Post</title>
                <link rel="stylesheet" href="/static/css/style.css">
            </head>
            <body>
                {content}
            </body>
            </html>
            """
        else:
            return f"""
            <html>
            <head>
                <title>BlogSphere - Post</title>
                <link rel="stylesheet" href="/static/css/style.css">
            </head>
            <body>
                <h1>Blog Post</h1>
                <pre>{content}</pre>
                <p><a href="/">Back to Home</a></p>
            </body>
            </html>
            """
    except PermissionError as e:
        return f"Permission error accessing file: {requested_file} ({str(e)})", 403
    except FileNotFoundError:
        return f"File not found: {requested_file}", 404
    except Exception as e:
        return f"Error loading page: {str(e)}", 500

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        result = f"""
        <div class="search-result">
            <h3>Search Results</h3>
            <p>You searched for: {query}</p>
            <div class="result-content">No matches found.</div>
        </div>
        """
        if re.search(r'<[^>]+>', query):
            response = make_response(render_template('search.html', query=query, result=result))
            response.set_cookie(
                key='flag',
                value='flag{r3fl3ct3d_xss_pwn3d}',
                max_age=3600,
                path='/'
            )
            return response
    else:
        result = """
        <div class="initial-search">
            <p>Enter a search term above to begin...</p>
        </div>
        """
    return render_template('search.html', query=query, result=result)

@app.route('/flag')
def get_flag():
    flag = request.cookies.get('flag', 'Flag not found!')
    return f"""
    <h2>Captured Flag</h2>
    <p>{flag}</p>
    <a href='/search'>Back to Search</a>
    """

@app.route('/login')
def login():
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    auth_url = f"{IDP_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&state={state}"
    return redirect(auth_url, code=302)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not state: #or state != session.get('oauth_state'):
        return "Invalid state parameter", 400
    if not code:
        return "No authorization code provided", 400
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)