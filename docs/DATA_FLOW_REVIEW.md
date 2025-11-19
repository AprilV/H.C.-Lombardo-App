# DATA FLOW REVIEW
**Date:** October 14, 2025  
**System:** H.C. Lombardo NFL Analytics

---

## 📊 DATA SOURCES (Where Data Comes From)

### Your database gets data from **BOTH** API calls AND web scraping:

### 1. **ESPN API** (Official API - Live Data)
- **URL:** `http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard`
- **Data Provided:**
  - ✅ Win-Loss-Tie records (e.g., "5-2-1")
  - ✅ Team names & abbreviations
  - ✅ Games played
  - ✅ Season year and type
- **Method:** API calls (JSON responses)
- **Coverage:** ~30 teams typically (ESPN doesn't always have all 32)

### 2. **TeamRankings.com** (Web Scraping - Statistics)
- **PPG URL:** `https://www.teamrankings.com/nfl/stat/points-per-game`
- **PA URL:** `https://www.teamrankings.com/nfl/stat/opponent-points-per-game`
- **Data Provided:**
  - ✅ Points Per Game (PPG) - offense
  - ✅ Points Allowed (PA) - defense
  - ✅ **226+ additional stats available** (not yet fully integrated)
- **Method:** Web scraping with BeautifulSoup (scrapes HTML tables)
- **Coverage:** All 32 teams reliably

---

## 🔄 DATA FLOW (How Data Gets to Database)

```
STARTUP SEQUENCE (startup.py):
    ↓
1. Check Prerequisites (DB, Python, Node)
    ↓
2. Ensure Database Schema (create tables)
    ↓
3. Update Live Data → LiveDataUpdater
    ↓
    Calls multi_source_data_fetcher.py
    ↓
    ┌─────────────────────────────────────┐
    │ multi_source_data_fetcher.py        │
    │                                     │
    │ 1️⃣ Fetch ESPN API (standings)      │
    │    • Wins, Losses, Ties            │
    │    • Team names & abbreviations    │
    │                                     │
    │ 2️⃣ Scrape TeamRankings PPG         │
    │    • Points Per Game (offense)     │
    │                                     │
    │ 3️⃣ Scrape TeamRankings PA          │
    │    • Points Allowed (defense)      │
    │                                     │
    │ 4️⃣ Merge All Data                  │
    │    • Match teams by name           │
    │    • Normalize team names          │
    │    • Ensure all 32 teams           │
    │                                     │
    │ 5️⃣ Update PostgreSQL Database      │
    │    • UPDATE if team exists         │
    │    • INSERT if team is new         │
    └─────────────────────────────────────┘
    ↓
4. Start Flask API Server (port 5000)
    ↓
5. Start React Frontend (port 3000)
```

---

## 💾 DATABASE STRUCTURE

### **Table:** `teams`
```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name TEXT,
    abbreviation TEXT UNIQUE,
    wins INTEGER,              -- FROM: ESPN API
    losses INTEGER,            -- FROM: ESPN API
    ties INTEGER,              -- FROM: ESPN API (NEW - Oct 14)
    ppg REAL,                  -- FROM: TeamRankings scrape
    pa REAL,                   -- FROM: TeamRankings scrape
    games_played INTEGER,      -- FROM: ESPN API (W+L+T)
    stats JSONB                -- FOR FUTURE: 37+ additional stats
);
```

### **Current Data Storage:**
- ✅ **wins, losses, ties** → ESPN API
- ✅ **ppg, pa** → TeamRankings.com scraping
- ⏸️ **stats (JSONB)** → Not yet populated (ready for 37+ stats)

---

## 🚀 API SERVER (How Frontend Gets Data)

### **File:** `api_server.py` (Flask server on port 5000)

The API **does NOT fetch data** - it only **reads from database**.

### **Main Endpoints:**

#### 1. **GET /api/teams**
```json
{
  "count": 32,
  "teams": [
    {
      "name": "Dallas Cowboys",
      "abbreviation": "DAL",
      "wins": 2,
      "losses": 3,
      "ties": 1,
      "ppg": 20.5,
      "pa": 28.2,
      "games_played": 6
    },
    ...
  ]
}
```
- **Data Source:** PostgreSQL database (SELECT query)
- **Refresh Rate:** Only updates when `multi_source_data_fetcher.py` runs

#### 2. **GET /api/teams/{abbreviation}**
```json
{
  "name": "Dallas Cowboys",
  "abbreviation": "DAL",
  "wins": 2,
  "losses": 3,
  "ties": 1,
  "ppg": 20.5,
  "pa": 28.2,
  "games_played": 6
}
```
- **Data Source:** PostgreSQL database (SELECT query)
- **Returns:** Single team data

#### 3. **GET /health**
- **Purpose:** Health check (confirms DB connection)
- **Returns:** Database status, team count

---

## 📝 DATA UPDATE FREQUENCY

### **Current System:**
- ✅ Data fetched **ONCE** during startup (`startup.py`)
- ❌ No automatic refresh (static until restart)
- ⏸️ `live_data_updater.py` exists but not scheduled for periodic updates

### **How to Refresh Data:**
1. **Manual:** Run `python multi_source_data_fetcher.py`
2. **Restart System:** Run `python startup.py` (fetches fresh data on start)
3. **Future:** Schedule periodic updates (cron job, scheduler)

---

## 🎯 SUMMARY

### **Where Data Comes From:**
1. ✅ **ESPN API** → Win/Loss/Tie records, team info
2. ✅ **TeamRankings.com scraping** → PPG, PA, 226+ stats

### **How Data Gets to Database:**
- `startup.py` calls `live_data_updater.py`
- Which runs `multi_source_data_fetcher.py`
- Which **fetches from ESPN API** + **scrapes TeamRankings.com**
- Then **merges** and **writes to PostgreSQL**

### **How Frontend Gets Data:**
- React calls Flask API (`http://localhost:5000/api/teams`)
- Flask API **reads from PostgreSQL database**
- Flask API **does NOT** fetch from ESPN/TeamRankings directly

### **Data Freshness:**
- ⚠️ **Only updated on system startup** (not real-time)
- 💡 **Can manually update:** Run `multi_source_data_fetcher.py`
- 📅 **For live updates:** Would need scheduled task (not implemented yet)

---

## 🔮 FUTURE ENHANCEMENTS (Not Yet Implemented)

### **37+ Stats from TeamRankings:**
- ✅ **Configuration exists:** `stats_config.py` (20 offense, 11 defense, 6 special teams)
- ✅ **Fetcher exists:** `universal_stat_fetcher.py` (can fetch any stat)
- ❌ **Not integrated:** Not stored in database yet
- 📦 **Plan:** Store in `stats` JSONB column

### **Scheduled Updates:**
- ⏸️ No automatic refresh currently
- 💡 Could add: Periodic updates every 5-15 minutes during games
- 💡 Could add: Daily updates during off-season

### **Additional API Endpoints (Planned):**
- `/api/stats/available` → List all 37+ stats for dropdown
- `/api/stats/{category}/{stat_key}` → Fetch any stat dynamically

---

## ✅ DATA VALIDATION (Test Results - Oct 14, 2025)

### **Comprehensive Tests (test_system.py):**
- ✅ **Database Schema:** Ties column exists (INTEGER)
- ✅ **Ties Data:** Dallas (2-3-1), Green Bay (3-1-1) stored correctly
- ✅ **Data Completeness:** All 32 teams with PPG/PA data
- ✅ **Calculation:** games_played = wins + losses + ties ✓
- ⚠️ **API Endpoints:** Code correct, requires manual verification

---

## 📚 KEY FILES

| File | Purpose | Data Source |
|------|---------|-------------|
| `multi_source_data_fetcher.py` | **Fetches & merges data** | ESPN API + TeamRankings scraping |
| `live_data_updater.py` | **Orchestrates updates** | Calls multi_source_data_fetcher |
| `startup.py` | **System startup** | Calls live_data_updater on start |
| `api_server.py` | **Serves data to frontend** | Reads from PostgreSQL |
| `universal_stat_fetcher.py` | **Can fetch 226+ stats** | TeamRankings scraping (not yet integrated) |
| `stats_config.py` | **Configuration for 37 stats** | N/A (config file) |

---

## 🎨 ANSWER TO YOUR QUESTION

> "Where is the data coming from in the db? api? Scraping? both."

### **ANSWER: BOTH! 🎯**

**Your database gets populated by:**
1. **ESPN API calls** → Win/Loss/Tie records
2. **Web scraping TeamRankings.com** → PPG/PA statistics

**The Flask API server:**
- Does **NOT** fetch from ESPN or scrape websites
- Only **reads from PostgreSQL database**
- Acts as a bridge between database and React frontend

**Data flow:**
```
ESPN API + TeamRankings Scraping
          ↓
  multi_source_data_fetcher.py
          ↓
  PostgreSQL Database
          ↓
  Flask API Server (api_server.py)
          ↓
  React Frontend
```

**Freshness:**
- Data updated **once on startup**
- Can manually update by running `multi_source_data_fetcher.py`
- Not real-time (yet)
