"""
H.C. Lombardo NFL Analytics - Startup Manager
Sequential startup with health checks. Each service waits for the previous.
Run from project root: python startup.py
"""
import subprocess
import socket
import time
import sys
import os
from pathlib import Path

ROOT    = Path(__file__).parent
VENV_PY = Path('C:/Users/april/AppData/Local/Python/bin/python3.exe')


def port_open(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = s.connect_ex(('127.0.0.1', port))
    s.close()
    return r == 0

def wait_port(port, name, timeout=90):
    print(f'   Waiting for {name} on port {port}...')
    for i in range(timeout):
        if port_open(port):
            print(f'   [OK] {name} is up')
            return True
        time.sleep(1)
    print(f'   [ERROR] {name} did not start within {timeout}s')
    return False

def open_window(title, command):
    subprocess.Popen(
        ['powershell', '-NoExit', '-Command',
         f"$host.UI.RawUI.WindowTitle = '{title}'; {command}"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

print()
print('=' * 60)
print('  H.C. LOMBARDO NFL ANALYTICS - STARTUP')
print('=' * 60)

# ── Step 1: Database ───────────────────────────────────────────
print('\n[1/5] Checking database...')
try:
    import psycopg2
    conn = psycopg2.connect(
        host='localhost', port=5432,
        database='nfl_analytics', user='postgres', password='aprilv120'
    )
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM teams')
    count = cur.fetchone()[0]
    conn.close()
    print(f'   [OK] PostgreSQL ready — {count} teams loaded')
except Exception as e:
    print(f'   [ERROR] Database not available: {e}')
    print('   Make sure PostgreSQL is running then try again.')
    input('\nPress Enter to exit...')
    sys.exit(1)

# ── Step 2: Flask API ──────────────────────────────────────────
print('\n[2/5] Starting Flask API server...')
if port_open(5000):
    print('   [OK] API already running on port 5000')
else:
    py = str(VENV_PY)
    open_window('H.C. Lombardo API', f"cd '{ROOT}'; & '{py}' api_server.py")
    if not wait_port(5000, 'Flask API', 30):
        print('   [ERROR] API failed to start. Check the API window for errors.')
        input('\nPress Enter to exit...')
        sys.exit(1)

# ── Step 3: Log Watcher ────────────────────────────────────────
print('\n[3/5] Starting Dev Log Watcher...')
if port_open(8765):
    print('   [OK] Log watcher already running on port 8765')
else:
    py = str(VENV_PY)
    open_window('H.C. Lombardo Dev Log', f"cd '{ROOT}'; & '{py}' log_watcher.py")
    wait_port(8765, 'Log Watcher', 15)

# ── Step 4: Live Data Updater ──────────────────────────────────
print('\n[4/5] Starting Live Data Updater...')
py = str(VENV_PY)
open_window('H.C. Lombardo Data Updater',
            f"cd '{ROOT}'; & '{py}' live_data_updater.py --continuous 15")
print('   [OK] Data updater started (updates every 15 minutes)')
time.sleep(2)

# ── Step 5: React Frontend ─────────────────────────────────────
print('\n[5/5] Starting React frontend...')
if port_open(3000):
    print('   [OK] React already running on port 3000')
else:
    open_window('H.C. Lombardo Frontend',
                f"cd '{ROOT}\\frontend'; $env:BROWSER='none'; npm start")
    if not wait_port(3000, 'React', 90):
        print('   [ERROR] React failed to start. Check the Frontend window.')
        input('\nPress Enter to exit...')
        sys.exit(1)

# ── Done ───────────────────────────────────────────────────────
subprocess.Popen(['cmd', '/c', 'start', 'http://localhost:3000'], shell=True)

print()
print('=' * 60)
print('  ALL SERVICES RUNNING')
print('=' * 60)
print(f'  App:      http://localhost:3000')
print(f'  API:      http://localhost:5000/health')
print(f'  Logbook:  http://localhost:8765/')
print('=' * 60)
print()
input('Press Enter to exit this window (services keep running)...')
