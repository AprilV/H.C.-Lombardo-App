# 🎬 Live Data Integration Demo Script
**H.C. Lombardo NFL Analytics Dashboard**

---

## 🎯 Demo: Hybrid Live/Static Data System

This script shows both modes of operation for Dr. Foster.

---

### Part 1: Static Mode (API Offline) 📊

**What to Say:**
> "First, let me show you the dashboard works perfectly even without the backend running. This ensures reliability for presentations."

**Steps:**
1. Make sure NO API server is running:
   ```powershell
   # Check if running
   netstat -ano | findstr :5000
   
   # If running, stop it
   Stop-Process -Name python* -Force
   ```

2. Open dashboard:
   ```powershell
   Start-Process "c:\IS330\H.C Lombardo App\testbed\dr_foster_interface_v2\index.html"
   ```

3. **Point out:**
   - Bottom-right shows **"📊 Static Data"** in blue
   - All stats display correctly
   - Dashboard fully functional
   - No errors or broken features

4. **Open browser console (F12):**
   - Shows: `📊 API offline - using static data`
   - Proves graceful fallback

---

### Part 2: Live Mode (API Running) 🟢

**What to Say:**
> "Now let me demonstrate real-time integration with our PostgreSQL database through the Flask API."

**Steps:**
1. Start the API server:
   ```powershell
   cd "c:\IS330\H.C Lombardo App"
   python api_server.py
   ```
   
   **Wait for:**
   ```
   * Running on http://127.0.0.1:5000
   * Running on http://localhost:5000
   ```

2. **Test API is working:**
   ```powershell
   # In a NEW PowerShell window
   Invoke-RestMethod -Uri "http://localhost:5000/api/teams/count" -Method Get
   ```
   
   **Should see:**
   ```json
   {
       "count": 32,
       "expected": 32,
       "status": "correct"
   }
   ```

3. **Refresh the dashboard:**
   - Press `Ctrl + Shift + R` (hard refresh)
   - OR close and reopen: 
     ```powershell
     Start-Process "c:\IS330\H.C Lombardo App\testbed\dr_foster_interface_v2\index.html"
     ```

4. **Point out:**
   - Bottom-right now shows **"🟢 Live Data"** in green
   - Hover over indicator: "Connected to Flask API (Port 5000)"
   - Stats now pulling from actual database

5. **Open browser console (F12):**
   - Shows: `🚀 Initializing H.C. Lombardo Dashboard...`
   - Shows: `📊 Dashboard updated: 32 teams tracked`
   - Proves live connection

---

### Part 3: Failover Demo (The Impressive Part!) 💪

**What to Say:**
> "What makes this truly production-ready is the automatic failover. Watch what happens if the API goes down mid-session."

**Steps:**
1. With dashboard open in **Live Mode** (🟢):
   - Show the green indicator
   - Show live data in console

2. **Stop the API server:**
   ```powershell
   # In the PowerShell running api_server.py
   Ctrl + C
   # OR
   Stop-Process -Name python* -Force
   ```

3. **Refresh the dashboard:**
   ```powershell
   # In browser, press F5 or Ctrl + R
   ```

4. **Point out:**
   - Indicator automatically switches to **"📊 Static Data"**
   - Dashboard continues working perfectly
   - No errors, no broken features
   - User never sees a failure

5. **Explain:**
   > "This graceful degradation ensures Dr. Foster can always access the dashboard, whether the backend is running or not. Perfect for demos, development, and production."

---

### Part 4: Auto-Refresh Demo ⏰

**What to Say:**
> "When connected live, the dashboard automatically refreshes data every 5 minutes to stay current."

**Steps:**
1. Start API server again:
   ```powershell
   cd "c:\IS330\H.C Lombardo App"
   python api_server.py
   ```

2. Open dashboard (will connect to live mode)

3. **Open browser console (F12)**

4. **Wait 5 minutes** (or modify the interval in code to 30 seconds for demo):
   - In `index.html`, find:
     ```javascript
     }, 300000); // 5 minutes
     ```
   - Change to:
     ```javascript
     }, 30000); // 30 seconds for demo
     ```

5. **Watch console:**
   - Every 30 seconds: `🔄 Refreshing dashboard data...`
   - Every 30 seconds: `📊 Dashboard updated: 32 teams tracked`

6. **Explain:**
   > "In production, this means the dashboard always shows current data without manual refreshes."

---

## 🎓 Key Points for Dr. Foster

### Architecture Benefits
1. **Separation of Concerns**
   - Frontend works independently
   - Backend can be updated separately
   - True three-tier architecture

2. **Fault Tolerance**
   - Graceful degradation
   - No single point of failure
   - Always accessible

3. **Real-time Updates**
   - 5-minute auto-refresh
   - Shows actual database state
   - No manual updates needed

4. **Production Ready**
   - CORS configured
   - Error handling
   - Status indicators
   - Logging enabled

### Technical Highlights
- ✅ **Async/Await JavaScript** - Modern ES6+ features
- ✅ **Fetch API** - RESTful communication
- ✅ **Timeout Handling** - 3-second graceful failure
- ✅ **CORS Configuration** - Secure cross-origin requests
- ✅ **PostgreSQL Integration** - Real database queries
- ✅ **Flask REST API** - Industry-standard backend
- ✅ **Hybrid Fallback** - Static + Live data

---

## 📊 Stats That Update Live

### Currently Implemented
- Team count from database

### Easy to Add (5 minutes each)

**1. Game Count:**
```python
# In api_server.py
@app.route('/api/games/count')
def get_games_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM games")
    count = cursor.fetchone()[0]
    return jsonify({"count": count})
```

**2. Prediction Count:**
```python
@app.route('/api/predictions/count')
def get_predictions_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions")
    count = cursor.fetchone()[0]
    return jsonify({"count": count})
```

**3. Model Accuracy:**
```python
@app.route('/api/model/accuracy')
def get_model_accuracy():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT accuracy FROM model_metrics ORDER BY updated_at DESC LIMIT 1")
    accuracy = cursor.fetchone()[0]
    return jsonify({"accuracy": accuracy})
```

---

## 🎬 Full Demo Script (2 minutes)

### Opening
> "I'd like to demonstrate the dashboard's hybrid data system, which showcases production-ready architecture."

### Static Mode (30 seconds)
1. Open dashboard (API offline)
2. Show 📊 Static Data indicator
3. Explain: "Works offline for reliability"

### Live Mode (30 seconds)
1. Start API server
2. Refresh dashboard
3. Show 🟢 Live Data indicator
4. Explain: "Now pulling from PostgreSQL"

### Failover (30 seconds)
1. Stop API server
2. Refresh dashboard
3. Show automatic switch to static
4. Explain: "Graceful degradation - never breaks"

### Closing (30 seconds)
> "This demonstrates separation of concerns, fault tolerance, and real-time updates—all hallmarks of production-ready software."

---

## 🔧 Quick Testing Commands

### Check if API is running:
```powershell
netstat -ano | findstr :5000
```

### Test API directly:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
Invoke-RestMethod -Uri "http://localhost:5000/api/teams/count" -Method Get
```

### Start API:
```powershell
cd "c:\IS330\H.C Lombardo App"
python api_server.py
```

### Stop API:
```powershell
Stop-Process -Name python* -Force
```

### Open Dashboard:
```powershell
Start-Process "c:\IS330\H.C Lombardo App\testbed\dr_foster_interface_v2\index.html"
```

### Check browser console:
```
1. Open dashboard
2. Press F12
3. Click "Console" tab
4. Look for connection messages
```

---

## 🎯 Success Indicators

### Dashboard Working:
- ✅ Opens without errors
- ✅ Shows all content and tabs
- ✅ 3D visualization loads
- ✅ Status indicator appears

### Static Mode Working:
- ✅ Shows 📊 Static Data (blue)
- ✅ Stats display correctly
- ✅ No JavaScript errors
- ✅ Console shows "API offline - using static data"

### Live Mode Working:
- ✅ Shows 🟢 Live Data (green)
- ✅ Stats update from database
- ✅ Console shows "Dashboard updated: X teams tracked"
- ✅ Auto-refresh starts (check console in 5 min)

### Failover Working:
- ✅ Switches modes automatically
- ✅ No errors during transition
- ✅ Dashboard remains functional
- ✅ Indicator color changes correctly

---

## 💡 Troubleshooting

### Issue: Always shows Static Data
**Fix:** Make sure API is running and check CORS settings

### Issue: CORS Error in Console
**Fix:** Added `@app.after_request` to api_server.py already

### Issue: Indicator doesn't appear
**Fix:** Check if `data-mode-indicator` CSS is being blocked

### Issue: Stats don't update
**Fix:** Hard refresh with Ctrl + Shift + R

---

**Ready to impress Dr. Foster!** 🎉

---

*Demo Script for H.C. Lombardo Dashboard*  
*Live/Static Hybrid Data System*  
*Version 2.0 - October 9, 2025*
