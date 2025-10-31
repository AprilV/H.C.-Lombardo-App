# HCL SCHEMA TESTBED TESTING GUIDE
**H.C. Lombardo App - Phase 2A Database Expansion**

**Created:** October 28, 2025  
**Author:** April V. Sykes  
**Reference:** PHASE2_IMPLEMENTATION_PLAN.md, SPRINT_8_PLAN.md

---

## Overview

This guide walks through testing the HCL (Historical Context Layer) schema in the testbed environment before deploying to production. The HCL schema enables game-by-game historical analysis, which is foundational for ML predictive analytics.

### What We're Building

**Current State:**
- 3 tables: `teams`, `stats_metadata`, `update_metadata`
- ~140 games (current 2025 season aggregates only)
- No game-by-game historical data

**Target State (Phase 2A):**
- HCL schema with 5 tables: `games`, `team_game_stats`, `betting_lines`, `injuries`, `weather`
- 1 materialized view: `v_game_matchup_display`
- ~600 games (2022-2025 seasons, game-by-game data)
- 47+ performance metrics per team per game

---

## Prerequisites

### 1. Verify nfl_data_py Installation

```powershell
cd "c:\IS330\H.C Lombardo App"
python -c "import nfl_data_py; print(f'nfl_data_py version: {nfl_data_py.__version__}')"
```

**Expected Output:** `nfl_data_py version: 0.3.3` (or similar)

**If not installed:**
```powershell
pip install nfl_data_py
```

### 2. Verify Database Connection

```powershell
python check_db_schema.py
```

**Expected Output:**
```
Connected to database successfully!
Total Tables: 3
...
```

### 3. Check Required Files

- ✅ `testbed_hcl_schema.sql` - Schema creation SQL
- ✅ `ingest_historical_games.py` - Data loader script
- ✅ `.env` - Database credentials

---

## Testing Process

### Phase 1: Create Testbed Schema (2-3 minutes)

#### Step 1.1: Open pgAdmin or psql

**Option A: pgAdmin (GUI)**
1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click on `nfl_analytics` database → Query Tool

**Option B: psql (Command Line)**
```powershell
psql -U postgres -d nfl_analytics
```

#### Step 1.2: Run Schema Creation SQL

Copy/paste entire contents of `testbed_hcl_schema.sql` into Query Tool and execute.

**Expected Output:**
```
CREATE SCHEMA
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
...
CREATE MATERIALIZED VIEW
Query returned successfully.
```

#### Step 1.3: Verify Schema Created

```sql
-- Check that schema exists
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name = 'hcl_test';

-- Check tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'hcl_test'
ORDER BY table_name;

-- Expected: 5 tables
-- betting_lines, games, injuries, team_game_stats, weather
```

**Expected Result:** 5 tables listed

---

### Phase 2: Load 2024 Season Data (Test with Small Dataset)

#### Step 2.1: Load 2024 Season Only

Start with just 2024 season (~270 games = 540 team-game records) to verify loader works correctly.

```powershell
cd "c:\IS330\H.C Lombardo App"
python ingest_historical_games.py --testbed --seasons 2024
```

**Expected Output:**
```
================================================================================
H.C. LOMBARDO APP - HISTORICAL DATA LOADER
================================================================================
Schema: hcl_test
Seasons: [2024]
Timestamp: 2025-10-28 ...
================================================================================
Connected to database: nfl_analytics
Loading schedules for seasons: [2024]
Fetched 272 games from nflverse
Inserted 272 games into hcl_test.games
✓ Loaded 272 games
Loading team-game stats for seasons: [2024]
Fetching play-by-play data from nflverse... (this may take a few minutes)
Fetched 45000+ plays
Processing 272 unique games
Processed 50/272 games...
Processed 100/272 games...
Processed 150/272 games...
Processed 200/272 games...
Processed 250/272 games...
Calculated stats for 544 team-game records
Inserted 544 team-game records into hcl_test.team_game_stats
✓ Loaded 544 team-game records
Refreshing materialized views...
Views refreshed successfully
✓ Refreshed materialized views
Running verification queries...
  Games table: 272 records
  Team-game stats table: 544 records
  Games by season:
    2024: 272 games
  No NULL critical stats found (good!)
================================================================================
DATA LOAD COMPLETE!
================================================================================
```

#### Step 2.2: Verify Data Loaded Correctly

```sql
-- Check row counts
SELECT 
  'games' AS table_name, 
  COUNT(*) AS row_count 
FROM hcl_test.games
UNION ALL
SELECT 
  'team_game_stats', 
  COUNT(*) 
FROM hcl_test.team_game_stats;

-- Expected:
-- games: 272
-- team_game_stats: 544

-- Check specific game (2024 Week 1: Kansas City @ Baltimore)
SELECT 
  game_id, 
  home_team, 
  away_team, 
  home_score, 
  away_score,
  winner
FROM hcl_test.v_game_matchup_display
WHERE season = 2024 AND week = 1 AND home_team = 'BAL'
ORDER BY game_date;

-- Expected: 1 row showing KC vs BAL with correct scores

-- Check team stats for one team
SELECT 
  game_id,
  opponent,
  is_home,
  points,
  total_yards,
  passing_yards,
  rushing_yards,
  turnovers,
  result
FROM hcl_test.team_game_stats
WHERE team = 'KC' AND season = 2024 AND week = 1;

-- Expected: 1 row with KC stats vs BAL
```

#### Step 2.3: Data Quality Checks

```sql
-- Check for negative values (should be 0)
SELECT COUNT(*) as negative_stats
FROM hcl_test.team_game_stats
WHERE points < 0 OR total_yards < 0;

-- Check for unreasonable completion percentages
SELECT team, game_id, completion_pct
FROM hcl_test.team_game_stats
WHERE completion_pct > 100 OR completion_pct < 0;

-- Check for missing game scores
SELECT COUNT(*) as missing_scores
FROM hcl_test.games
WHERE home_score IS NULL OR away_score IS NULL;

-- Verify wins/losses match scores
SELECT 
  g.game_id,
  g.home_team,
  g.away_team,
  g.home_score,
  g.away_score,
  h.result as home_result,
  a.result as away_result
FROM hcl_test.games g
JOIN hcl_test.team_game_stats h ON g.game_id = h.game_id AND h.is_home = TRUE
JOIN hcl_test.team_game_stats a ON g.game_id = a.game_id AND a.is_home = FALSE
WHERE 
  (g.home_score > g.away_score AND h.result != 'W') OR
  (g.home_score < g.away_score AND h.result != 'L')
LIMIT 10;

-- Expected: 0 rows (all results should match scores)
```

---

### Phase 3: Load Full Historical Data (2022-2025)

If 2024 data loads successfully, proceed with full historical load.

#### Step 3.1: Load All Seasons

```powershell
python ingest_historical_games.py --testbed --seasons 2022 2023 2024 2025
```

**Expected Duration:** 10-20 minutes (fetching ~600 games worth of play-by-play data)

**Expected Output:**
```
...
Seasons: [2022, 2023, 2024, 2025]
...
Fetched ~1100 games from nflverse
Inserted ~1100 games into hcl_test.games
✓ Loaded ~1100 games
...
Inserted ~2200 team-game records into hcl_test.team_game_stats
✓ Loaded ~2200 team-game records
...
  Games by season:
    2025: ~140 games
    2024: ~270 games
    2023: ~270 games
    2022: ~270 games
...
DATA LOAD COMPLETE!
```

#### Step 3.2: Verify Full Dataset

```sql
-- Check season breakdown
SELECT 
  season, 
  COUNT(*) as game_count,
  MIN(week) as first_week,
  MAX(week) as last_week
FROM hcl_test.games
GROUP BY season
ORDER BY season DESC;

-- Expected:
-- 2025: ~140 games, weeks 1-8 (current season)
-- 2024: ~270 games, weeks 1-18 + playoffs
-- 2023: ~270 games, weeks 1-18 + playoffs
-- 2022: ~270 games, weeks 1-18 + playoffs

-- Check data completeness
SELECT 
  season,
  COUNT(*) as total_records,
  SUM(CASE WHEN points IS NULL THEN 1 ELSE 0 END) as null_points,
  SUM(CASE WHEN total_yards IS NULL THEN 1 ELSE 0 END) as null_yards,
  AVG(points) as avg_points,
  AVG(total_yards) as avg_yards
FROM hcl_test.team_game_stats
GROUP BY season
ORDER BY season DESC;

-- Expected: 
-- All null_points and null_yards should be 0
-- avg_points should be ~22-24 per team
-- avg_yards should be ~320-350 per team
```

---

### Phase 4: Validate Materialized View

#### Step 4.1: Test Matchup View Queries

```sql
-- Get Week 1 matchups for 2024
SELECT 
  game_id,
  game_date,
  home_team,
  away_team,
  home_score,
  away_score,
  home_total_yards,
  away_total_yards,
  home_turnovers,
  away_turnovers,
  winner
FROM hcl_test.v_game_matchup_display
WHERE season = 2024 AND week = 1
ORDER BY game_date;

-- Expected: 16 rows (16 games in Week 1)

-- Get all Chiefs games in 2024
SELECT 
  week,
  CASE WHEN home_team = 'KC' THEN away_team ELSE home_team END as opponent,
  CASE WHEN home_team = 'KC' THEN 'HOME' ELSE 'AWAY' END as location,
  CASE WHEN home_team = 'KC' THEN home_score ELSE away_score END as kc_score,
  CASE WHEN home_team = 'KC' THEN away_score ELSE home_score END as opp_score,
  winner
FROM hcl_test.v_game_matchup_display
WHERE season = 2024 AND (home_team = 'KC' OR away_team = 'KC')
ORDER BY week;

-- Expected: ~8-10 games for current season
```

#### Step 4.2: Performance Check

```sql
-- Test view query speed
EXPLAIN ANALYZE
SELECT *
FROM hcl_test.v_game_matchup_display
WHERE season = 2024 AND week = 1;

-- Expected execution time: < 50ms (with indexes)
```

---

### Phase 5: Test API Integration (Optional)

If you want to test the testbed data with the existing API:

#### Step 5.1: Create Test Endpoint

Add to `api_server.py` (temporary):

```python
@app.route('/api/testbed/games', methods=['GET'])
def get_testbed_games():
    """Test endpoint for testbed HCL data"""
    season = request.args.get('season', 2024, type=int)
    week = request.args.get('week', 1, type=int)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * 
                FROM hcl_test.v_game_matchup_display
                WHERE season = %s AND week = %s
                ORDER BY game_date
            """, (season, week))
            games = cur.fetchall()
            return jsonify(games)
    finally:
        conn.close()
```

#### Step 5.2: Test with Browser

```
http://localhost:5001/api/testbed/games?season=2024&week=1
```

**Expected:** JSON array with 16 games

---

## Troubleshooting

### Error: "Schema already exists"

**Solution:** Drop and recreate

```sql
DROP SCHEMA IF EXISTS hcl_test CASCADE;
-- Then re-run testbed_hcl_schema.sql
```

### Error: "Module 'nfl_data_py' not found"

**Solution:**
```powershell
pip install nfl_data_py
```

### Error: "Connection refused" or "Database does not exist"

**Solution:** Verify `.env` file has correct credentials

```powershell
# Check .env file
cat .env | Select-String "DB_"

# Should show:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=nfl_analytics
# DB_USER=postgres
# DB_PASSWORD=your_password
```

### Data Loader Hangs on "Fetching play-by-play data"

**Cause:** nflverse downloads large CSV files (~500MB+ per season)

**Solution:** Be patient (5-10 minutes first time), data is cached after first download

### NULL Stats Found

**Cause:** Some older games may have incomplete play-by-play data

**Solution:** This is expected for a small percentage (<5%) of very old games. Check if critical games (2022+) have data.

---

## Success Criteria

Before migrating to production, verify:

✅ **Schema Created**
- [ ] 5 tables exist in `hcl_test` schema
- [ ] 1 materialized view exists
- [ ] All indexes created

✅ **Data Loaded**
- [ ] 2022-2025 seasons loaded (~1100 games)
- [ ] Team-game stats loaded (~2200 records)
- [ ] Season breakdown matches expected (~270 games per full season)

✅ **Data Quality**
- [ ] No NULL critical stats (points, yards)
- [ ] No negative values
- [ ] Completion percentages 0-100%
- [ ] Win/loss results match scores
- [ ] Average stats reasonable (22-24 PPG, 320-350 YPG)

✅ **View Performance**
- [ ] Query execution < 50ms with indexes
- [ ] Materialized view refreshes successfully

✅ **Spot Checks**
- [ ] Verified at least 3 specific known games (scores match public sources)
- [ ] Chiefs 2024 season shows correct record
- [ ] Week 1 2024 has 16 games

---

## Next Steps After Successful Testing

### 1. Document Results

Create `TESTBED_VALIDATION_RESULTS.md` with:
- Row counts by table
- Sample queries executed
- Any anomalies found
- Performance metrics

### 2. Backup Production Database

```powershell
# Create backup before production deployment
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
pg_dump -U postgres -d nfl_analytics > "backups/nfl_analytics_before_hcl_$timestamp.sql"
```

### 3. Migrate to Production

Once testbed validated:

**Option A: Run production schema SQL manually**
1. Open `testbed_hcl_schema.sql`
2. Find/Replace: `hcl_test` → `hcl` (all occurrences)
3. Save as `production_hcl_schema.sql`
4. Execute in pgAdmin against `nfl_analytics` database

**Option B: Run production data loader**
```powershell
python ingest_historical_games.py --production --seasons 2022 2023 2024 2025
```

### 4. Update API Endpoints

Modify `api_server.py` to use `hcl.v_game_matchup_display` instead of testbed

### 5. Update Sprint 8 Documentation

Update `SPRINT_8_COMPLETE.md` with:
- Tables created (with row counts)
- Data loaded (season breakdown)
- Time spent
- Any issues encountered

---

## Reference Queries

### Quick Status Check

```sql
-- One-line status check
SELECT 
  (SELECT COUNT(*) FROM hcl_test.games) as games,
  (SELECT COUNT(*) FROM hcl_test.team_game_stats) as team_stats,
  (SELECT COUNT(DISTINCT season) FROM hcl_test.games) as seasons,
  (SELECT MAX(updated_at) FROM hcl_test.games) as last_update;
```

### Export Sample Data (for manual review)

```sql
-- Export 2024 Week 1 data to CSV
COPY (
  SELECT * FROM hcl_test.v_game_matchup_display
  WHERE season = 2024 AND week = 1
  ORDER BY game_date
) TO 'C:/IS330/H.C Lombardo App/testbed_week1_sample.csv' 
WITH CSV HEADER;
```

---

**Last Updated:** October 28, 2025  
**Status:** Ready for Testing  
**Estimated Testing Time:** 30-45 minutes total
