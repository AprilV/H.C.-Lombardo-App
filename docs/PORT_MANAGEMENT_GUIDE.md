# PORT MANAGEMENT & DEPLOYMENT GUIDE

**Developer:** April V  
**Date:** October 9, 2025  
**System:** H.C. Lombardo NFL Analytics Platform

---

## Table of Contents
1. [Problems & Solutions](#problems-we-encountered-today)
2. [DHCP-Inspired Port Management](#dhcp-inspired-port-management-system)
3. [Production Deployment](#production-deployment)
4. [Rollback Procedures](#rollback-procedures)
5. [Verification & Testing](#verification-checklist)

---

## Problems We Encountered Today

### 1. **React Not Listening on Port 3000**
- React compiled successfully but wasn't actually binding to the port
- `netstat` showed no process listening on 3000
- Multiple node processes running but none serving

### 2. **Flask API Process Management**
- Multiple Python processes competing for port 5000
- Background processes not properly terminated
- No clear visibility into which process owns which port

---

## Solutions & Best Practices

### Solution 1: Process Management Scripts

Create dedicated startup/shutdown scripts:

```powershell
# start_app.ps1
# Kill any existing processes
Stop-Process -Name python,node -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Flask API
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\IS330\H.C Lombardo App'; python api_server.py"

# Wait for API to start
Start-Sleep -Seconds 3

# Start React
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\IS330\H.C Lombardo App\frontend'; npm start"

Write-Host "✅ Both servers starting..." -ForegroundColor Green
Write-Host "Flask API: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "React App: http://localhost:3000" -ForegroundColor Cyan
```

```powershell
# stop_app.ps1
Write-Host "Stopping all app processes..." -ForegroundColor Yellow
Stop-Process -Name python,node -Force -ErrorAction SilentlyContinue
Write-Host "✅ All processes stopped" -ForegroundColor Green
```

---

### Solution 2: Port Checking Before Startup

Add port validation to your servers:

**For Flask (api_server.py):**
```python
import socket

def is_port_available(port):
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        return False

def kill_process_on_port(port):
    """Kill any process using the port (Windows)"""
    import subprocess
    try:
        # Find PID using the port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if 'LISTENING' in line:
                pid = line.strip().split()[-1]
                subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                print(f"✅ Killed process {pid} on port {port}")
    except Exception as e:
        print(f"⚠️  Could not kill process: {e}")

# Before app.run():
PORT = 5000
if not is_port_available(PORT):
    print(f"⚠️  Port {PORT} is in use. Attempting to free it...")
    kill_process_on_port(PORT)
    time.sleep(2)

if is_port_available(PORT):
    print(f"✅ Port {PORT} is available")
    app.run(host='127.0.0.1', port=PORT)
else:
    print(f"❌ Could not start - port {PORT} still in use")
```

---

### Solution 3: Environment-Based Configuration

**Create `.env` file:**
```bash
# Server Configuration
FLASK_PORT=5000
REACT_PORT=3000
FLASK_HOST=127.0.0.1

# Auto-kill processes on startup
AUTO_CLEANUP=true
```

**Update api_server.py:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv('FLASK_PORT', 5000))
AUTO_CLEANUP = os.getenv('AUTO_CLEANUP', 'false').lower() == 'true'

if AUTO_CLEANUP:
    kill_process_on_port(PORT)
```

---

### Solution 4: Docker Containers (BEST for Production)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_DB: nfl_analytics
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: aprilv120
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://postgres:aprilv120@postgres:5432/nfl_analytics
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
```

**Benefits:**
- No port conflicts (containers are isolated)
- Automatic cleanup on restart
- Easy to start/stop entire stack: `docker-compose up` / `docker-compose down`
- Works the same on all machines

---

### Solution 5: Process Monitoring Dashboard

**Create monitor_ports.py:**
```python
import subprocess
import time
from colorama import Fore, Style, init

init()

PORTS = {
    5000: 'Flask API',
    3000: 'React Frontend',
    5432: 'PostgreSQL'
}

def check_port(port):
    """Check if port is in use and return PID"""
    result = subprocess.run(
        f'netstat -ano | findstr :{port}',
        shell=True,
        capture_output=True,
        text=True
    )
    for line in result.stdout.split('\n'):
        if 'LISTENING' in line:
            pid = line.strip().split()[-1]
            return pid
    return None

def monitor():
    """Continuously monitor ports"""
    while True:
        print("\n" + "="*60)
        print("PORT STATUS MONITOR")
        print("="*60)
        
        for port, service in PORTS.items():
            pid = check_port(port)
            if pid:
                print(f"{Fore.GREEN}✅ {service:20s} Port {port} - PID {pid}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ {service:20s} Port {port} - NOT RUNNING{Style.RESET_ALL}")
        
        print("\nPress Ctrl+C to exit")
        time.sleep(5)

if __name__ == '__main__':
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n\nMonitor stopped")
```

---

### Solution 6: Systemd Services (Linux/WSL)

**For Linux or WSL, create systemd services:**

**/etc/systemd/system/hc-lombardo-api.service:**
```ini
[Unit]
Description=H.C. Lombardo NFL API
After=postgresql.service

[Service]
Type=simple
User=april
WorkingDirectory=/home/april/H.C Lombardo App
ExecStart=/usr/bin/python3 api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
# Start service
sudo systemctl start hc-lombardo-api

# Enable on boot
sudo systemctl enable hc-lombardo-api

# Check status
sudo systemctl status hc-lombardo-api

# View logs
sudo journalctl -u hc-lombardo-api -f
```

---

### Solution 7: Windows Task Scheduler

**Create scheduled task to start servers on login:**

```powershell
# Create task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File 'c:\IS330\H.C Lombardo App\start_app.ps1'"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
Register-ScheduledTask -TaskName "H.C. Lombardo App" -Action $action -Trigger $trigger -Principal $principal
```

---

### Solution 8: VS Code Tasks

**Create .vscode/tasks.json:**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Flask API",
      "type": "shell",
      "command": "python api_server.py",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Start React Frontend",
      "type": "shell",
      "command": "npm start",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Start Both Servers",
      "dependsOn": ["Start Flask API", "Start React Frontend"],
      "problemMatcher": []
    },
    {
      "label": "Stop All Servers",
      "type": "shell",
      "command": "Stop-Process -Name python,node -Force",
      "windows": {
        "command": "Stop-Process -Name python,node -Force"
      }
    }
  ]
}
```

**Usage:**
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "Start Both Servers"

---

### Solution 9: Health Check Endpoint

**Add to api_server.py:**
```python
import psutil
import time

@app.route('/api/system/health')
def system_health():
    """Comprehensive health check"""
    health = {
        'status': 'healthy',
        'timestamp': time.time(),
        'server': {
            'port': 5000,
            'pid': os.getpid(),
            'uptime': time.time() - START_TIME
        },
        'database': check_database_health(),
        'ports': {
            'flask': check_port_status(5000),
            'react': check_port_status(3000),
            'postgres': check_port_status(5432)
        }
    }
    return jsonify(health)

def check_port_status(port):
    """Check if port is listening"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return {
                'listening': True,
                'pid': conn.pid,
                'address': f"{conn.laddr.ip}:{conn.laddr.port}"
            }
    return {'listening': False}
```

---

## Recommended Setup for Your Project

### Immediate (Tonight):
1. **Create start_app.ps1 and stop_app.ps1** scripts
2. **Add port checking** to api_server.py
3. **Create monitor_ports.py** for visibility

### Short-term (This Week):
1. **Add .env file** for configuration
2. **Create VS Code tasks** for easy startup
3. **Install pip install python-dotenv psutil colorama**

### Long-term (Next Month):
1. **Learn Docker** - Best solution for port management
2. **Set up Docker Compose** for entire stack
3. **Add health check monitoring**

---

## Quick Reference Commands

```powershell
# Check what's using a port
netstat -ano | findstr :3000

# Kill process by PID
taskkill /F /PID <pid>

# Kill all Python/Node processes
Stop-Process -Name python,node -Force

# Find React process
Get-Process node | Where-Object {$_.StartTime -gt (Get-Date).AddHours(-1)}

# Check if port is available
Test-NetConnection -ComputerName localhost -Port 3000
```

---

## Your Current Pain Points & Solutions

| Problem | Current Impact | Solution |
|---------|---------------|----------|
| React compiles but doesn't bind | Have to restart multiple times | **Add port checker + auto-restart** |
| Multiple Python processes | Confusion about which is running | **Use PID tracking in api_server.py** |
| Manual process management | Time-consuming, error-prone | **Create start_app.ps1 script** |
| No visibility into port status | Hard to debug | **Use monitor_ports.py dashboard** |
| Processes left running after close | Ports blocked on next run | **Add cleanup to startup scripts** |

---

## DHCP-Inspired Port Management System

### Overview
April's innovation: Apply DHCP (Dynamic Host Configuration Protocol) principles to application-level port management.

**DHCP Concepts → Port Management:**
- IP address pool → Port range (5000-5010)
- DHCP lease → Port assignment tracking
- Conflict detection → Socket binding tests
- Automatic assignment → Find first available port

### Implementation Files
- `port_manager.py` - Core DHCP-style port management (300 lines)
- `api_server_v2.py` - Flask API with automatic port management
- `testbed/prototypes/port_management/` - Complete test suite (100% pass rate)

### Usage
```python
from port_manager import PortManager

pm = PortManager()
port = pm.get_port_for_service('flask_api')  # Auto-assigns from 5000-5010
print(f"Flask starting on port {port}")
```

**Documentation:** See `dr.foster.md` for complete technical details

---

## Production Deployment

### Prerequisites Checklist
- [ ] All testbed tests passed (100%)
- [ ] Backup created with timestamp
- [ ] Database accessible (PostgreSQL on 5432)
- [ ] No critical processes using ports 5000-5010
- [ ] React frontend ready

### Deployment Steps

**Step 1: Create Backup**
```powershell
cd "c:\IS330\H.C Lombardo App"
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
Copy-Item api_server.py "backups\api_server_backup_$timestamp.py"
```

**Step 2: Stop Current Production**
```powershell
Stop-Process -Name python* -Force
netstat -ano | findstr :5000  # Verify port is free
```

**Step 3: Deploy New Version**
```powershell
# Option A: Test new version (recommended)
python api_server_v2.py

# Option B: Replace production file
Copy-Item api_server_v2.py api_server.py
python api_server.py
```

**Step 4: Verify Deployment**
```powershell
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/port-status
curl http://127.0.0.1:5000/api/teams
```

---

## Rollback Procedures

### Critical Rollback (< 30 seconds)
**When:** API won't start, critical errors, service down

```powershell
# 1. Stop everything
Stop-Process -Name python* -Force

# 2. Start original version
cd "c:\IS330\H.C Lombardo App"
python api_server.py  # Original stable version

# 3. Verify
curl http://127.0.0.1:5000/health
```

### Standard Rollback (< 2 minutes)
**When:** Port conflicts, performance issues, unexpected behavior

```powershell
# 1. Stop current
Stop-Process -Name python* -Force

# 2. Restore from backup
cd "c:\IS330\H.C Lombardo App"
Copy-Item "backups\api_server_backup_YYYYMMDD_HHMMSS.py" api_server.py

# 3. Restart
python api_server.py

# 4. Verify
Invoke-RestMethod -Uri "http://127.0.0.1:5000/health"
```

### Return to Testbed
**When:** Need to debug issues before re-attempting deployment

```powershell
# 1. Rollback to stable version (use above)

# 2. Move to testbed
cd "c:\IS330\H.C Lombardo App\testbed\prototypes\port_management"

# 3. Run full test suite
python test_port_manager.py        # Unit tests
python test_flask_with_ports.py    # Flask integration
python test_full_api.py             # Complete API
python final_integration_test.py   # Full integration

# 4. Fix issues until 100% pass rate

# 5. Test live
python test_full_api.py --live

# 6. Only return to production after all tests pass
```

---

## Rollback Decision Matrix

| Symptom | Severity | Action | Timeline |
|---------|----------|--------|----------|
| API won't start | 🔴 CRITICAL | Immediate rollback | < 30 sec |
| Database connection fails | 🔴 CRITICAL | Immediate rollback | < 30 sec |
| Port conflicts persist | 🟡 HIGH | Standard rollback | < 2 min |
| Slow response times | 🟡 HIGH | Monitor, prepare rollback | 5 min |
| Minor logging errors | 🟢 LOW | Document, fix in testbed | Next cycle |
| React can't connect | 🔴 CRITICAL | Immediate rollback | < 30 sec |

---

## Verification Checklist

### Post-Deployment (Run within 5 minutes)

```powershell
Write-Host "=== DEPLOYMENT VERIFICATION ===" -ForegroundColor Cyan

# Test 1: Health
$health = Invoke-RestMethod -Uri "http://127.0.0.1:5000/health"
if ($health.status -eq "healthy") {
    Write-Host "✓ Health check passed" -ForegroundColor Green
} else {
    Write-Host "✗ ROLLBACK REQUIRED" -ForegroundColor Red
}

# Test 2: Port Status
$ports = Invoke-RestMethod -Uri "http://127.0.0.1:5000/port-status"
Write-Host "✓ Ports available: $($ports.port_range.available)" -ForegroundColor Green

# Test 3: Database
if ($health.teams -eq 32) {
    Write-Host "✓ Database: 32 teams" -ForegroundColor Green
} else {
    Write-Host "✗ ROLLBACK REQUIRED" -ForegroundColor Red
}

# Test 4: Teams Endpoint
$teams = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/teams"
if ($teams.Count -eq 32) {
    Write-Host "✓ Teams endpoint working" -ForegroundColor Green
} else {
    Write-Host "✗ ROLLBACK REQUIRED" -ForegroundColor Red
}
```

### Success Criteria
- ✅ All verification tests pass
- ✅ No errors in logs
- ✅ Response time < 200ms
- ✅ Port manager assigns port correctly
- ✅ React can fetch data

### Rollback Triggers
- ❌ Any verification test fails
- ❌ API unresponsive > 30 seconds
- ❌ Port conflicts unresolved
- ❌ Database errors
- ❌ React connection errors

---

## Best Practices (April's Rules)

1. ✅ **Always Test in Testbed First**
2. ✅ **Create Backup Before Deployment**
3. ✅ **Verify After Deployment**
4. ✅ **Have Rollback Plan Ready**
5. ✅ **Document Everything**
6. ✅ **Monitor for 5 Minutes Post-Deployment**
7. ✅ **Never Deploy Without 100% Test Pass**

**April's Golden Rule:** "If in doubt, rollback and debug in testbed. Production stability is paramount." 🎯

---

## Emergency Quick Reference

**Immediate Rollback:**
```powershell
Stop-Process -Name python* -Force
cd "c:\IS330\H.C Lombardo App"
python api_server.py
```

**Check Status:**
```powershell
curl http://127.0.0.1:5000/health
```

**View Logs:**
```powershell
cd "c:\IS330\H.C Lombardo App\logs"
Get-Content hc_lombardo_$(Get-Date -Format 'yyyyMMdd').log -Tail 50
```

---

## Next Steps - Pick Your Approach

**Option A: Simple (Good for Learning)**
- Create start_app.ps1 / stop_app.ps1
- Add port checking to api_server.py
- Use monitor_ports.py when debugging

**Option B: Intermediate (Good for Development)**
- Set up VS Code tasks
- Add .env configuration
- Create health check endpoint

**Option C: Professional (Good for Production)**
- Learn Docker basics
- Create docker-compose.yml
- Deploy as containers

**My Recommendation:** Start with Option A tonight, move to Option B this week, learn Option C over next month.

---

Would you like me to implement any of these solutions right now?
