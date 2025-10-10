"""
STEP 2B: Diagnose Flask Server Issue
Figure out why Flask servers immediately exit
"""
import sys
import traceback
from flask import Flask, jsonify

def test_flask_app():
    """Test if we can create and run a Flask app"""
    print("=" * 60)
    print("DIAGNOSTIC: Why does Flask exit immediately?")
    print("=" * 60)
    
    print("\n1. Testing Flask import...")
    try:
        from flask import Flask
        print("   ✓ Flask imported successfully")
    except Exception as e:
        print(f"   ✗ Flask import failed: {e}")
        return False
    
    print("\n2. Testing Flask app creation...")
    try:
        app = Flask(__name__)
        print("   ✓ App created successfully")
    except Exception as e:
        print(f"   ✗ App creation failed: {e}")
        return False
    
    print("\n3. Testing route definition...")
    try:
        @app.route('/')
        def test():
            return jsonify({"test": "works"})
        print("   ✓ Route defined successfully")
    except Exception as e:
        print(f"   ✗ Route definition failed: {e}")
        return False
    
    print("\n4. Testing with test client (no server needed)...")
    try:
        with app.test_client() as client:
            response = client.get('/')
            data = response.get_json()
            print(f"   ✓ Test client works: {data}")
    except Exception as e:
        print(f"   ✗ Test client failed: {e}")
        traceback.print_exc()
        return False
    
    print("\n5. Testing if we can bind to port 5001...")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 5001))
        sock.close()
        print("   ✓ Can bind to port 5001")
    except Exception as e:
        print(f"   ✗ Cannot bind to port 5001: {e}")
        return False
    
    print("\n6. Checking Python version and threading support...")
    print(f"   Python version: {sys.version}")
    try:
        import threading
        print(f"   ✓ Threading module available")
    except:
        print(f"   ✗ Threading module not available")
        return False
    
    print("\n" + "=" * 60)
    print("All diagnostics passed. Flask should work.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_flask_app()
    sys.exit(0 if success else 1)
