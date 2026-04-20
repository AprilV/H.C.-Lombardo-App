"""
H.C. Lombardo NFL Analytics - Shutdown Manager
Gracefully stops all services in reverse order.
Run from project root: python shutdown.py
"""
import socket
import time
import sys

try:
    import psutil
except ImportError:
    print('[ERROR] psutil not installed. Run: pip install psutil')
    sys.exit(1)

def port_open(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = s.connect_ex(('127.0.0.1', port))
    s.close()
    return r == 0

def stop_port(port, name):
    print(f'\n[STOP] Stopping {name} (port {port})...')
    stopped = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.net_connections():
                if conn.laddr.port == port:
                    print(f'   Stopping {proc.info["name"]} (PID {proc.pid})...')
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                        print(f'   [OK] Stopped')
                    except psutil.TimeoutExpired:
                        proc.kill()
                        print(f'   [OK] Force stopped')
                    stopped = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            continue
    if not stopped:
        print(f'   [INFO] Nothing running on port {port}')
    time.sleep(1)

def stop_node():
    print('\n[STOP] Stopping React / Node processes...')
    found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'node' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info.get('cmdline') or [])
                if 'react-scripts' in cmdline or 'webpack' in cmdline:
                    print(f'   Stopping node (PID {proc.pid})...')
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    print(f'   [OK] Stopped')
                    found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not found:
        print('   [INFO] No React/Node processes found')
    time.sleep(1)

print()
print('=' * 60)
print('  H.C. LOMBARDO NFL ANALYTICS - SHUTDOWN')
print('=' * 60)

# Shutdown in reverse startup order — delays between each
stop_node()
time.sleep(2)
stop_port(3000, 'React Frontend')
time.sleep(2)
stop_port(8765, 'Dev Log Watcher')
time.sleep(2)
stop_port(5000, 'Flask API')
time.sleep(2)

# Verify
print('\n[CHECK] Verifying all ports are clear...')
all_clear = True
for port, name in [(3000, 'React'), (5000, 'Flask API'), (8765, 'Log Watcher')]:
    if port_open(port):
        print(f'   [WARN] Port {port} ({name}) still in use')
        all_clear = False
    else:
        print(f'   [OK] Port {port} ({name}) clear')

print()
print('=' * 60)
if all_clear:
    print('  SHUTDOWN COMPLETE')
else:
    print('  SHUTDOWN COMPLETE WITH WARNINGS')
print('=' * 60)
print()
input('Press Enter to close...')
