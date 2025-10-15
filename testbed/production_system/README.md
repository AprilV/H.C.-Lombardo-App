# Production System - Testbed

Production-grade startup, shutdown, and data management system for H.C. Lombardo App.

## 🎯 Purpose

This testbed validates production deployment practices:
- Sequential startup with health checks
- Live data updates from ESPN API
- Graceful shutdown procedures
- Service verification and retry logic

## 📁 Components

### 1. `startup.py` - Production Startup Manager
**Purpose**: Orchestrates complete system startup with verification

**Features**:
- ✅ Prerequisite checking (database, dependencies, ports)
- ✅ Automatic data refresh from ESPN API
- ✅ Sequential service startup (API → React)
- ✅ Health checks with retries and timeouts
- ✅ Automatic browser launch
- ✅ Clear status reporting

**Usage**:
```powershell
cd "c:\IS330\H.C Lombardo App\testbed\production_system"
python startup.py
```

**What it does**:
1. Checks PostgreSQL database connection
2. Verifies Python/Node dependencies
3. Updates NFL data from ESPN API
4. Starts Flask API server (port 5000)
5. Waits for API to be ready (with retries)
6. Starts React frontend (port 3000)
7. Waits for React to compile and serve
8. Runs final health check on all services
9. Opens browser to http://localhost:3000

### 2. `shutdown.py` - Production Shutdown Manager
**Purpose**: Gracefully stops all system services

**Features**:
- ✅ Finds processes by port (5000, 3000)
- ✅ Graceful termination with fallback to force kill
- ✅ Cleans up Python and Node processes
- ✅ Verification that all services stopped
- ✅ Force mode for stubborn processes

**Usage**:
```powershell
# Normal shutdown
python shutdown.py

# Force shutdown (aggressive)
python shutdown.py --force
```

**What it does**:
1. Finds React dev server (port 3000) and Node.js processes
2. Terminates React gracefully (5s timeout)
3. Finds API server (port 5000) and Python processes
4. Terminates API gracefully (5s timeout)
5. Force kills any remaining related processes
6. Verifies all ports are freed

### 3. `health_check.py` - Service Health Monitor
**Purpose**: Verifies service availability with retries

**Features**:
- ✅ Database connectivity testing
- ✅ API endpoint health checks
- ✅ React frontend availability
- ✅ Configurable retries and timeouts
- ✅ Detailed status reporting

**Usage**:
```powershell
# Run full health check
python health_check.py
```

**What it checks**:
- PostgreSQL database connection and team count
- API /health endpoint response
- API /api/teams endpoint with data validation
- React dev server on localhost:3000

**Exit codes**:
- `0` = All checks passed
- `1` = One or more checks failed

### 4. `live_data_updater.py` - ESPN Data Fetcher
**Purpose**: Fetches and updates live NFL standings

**Features**:
- ✅ ESPN API integration
- ✅ Automatic standings extraction
- ✅ Database upsert (update or insert)
- ✅ Continuous update mode
- ✅ Error handling and retry logic

**Usage**:
```powershell
# Single update
python live_data_updater.py

# Continuous updates every 30 minutes
python live_data_updater.py --continuous 30

# Continuous updates every 2 hours
python live_data_updater.py --continuous 120
```

**Data fetched**:
- Team names and abbreviations
- Current win-loss records
- Points per game (PPG)
- Points allowed (PA)
- Season information

## 🚀 Quick Start

### First-Time Setup
```powershell
# Navigate to testbed
cd "c:\IS330\H.C Lombardo App\testbed\production_system"

# Install dependencies (if needed)
pip install psutil requests psycopg2 flask

# Start the system
python startup.py
```

### Daily Usage
```powershell
# Start everything
python startup.py

# When done, shutdown everything
python shutdown.py
```

## 🧪 Testing Procedures

### Test 1: Basic Startup/Shutdown
```powershell
# Test startup
python startup.py
# Wait for "STARTUP COMPLETE" message
# Verify browser opens to http://localhost:3000

# Test shutdown
python shutdown.py
# Verify "SHUTDOWN COMPLETE" message
```

### Test 2: Health Checks
```powershell
# With services running
python health_check.py
# Should show all green checkmarks

# With services stopped
python health_check.py
# Should show connection errors and exit code 1
```

### Test 3: Live Data Update
```powershell
# Update data from ESPN
python live_data_updater.py
# Should fetch 32 teams and update database

# Verify in database
$env:PGPASSWORD="aprilv120"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d nfl_analytics -c "SELECT name, wins, losses FROM teams ORDER BY wins DESC LIMIT 5;"
```

### Test 4: Recovery from Failures

**Scenario A: API fails to start**
```powershell
# Manually occupy port 5000
python -m http.server 5000
# In another terminal
python startup.py
# Should detect port in use and try to use existing service or fail gracefully
```

**Scenario B: Database offline**
```powershell
# Stop PostgreSQL service
Stop-Service postgresql-x64-18
# Try startup
python startup.py
# Should fail with clear database connection error
```

**Scenario C: React takes too long**
```powershell
# Startup gives React 60 seconds to compile
# If it exceeds, should show timeout error
# Manually check: netstat -ano | findstr 3000
```

## 🔍 Monitoring

### Check Running Services
```powershell
# Check ports
netstat -ano | findstr "5000 3000"

# Check processes
Get-Process | Where-Object {$_.ProcessName -like '*python*' -or $_.ProcessName -like '*node*'}
```

### View Logs
```powershell
# API server logs (if running in terminal window)
# React logs (if running in terminal window)

# Or redirect to files in startup.py
```

## 🛠️ Configuration

### Timeouts and Retries
Edit in respective files:

**startup.py**:
```python
self.health_checker = HealthChecker(max_retries=10, retry_delay=2)
```

**health_check.py**:
```python
def __init__(self, max_retries=10, retry_delay=2):
```

**live_data_updater.py**:
```python
response = self.session.get(url, timeout=10)
```

### Database Connection
All files use:
```python
db_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'nfl_analytics',
    'user': 'postgres',
    'password': 'aprilv120'
}
```

## 📊 Expected Behavior

### Successful Startup Output
```
======================================================================
🏈 H.C. LOMBARDO APP - PRODUCTION STARTUP
======================================================================

🔍 CHECKING PREREQUISITES
======================================================================
✅ Database ready: Connected (32 teams)
✅ Python dependencies installed
✅ npm version: 10.x.x
✅ Ports available

📊 UPDATING NFL DATA
======================================================================
📡 Fetching live data from ESPN API...
✅ Fetched data for 32 teams
✅ Updated 32 teams in database

🚀 STARTING API SERVER
======================================================================
✅ API fully operational: 32 teams available

🎨 STARTING REACT FRONTEND
======================================================================
✅ React frontend ready

🏥 FINAL SYSTEM HEALTH CHECK
======================================================================
✅ database: Connected (32 teams)
✅ api_health: HTTP 200
✅ api_teams: 32 teams available
✅ react_frontend: HTTP 200

✅ STARTUP COMPLETE - ALL SYSTEMS OPERATIONAL
```

### Successful Shutdown Output
```
======================================================================
🛑 H.C. LOMBARDO APP - GRACEFUL SHUTDOWN
======================================================================

🛑 Shutting down React frontend...
   Stopping React Server (node.exe) (PID: 12345)...
   ✅ React Server stopped gracefully

🛑 Shutting down API server...
   Stopping API Server (python.exe) (PID: 67890)...
   ✅ API Server stopped gracefully

🔍 Verifying shutdown...
   ✅ All services stopped successfully

✅ SHUTDOWN COMPLETE
```

## 🐛 Troubleshooting

### "Database not available"
```powershell
# Check PostgreSQL is running
Get-Service postgresql-x64-18

# Start if stopped
Start-Service postgresql-x64-18

# Test connection manually
$env:PGPASSWORD="aprilv120"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d nfl_analytics -c "SELECT 1"
```

### "Port already in use"
```powershell
# Find what's using the port
netstat -ano | findstr "5000"

# Kill the process
taskkill /F /PID <PID>
```

### "React failed to start"
```powershell
# Check npm install was done
cd "c:\IS330\H.C Lombardo App\frontend"
npm install

# Try manual start to see errors
npm start
```

## 📝 Best Practices Implemented

1. **Sequential Startup**: Services start in dependency order
2. **Health Checks**: Every service verified before proceeding
3. **Retry Logic**: Automatic retries with exponential backoff
4. **Graceful Degradation**: ESPN failure doesn't prevent startup
5. **Clean Shutdown**: Processes terminated gracefully
6. **Error Reporting**: Clear, actionable error messages
7. **Idempotent**: Can run multiple times safely
8. **Verification**: Post-startup health check confirms all systems

## 🚀 Next Steps

After testbed validation:
1. Move scripts to project root
2. Create Windows shortcuts for startup/shutdown
3. Add to Windows Task Scheduler for auto-start
4. Configure continuous data updates (cron/scheduled task)
5. Add logging to files for production monitoring

## 📦 Dependencies

```
Python packages:
- psycopg2 (database)
- requests (HTTP/API)
- flask (web server)
- psutil (process management)

System:
- PostgreSQL 18
- Node.js + npm
- Python 3.11+
```

## ⚡ Performance

- Startup time: 15-45 seconds (depending on React compilation)
- Health check: 2-5 seconds per service
- Data update: 5-10 seconds from ESPN
- Shutdown: 5-10 seconds

## 🎓 Learning Outcomes

This testbed demonstrates:
- Production deployment best practices
- Service orchestration patterns
- Health monitoring and observability
- Graceful startup and shutdown
- Error handling and recovery
- Integration testing strategies
