import netifaces

def get_ip_address(interface):
    try:
        # Get all addresses for the specified interface
        addresses = netifaces.ifaddresses(interface)
        # Check for IPv4 address (AF_INET)
        if netifaces.AF_INET in addresses:
            return addresses[netifaces.AF_INET][0]['addr']
        else:
            return f"No IPv4 address found for {interface}"
    except ValueError:
        return f"Interface {interface} not found"
    except Exception as e:
        return f"Error: {str(e)}"

obj = get_ip_address("enp0s8")
print(obj)