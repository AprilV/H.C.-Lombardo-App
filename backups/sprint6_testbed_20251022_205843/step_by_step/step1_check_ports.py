"""
STEP 1: Check Port Availability
Test ports 5000-5005 to find available ones for our servers
"""
import socket

def check_port(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        # Try to bind to the port
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True, "AVAILABLE"
    except OSError as e:
        return False, f"IN USE ({e})"

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1: PORT AVAILABILITY CHECK")
    print("=" * 60)
    
    ports_to_check = [5000, 5001, 5002, 5003, 5004, 5005, 8000, 8001]
    
    available_ports = []
    used_ports = []
    
    for port in ports_to_check:
        available, status = check_port(port)
        status_symbol = "✓" if available else "✗"
        print(f"Port {port}: {status_symbol} {status}")
        
        if available:
            available_ports.append(port)
        else:
            used_ports.append(port)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Available ports: {available_ports}")
    print(f"Used ports: {used_ports}")
    print("=" * 60)
    
    if len(available_ports) >= 2:
        print(f"\n✓ PASS: Found {len(available_ports)} available ports")
        print(f"Recommended: Use port {available_ports[0]} for backend")
        exit(0)
    else:
        print(f"\n✗ FAIL: Only {len(available_ports)} ports available, need at least 2")
        exit(1)
