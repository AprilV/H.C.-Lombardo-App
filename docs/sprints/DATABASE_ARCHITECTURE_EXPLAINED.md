# Database Architecture - Explained

## Your Question:
**"Is the historical database being updated with 2025 stats as well?"**

## Short Answer: 
**YES! There is only ONE database with ONE unified schema. All data (1999-2025) lives together in the same place, and 2025 data IS being updated as the season progresses.**

---

## Database Structure

### Single Database: `nfl_analytics`
You have **one PostgreSQL database** called `nfl_analytics` with different **schemas** (think of schemas as folders inside the database):

```
nfl_analytics (DATABASE)
├── public schema (default)
│   └── teams table (current season standings - 32 teams)
│
└── hcl schema (Historical Context Layer)
    ├── games table (7,263 games from 1999-2025)
    ├── team_game_stats table (14,312 records from 1999-2025)
    ├── betting_lines table (historical odds)
    └── team_info table (32 NFL teams metadata)
```

---

## How It Works

### 1. **Historical Data (What We Just Loaded)**
- **Location**: `hcl.games` and `hcl.team_game_stats` tables
- **Data Range**: 1999-2025 (all 27 seasons)
- **Purpose**: Machine learning training, historical analysis, looking up past games
- **Status**: ✅ **INCLUDES 2025 DATA!**
- **Update Frequency**: Static for past seasons, but 2025 gets updated

### 2. **Live/Current Season Data**
- **Location**: `public.teams` table
- **Data**: Current season standings (W-L-T, PPG, PA, etc.)
- **Purpose**: Homepage dashboard showing current rankings
- **Update Frequency**: Updated every 15 minutes (or on-demand)
- **Updater**: `multi_source_data_fetcher.py` + `live_data_updater.py`

---

## The Key Point: 2025 Data is in BOTH Places

### Scenario 1: Historical Data (hcl schema)
```sql
-- This query gets 2025 games with full EPA stats
SELECT * FROM hcl.team_game_stats 
WHERE season = 2025;
-- Returns: All completed 2025 games with EPA calculations
```

**When updated:**
- We just loaded Week 1-10 (completed games)
- Future weeks get added after games finish
- Can re-run `step3_load_full_historical_data.py` to refresh 2025 data

### Scenario 2: Current Standings (public schema)
```sql
-- This query gets current season team standings
SELECT * FROM teams;
-- Returns: 32 teams with current W-L-T records, PPG, PA
```

**When updated:**
- Live updater runs every 15 minutes
- Fetches from ESPN API and TeamRankings.com
- Shows up-to-the-minute standings on homepage

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  NFL DATA SOURCES                       │
│  • nflverse (play-by-play, schedules, EPA)             │
│  • ESPN API (live standings)                            │
│  • TeamRankings.com (PPG, PA stats)                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              nfl_analytics DATABASE                      │
│                                                          │
│  ┌─────────────────────────────────────────────┐       │
│  │  hcl schema (Historical Context Layer)      │       │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │       │
│  │  • games (7,263 games, 1999-2025)           │       │
│  │  • team_game_stats (14,312 records + EPA)   │       │
│  │  • Updated: After games complete             │       │
│  │  • Purpose: ML training, historical lookup   │       │
│  └─────────────────────────────────────────────┘       │
│                                                          │
│  ┌─────────────────────────────────────────────┐       │
│  │  public schema (Current Season)              │       │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │       │
│  │  • teams (32 teams, current standings)       │       │
│  │  • Updated: Every 15 minutes (live)          │       │
│  │  • Purpose: Homepage dashboard               │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                H.C. LOMBARDO APP                         │
│  • Homepage: Shows live standings (public.teams)        │
│  • Analytics: Shows historical data (hcl.team_stats)    │
│  • ML Model: Trains on hcl data (1999-2025)            │
└─────────────────────────────────────────────────────────┘
```

---

## Detailed Example: How 2025 Data Works

### Week 1 (September 2025) - Game Completes
1. **Immediate**: Live updater sees game finished
   - Updates `public.teams` (Chiefs now 1-0, 49ers now 0-1)
   
2. **Later**: Historical loader runs (manual or scheduled)
   - Downloads play-by-play for completed Week 1 games
   - Calculates EPA for each team-game
   - Inserts into `hcl.games` and `hcl.team_game_stats`
   - Now 2025 Week 1 available for historical analysis

### Week 10 (November 2025) - Current State
- **Live standings** (`public.teams`): Shows 10-week records
- **Historical data** (`hcl.*`): Has Weeks 1-10 with full EPA
- **Your ML model**: Can train on all completed 2025 games

### Week 18 (January 2026) - Season Ends
- **Live standings**: Final 2025 records (17-week season)
- **Historical data**: Complete 2025 season with all EPA stats
- **Status**: 2025 becomes "static" historical data
- **Next**: 2026 season starts, process repeats

---

## What We Just Did (Sprint 9 Data Load)

### Before Today:
```
hcl.games: 1,126 games (2022-2025)
hcl.team_game_stats: 1,950 records (no EPA)
```

### After Today:
```
hcl.games: 7,263 games (1999-2025) ✅
hcl.team_game_stats: 14,312 records (with EPA) ✅
```

**This INCLUDES all completed 2025 games!**
- 2025 Week 1-10 games are in there
- As more 2025 games finish, you can re-run the loader
- Or manually add new games using the same script

---

## Updating 2025 Data

### Option 1: Re-run Full Loader (Recommended)
```bash
python testbed/sprint9_ml/step3_load_full_historical_data.py
```
- Downloads ALL seasons including latest 2025 games
- Takes ~4-5 minutes
- Safe: Uses INSERT...ON CONFLICT (won't duplicate data)

### Option 2: Incremental Update (Future Enhancement)
```bash
# Not built yet, but could do:
python update_current_season.py --season 2025 --weeks 11-12
```
- Only fetches new weeks
- Faster (seconds vs minutes)
- Good for mid-season updates

### Option 3: Live Updater (Different Purpose)
```bash
python live_data_updater.py
```
- Updates `public.teams` standings
- Does NOT update `hcl.*` historical data
- For homepage dashboard only

---

## Key Differences: Historical vs Live Data

| Feature | Historical (hcl.*) | Live (public.teams) |
|---------|-------------------|---------------------|
| **Time Range** | 1999-2025 (27 seasons) | Current season only |
| **Granularity** | Game-by-game | Season totals |
| **EPA Stats** | ✅ Yes (13 columns) | ❌ No |
| **Update Frequency** | After games complete | Every 15 minutes |
| **Purpose** | ML training, analysis | Homepage dashboard |
| **Data Volume** | 14,312 team-games | 32 teams |
| **Used For** | Analytics tab, predictions | Homepage standings |

---

## Common Scenarios

### Scenario 1: "I want to see Chiefs stats from 2023"
```sql
SELECT * FROM hcl.team_game_stats
WHERE team = 'KC' AND season = 2023;
```
✅ This is in historical data (hcl schema)

### Scenario 2: "What's the Chiefs current record this season?"
```sql
SELECT * FROM public.teams WHERE abbreviation = 'KC';
```
✅ This is in live standings (public schema)

### Scenario 3: "Train ML model to predict next week's games"
```python
# Use historical data (1999-2025 including completed 2025 games)
query = "SELECT * FROM hcl.team_game_stats"
# Model learns from 14,312 examples
```
✅ Uses hcl schema with EPA stats

### Scenario 4: "Update homepage with latest scores"
```python
# Run live updater
python live_data_updater.py
# Updates public.teams table
```
✅ Updates public schema

---

## Summary

### ✅ Your Database Setup:
- **One database**: `nfl_analytics`
- **Two schemas**: 
  - `hcl` = Historical data (1999-2025) with EPA
  - `public` = Current season live standings

### ✅ 2025 Data is in BOTH:
- **Historical (hcl.*)**: All completed 2025 games with full stats
- **Live (public.teams)**: Current 2025 season standings

### ✅ Updates:
- **Historical**: Re-run loader script after games complete
- **Live**: Runs automatically every 15 minutes

### ✅ ML Model Uses:
- Trains on **hcl schema** data (14,312 records with EPA)
- Includes all completed 2025 games
- Can predict future games based on historical patterns

---

## Next Steps

### Option 1: Keep 2025 Current (Recommended)
After Week 11 games finish:
```bash
cd "c:\IS330\H.C Lombardo App"
python testbed/sprint9_ml/step3_load_full_historical_data.py
```
This will add Week 11 games to your historical data.

### Option 2: Build Incremental Updater (Sprint 10?)
Create a script that only fetches new weeks:
```python
# update_new_games.py
# Checks what weeks you have, only fetches new ones
```

### Option 3: Automate (Production Feature)
Set up scheduled task to run weekly:
```bash
# Windows Task Scheduler
# Every Monday morning, run historical loader
```

---

## Questions?

**Q: Is 2025 data "static" or "live"?**  
A: It's **semi-live**. Completed games are static, but the season is ongoing. You need to manually refresh to get new weeks.

**Q: Will 2025 games overwrite when I re-run the loader?**  
A: No! The script uses `INSERT...ON CONFLICT` which updates existing records. Safe to re-run.

**Q: Should I update historical data every week?**  
A: Optional. For ML training, you have enough data. But yes, adding current season helps model see latest trends.

**Q: Does the live updater add games to hcl schema?**  
A: No. Live updater only updates `public.teams` standings. Historical loader adds to `hcl.*` schema.

---

**Bottom Line**: You have a unified database where all years (1999-2025) live together in the `hcl` schema. The 2025 season IS included in your historical data and can be refreshed by re-running the loader script. The "live" updater is separate and only maintains current standings for the homepage dashboard.
