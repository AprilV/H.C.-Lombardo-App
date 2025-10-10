# H.C. Lombardo NFL Analytics Platform

Professional NFL analytics system for gambling line generation and statistical analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 18
- Node.js (for React frontend)

### Start Production System

**Terminal 1 - Backend API:**
```powershell
cd "c:\IS330\H.C Lombardo App"
python api_server.py
```

**Terminal 2 - Frontend:**
```powershell
cd "c:\IS330\H.C Lombardo App\frontend"
npm start
```

**Access:** http://localhost:3000

## 📊 System Architecture

```
React Frontend (Port 3000) ←→ Flask API (Port 5000) ←→ PostgreSQL Database
```

## 📁 Project Structure

- `api_server.py` - Production Flask REST API
- `frontend/` - Production React application
- `app.py` - Original Flask dashboard
- `logging_config.py` - Logging system
- `log_viewer.py` - Log viewing utility
- `testbed/` - Testing and development area

## 📖 Documentation

- **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)** - Production system details
- **[testbed/step_by_step/](testbed/step_by_step/)** - Testing methodology & results

## 🔧 Tools

- **View Logs:** `python log_viewer.py`
- **Quick Logs:** `python quick_logs.py`
- **Database Check:** `python check_database.py`

## ✅ Status

**Production:** ✅ Operational  
**Backend API:** Running on port 5000  
**Frontend:** Running on port 3000  
**Database:** 32 NFL teams loaded

---

Built with slow, methodical, tested approach. See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for details.
