# Phase 2 Implementation Plan
**HC Lombardo - Historical Data & Betting Analytics**

Created: October 22, 2025
Status: READY TO BUILD
Reference Version: ChatGPT v1.8.0 (translated to Flask)

---

## Executive Summary

**Goal:** Add historical data storage, advanced analytics, and betting insights to HC Lombardo.

**Approach:** Incremental build using ChatGPT's FastAPI v1.8.0 as reference, translated to Flask/psycopg2.

**Timeline:** 3 phases (Foundation → API → Enhancement)

**Tech Stack:**
- Database: PostgreSQL (existing `nfl_analytics`)
- Data Source: nflverse (free, public)
- API Framework: Flask (existing app.py)
- Data Loaders: Python + pandas + nflreadpy

---

## Phase 2A: Foundation (Data Layer)

### Prerequisites Check

**✅ Already Have:**
- PostgreSQL database (`nfl_analytics` on localhost:5432)
- `db_config.py` for connection management
- `nfl-data-py` installed (v0.3.3)
- Tested Week 1 aggregation successfully

**❌ Need to Install:**
```bash
pip install nflreadpy  # Schedules, injuries, rosters
pip install polars     # Optional: faster processing
```

**❌ Need to Create:**
- `hcl` schema in PostgreSQL
- 4 new tables: `games`, `betting_lines`, `injuries`, `weather`
- 3 new views: `v_game_matchup_display`, `v_game_matchup_with_lines`, `v_game_matchup_with_proj`

### Database Setup Tasks

#### 1. Create Schema

```sql
-- Run in pgAdmin or psql
CREATE SCHEMA IF NOT EXISTS hcl;
SET search_path = hcl, public;
```

#### 2. Create Core Tables

**From `PHASE2_ADDITIONAL_DATA_SOURCES.md`, copy SQL for:**

a. **hcl.games** (game metadata)
```sql
CREATE TABLE IF NOT EXISTS hcl.games (
  game_id          TEXT PRIMARY KEY,
  season           INT NOT NULL,
  week             INT NOT NULL,
  game_date        DATE,
  kickoff_time_utc TIMESTAMPTZ,
  home_team        TEXT NOT NULL,
  away_team        TEXT NOT NULL,
  stadium          TEXT,
  city             TEXT,
  state            TEXT,
  timezone         TEXT,
  is_postseason    BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_games_season_week ON hcl.games(season, week);
CREATE INDEX IF NOT EXISTS idx_games_kickoff ON hcl.games(kickoff_time_utc);
```

b. **hcl.team_game_stats** (from existing nflverse_data_loader.py)
- This replaces the CSV output approach
- Direct database insert instead

c. **hcl.betting_lines** (optional - for future)
```sql
CREATE TABLE IF NOT EXISTS hcl.betting_lines (
  game_id          TEXT    NOT NULL,
  book             TEXT    NOT NULL,
  line_type        TEXT    NOT NULL,
  open_value       DOUBLE PRECISION,
  open_time_utc    TIMESTAMPTZ,
  close_value      DOUBLE PRECISION,
  close_time_utc   TIMESTAMPTZ,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (game_id, book, line_type)
);

CREATE INDEX IF NOT EXISTS idx_blines_type ON hcl.betting_lines(line_type);
```

d. **hcl.injuries** (optional - for future)
```sql
CREATE TABLE IF NOT EXISTS hcl.injuries (
  season       INT NOT NULL,
  week         INT NOT NULL,
  team         TEXT NOT NULL,
  full_name    TEXT,
  position     TEXT,
  status       TEXT,
  designation  TEXT,
  report_date  DATE,
  gsis_id      TEXT,
  updated_at   TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (season, week, team, full_name)
);
```

e. **hcl.weather** (optional - for future)
```sql
CREATE TABLE IF NOT EXISTS hcl.weather (
  game_id        TEXT PRIMARY KEY,
  roof           TEXT,
  surface        TEXT,
  temp_f         DOUBLE PRECISION,
  wind_mph       DOUBLE PRECISION,
  precip_prob    DOUBLE PRECISION,
  source         TEXT,
  observed_time  TIMESTAMPTZ,
  updated_at     TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3. Create Views

**a. v_game_matchup_display** (base stats, no betting)
- One row per game (home vs away pivoted)
- Uses hcl.games + hcl.team_game_stats
- 43 columns total

**SQL from ChatGPT's v_game_matchup_display.sql reference**

**b. v_game_matchup_with_proj** (adds betting analytics)
- Extends v_game_matchup_display
- Adds market lines (LATERAL joins to betting_lines)
- Adds projections (calculated fields)
- Adds edge calculations
- 49 columns total

**SQL from ChatGPT's PHASE2_ADDITIONAL_DATA_SOURCES.md**

### Data Loaders

#### 1. Enhance Existing Loader

**File:** `nflverse_data_loader.py` (already exists)

**Changes Needed:**
- Add database output mode (alongside CSV)
- Add 5 missing fields:
  - `penalty_yards`
  - `starting_field_pos_yds`
  - `early_down_success_rate`
  - `fourth_down_att`, `fourth_down_conv`
  - `drives`
- UPSERT to `hcl.team_game_stats` table

**Pattern:** Use ChatGPT's `hcl_ingest_team_game_mvp.py` as reference

#### 2. Create Schedule Loader

**File:** `ingest_schedules.py` (new)

**Purpose:** Populate `hcl.games` from nflverse schedules

**Source:** ChatGPT's `PHASE2_ADDITIONAL_DATA_SOURCES.md` (Section B)

**Usage:**
```bash
python ingest_schedules.py --seasons 2022 2023 2024
```

**Priority:** HIGH (needed before views work)

#### 3. Create Injuries Loader (Optional)

**File:** `ingest_injuries.py` (new)

**Purpose:** Weekly injury reports for advanced analysis

**Source:** ChatGPT's `PHASE2_ADDITIONAL_DATA_SOURCES.md` (Section D)

**Priority:** LOW (nice-to-have, not critical for MVP)

#### 4. Betting Lines CSV Loader (Optional)

**File:** `ingest_betting_lines_csv.py` (new)

**Purpose:** Import historical odds data

**Source:** ChatGPT's `PHASE2_ADDITIONAL_DATA_SOURCES.md` (Section A)

**Priority:** MEDIUM (needed for projections/edge features)

**Note:** Can start without betting lines, add later

### Testing Strategy

**Test Plan:**
1. Load schedules for 2024 Week 1 only (16 games)
2. Load PBP for 2024 Week 1 (validate 32 team-game records)
3. Query `v_game_matchup_display` (should return 16 rows)
4. Validate KC vs BAL game (home_team=BAL, away_team=KC)
5. Check all 43 columns populated correctly

**Validation Queries:**
```sql
-- Count games
SELECT COUNT(*) FROM hcl.games WHERE season=2024 AND week=1;
-- Expected: 16

-- Count team-game stats
SELECT COUNT(*) FROM hcl.team_game_stats WHERE season=2024 AND week=1;
-- Expected: 32

-- View test
SELECT game_id, home_team, away_team, home_ppg_for, away_ppg_for
FROM hcl.v_game_matchup_display
WHERE season=2024 AND week=1
ORDER BY game_date;
-- Expected: 16 rows with correct stats
```

---

## Phase 2B: API Translation (Flask)

### Endpoint Roadmap

**Build Order (prioritized by dependency):**

**Tier 1 - Core Metadata (No views needed)**
1. `GET /api/seasons` - List available seasons
2. `GET /api/weeks?season={}` - List available weeks
3. `GET /api/next_week?tz={}` - Next upcoming week

**Tier 2 - Base Matchups (Requires v_game_matchup_display)**
4. `GET /api/matchups?season={}&week={}` - Weekly matchups
5. `GET /api/matchups/{game_id}` - Single game matchup

**Tier 3 - Analytics (Requires v_game_matchup_display)**
6. `GET /api/week_summary?season={}&week={}` - Week aggregates

**Tier 4 - Betting (Requires v_game_matchup_with_proj + betting_lines)**
7. `GET /api/matchups_with_proj?season={}&week={}` - Matchups + projections
8. `GET /api/matchups_with_proj/{game_id}` - Single game + projections
9. `GET /api/upcoming_matchups_with_proj?tz={}` - Next week + projections
10. `GET /api/lines?season={}&week={}` - Query betting lines

**Tier 5 - Convenience (Optional)**
11. `GET /api/edges?min_edge={}` - Filter by edge threshold

### Flask Translation Patterns

**Pattern 1: Database Connection**

**ChatGPT (SQLAlchemy):**
```python
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
with engine.begin() as cxn:
    result = cxn.execute(text(sql), params)
```

**HC Lombardo (psycopg2 via db_config.py):**
```python
from db_config import get_db_connection

conn = get_db_connection()
try:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
finally:
    conn.close()
```

**Pattern 2: Query Parameters**

**ChatGPT (FastAPI):**
```python
@app.get("/api/matchups")
def get_matchups(
    season: int = Query(..., ge=1999),
    week: int = Query(..., ge=1, le=23)
):
```

**HC Lombardo (Flask):**
```python
@app.route('/api/matchups')
def get_matchups():
    season = request.args.get('season', type=int)
    week = request.args.get('week', type=int)
    
    if not season or season < 1999:
        return jsonify({'error': 'Invalid season'}), 400
    if not week or week < 1 or week > 23:
        return jsonify({'error': 'Invalid week'}), 400
```

**Pattern 3: Response Models**

**ChatGPT (Pydantic):**
```python
class Matchup(BaseModel):
    season: int
    week: int
    game_id: str
    # ... 40 more fields
```

**HC Lombardo (Flask):**
```python
# No model classes needed
# Return dict from database directly
return jsonify(rows)
```

**Pattern 4: Timezone Handling**

**Same in both** (PostgreSQL `AT TIME ZONE` works identically):
```python
sql = "SELECT (NOW() AT TIME ZONE %s) AT TIME ZONE 'UTC' AS now_ref_utc"
cur.execute(sql, (tz,))
```

**Pattern 5: CTE Queries**

**Same in both** (PostgreSQL CTEs work identically):
```python
sql = """
    WITH weekly AS (
      SELECT season, week, MIN(kickoff_time_utc) AS first_kick
      FROM hcl.games
      WHERE COALESCE(is_postseason, FALSE) = FALSE
      GROUP BY season, week
    )
    SELECT season, week FROM weekly
    WHERE first_kick >= %s
    ORDER BY first_kick ASC LIMIT 1
"""
cur.execute(sql, (now_ref_utc,))
```

### File Structure

**New Files to Create:**

```
c:\IS330\H.C Lombardo App\
├── api/
│   ├── __init__.py
│   ├── matchups.py         # Matchup endpoints (Tier 2)
│   ├── analytics.py        # Week summary (Tier 3)
│   ├── betting.py          # Projections + lines (Tier 4)
│   └── metadata.py         # Seasons/weeks/next_week (Tier 1)
├── loaders/
│   ├── __init__.py
│   ├── ingest_schedules.py
│   ├── ingest_injuries.py
│   └── ingest_betting_lines_csv.py
├── sql/
│   ├── schema/
│   │   ├── 01_create_tables.sql
│   │   └── 02_create_views.sql
│   └── queries/
│       └── matchup_queries.py (helper functions)
└── app.py (integrate new API routes)
```

**OR Simpler Approach (Start Here):**

```
c:\IS330\H.C Lombardo App\
├── matchup_api.py          # All new endpoints in one file
├── ingest_schedules.py     # New loader
└── app.py (import matchup_api routes)
```

### Integration with Existing App

**Current app.py has:**
- Port 5000 (Flask API)
- `/api/teams` endpoint
- `/health` endpoint
- CORS enabled

**Add to app.py:**
```python
from matchup_api import matchup_blueprint

app.register_blueprint(matchup_blueprint, url_prefix='/api')
```

**OR directly add routes to app.py** (simpler for now)

---

## Phase 2C: Enhancement (Optional)

### Performance Optimization

**1. Database Indexing**
```sql
CREATE INDEX idx_team_game_stats_lookup ON hcl.team_game_stats(season, week, team);
CREATE INDEX idx_games_season_week ON hcl.games(season, week);
```

**2. Caching (Optional)**
- Use `flask-caching` for frequently accessed endpoints
- Cache `/api/matchups` responses for 15 minutes
- Cache `/api/week_summary` for 1 hour

**3. Connection Pooling**
- Already handled by `db_config.py`
- Verify pool size adequate (default 20 connections)

### Automation

**1. Data Refresh Script**

**File:** `refresh_data.py` (new)

```python
#!/usr/bin/env python
"""
Daily data refresh script
Run via cron: 0 2 * * * python refresh_data.py
"""
import subprocess
from datetime import datetime

def refresh_schedules():
    """Update schedules for current season"""
    current_season = datetime.now().year
    subprocess.run([
        "python", "ingest_schedules.py",
        "--seasons", str(current_season)
    ])

def refresh_injuries():
    """Update weekly injury reports"""
    current_season = datetime.now().year
    subprocess.run([
        "python", "ingest_injuries.py",
        "--seasons", str(current_season)
    ])

if __name__ == "__main__":
    print("Starting data refresh...")
    refresh_schedules()
    refresh_injuries()
    print("Data refresh complete!")
```

**2. Windows Scheduled Task** (for local development)
```powershell
# Create scheduled task to run daily at 2 AM
$action = New-ScheduledTaskAction -Execute "python" -Argument "c:\IS330\H.C Lombardo App\refresh_data.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "HC_Lombardo_Data_Refresh" -Action $action -Trigger $trigger
```

### Advanced Features (Future)

**1. `/api/edges` Endpoint**

**When to add:** After backtesting proves projection accuracy

```python
@app.route('/api/edges')
def get_edges():
    min_edge = request.args.get('min_edge', type=float, default=1.5)
    season = request.args.get('season', type=int)
    week = request.args.get('week', type=int)
    
    sql = """
        SELECT * FROM hcl.v_game_matchup_with_proj
        WHERE season = %s AND week = %s
          AND ABS(edge_spread_points) >= %s
        ORDER BY ABS(edge_spread_points) DESC
    """
    # ... execute and return
```

**2. Player-Level Stats**

**Table:** `hcl.player_game_stats`

**Use case:** "Show me all WRs with 100+ yards this week"

**Priority:** LOW (team-level sufficient for MVP)

**3. Live Score Updates**

**Integration:** Keep existing ESPN API for live scores

**New:** Add `hcl.games.home_score`, `away_score` columns

**Update:** Live updater writes to both current system + hcl.games

---

## Testing Strategy

### Unit Tests

**Test each loader:**
```bash
pytest tests/test_ingest_schedules.py
pytest tests/test_nflverse_loader.py
```

**Test each API endpoint:**
```bash
pytest tests/test_matchup_api.py
```

### Integration Tests

**End-to-end flow:**
1. Load Week 1 schedules
2. Load Week 1 PBP
3. Query `/api/matchups?season=2024&week=1`
4. Validate response matches expected structure

### Performance Tests

**Benchmark queries:**
```python
import time
start = time.time()
response = requests.get('http://localhost:5000/api/matchups?season=2024&week=8')
elapsed = time.time() - start
assert elapsed < 0.1  # Should be under 100ms
```

---

## Rollout Plan

### Week 1: Foundation
- ✅ Install nflreadpy
- ✅ Create database tables (hcl schema)
- ✅ Create `ingest_schedules.py`
- ✅ Load 2024 Week 1 data
- ✅ Validate data quality

### Week 2: Core API
- ✅ Build Tier 1 endpoints (seasons, weeks, next_week)
- ✅ Build Tier 2 endpoints (matchups)
- ✅ Test with Postman/curl
- ✅ Integrate with existing app.py

### Week 3: Analytics
- ✅ Create v_game_matchup_display view
- ✅ Build Tier 3 endpoint (week_summary)
- ✅ Load historical data (2022-2024)
- ✅ Test performance with full dataset

### Week 4: Betting (Optional)
- ✅ Create betting_lines table
- ✅ Find historical odds CSV data
- ✅ Create v_game_matchup_with_proj view
- ✅ Build Tier 4 endpoints
- ✅ Test projections accuracy

### Week 5: Polish
- ✅ Add error handling
- ✅ Add logging
- ✅ Write documentation
- ✅ Create data refresh automation

---

## Success Criteria

**Phase 2A Complete When:**
- ✅ All tables created and indexed
- ✅ Schedules loaded for 2022-2024
- ✅ PBP aggregated for 2024 season
- ✅ Views return correct data for test queries

**Phase 2B Complete When:**
- ✅ All Tier 1-3 endpoints working
- ✅ Response times < 100ms for most queries
- ✅ API integrated with existing app.py
- ✅ No errors in logs for valid requests

**Phase 2C Complete When:**
- ✅ Automated data refresh working
- ✅ Performance optimized (caching, indexes)
- ✅ Documentation complete
- ✅ Frontend consuming new endpoints

---

## Risk Mitigation

**Risk 1:** nflverse data changes format
- **Mitigation:** Version pin `nflreadpy`, add schema validation

**Risk 2:** Database performance degrades with 3+ seasons
- **Mitigation:** Partition tables by season, add indexes

**Risk 3:** Betting lines data hard to source
- **Mitigation:** Start without it, views handle NULL gracefully

**Risk 4:** Projection model inaccurate
- **Mitigation:** Start with simple linear model, tune weights via backtest

---

## Next Action Items

**IMMEDIATE (Today):**
1. Install `nflreadpy`
2. Create `hcl` schema in PostgreSQL
3. Create `hcl.games` table
4. Create `ingest_schedules.py`
5. Test with 2024 Week 1 data

**SHORT TERM (This Week):**
1. Enhance `nflverse_data_loader.py` to write to database
2. Create `v_game_matchup_display` view
3. Build first 3 Flask endpoints (seasons, weeks, matchups)
4. Test with Postman

**MEDIUM TERM (Next 2 Weeks):**
1. Load full historical data (2022-2024)
2. Build week_summary endpoint
3. Create data refresh automation
4. Performance testing

**LONG TERM (Month 2+):**
1. Add betting lines (if odds data sourced)
2. Build frontend matchup display
3. Backtest projection model
4. Add `/api/edges` if valuable

---

## Reference Documents

**Saved in `testbed/chatgpt_reference/`:**
1. `matchup_api_v1.8.0_COMPLETE_FINAL.py` - Full FastAPI reference (11 endpoints)
2. `PHASE2_ADDITIONAL_DATA_SOURCES.md` - Data loaders, schemas, SQL
3. Earlier versions (v1.5.0 - v1.7.0) - Feature evolution

**Key SQL Files Needed:**
- ChatGPT's view definitions (extract from v1.8.0 comments)
- Table schemas (from PHASE2_ADDITIONAL_DATA_SOURCES.md)

**Key Python Patterns:**
- UPSERT logic (from ChatGPT loaders)
- CTE queries (from next_week logic)
- LATERAL joins (from betting_lines views)

---

## Decision Log

**Decisions Made:**
1. **Use Flask, not FastAPI** - Match existing app architecture
2. **Start without betting lines** - Can add later when data sourced
3. **Incremental rollout** - Foundation → API → Enhancement
4. **Test with small dataset first** - Week 1 only, then expand
5. **Skip `/api/edges` initially** - Add after backtest validates projections

**Decisions Deferred:**
- Exact projection model weights (need backtest)
- Caching strategy (measure performance first)
- Player-level stats (not needed for MVP)
- Docker deployment (local development first)

---

## Questions to Resolve

1. **Database:** Use existing `nfl_analytics` or create `nfl_analytics_testbed`?
   - **Decision:** Start with testbed, migrate to production after validation

2. **API File Structure:** Separate blueprints or single file?
   - **Decision:** Start with single `matchup_api.py`, refactor if it grows

3. **Data Refresh:** Manual or automated?
   - **Decision:** Manual initially, automate in Phase 2C

4. **Betting Lines:** Find data source now or build without?
   - **Decision:** Build without, add later when source found

---

## Conclusion

**We are READY TO BUILD.**

All prerequisites identified, reference code archived, translation patterns documented.

**First commit will be:** Database schema + schedule loader + Week 1 test.

**Timeline:** Expect working Tier 1-2 endpoints within 1 week, full Phase 2B within 2 weeks.

**Let's start with Phase 2A, Task 1: Install nflreadpy and create database schema.**
