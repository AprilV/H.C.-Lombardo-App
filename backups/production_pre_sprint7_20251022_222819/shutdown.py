"""
Production Shutdown Manager
Gracefully stops all system services
"""
import subprocess
import psutil
import time
import sys

class ShutdownManager:
    """Manages graceful shutdown of all system components"""
    
    def __init__(self):
        self.stopped_processes = []
    
    def find_processes_by_port(self, port: int) -> list:
        """Find all processes listening on a specific port"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get connections separately (not available in process_iter attrs)
                connections = proc.connections()
                if connections:
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr.port == port:
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'port': port
                            })
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
        
        return processes
    
    def find_python_processes(self, script_pattern: str = None) -> list:
        """Find Python processes, optionally filtered by script name"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    
                    if script_pattern is None or script_pattern in cmdline:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def find_node_processes(self) -> list:
        """Find Node.js processes (React dev server)"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'node' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    
                    # Look for React dev server patterns
                    if 'react-scripts' in cmdline or 'webpack' in cmdline:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def stop_process(self, pid: int, name: str, timeout: int = 5) -> bool:
        """Stop a process gracefully, force if necessary"""
        try:
            proc = psutil.Process(pid)
            
            # Try graceful termination first
            print(f"   Stopping {name} (PID: {pid})...")
            proc.terminate()
            
            # Wait for graceful shutdown
            try:
                proc.wait(timeout=timeout)
                print(f"   ✅ {name} stopped gracefully")
                return True
            except psutil.TimeoutExpired:
                # Force kill if still running
                print(f"   ⏳ Forcing {name} to stop...")
                proc.kill()
                proc.wait(timeout=2)
                print(f"   ✅ {name} force stopped")
                return True
                
        except psutil.NoSuchProcess:
            print(f"   ℹ️  {name} already stopped")
            return True
        except psutil.AccessDenied:
            print(f"   ❌ Access denied stopping {name}")
            return False
        except Exception as e:
            print(f"   ❌ Error stopping {name}: {str(e)}")
            return False
    
    def shutdown_api_server(self) -> bool:
        """Shutdown Flask API server on port 5000"""
        print("\n🛑 Shutting down API server...")
        
        # Find by port
        processes = self.find_processes_by_port(5000)
        
        if not processes:
            print("   ℹ️  No API server running on port 5000")
            return True
        
        success = True
        for proc in processes:
            if not self.stop_process(proc['pid'], f"API Server ({proc['name']})"):
                success = False
        
        return success
    
    def shutdown_react_frontend(self) -> bool:
        """Shutdown React dev server on port 3000"""
        print("\n🛑 Shutting down React frontend...")
        
        # Find by port
        processes = self.find_processes_by_port(3000)
        
        if not processes:
            print("   ℹ️  No React server running on port 3000")
            return True
        
        success = True
        for proc in processes:
            if not self.stop_process(proc['pid'], f"React Server ({proc['name']})"):
                success = False
        
        # Also stop Node processes
        node_procs = self.find_node_processes()
        for proc in node_procs:
            if not self.stop_process(proc['pid'], f"Node.js ({proc['name']})"):
                success = False
        
        return success
    
    def cleanup_python_processes(self) -> bool:
        """Stop any remaining Python processes related to the app"""
        print("\n🧹 Cleaning up Python processes...")
        
        # Find api_server.py processes
        api_procs = self.find_python_processes('api_server.py')
        
        if not api_procs:
            print("   ℹ️  No additional Python processes found")
            return True
        
        success = True
        for proc in api_procs:
            if not self.stop_process(proc['pid'], "Python (api_server)"):
                success = False
        
        return success
    
    def verify_shutdown(self) -> bool:
        """Verify all services are stopped"""
        print("\n🔍 Verifying shutdown...")
        
        issues = []
        
        # Check ports
        for port, name in [(5000, "API"), (3000, "React")]:
            procs = self.find_processes_by_port(port)
            if procs:
                issues.append(f"Port {port} ({name}) still in use")
        
        if issues:
            print("   ⚠️  Issues detected:")
            for issue in issues:
                print(f"      • {issue}")
            return False
        else:
            print("   ✅ All services stopped successfully")
            return True
    
    def run_shutdown(self) -> bool:
        """Run complete shutdown sequence"""
        print("\n" + "="*70)
        print("🛑 H.C. LOMBARDO APP - GRACEFUL SHUTDOWN")
        print("="*70)
        
        # Shutdown in reverse order
        self.shutdown_react_frontend()
        time.sleep(1)
        
        self.shutdown_api_server()
        time.sleep(1)
        
        self.cleanup_python_processes()
        time.sleep(1)
        
        # Verify
        success = self.verify_shutdown()
        
        print("\n" + "="*70)
        if success:
            print("✅ SHUTDOWN COMPLETE")
        else:
            print("⚠️  SHUTDOWN COMPLETED WITH WARNINGS")
            print("   Some processes may still be running")
            print("   💡 Try running with --force for aggressive cleanup")
        print("="*70 + "\n")
        
        return success

def main():
    manager = ShutdownManager()
    
    # Check for force flag
    force = '--force' in sys.argv
    
    if force:
        print("\n⚠️  FORCE MODE: Will aggressively stop all related processes\n")
        time.sleep(2)
    
    success = manager.run_shutdown()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
