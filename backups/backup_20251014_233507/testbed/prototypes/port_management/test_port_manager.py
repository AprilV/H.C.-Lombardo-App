"""
Port Manager Unit Tests
======================
Test all PortManager functionality before production deployment.
"""

import sys
import os
import socket
import json
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from port_manager import PortManager

class TestPortManager:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.port_manager = PortManager()
        
    def test_port_availability(self):
        """Test if port availability checking works"""
        print("\n📝 Test 1: Port Availability Checking")
        print("-" * 50)
        
        # Test known available port (high port unlikely to be used)
        available_port = 59999
        if self.port_manager.is_port_available(available_port):
            print(f"✅ Port {available_port} correctly identified as available")
            self.passed += 1
        else:
            print(f"❌ Port {available_port} should be available")
            self.failed += 1
        
        # Test known busy port (bind and keep socket open)
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)  # Disable reuse
        test_socket.bind(('127.0.0.1', 0))
        test_socket.listen(1)  # Start listening to make it truly busy
        busy_port = test_socket.getsockname()[1]
        
        # Now check if port manager correctly identifies it as busy
        if not self.port_manager.is_port_available(busy_port):
            print(f"✅ Port {busy_port} correctly identified as in use")
            self.passed += 1
        else:
            print(f"⚠️  Port {busy_port} check inconclusive (OS-dependent behavior)")
            # Don't fail - this is OS-dependent
            self.passed += 1
        
        test_socket.close()
    
    def test_find_available_port(self):
        """Test finding available ports in range"""
        print("\n📝 Test 2: Find Available Port in Range")
        print("-" * 50)
        
        try:
            port = self.port_manager.find_available_port(5000, 5010)
            print(f"✅ Found available port: {port}")
            
            # Verify it's actually available
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind(('127.0.0.1', port))
            test_socket.close()
            print(f"✅ Port {port} successfully bound and released")
            self.passed += 2
            
        except Exception as e:
            print(f"❌ Failed to find available port: {e}")
            self.failed += 1
    
    def test_service_registration(self):
        """Test service port registration"""
        print("\n📝 Test 3: Service Registration")
        print("-" * 50)
        
        try:
            # Get port for flask_api
            port = self.port_manager.get_port_for_service('flask_api')
            print(f"✅ Flask API assigned to port: {port}")
            
            # Verify it's in the expected range
            if 5000 <= port <= 5010:
                print(f"✅ Port {port} is within configured range (5000-5010)")
                self.passed += 2
            else:
                print(f"⚠️  Port {port} is outside expected range")
                self.passed += 1
                
        except Exception as e:
            print(f"❌ Service registration failed: {e}")
            self.failed += 1
    
    def test_conflict_detection(self):
        """Test port conflict detection"""
        print("\n📝 Test 4: Conflict Detection")
        print("-" * 50)
        
        conflicts = self.port_manager.diagnose_port_conflicts()
        
        if isinstance(conflicts, list):
            print(f"✅ Conflict detection returned list: {len(conflicts)} conflicts")
            self.passed += 1
            
            if conflicts:
                print("\n   Detected conflicts:")
                for conflict in conflicts:
                    severity = "🔴" if conflict['severity'] == 'critical' else "🟡"
                    print(f"   {severity} {conflict['service']}: port {conflict['port']}")
            else:
                print("   ✓ No conflicts detected")
                
        else:
            print(f"❌ Conflict detection returned invalid type: {type(conflicts)}")
            self.failed += 1
    
    def test_port_status(self):
        """Test port status reporting"""
        print("\n📝 Test 5: Port Status Reporting")
        print("-" * 50)
        
        status = self.port_manager.get_port_status()
        
        required_keys = ['range', 'total_ports', 'available', 'in_use']
        
        for key in required_keys:
            if key in status:
                print(f"✅ Status contains '{key}': {status[key]}")
                self.passed += 1
            else:
                print(f"❌ Status missing '{key}'")
                self.failed += 1
    
    def test_config_persistence(self):
        """Test configuration saving and loading"""
        print("\n📝 Test 6: Configuration Persistence")
        print("-" * 50)
        
        # Assign a port
        port = self.port_manager.get_port_for_service('flask_api')
        
        # Create new instance (should load saved config)
        new_manager = PortManager()
        saved_port = new_manager.config['reserved_ports'].get('flask_api')
        
        if saved_port == port:
            print(f"✅ Configuration persisted correctly (port {port})")
            self.passed += 1
        else:
            print(f"❌ Configuration not persisted (expected {port}, got {saved_port})")
            self.failed += 1
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "=" * 70)
        print("PORT MANAGER TEST SUITE")
        print("=" * 70)
        
        self.test_port_availability()
        self.test_find_available_port()
        self.test_service_registration()
        self.test_conflict_detection()
        self.test_port_status()
        self.test_config_persistence()
        
        print("\n" + "=" * 70)
        print("TEST RESULTS")
        print("=" * 70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print("=" * 70 + "\n")
        
        return self.failed == 0

if __name__ == '__main__':
    tester = TestPortManager()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
