from flask import Flask, request, redirect, render_template_string, session
import secrets
import netifaces

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secure session key

# Dynamically determine the server's IP address
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

# Simulated client registry
CLIENTS = {
    "blogsphere_client": {
        "client_secret": "secret123",
        "redirect_uris": [f"http://{SERVER_IP}:5000/callback"],
    }
}

# Simulated user database
USERS = {
    "user1": {"password": "password123", "name": "Test User"}
}

@app.route('/auth')
def authorize():
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    response_type = request.args.get('response_type')
    state = request.args.get('state')

    if not all([client_id, redirect_uri, response_type, state]):
        return "Missing parameters", 400

    if client_id not in CLIENTS or response_type != "code":
        return "Invalid client or response_type", 400

    # Store parameters in session for post-login redirect
    session['auth_params'] = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': response_type,
        'state': state
    }

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .login-container {
                    background: #ffffff;
                    padding: 20px 30px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    width: 100%;
                    max-width: 400px;
                }
                h1 {
                    text-align: center;
                    color: #333;
                    margin-bottom: 20px;
                }
                form {
                    display: flex;
                    flex-direction: column;
                }
                input[type="text"], input[type="password"] {
                    padding: 10px;
                    margin-bottom: 15px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 16px;
                }
                input[type="submit"] {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 4px;
                    font-size: 16px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #0056b3;
                }
                .footer {
                    text-align: center;
                    margin-top: 15px;
                    font-size: 14px;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>Login</h1>
                <form method="post" action="/login">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <input type="submit" value="Login">
                </form>
                <div class="footer">
                    <p>&copy; 2025 Identity Provider</p>
                </div>
            </div>
        </body>
        </html>
    """)

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    auth_params = session.get('auth_params', {})
    if not auth_params:
        return "Session expired", 400
    if username in USERS and USERS[username]['password'] == password:
        client_id = auth_params['client_id']
        redirect_uri = auth_params['redirect_uri']
        state = auth_params['state']
        if client_id == "blogsphere_client":  # Vulnerable: No redirect_uri validation
            auth_code = f"code_{secrets.token_hex(8)}"
            redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
            return redirect(redirect_url)
        return "Invalid client configuration", 400
    return "Invalid credentials", 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)