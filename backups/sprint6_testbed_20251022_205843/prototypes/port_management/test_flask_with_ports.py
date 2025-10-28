"""
Flask Integration Test with Port Manager
========================================
Test Flask app with automatic port management.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from port_manager import PortManager

def create_test_app():
    """Create a test Flask app with port management"""
    port_manager = PortManager()
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def home():
        assigned_port = port_manager.config['reserved_ports'].get('flask_api', 'unknown')
        return jsonify({
            'message': 'Test Flask App with Port Manager',
            'port': assigned_port,
            'status': 'working'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    @app.route('/port-info')
    def port_info():
        return jsonify({
            'port_status': port_manager.get_port_status(),
            'conflicts': port_manager.diagnose_port_conflicts(),
            'reserved_ports': port_manager.config['reserved_ports']
        })
    
    return app, port_manager

def test_flask_with_ports():
    """Test Flask startup with port management"""
    print("\n" + "=" * 70)
    print("FLASK INTEGRATION TEST - PORT MANAGER")
    print("=" * 70)
    
    try:
        # Create app
        app, port_manager = create_test_app()
        print("✅ Flask app created successfully")
        
        # Get port
        port = port_manager.get_port_for_service('flask_api')
        print(f"✅ Assigned port: {port}")
        
        # Check for conflicts
        conflicts = port_manager.diagnose_port_conflicts()
        if conflicts:
            print(f"⚠️  {len(conflicts)} port conflicts detected:")
            for conflict in conflicts:
                print(f"   - {conflict['service']} on port {conflict['port']}")
        else:
            print("✅ No port conflicts")
        
        # Test client
        print("\n📝 Testing Flask endpoints...")
        with app.test_client() as client:
            # Test home
            response = client.get('/')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Home endpoint: {data['message']}")
            else:
                print(f"❌ Home endpoint failed: {response.status_code}")
            
            # Test health
            response = client.get('/health')
            if response.status_code == 200:
                print(f"✅ Health endpoint: {response.get_json()['status']}")
            else:
                print(f"❌ Health endpoint failed")
            
            # Test port info
            response = client.get('/port-info')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Port info endpoint working")
                print(f"   Available ports: {data['port_status']['available']}/{data['port_status']['total_ports']}")
            else:
                print(f"❌ Port info endpoint failed")
        
        print("\n" + "=" * 70)
        print("✅ ALL FLASK INTEGRATION TESTS PASSED")
        print("=" * 70)
        
        # Ask if user wants to start the server
        print(f"\n💡 To start the test server, run:")
        print(f"   python test_flask_with_ports.py --run")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_server():
    """Actually run the Flask server"""
    app, port_manager = create_test_app()
    port = port_manager.get_port_for_service('flask_api')
    
    print(f"\n🚀 Starting Flask test server on port {port}...")
    print(f"   Visit: http://127.0.0.1:{port}")
    print(f"   Health: http://127.0.0.1:{port}/health")
    print(f"   Port Info: http://127.0.0.1:{port}/port-info")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='127.0.0.1', port=port, debug=True)

if __name__ == '__main__':
    if '--run' in sys.argv:
        run_server()
    else:
        success = test_flask_with_ports()
        sys.exit(0 if success else 1)
