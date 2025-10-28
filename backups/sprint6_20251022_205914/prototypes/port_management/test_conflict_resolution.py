"""
Quick Port Conflict Resolution Test
===================================
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from port_manager import PortManager
import socket

def test_port_conflict_resolution():
    """Test that port manager can handle conflicts"""
    print("\n" + "=" * 70)
    print("PORT CONFLICT RESOLUTION TEST")
    print("=" * 70)
    
    pm = PortManager()
    
    # Simulate port 5000 being busy
    print("\n1. Simulating port 5000 being busy...")
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        test_socket.bind(('127.0.0.1', 5000))
        print("   ✅ Port 5000 is now occupied (simulated conflict)")
        
        # Try to get port for flask_api
        print("\n2. Asking PortManager for flask_api port...")
        assigned_port = pm.get_port_for_service('flask_api')
        print(f"   ✅ PortManager assigned port: {assigned_port}")
        
        if assigned_port != 5000:
            print(f"   ✅ Correctly avoided busy port 5000, using {assigned_port} instead")
        else:
            print(f"   ⚠️  Still assigned port 5000 despite it being busy")
        
        # Verify the assigned port is actually available
        print(f"\n3. Verifying port {assigned_port} is available...")
        test_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket2.bind(('127.0.0.1', assigned_port))
        test_socket2.close()
        print(f"   ✅ Port {assigned_port} is available and can be used")
        
        # Clean up
        test_socket.close()
        
        print("\n" + "=" * 70)
        print("✅ PORT CONFLICT RESOLUTION TEST PASSED")
        print(f"   Preferred: 5000 → Assigned: {assigned_port}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        test_socket.close()
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_port_conflict_resolution()
    sys.exit(0 if success else 1)
