# H.C. Lombardo App - Startup & Shutdown Guide

**Last Updated:** October 14, 2025

---

## 🚀 Quick Start

### Start Everything
```powershell
cd "c:\IS330\H.C Lombardo App"
python startup.py
```

### Stop Everything
```powershell
cd "c:\IS330\H.C Lombardo App"
python shutdown.py
```

---

## 📂 System Architecture

### Database Location
- **PostgreSQL 18** installed at: `C:\Program Files\PostgreSQL\18`
- **Data Directory**: `C:\Program Files\PostgreSQL\18\data`
- **Database Name**: `nfl_analytics`
- **Current Size**: ~8.3 MB
- **Tables**: `teams` (32 NFL teams)
- **Access**: localhost:5432 (user: postgres)

### Application Structure
```
c:\IS330\H.C Lombardo App\
├── startup.py              # Master startup orchestrator
├── shutdown.py             # Graceful shutdown manager
├── health_check.py         # Service health monitoring
├── live_data_updater.py    # ESPN API data fetcher
├── api_server.py           # Flask REST API (port 5000)
├── nfl_database_loader.py  # Database initialization (32 teams)
├── update_current_standings.py  # Manual standings update
├── frontend/               # React app (port 3000)
│   ├── src/
│   ├── public/
│   └── package.json
└── dr.foster/              # HTML dashboard for assignment
    └── index.html
```

---

## 🔧 What Startup Does (Automatic)

### Step 1: Prerequisites Check ✅
- PostgreSQL connection (localhost:5432)
- Python dependencies (flask, psycopg2, requests)
- Node.js/npm installation
- **Port 5000** availability (API)
- **Port 3000** availability (React)

### Step 2: Database Schema Validation ✅
- Verifies `teams` table exists
- Adds UNIQUE constraint on `abbreviation` column
- Removes duplicate teams if any
- **Expected**: Exactly 32 NFL teams

### Step 3: Live Data Update 🔄
- Fetches current standings from ESPN API
- Updates team records (wins/losses)
- **Runs automatically every 6 hours**
- Gracefully continues if ESPN is down

### Step 4: Start API Server 🌐
- Launches Flask API on **port 5000**
- Opens new PowerShell window
- Waits for `/health` endpoint to respond
- Verifies `/api/teams` returns data
- **Timeout**: 30 seconds with retries

### Step 5: Start React Frontend 🎨
- Launches React dev server on **port 3000**
- Opens new PowerShell window
- Waits for webpack compilation
- **First run**: 15-30 seconds
- **Subsequent runs**: 5-10 seconds

### Step 6: Open Browser 🌍
- Automatically opens http://localhost:3000
- Shows NFL team dashboard with live data

---

## 🛑 What Shutdown Does (Automatic)

### Step 1: Stop React Frontend
- Finds process on port 3000
- Graceful termination (SIGTERM)
- Verifies port is freed

### Step 2: Stop API Server
- Finds process on port 5000
- Graceful termination (SIGTERM)
- Verifies port is freed

### Step 3: Cleanup
- Terminates any orphaned Python processes
- Final verification of all ports

---

## 📊 Port Reference

| Service        | Port | Protocol | Purpose                          |
|----------------|------|----------|----------------------------------|
| PostgreSQL     | 5432 | TCP      | Database server                  |
| Flask API      | 5000 | HTTP     | REST API backend                 |
| React Frontend | 3000 | HTTP     | Web application UI               |

---

## 🔍 Verification Commands

### Check if services are running
```powershell
netstat -ano | findstr ":5000.*LISTENING"  # API Server
netstat -ano | findstr ":3000.*LISTENING"  # React Frontend
netstat -ano | findstr ":5432.*LISTENING"  # PostgreSQL
```

### Check database
```powershell
$env:PGPASSWORD="REDACTED_DB_PASSWORD"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d nfl_analytics -c "SELECT COUNT(*) FROM teams;"
```

### Test API manually
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health"
Invoke-RestMethod -Uri "http://localhost:5000/api/teams" | Select-Object -First 5
```

---

## 🚨 Troubleshooting

### Port Already in Use
**Symptom**: Startup fails with "Port 5000/3000 occupied"

**Solution**:
```powershell
# Run shutdown first
python shutdown.py

# Or manually kill processes
netstat -ano | findstr ":5000"  # Find PID
taskkill /F /PID <PID>
```

### Database Connection Failed
**Symptom**: "Database not available"

**Check**:
1. Is PostgreSQL running? Check Windows Services
2. Can you connect manually?
   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d nfl_analytics
   ```

### React Won't Start
**Symptom**: Webpack compilation errors

**Solution**:
```powershell
cd frontend
npm install  # Reinstall dependencies
npm start    # Try manually
```

### ESPN Data Not Updating
**Symptom**: Team records are stale

**Manual Update**:
```powershell
python update_current_standings.py  # Use pre-defined records
# OR
python espn_data_fetcher.py  # Fetch from ESPN API
```

---

## 🔐 Security Notes

### Database Credentials
- **Username**: postgres
- **Password**: REDACTED_DB_PASSWORD (stored in environment/code)
- **Access**: localhost only (not exposed to network)

### Recommendation for Production
1. Move password to `.env` file
2. Add `.env` to `.gitignore`
3. Use environment variables:
   ```powershell
   $env:DB_PASSWORD="REDACTED_DB_PASSWORD"
   ```

---

## 📝 Manual Operations

### Reload Database with Fresh Data
```powershell
cd "c:\IS330\H.C Lombardo App"
python nfl_database_loader.py
python update_current_standings.py
```

### Update Only Live Standings
```powershell
python update_current_standings.py
```

### Fetch Latest ESPN Data
```powershell
python espn_data_fetcher.py
```

### View Logs
```powershell
cd logs
Get-Content hc_lombardo_20251014.log -Tail 50
```

---

## 🎯 Production Checklist

Before deploying or demonstrating:

- [ ] Run `python shutdown.py` to clean state
- [ ] Verify database has 32 teams
- [ ] Run `python startup.py`
- [ ] Wait for "✅ ALL SERVICES RUNNING"
- [ ] Verify browser opens to http://localhost:3000
- [ ] Check that team data appears
- [ ] Test a few API endpoints manually

---

## 📞 Quick Reference Commands

```powershell
# Full System
python startup.py          # Start everything
python shutdown.py         # Stop everything

# Data Management
python nfl_database_loader.py        # Reset to base 32 teams
python update_current_standings.py   # Update with current records
python espn_data_fetcher.py          # Fetch live from ESPN

# Manual Server Start (for debugging)
python api_server.py       # API only (port 5000)
cd frontend; npm start     # React only (port 3000)

# Database Access
$env:PGPASSWORD="REDACTED_DB_PASSWORD"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d nfl_analytics
```

---

## 🔄 System Startup Flow

```
startup.py
    ↓
Prerequisites Check
    ↓
Database Schema Validation
    ↓
Live Data Update (ESPN API)
    ↓
Start API Server (port 5000)
    ↓ (wait for health check)
Start React Frontend (port 3000)
    ↓ (wait for webpack)
Open Browser
    ↓
✅ SYSTEM READY
```

---

**Questions or Issues?**
- Check logs in `logs/` directory
- Review error messages in terminal windows
- Run health checks to isolate problem
- Verify all prerequisites are met

**Last Test**: October 14, 2025 12:48 PM - All systems operational ✅
