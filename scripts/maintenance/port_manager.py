"""
PORT MANAGEMENT SYSTEM
======================
Prevents port conflicts by managing a reserved port range for the application.

Concept: Similar to DHCP in networking, we reserve a range of ports and 
automatically assign available ports when services start.
"""

import socket
import json
import os
from pathlib import Path
from datetime import datetime

class PortManager:
    """
    Manages port allocation for multi-service applications.
    
    Features:
    - Reserved port range (configurable)
    - Automatic port discovery
    - Port conflict detection
    - Port reservation tracking
    - Graceful fallback
    """
    
    def __init__(self, config_file='.port_config.json'):
        self.config_file = Path(__file__).parent / config_file
        self.config = self._load_config()
        
    def _load_config(self):
        """Load or create port configuration"""
        default_config = {
            'port_range': {
                'start': 5000,
                'end': 5010,
                'description': 'Reserved port range for H.C. Lombardo App'
            },
            'services': {
                'flask_api': {
                    'preferred_port': 5000,
                    'required': True,
                    'description': 'Flask REST API'
                },
                'react_dev': {
                    'preferred_port': 3000,
                    'required': True,
                    'description': 'React Development Server'
                },
                'postgresql': {
                    'preferred_port': 5432,
                    'required': True,
                    'description': 'PostgreSQL Database'
                }
            },
            'reserved_ports': {},
            'last_updated': None
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config):
        """Save configuration to file"""
        config['last_updated'] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.config = config
    
    def is_port_available(self, port):
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False
    
    def find_available_port(self, start_port=None, end_port=None):
        """Find the first available port in range"""
        start = start_port or self.config['port_range']['start']
        end = end_port or self.config['port_range']['end']
        
        for port in range(start, end + 1):
            if self.is_port_available(port):
                return port
        return None
    
    def get_port_for_service(self, service_name):
        """
        Get an available port for a service.
        
        Strategy:
        1. Try preferred port
        2. Try last used port (if recorded)
        3. Find next available in range
        4. Return None if none available
        """
        service = self.config['services'].get(service_name)
        if not service:
            raise ValueError(f"Unknown service: {service_name}")
        
        # Try preferred port first
        preferred = service['preferred_port']
        if self.is_port_available(preferred):
            self._reserve_port(service_name, preferred)
            return preferred
        
        # Try last used port
        last_port = self.config['reserved_ports'].get(service_name)
        if last_port and self.is_port_available(last_port):
            self._reserve_port(service_name, last_port)
            return last_port
        
        # Find any available port in range
        available = self.find_available_port()
        if available:
            self._reserve_port(service_name, available)
            return available
        
        # No ports available
        if service['required']:
            raise RuntimeError(f"No available ports for required service: {service_name}")
        return None
    
    def _reserve_port(self, service_name, port):
        """Record port reservation"""
        self.config['reserved_ports'][service_name] = port
        self._save_config(self.config)
    
    def release_port(self, service_name):
        """Release a reserved port"""
        if service_name in self.config['reserved_ports']:
            del self.config['reserved_ports'][service_name]
            self._save_config(self.config)
    
    def get_port_status(self):
        """Get status of all ports in range"""
        start = self.config['port_range']['start']
        end = self.config['port_range']['end']
        
        status = {
            'range': f"{start}-{end}",
            'total_ports': end - start + 1,
            'available': 0,
            'in_use': 0,
            'ports': {}
        }
        
        for port in range(start, end + 1):
            available = self.is_port_available(port)
            status['ports'][port] = 'available' if available else 'in_use'
            if available:
                status['available'] += 1
            else:
                status['in_use'] += 1
        
        return status
    
    def diagnose_port_conflicts(self):
        """Diagnose and report port conflicts"""
        conflicts = []
        
        for service_name, service_config in self.config['services'].items():
            preferred = service_config['preferred_port']
            if not self.is_port_available(preferred):
                conflicts.append({
                    'service': service_name,
                    'port': preferred,
                    'description': service_config['description'],
                    'severity': 'critical' if service_config['required'] else 'warning'
                })
        
        return conflicts


# Flask integration
def create_flask_app_with_port_manager():
    """
    Example: Flask app with automatic port management
    """
    from flask import Flask
    
    app = Flask(__name__)
    port_mgr = PortManager()
    
    # Get available port
    port = port_mgr.get_port_for_service('flask_api')
    
    @app.route('/port-status')
    def port_status():
        return port_mgr.get_port_status()
    
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'port': port,
            'service': 'flask_api'
        }
    
    return app, port


# Startup script with port management
def start_with_port_management():
    """
    Startup script that handles port conflicts gracefully
    """
    port_mgr = PortManager()
    
    print("=" * 70)
    print("H.C. LOMBARDO APP - INTELLIGENT PORT MANAGEMENT")
    print("=" * 70)
    
    # Check for conflicts
    conflicts = port_mgr.diagnose_port_conflicts()
    if conflicts:
        print("\n⚠️  PORT CONFLICTS DETECTED:")
        for conflict in conflicts:
            print(f"  - {conflict['service']} (port {conflict['port']}): {conflict['severity']}")
        print("\n🔧 Attempting automatic resolution...\n")
    
    # Get ports for all services
    services_to_start = ['flask_api', 'react_dev']
    port_assignments = {}
    
    for service in services_to_start:
        try:
            port = port_mgr.get_port_for_service(service)
            port_assignments[service] = port
            print(f"✓ {service}: Port {port} assigned")
        except Exception as e:
            print(f"✗ {service}: {e}")
    
    # Display final status
    print("\n" + "=" * 70)
    print("PORT ALLOCATION COMPLETE")
    print("=" * 70)
    
    status = port_mgr.get_port_status()
    print(f"Range: {status['range']}")
    print(f"Available: {status['available']}/{status['total_ports']}")
    print(f"In Use: {status['in_use']}/{status['total_ports']}")
    
    return port_assignments


# Command-line interface
if __name__ == "__main__":
    import sys
    
    port_mgr = PortManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            status = port_mgr.get_port_status()
            print(json.dumps(status, indent=2))
        
        elif command == "check":
            conflicts = port_mgr.diagnose_port_conflicts()
            if conflicts:
                print("CONFLICTS FOUND:")
                for c in conflicts:
                    print(f"  {c['service']}: port {c['port']} ({c['severity']})")
            else:
                print("✓ No conflicts detected")
        
        elif command == "assign":
            if len(sys.argv) > 2:
                service = sys.argv[2]
                port = port_mgr.get_port_for_service(service)
                print(f"{service}: {port}")
            else:
                print("Usage: python port_manager.py assign <service_name>")
        
        elif command == "release":
            if len(sys.argv) > 2:
                service = sys.argv[2]
                port_mgr.release_port(service)
                print(f"Released port for {service}")
            else:
                print("Usage: python port_manager.py release <service_name>")
        
        else:
            print("Unknown command. Available: status, check, assign, release")
    else:
        # Run startup sequence
        start_with_port_management()
