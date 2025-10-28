# 🔄 Live Data Integration Guide
**H.C. Lombardo NFL Analytics Dashboard**  
**Date:** October 9, 2025  
**Feature:** Hybrid Live/Static Data System

---

## 📊 Overview

The dashboard now features a **hybrid data system** that automatically:
- ✅ **Connects to your Flask API** (port 5000) for real-time data
- ✅ **Falls back to static data** if API is offline
- ✅ **Auto-refreshes** every 5 minutes when live
- ✅ **Shows status indicator** (Live 🟢 or Static 📊)

---

## 🎯 How It Works

### 1. **Initial Load**
When the page loads, it attempts to connect to your Flask API:

```javascript
// Tries to fetch: http://localhost:5000/api/teams/count
// Timeout: 3 seconds
// If successful → Live Mode 🟢
// If fails → Static Mode 📊
```

### 2. **Live Mode (API Running)**
```
Dashboard → Flask API (Port 5000) → PostgreSQL → Live Data
         ↓
    Updates every 5 minutes
         ↓
    Shows: "🟢 Live Data" indicator
```

**What Updates:**
- Team count (from database)
- Database table count
- Last update timestamp
- Any other stats you add endpoints for

### 3. **Static Mode (API Offline)**
```
Dashboard → API Timeout (3 seconds) → Static Fallback Data
         ↓
    Uses hardcoded values
         ↓
    Shows: "📊 Static Data" indicator
```

**Static Values:**
- 32 NFL Teams
- 15+ Database Tables
- Demo/presentation ready

---

## 🚀 Usage Instructions

### For Dr. Foster's Demo (No API Required)
1. **Just open the dashboard** - `dr.foster/index.html`
2. Dashboard shows static data
3. Bottom-right shows "📊 Static Data"
4. Everything works perfectly for presentation

### For Live Data Testing
1. **Start your Flask API:**
   ```powershell
   cd "c:\IS330\H.C Lombardo App"
   python api_server.py
   ```
   - Server starts on port 5000
   - CORS enabled for localhost

2. **Open the dashboard:**
   ```powershell
   Start-Process "dr.foster\index.html"
   ```

3. **Check the indicator:**
   - **🟢 Live Data** = Connected to API
   - **📊 Static Data** = Using cached data

4. **Test the connection:**
   - Open browser console (F12)
   - Look for: `🚀 Initializing H.C. Lombardo Dashboard...`
   - Success: `📊 Dashboard updated: 32 teams tracked`
   - Offline: `📊 API offline - using static data`

---

## 🔧 API Endpoints Used

### Current Integration
```
GET http://localhost:5000/api/teams/count
Response: { "count": 32, "expected": 32, "status": "correct" }
```

### Ready to Add
You can easily extend the live data by adding more API calls:

```javascript
// In fetchLiveData() function
const teamsResponse = await fetch(`${API_BASE_URL}/api/teams`);
const gamesResponse = await fetch(`${API_BASE_URL}/api/games/count`);
const predictionsResponse = await fetch(`${API_BASE_URL}/api/predictions/count`);
```

---

## 📈 Adding More Live Stats

### Step 1: Create API Endpoint
Add to `api_server.py`:

```python
@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get all dashboard statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get team count
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        
        # Get game count
        cursor.execute("SELECT COUNT(*) FROM games")
        game_count = cursor.fetchone()[0]
        
        # Get prediction count
        cursor.execute("SELECT COUNT(*) FROM predictions")
        prediction_count = cursor.fetchone()[0]
        
        # Get latest update time
        cursor.execute("SELECT MAX(last_updated) FROM update_metadata")
        last_update = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "teams": team_count,
            "games": game_count,
            "predictions": prediction_count,
            "lastUpdate": str(last_update) if last_update else "N/A",
            "databaseTables": 15
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Step 2: Update Dashboard Fetch
In `index.html`, modify `fetchLiveData()`:

```javascript
async function fetchLiveData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`, {
            signal: controller.signal,
            mode: 'cors'
        });
        
        if (response.ok) {
            const data = await response.json();
            isLiveMode = true;
            updateDataModeIndicator(true);
            return data; // Now has all stats!
        }
    } catch (error) {
        // ... fallback to static
    }
}
```

### Step 3: Update More Stats
Add more IDs to HTML and update them:

```javascript
function updateDashboardStats(data) {
    // Update all stats
    document.getElementById('stat-teams').textContent = data.teams;
    document.getElementById('stat-games').textContent = data.games;
    document.getElementById('stat-predictions').textContent = data.predictions;
    document.getElementById('stat-tables').textContent = data.databaseTables + '+';
    
    // Update last update time
    if (data.lastUpdate) {
        const updateElement = document.getElementById('last-update');
        if (updateElement) {
            updateElement.textContent = `Last Updated: ${data.lastUpdate}`;
        }
    }
}
```

---

## 🎨 Status Indicator

The floating indicator at bottom-right shows current mode:

### Live Mode (🟢)
```
🟢 Live Data
- Background: Green (rgba(16, 185, 129, 0.9))
- Tooltip: "Connected to Flask API (Port 5000)"
- Auto-refreshes every 5 minutes
```

### Static Mode (📊)
```
📊 Static Data
- Background: Blue (rgba(59, 130, 246, 0.9))
- Tooltip: "Using cached data - API server offline"
- No auto-refresh
```

---

## ⚙️ Configuration Options

### Change API URL
```javascript
const API_BASE_URL = 'http://localhost:5000'; // Default
// For production: 'https://yourdomain.com/api'
```

### Change Refresh Interval
```javascript
dataUpdateInterval = setInterval(async () => {
    // ...refresh code...
}, 300000); // 300000ms = 5 minutes

// Options:
// 60000 = 1 minute
// 180000 = 3 minutes
// 600000 = 10 minutes
```

### Change Timeout
```javascript
const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 seconds

// Adjust for slower connections:
// 5000 = 5 seconds
// 10000 = 10 seconds
```

---

## 🐛 Troubleshooting

### Issue: Always Shows Static Data
**Cause:** API server not running or CORS blocking

**Solution:**
1. Start API server:
   ```powershell
   cd "c:\IS330\H.C Lombardo App"
   python api_server.py
   ```

2. Check CORS in `api_server.py`:
   ```python
   CORS(app, resources={
       r"/*": {
           "origins": ["http://localhost:3000", "*"],  # Add * for testing
           "methods": ["GET", "POST"],
           "allow_headers": ["Content-Type"]
       }
   })
   ```

3. Check browser console for errors (F12)

### Issue: CORS Error
**Error:** `Access-Control-Allow-Origin`

**Solution:**
```python
# In api_server.py, add after CORS(app):
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response
```

### Issue: Data Not Updating
**Cause:** Browser caching

**Solution:**
1. Hard refresh: `Ctrl + Shift + R`
2. Clear cache
3. Check console for refresh messages

---

## 📊 What Data Updates

### Current (Implemented)
- ✅ Team count from database
- ✅ Live/Static mode indicator
- ✅ Console logging

### Easy to Add
- 🔄 Game count
- 🔄 Prediction count
- 🔄 Model accuracy
- 🔄 Last update timestamp
- 🔄 Database size
- 🔄 API response time

### Future Enhancements
- 🔮 Real-time game scores
- 🔮 Live prediction updates
- 🔮 Database health metrics
- 🔮 User activity tracking
- 🔮 Performance charts

---

## 🎓 For Dr. Foster

### Why This Matters
This demonstrates:
- ✅ **Separation of Concerns** - Frontend independent of backend
- ✅ **Graceful Degradation** - Works offline or online
- ✅ **Real-time Updates** - Shows live system state
- ✅ **Production Ready** - Handles errors gracefully
- ✅ **User Experience** - Clear status indicators

### Demo Scenarios

**Scenario 1: Offline Demo**
- Dashboard opens instantly
- Shows static data
- Perfect for presentation
- No dependencies

**Scenario 2: Live Demo**
- Start API server first
- Dashboard connects automatically
- Shows real database stats
- Updates every 5 minutes
- Proves full-stack integration

**Scenario 3: Failover Demo**
1. Start with API running (🟢 Live Data)
2. Stop API server
3. Refresh page
4. Dashboard switches to static (📊 Static Data)
5. Proves robust error handling

---

## 🔐 Security Notes

### Development Mode
- CORS allows localhost
- No authentication required
- Open endpoints

### Production Considerations
```python
# Add to api_server.py for production:

# 1. API Key Authentication
@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.environ.get('API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401

# 2. Rate Limiting
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["100 per hour"])

# 3. HTTPS Only
if not request.is_secure:
    return redirect(request.url.replace("http://", "https://"))
```

---

## 📝 Testing Checklist

### Basic Functionality
- [ ] Dashboard opens without API (shows 📊 Static Data)
- [ ] Dashboard opens with API running (shows 🟢 Live Data)
- [ ] Team count updates from database
- [ ] Status indicator shows correct mode
- [ ] Console shows connection status

### Error Handling
- [ ] API timeout handled (3 seconds)
- [ ] Falls back to static data on error
- [ ] No JavaScript errors in console
- [ ] Indicator updates correctly on failure

### Refresh System
- [ ] Auto-refresh starts in live mode only
- [ ] Refresh interval works (5 minutes)
- [ ] Can manually refresh page
- [ ] Data persists across tab switches

---

## 🎉 Summary

Your dashboard now has:
- ✅ **Hybrid data system** - Live API or static fallback
- ✅ **Auto-updates** - Every 5 minutes when live
- ✅ **Visual indicator** - Shows current mode
- ✅ **Graceful errors** - Never breaks the demo
- ✅ **Easy to extend** - Add more endpoints anytime

**Perfect for:**
- Dr. Foster's demo (static mode)
- Your development (live mode)
- Production deployment (hybrid mode)
- Portfolio showcase (impressive!)

---

**Next Steps:**
1. Test with API running
2. Test without API running
3. Show Dr. Foster both modes
4. Add more endpoints as needed
5. Deploy to production!

---

*Generated by GitHub Copilot for VS Code*  
*Hybrid Live/Static Data Integration*  
*Version 2.0 - October 9, 2025*
