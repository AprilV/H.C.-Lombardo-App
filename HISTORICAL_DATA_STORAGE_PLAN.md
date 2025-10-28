# Historical Data Storage & Future Features Plan

**Date**: October 22, 2025  
**Status**: Sprint 5-6 In Progress - Database Schema Created  
**Timeline**: October 22 - November 5, 2025 (2 weeks)

---

## 📋 SPRINT 5-6 OVERVIEW

**Goal**: Add historical game storage and team analytics to HC Lombardo betting app

**What We're Building:**
1. **Database Foundation** - PostgreSQL schema with 2 tables, 3 views, 5 indexes
2. **Team Analytics** - 47 statistical metrics per game (EPA, success rate, momentum)
3. **Projection Model** - Spread/total predictions using advanced metrics
4. **Team Detail Pages** - User selects team, stats, filters (home/away, last N games)

**What We're NOT Building (Yet):**
- Betting lines integration (no data source currently)
- Weather data (low priority)
- Injuries data (Sprint 7+)

---

## ✅ SPRINT 5 COMPLETED (Week 1)

### Database Schema Created
- ✅ `testbed/schema/hcl_schema.sql` - Complete SQL schema (620 lines)
- ✅ `testbed/setup_test_db.py` - Database setup script with validation
- ✅ `hcl.games` table - Game metadata (16 columns)
- ✅ `hcl.team_game_stats` table - Performance metrics (50+ columns, 47 stats)
- ✅ `v_team_season_stats` view - Season aggregates for team pages
- ✅ `v_game_matchup_display` view - Week browsing with home/away pivoted
- ✅ `v_game_matchup_with_proj` view - Adds spread/total projections
- ✅ 5 indexes for query performance

### Key Decisions Made
1. **Testbed First**: Build in `nfl_analytics_test` database, migrate to production later
2. **Flask Not FastAPI**: Translate ChatGPT's FastAPI patterns to our Flask architecture
3. **Team-Centric Design**: Focus on team detail pages (user's vision) not just week browsing
4. **47 Metrics**: Track comprehensive stats (EPA, SR, YPP, turnovers, momentum, efficiency)
5. **Projection Baseline**: Use ChatGPT's formulas as starting point, backtest later

---

## ✅ SPRINT 6 COMPLETED (Week 2)

### Data Loading
- ✅ Enhanced `testbed/nflverse_data_loader.py` to write to database (not just CSV)
- ✅ Added `--output database` flag with `--db-name` option
- ✅ UPSERT logic to prevent duplicates (ON CONFLICT DO UPDATE)
- ✅ Loaded 2024 Week 7 data: 15 games, 30 team-game records
- ✅ Validated with 7-step SQL validation script (all checks passed)

### API Development
- ✅ Created `testbed/historical_api.py` - Flask API with 4 endpoints
- ✅ `GET /api/teams` - List all 32 teams with season stats
- ✅ `GET /api/teams/<abbr>` - Team season overview (offense, defense, splits)
- ✅ `GET /api/teams/<abbr>/games` - Team game-by-game history
- ✅ `GET /api/games?season=X&week=Y` - All games for a specific week
- ✅ Tested with comprehensive test suite (`testbed/test_api_endpoints.py`)
- ✅ **All 6 tests passed**: Root, teams list, team overview, team games, games by week, error handling

**Achievement**: Database operational with Week 7 data + 4 working API endpoints tested and validated

---

## 📊 DATABASE SCHEMA DETAILS

### Table: hcl.games
Stores game metadata - one row per game

**Key Columns:**
- `game_id` (PK): Format YYYY_WW_AWAY_HOME (e.g., '2024_07_KC_SF')
- `season`, `week`, `game_type` ('REG', 'WC', 'DIV', 'CONF', 'SB')
- `home_team`, `away_team`, `home_score`, `away_score`
- `game_date`, `kickoff_time_utc` (timezone-aware)
- `stadium`, `city`, `state`

### Table: hcl.team_game_stats
Stores team performance - two rows per game (home + away)

**47 Statistical Metrics:**

**Core Efficiency:**
- `epa_per_play` - Expected Points Added (KEY betting metric)
- `epa_per_play_defense` - EPA allowed
- `success_rate` - % of plays that "succeed"
- `success_rate_defense` - Success rate allowed

**Offense:**
- Total plays, yards, yards per play
- Passing: yards, attempts, completions, TDs, INTs
- Rushing: yards, attempts, TDs
- First downs, explosive plays (20+ yards)

**Situational:**
- Third down: attempts, conversions, rate
- Fourth down: attempts, conversions, rate
- Red zone: attempts, scores, TDs, efficiency
- Time of possession

**Turnovers:**
- Turnovers lost, turnovers gained, differential

**Scoring:**
- Touchdowns, field goals, extra points, 2-pt conversions

**Momentum (Last 3 Games):**
- `epa_last_3_games` - Rolling average EPA
- `yards_per_play_last_3` - Rolling average YPP
- `ppg_last_3_games` - Rolling average points

### View: v_team_season_stats
Season-level aggregates per team (for team detail page overview)

**Provides:**
- Record (wins/losses)
- Scoring averages (PPG for/against)
- EPA averages (offense/defense)
- Efficiency metrics (3rd down, red zone)
- Turnover totals
- Home/away splits

### View: v_game_matchup_display
Matchup view with home/away stats in single row

**Provides:**
- Game metadata
- Home team season stats (up to that game)
- Away team season stats (up to that game)
- Momentum indicators (last 3 games)
- Matchup differentials (EPA diff, YPP diff, etc.)

### View: v_game_matchup_with_proj
Extends matchup view with projections

**Adds:**
- `projected_spread` - Formula: `-2.2*EPA_diff - 8.0*SR_diff - 1.2` (HFA)
- `projected_total` - Formula: `PPG_sum + 14.0*EPA_sum`
- `spread_confidence` - HIGH/MEDIUM/LOW based on differential
- `matchup_type` - MISMATCH/SHOOTOUT/DEFENSIVE_BATTLE/EVEN

---

## 🔧 TECHNICAL IMPLEMENTATION

### Projection Formulas (ChatGPT Baseline)

**Spread:**
```
projected_spread = -2.2 * (home_epa - away_epa) 
                   - 8.0 * (home_sr - away_sr) 
                   - 1.2  (home field advantage)
```
- Negative spread = home favored
- Example: -7.5 means home favored by 7.5 points

**Total:**
```
projected_total = (home_ppg + away_ppg) 
                  + 14.0 * (home_epa + away_epa)
```
- Predicts combined score
- Example: 48.5 means Over/Under at 48.5 points

**Note:** These are baseline formulas. We will backtest against 2022-2024 data to tune weights.

### Indexes for Performance
1. `idx_games_season_week` - Fast week queries
2. `idx_games_kickoff` - Fast "next week" logic
3. `idx_team_stats_team` - Fast team detail pages
4. `idx_team_stats_season_week` - Fast filtering
5. `idx_team_stats_game_id` - Fast joins

### UPSERT Pattern (Prevent Duplicates)
```sql
INSERT INTO hcl.games (game_id, season, week, ...)
VALUES (%s, %s, %s, ...)
ON CONFLICT (game_id) 
DO UPDATE SET 
    home_score = EXCLUDED.home_score,
    away_score = EXCLUDED.away_score,
    updated_at = CURRENT_TIMESTAMP;
```

---

## 🎨 USER EXPERIENCE (THE VISION)

### Team Detail Page Flow

1. **User clicks team logo** (e.g., "Kansas City Chiefs")

2. **Page shows:**
   - Season record (6-1)
   - Season averages (27.3 PPG, +0.24 EPA/play)
   - Stat selector: ☑ EPA ☑ Success Rate ☐ Turnovers ☑ PPG
   - Game-by-game table with selected stats
   - Trend chart (EPA over last 7 weeks)
   - Filters: [All Games ▼] [All Opponents ▼] [Last: 5 ▼]

3. **User can:**
   - Select which stats to view (checkboxes)
   - Filter by home/away games
   - Filter by opponent or division
   - See last N games only (momentum)
   - Compare to another team

### Week Selector Flow

1. **Dropdown shows:** Week 1, Week 2, ..., Week 8 (Live), ..., Playoffs

2. **User selects Week 7**

3. **Page shows:**
   - All 16 games from Week 7
   - Final scores + team stats
   - Matchup edges (which team had statistical advantage)
   - Our projections vs actual results

---

## 📅 REMAINING TIMELINE

### Week 2 (Sprint 6) - October 29 - November 5
- **Data Loading**: Enhance loader, load Week 7, validate
- **API Development**: 3 endpoints (teams list, team detail, team games)
- **Testing**: Query performance, data accuracy

### Week 3 (Sprint 7) - November 6-12
- **Frontend**: Team detail page UI
- **Frontend**: Stat selector checkboxes
- **Frontend**: Game history table
- **Frontend**: Filter controls
- **Integration**: Wire API to frontend

### Week 4 (Sprint 8) - November 13-19
- **Historical Data**: Load 2022-2024 full seasons
- **Backtest**: Test projection accuracy
- **Polish**: Performance optimization, bug fixes
- **Documentation**: User guide, API docs

---

## 📚 REFERENCE MATERIALS ARCHIVED

All ChatGPT reference code saved in `testbed/chatgpt_reference/`:
- `matchup_api_v1.5.0_FINAL.py` - Upcoming matchups + timezone
- `matchup_api_v1.6.0_COMPLETE.py` - Fallback logic
- `matchup_api_v1.7.0_COMPLETE.py` - Week summary analytics
- `matchup_api_v1.8.0_COMPLETE_FINAL.py` - Betting integration (11 endpoints)
- `PHASE2_ADDITIONAL_DATA_SOURCES.md` - Data pipeline documentation

---

## 🚀 NEXT IMMEDIATE STEPS

1. **Run setup script**: `python testbed/setup_test_db.py`
2. **Verify database created**: Check for `nfl_analytics_test` in PostgreSQL
3. **Enhance loader**: Add database output to `nflverse_data_loader.py`
4. **Load test data**: Run with Week 7 data
5. **Build team API**: Start with `/api/teams` endpoint

---

---

## 🔑 SPORTRADAR API CREDENTIALS

**API Key**: `TuH3WpobOAO1cCQAigHdacAKDcqgwx6mWetV3jmd`  
**API Provider**: Sportradar NFL API v7  
**Documentation**: https://developer.sportradar.com/football/reference/nfl-overview  
**Environment Variable**: `SPORTRADAR_API_KEY`  
**Base URL**: `https://api.sportradar.us/nfl/official/trial/v7/en/`

### ⚠️ TRIAL API TESTING RESULTS (Oct 22, 2025)

**Status**: ❌ **NOT RECOMMENDED FOR PRODUCTION**

**Test Results**:
- ✅ League Hierarchy: Works (200 OK, got team IDs)
- ❌ Standings: 404 Error (endpoint/year issue)
- ❌ Schedule: 429 Rate Limit (Too Many Requests)
- ❌ Statistics: 429 Rate Limit (Too Many Requests)

**Rate Limit Issues**:
- Hit rate limit after only 3-4 API calls
- Trial key has **severe restrictions**
- Cannot make multiple requests in succession
- Unsuitable for 15-minute auto-updates
- Cannot handle continuous testing

**Available Endpoints** (from documentation):
- Current Season/Week Schedule, Daily Change Log, Daily Transactions
- Game Boxscore, Play-by-Play, Roster, Statistics
- League Hierarchy, Player Profile, Postgame Standings
- Seasonal Statistics (complete team/player stats)
- Weekly Depth Charts, Weekly Injuries, Team Rosters
- Push Feeds (real-time events, stats) - Realtime access only

**Conclusion**: Trial key insufficient for production. Requires paid plan or alternative free API.

---

## 🔄 CURRENT DATA SOURCES (STABLE & FREE)

**ESPN API** (Free, No Rate Limits):
- ✅ Standings (W-L-T records)
- ✅ Team names, abbreviations, logos
- ✅ Real-time game scores
- ✅ Current in use: `espn_data_fetcher.py`, `multi_source_data_fetcher.py`

**TeamRankings.com** (Web Scraping):
- ✅ PPG (Points Per Game)
- ✅ PA (Points Allowed)
- ⚠️ Requires scraping (can break if site changes)
- ✅ Current in use: `scrape_teamrankings.py`, `multi_source_data_fetcher.py`

**Current Mix**: 60% API / 40% Scraping - **Working Reliably**

---

## 🎯 NEW SOLUTION: NFLVERSE (BEST OPTION!)

**Package**: `nfl-data-py` (Python library)  
**Source**: https://pypi.org/project/nfl-data-py/  
**GitHub**: https://github.com/nflverse/nflverse-pbp  
**License**: MIT (Free, Open Source)  
**Data Source**: nflfastR, nfldata, NFL official sources

### ✅ Why This Is Perfect for H.C. Lombardo

**1. FREE & NO RATE LIMITS**
- Community-maintained, open source
- No API keys needed
- Unlimited requests
- Professionally maintained by nflverse team

**2. COMPREHENSIVE DATA (Everything We Need!)**
- ✅ Play-by-play data (1999-present)
- ✅ Weekly team/player stats
- ✅ Seasonal statistics
- ✅ **Historical data** (any year from 1999+)
- ✅ Rosters, depth charts, injuries
- ✅ Schedules, game results
- ✅ Draft picks, combine data
- ✅ Scoring lines, win totals
- ✅ Team info (colors, logos, etc.)

**3. SOLVES ALL OUR PROBLEMS**
- ❌ No web scraping needed
- ✅ Historical queries built-in
- ✅ "Stats from 2 days ago" = query specific week/date
- ✅ "Last year's stats" = query 2024 season
- ✅ Week-by-week data for time-series
- ✅ All stats in structured DataFrames

**4. EASY INTEGRATION**
```python
import nfl_data_py as nfl

# Get current season stats
stats_2025 = nfl.import_seasonal_data([2025])

# Get historical stats (last year)
stats_2024 = nfl.import_seasonal_data([2024])

# Get weekly data for specific weeks
week_7 = nfl.import_weekly_data([2025])

# Get schedules
schedule = nfl.import_schedules([2025])

# Get team info
teams = nfl.import_team_desc()
```

### 📊 Available Data

**Team Statistics**:
- Wins, losses, ties
- Points for/against
- Offensive stats (rushing, passing, receiving)
- Defensive stats (sacks, interceptions, etc.)
- Special teams stats
- Advanced analytics

**Historical Access**:
- Seasons: 1999-present
- Weekly breakdowns
- Game-by-game results
- Season totals
- Career stats

**Additional Features**:
- Injury reports
- Depth charts
- Player rosters
- Draft information
- Combine results
- NGS (Next Gen Stats)
- Pro Football Reference data integration

### 🚀 Implementation Plan

**Phase 1: Install & Test**
1. Install: `pip install nfl-data-py`
2. Test data retrieval
3. Verify historical access
4. Map to our database schema

**Phase 2: Replace Current Fetchers**
1. Replace `scrape_teamrankings.py` → Use nflverse
2. Keep ESPN as backup/supplement
3. 100% API-based, no scraping

**Phase 3: Historical Storage**
1. Populate database with historical data
2. Enable "2 days ago", "last week", "last year" queries
3. Build time-series analysis

**Phase 4: Advanced Features**
- Injury tracking
- Player stats
- Game predictions
- Betting line integration (separate source)

---

## 🎯 PROJECT VISION

H.C. Lombardo NFL Analytics will be a **comprehensive betting analytics platform** with:
- Historical stat tracking (daily/weekly/yearly)
- User-selected stat comparisons
- NFL game predictions
- Live betting line tracking
- User input data storage
- Time-series analysis

---

## 📊 DATA REQUIREMENTS

### 1. Historical Stats Storage
**User Need**: "I want to see what the stats were 2 days ago, last week, or last year"

**Required Features**:
- Store stats with timestamps
- Query by date/time range
- Compare current vs historical
- Track stat changes over time

**Data to Track**:
- Team stats (PPG, PA, wins, losses, ties)
- Advanced stats (37+ stats from TeamRankings)
- Game-by-game results
- Week-by-week progression
- Season-by-season archives

### 2. Betting Lines Storage
**User Need**: "Betting lines change - we need storage for this"

**Required Features**:
- Track betting lines over time (lines move constantly)
- Store multiple bookmaker odds
- Historical line movement
- Opening vs closing lines
- Live in-game betting odds

**Data to Track**:
- Point spreads (with timestamps)
- Money lines
- Over/Under totals
- Prop bets
- Line movement history (hour-by-hour)

### 3. User Input Data
**User Need**: "We will have user input in the future data to store"

**Required Features**:
- User predictions
- User bet tracking
- Custom analysis notes
- Favorite teams/stats
- User settings/preferences

### 4. Game Predictions
**User Need**: "We will be doing NFL game predictions"

**Required Features**:
- Prediction algorithms
- Historical prediction accuracy
- Model performance tracking
- Confidence scores
- Win probability calculations

---

## 🗄️ DATABASE SCHEMA EXPANSION

### Current State (INSUFFICIENT)
```
✅ teams (11 columns) - current data only, overwrites every 15 min
✅ stats_metadata (7 columns) - stat definitions
✅ update_metadata (2 columns) - simple update log
```

**Problem**: No historical data retention, no betting data, no user data

---

### Proposed New Tables

#### 1. `team_stats_history` (Historical Stats)
```sql
CREATE TABLE team_stats_history (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    recorded_at TIMESTAMP NOT NULL,
    wins INTEGER,
    losses INTEGER,
    ties INTEGER,
    ppg DECIMAL(5,2),
    pa DECIMAL(5,2),
    games_played INTEGER,
    week INTEGER,  -- NFL week number
    season INTEGER,  -- 2025, 2024, etc.
    stats JSONB  -- 37+ advanced stats
);

-- Index for fast time-series queries
CREATE INDEX idx_stats_history_time ON team_stats_history(team_id, recorded_at);
CREATE INDEX idx_stats_history_week ON team_stats_history(team_id, season, week);
```

**Purpose**: Store snapshots of team stats at different points in time
**Update Frequency**: Every 15 minutes + end of each game + weekly snapshots

#### 2. `betting_lines` (Live Betting Data)
```sql
CREATE TABLE betting_lines (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    bookmaker VARCHAR(50),  -- 'DraftKings', 'FanDuel', etc.
    line_type VARCHAR(20),  -- 'spread', 'moneyline', 'total'
    recorded_at TIMESTAMP NOT NULL,
    home_line DECIMAL(6,2),  -- e.g., -7.5
    away_line DECIMAL(6,2),
    total DECIMAL(5,1),  -- Over/Under
    home_odds INTEGER,  -- e.g., -110
    away_odds INTEGER,
    is_live BOOLEAN,  -- Live in-game line?
    game_time_remaining VARCHAR(10)  -- e.g., 'Q3 8:42'
);

CREATE INDEX idx_betting_lines_game ON betting_lines(game_id, recorded_at);
CREATE INDEX idx_betting_lines_time ON betting_lines(recorded_at);
```

**Purpose**: Track betting line movements over time
**Update Frequency**: Every 5-10 minutes pre-game, every 30 seconds during live games

#### 3. `games` (Game Schedule & Results)
```sql
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    game_date TIMESTAMP NOT NULL,
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    home_score INTEGER,
    away_score INTEGER,
    game_status VARCHAR(20),  -- 'scheduled', 'in_progress', 'final'
    venue VARCHAR(100),
    weather JSONB  -- temperature, wind, precipitation
);

CREATE INDEX idx_games_schedule ON games(season, week);
CREATE INDEX idx_games_teams ON games(home_team_id, away_team_id);
```

**Purpose**: Core game data for predictions and historical analysis

#### 4. `predictions` (Game Predictions)
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    model_name VARCHAR(50),  -- 'HC_Lombardo_v1', 'User_Input', etc.
    predicted_at TIMESTAMP NOT NULL,
    predicted_winner_id INTEGER REFERENCES teams(id),
    predicted_home_score DECIMAL(5,2),
    predicted_away_score DECIMAL(5,2),
    confidence_score DECIMAL(5,4),  -- 0.0 to 1.0
    factors JSONB,  -- What influenced the prediction
    actual_correct BOOLEAN  -- Was prediction correct?
);

CREATE INDEX idx_predictions_game ON predictions(game_id);
CREATE INDEX idx_predictions_accuracy ON predictions(actual_correct);
```

**Purpose**: Track prediction performance and model accuracy

#### 5. `user_bets` (User Bet Tracking)
```sql
CREATE TABLE user_bets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,  -- Future: link to user accounts
    game_id INTEGER REFERENCES games(id),
    bet_type VARCHAR(20),  -- 'spread', 'moneyline', 'total', 'prop'
    bet_amount DECIMAL(10,2),
    odds INTEGER,
    placed_at TIMESTAMP NOT NULL,
    result VARCHAR(10),  -- 'win', 'loss', 'push'
    payout DECIMAL(10,2)
);
```

**Purpose**: Track user betting history and performance

#### 6. `advanced_stats_history` (37+ Stats Over Time)
```sql
CREATE TABLE advanced_stats_history (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    stat_key VARCHAR(50),  -- 'offense_points_per_game', etc.
    stat_value DECIMAL(10,4),
    recorded_at TIMESTAMP NOT NULL,
    week INTEGER,
    season INTEGER
);

CREATE INDEX idx_advanced_stats ON advanced_stats_history(team_id, stat_key, recorded_at);
```

**Purpose**: Store all 37+ TeamRankings stats historically

---

## 🔄 DATA UPDATE STRATEGY

### Every 15 Minutes (Current + New)
1. ✅ Update `teams` table (current data)
2. **NEW**: Insert snapshot into `team_stats_history`
3. **NEW**: Insert snapshot into `advanced_stats_history`

### Every 5-10 Minutes (Betting Lines)
1. **NEW**: Fetch betting lines from APIs
2. **NEW**: Insert into `betting_lines` table
3. **NEW**: Track line movement

### After Each Game
1. **NEW**: Update `games` table with final scores
2. **NEW**: Calculate prediction accuracy
3. **NEW**: Update `predictions` with `actual_correct`

### Daily Snapshots
1. **NEW**: End-of-day snapshot of all stats
2. **NEW**: Weekly rollup calculations
3. **NEW**: Season-to-date aggregations

---

## 📈 QUERY CAPABILITIES (Once Implemented)

### Time-Based Queries
```sql
-- Stats from 2 days ago
SELECT * FROM team_stats_history 
WHERE team_id = 1 AND recorded_at >= NOW() - INTERVAL '2 days'
ORDER BY recorded_at DESC LIMIT 1;

-- Last week's stats
SELECT * FROM team_stats_history 
WHERE team_id = 1 AND week = (CURRENT_WEEK - 1);

-- Last year's stats
SELECT * FROM team_stats_history 
WHERE team_id = 1 AND season = 2024;
```

### Betting Line Movement
```sql
-- How did the line move for this game?
SELECT recorded_at, home_line, away_line 
FROM betting_lines 
WHERE game_id = 123 
ORDER BY recorded_at;
```

### Prediction Accuracy
```sql
-- Model accuracy over last 10 games
SELECT 
    model_name,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN actual_correct THEN 1 ELSE 0 END) as correct,
    ROUND(AVG(CASE WHEN actual_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as accuracy_pct
FROM predictions
GROUP BY model_name;
```

---

## 💾 DATABASE DESIGN (NFLVERSE INTEGRATION)

### Current Schema (Keep As-Is)
```sql
teams (
    id SERIAL PRIMARY KEY,
    name TEXT,
    abbreviation TEXT,
    wins INT,
    losses INT,
    ties INT,
    ppg DECIMAL,
    pa DECIMAL,
    games_played INT,
    last_updated TIMESTAMP
)
```
**Purpose**: Current season snapshot for fast API responses (localhost:5000/api/teams)

---

### NEW Tables (Add for Historical + Betting)

#### 1. `team_stats_weekly` - Weekly Historical Data
```sql
CREATE TABLE team_stats_weekly (
    id SERIAL PRIMARY KEY,
    season INT NOT NULL,
    week INT NOT NULL,
    team_abbr VARCHAR(5) NOT NULL,
    team_name TEXT,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    ties INT DEFAULT 0,
    points_for INT DEFAULT 0,
    points_against INT DEFAULT 0,
    games_played INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(season, week, team_abbr)
);

CREATE INDEX idx_team_stats_weekly_lookup ON team_stats_weekly(season, week, team_abbr);
CREATE INDEX idx_team_stats_weekly_team ON team_stats_weekly(team_abbr, season, week);
```
**Purpose**: 
- Store weekly snapshots for time-series queries
- "Stats from 2 days ago" = query specific week
- "Last week's stats" = previous week query
- "Last year's stats" = query season 2024

**Populated From**: nflverse `import_schedules()` - aggregate wins/losses, points by week

---

#### 2. `games` - Game Schedule & Results
```sql
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    game_id TEXT UNIQUE NOT NULL,  -- nflverse game_id
    season INT NOT NULL,
    week INT NOT NULL,
    game_type VARCHAR(10),  -- 'REG', 'POST', 'PRE'
    gameday DATE,
    gametime TIME,
    home_team VARCHAR(5) NOT NULL,
    away_team VARCHAR(5) NOT NULL,
    home_score INT,
    away_score INT,
    location TEXT,
    stadium TEXT,
    roof VARCHAR(20),
    surface VARCHAR(20),
    temp INT,
    wind INT,
    home_coach TEXT,
    away_coach TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(game_id)
);

CREATE INDEX idx_games_schedule ON games(season, week, game_type);
CREATE INDEX idx_games_teams ON games(home_team, away_team);
CREATE INDEX idx_games_date ON games(gameday);
```
**Purpose**: 
- Complete game schedule
- Historical game results
- Game details (weather, location, coaches)

**Populated From**: nflverse `import_schedules()`

---

#### 3. `betting_lines` - Betting Data (Separate Page!)
```sql
CREATE TABLE betting_lines (
    id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL,  -- FK to games.game_id
    season INT NOT NULL,
    week INT NOT NULL,
    home_team VARCHAR(5),
    away_team VARCHAR(5),
    spread_line DECIMAL(4,1),  -- e.g., -7.5
    away_spread_odds INT,      -- e.g., -110
    home_spread_odds INT,
    away_moneyline INT,        -- e.g., +150
    home_moneyline INT,        -- e.g., -180
    total_line DECIMAL(4,1),   -- Over/Under e.g., 47.5
    over_odds INT,
    under_odds INT,
    recorded_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    UNIQUE(game_id)
);

CREATE INDEX idx_betting_lines_game ON betting_lines(game_id);
CREATE INDEX idx_betting_lines_week ON betting_lines(season, week);
```
**Purpose**: 
- Betting lines (spread, moneyline, totals)
- Historical line tracking
- **Separate page in app** for betting analysis

**Populated From**: nflverse `import_schedules()` - has betting data built-in!

---

### Database Relationships

```
teams (current snapshot)
  └── No relationships (standalone for speed)

team_stats_weekly (historical)
  └── Links to teams via team_abbr (not enforced FK for flexibility)

games (schedule/results)
  ├── home_team → teams.abbreviation
  └── away_team → teams.abbreviation

betting_lines (odds/lines)
  └── game_id → games.game_id (FK enforced)
```

**Why This Design:**
1. **`teams` table unchanged** - Current app keeps working
2. **Historical in separate table** - Time-series queries optimized
3. **Betting isolated** - Can show/hide, separate concerns
4. **Flexible** - Can query any time period without breaking current API

---

## 🎨 UI/UX DESIGN - User Access

### Current App Pages (Keep)
1. **Home Page** - Current standings (uses `teams` table)
   - URL: `http://localhost:5000/`
   - Data: `/api/teams` endpoint

2. **Dr. Foster Dashboard** - Database viewer
   - URL: `file:///.../dr.foster/index.html`
   - Data: Direct database queries

---

### NEW Pages/Features

#### 3. **Historical Stats Page** (NEW)
**URL**: `http://localhost:5000/historical` or tab on main page

**Features**:
- Dropdown: Select Season (2024, 2023, 2022, etc.)
- Dropdown: Select Week (1-18)
- Button: "Compare to Current"
- Display: Team stats for selected time period

**User Flow**:
```
User selects: Season 2024, Week 5
↓
App queries: team_stats_weekly WHERE season=2024 AND week=5
↓
Display: Stats from that specific week
```

**API Endpoint**: 
```
GET /api/historical/stats?season=2024&week=5
GET /api/historical/stats?season=2024  (full season)
GET /api/historical/compare?team=DAL&weeks=5,6,7  (trend)
```

---

#### 4. **Betting Lines Page** (NEW - SEPARATE)
**URL**: `http://localhost:5000/betting` or `/odds`

**Features**:
- Current week betting lines
- Historical line movement (if we track updates)
- Spread, moneyline, totals
- Best bets analysis (future)

**User Flow**:
```
User opens betting page
↓
App queries: betting_lines JOIN games WHERE week=CURRENT_WEEK
↓
Display: All games with odds
```

**API Endpoints**:
```
GET /api/betting/current-week
GET /api/betting/game/{game_id}
GET /api/betting/team/{abbr}  (all games for team)
```

**Display Format**:
```
Week 7 Betting Lines
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Game: DEN @ NO (Thu 10/17 8:15 PM)
  Spread:  NO -3.5 (-110) / DEN +3.5 (-110)
  Moneyline: NO -180 / DEN +150
  Total: 47.5 (Over -110 / Under -110)

Game: NYJ @ PIT (Sun 10/20 1:00 PM)
  Spread:  PIT -1.5 (-110) / NYJ +1.5 (-110)
  ...
```

---

#### 5. **User Timeline Feature** (Future - Phase 3)
**Dropdown on main page**: "View stats from..."
- Today
- Yesterday
- 2 days ago
- Last week
- 2 weeks ago
- Last year (same week)
- Custom date

**Query Logic**:
```python
if selected == "2 days ago":
    # Calculate week from 2 days ago
    target_week = current_week - 1  # approximate
    query team_stats_weekly WHERE week=target_week
```

---

## 🔄 DATA FLOW

### Current Flow (Keep Running)
```
Every 15 minutes:
  multi_source_data_fetcher.py
    ↓
  UPDATE teams table (current snapshot)
    ↓
  API serves /api/teams
```

### NEW Flow (Add in Parallel)
```
Daily (or weekly):
  nflverse_data_fetcher.py
    ↓
  INSERT INTO team_stats_weekly (historical snapshots)
  INSERT INTO games (schedule updates)
  INSERT INTO betting_lines (odds updates)
    ↓
  New API endpoints serve historical/betting data
```

**Both systems run independently** - no breaking changes!

---

## 🚀 IMPLEMENTATION PHASES

### ✅ Phase 1: COMPLETE (Current State)
- [x] PostgreSQL database setup
- [x] Basic teams table
- [x] API endpoints working
- [x] 15-minute data updates
- [x] Live system running

### 🟡 Phase 2: TESTBED (In Progress)
- [ ] Install nfl-data-py ✅ DONE
- [ ] Test data retrieval ✅ DONE
- [ ] Create new tables in testbed database
- [ ] Build nflverse_data_fetcher.py
- [ ] Test historical queries
- [ ] Validate data accuracy vs current sources

### 🟡 Phase 3: Integration (Next)
- [ ] Add new API endpoints (historical, betting)
- [ ] Create historical stats page UI
- [ ] Create betting lines page UI
- [ ] Test full integration
- [ ] Deploy to production alongside System 1

### 🟡 Phase 4: Advanced Betting Analytics (Future)
Based on oddsmakers/professional analysis requirements:

**Core Team Metrics (Must Have)**:
- [ ] Offensive efficiency (yards/play, yards/game, points/game)
- [ ] Defensive efficiency (yards allowed, points allowed)
- [ ] Turnover differential (interceptions + fumbles)
- [ ] Sack differential (sacks made - sacks allowed)
- [ ] Success rate per play
- [ ] EPA (Expected Points Added) per play
- [ ] Pace (plays per game, drives per game)
- [ ] Point differential (points for - points against)
- [ ] Pythagorean expectation (expected wins)

**Situational Splits**:
- [ ] Home vs away performance splits
- [ ] Recent form (last 3 games, last 5 games)
- [ ] Division games vs non-division
- [ ] Conference games
- [ ] Weather performance (dome vs outdoor, cold weather)

**Matchup Analysis**:
- [ ] Offense vs defense matchup ratings
- [ ] Passing offense vs pass defense
- [ ] Rushing offense vs rush defense
- [ ] Red zone efficiency
- [ ] Third down conversion rates

**Contextual Factors**:
- [ ] Days of rest / bye week tracking
- [ ] Travel distance / time zone changes
- [ ] Injury impact scoring (key players out)
- [ ] Weather conditions (temp, wind, precipitation)
- [ ] Stadium factors (roof, surface, altitude)

**Market Intelligence**:
- [ ] Opening line vs current line movement
- [ ] Line movement tracking (sharp vs public money)
- [ ] Betting percentages (% on each side)
- [ ] Value detection (model projection vs market line)
- [ ] Closing line value analysis

**Data Windows**:
- [ ] Full season aggregates
- [ ] Rolling averages (3, 5, 8 game windows)
- [ ] Week-over-week trends
- [ ] Opponent-adjusted metrics
- [ ] Historical same-matchup performance

**Recommended MVP Stats (Start Here)**:
```sql
-- Phase 4A: Basic Efficiency (Immediate)
team_stats_weekly additions:
  - yards_per_play (offense & defense)
  - plays_per_game
  - turnover_differential
  - sack_differential
  - home_away_flag
  
-- Phase 4B: Recent Form (Week 2)
rolling_stats table:
  - last_3_games_ppg
  - last_3_games_pa
  - last_3_games_ypp
  - recent_ats_record (against the spread)
  
-- Phase 4C: Matchup Features (Week 3)
matchup_analysis table:
  - offense_rank vs defense_rank
  - pace_differential
  - style_matchup_score
  
-- Phase 4D: Market Data (Week 4)
line_movement table:
  - opening_spread
  - current_spread
  - line_move_direction
  - betting_percentages
  - sharp_money_indicator
```

**Data Sources for Advanced Stats**:
- ✅ nflverse: Play-by-play (EPA, success rate, game logs)
- ✅ nflverse: Team stats, schedules, rosters
- ⚠️ Betting data: OddsAPI or similar (line movement, percentages)
- ⚠️ Weather: OpenWeather API or similar
- ⚠️ Injuries: ESPN injury reports or nflverse

---

## 📋 CURRENT STATUS SUMMARY

**✅ Completed:**
- PostgreSQL database operational
- System 1 running stably (current stats)
- nfl-data-py tested and working
- Architecture designed
- Historical data accessible

**🔄 In Progress (Phase 2):**
- Testbed implementation starting
- Schema design for new tables
- nflverse data fetcher development

**⏳ Next Steps:**
1. Build testbed database with new tables
2. Create nflverse_data_fetcher.py
3. Populate historical data (2022-2024)
4. Test queries and data accuracy
5. Build new API endpoints
6. Create UI for historical/betting pages

**🎯 Long-term Vision (Phase 4):**
- Advanced betting analytics
- Model-based predictions
- Value bet detection
- Line movement tracking
- Comprehensive matchup analysis

---
- [ ] Create `team_stats_history` table
- [ ] Create `games` table
- [ ] Modify data updater to INSERT instead of UPDATE
- [ ] Create historical snapshot script
- [ ] Test time-series queries

### 🟡 Phase 3: Betting Integration
- [ ] Create `betting_lines` table
- [ ] Research betting line APIs (OddsAPI, The Odds API, etc.)
- [ ] Implement betting line scraper
- [ ] 5-10 minute betting line updates
- [ ] Line movement visualization

### 🟡 Phase 4: Predictions & Analytics
- [ ] Create `predictions` table
- [ ] Build prediction algorithms
- [ ] Track model accuracy
- [ ] Confidence scoring system

### 🟡 Phase 5: User Features
- [ ] Create `user_bets` table
- [ ] User authentication system
- [ ] Personal bet tracking
- [ ] Custom dashboards

### 🟡 Phase 6: Advanced Stats
- [ ] Create `advanced_stats_history` table
- [ ] Store all 37+ stats historically
- [ ] User stat selection UI
- [ ] Stat comparison tools

---

## 🛠️ IMMEDIATE NEXT STEPS

1. **Create migration script** for new tables
2. **Modify `live_data_updater.py`** to:
   - INSERT into history tables (not just UPDATE)
   - Keep current `teams` table for API speed
   - Archive data for historical queries
3. **Update API endpoints** to support time-based queries:
   - `/api/teams/{abbr}/history?date=2025-10-20`
   - `/api/teams/{abbr}/week/{week}`
   - `/api/games/{id}/betting_lines`
4. **Test data retention** (ensure no performance issues)

---

## 💾 STORAGE ESTIMATES

**Current**: ~32 rows in teams table  
**After Phase 2**: ~100,000 rows/year in history tables  
**After Phase 3**: ~1,000,000 rows/year in betting_lines (high frequency updates)  
**After Phase 6**: ~2,000,000 rows/year in advanced_stats_history (37 stats × 32 teams × frequent updates)

**Total**: ~3-5 million rows/year (manageable with PostgreSQL + indexes)

---

## 📋 BLOCKING ISSUES

**Cannot proceed with user features until**:
1. ✅ Database in place (DONE)
2. ✅ APIs working (DONE)
3. ✅ Data updates every 15 min (DONE)
4. ⚠️ **Historical data storage** (IN PROGRESS - THIS DOCUMENT)
5. ⚠️ **Betting line storage** (NEXT)
6. ⚠️ **Game schedule data** (NEXT)

---

## 🎯 DECISION NEEDED

**User**: Should we start Phase 2 now?

**Phase 2 Implementation** would:
1. Create historical tables
2. Modify data updater to archive snapshots
3. Keep current API fast (still uses `teams` table)
4. Enable "2 days ago" / "last week" queries
5. Take ~1-2 hours to implement and test

**Ready to proceed?**

---

## 📊 NFLVERSE STATS AUDIT RESULTS (Oct 22, 2024)

### ✅ AVAILABLE FROM NFLVERSE:

**BASIC STATS** (From schedules):
- Wins/Losses/Ties (from game results)
- Points For/Against 
- **BETTING LINES**: Spread, moneyline, total, over/under odds
- Weather data: Temperature, wind, roof type, surface
- Home/away splits
- Rest days (away_rest, home_rest)
- QB names, coaches, referees, stadium info

**OFFENSIVE STATS** (Aggregate from weekly player data):
- Passing: Yards, TDs, INTs, attempts
- Rushing: Yards, TDs, attempts
- Receiving: Yards, TDs, targets
- Sacks taken, fumbles lost
- Total yards (pass + rush)
- First downs

**CONTEXTUAL DATA**:
- Injury reports (6,215 records for 2024)
- Depth charts (37,312 records)
- Team info (logos, colors, divisions, conference)

**ADVANCED STATS** (From play-by-play - 372 columns!):
- EPA (Expected Points Added)
- Success rates
- Red zone efficiency
- Third/fourth down conversions
- Yards after catch, air yards
- Play-by-play detail (every snap)

### ❌ NOT AVAILABLE (Need external sources or calculation):
- Live line movement tracking (only final lines available)
- Sharp vs public money percentages
- Defensive stats as team totals (calculate from opponent offense)
- Opponent-adjusted metrics (calculate ourselves)

---

## 📋 BETTING STATS IMPLEMENTATION ROADMAP

Based on professional betting analytics research and nflverse capabilities:

### ✅ **PHASE 2: MUST-HAVE STATS** (START HERE)
*Core statistics essential for betting models - all derivable from nflverse*

**Timeline**: 2 weeks  
**Data Sources**: `nfl.import_schedules()` + `nfl.import_weekly_data()`

#### Stats to Implement:

| Stat | Priority | How to Get | nflverse Field(s) |
|------|----------|-----------|-------------------|
| **Plays** (total offensive) | MUST | Aggregate weekly | Sum `attempts + carries` per team |
| **Yards - Total** | MUST | Aggregate weekly | `passing_yards + rushing_yards` |
| **Yards - Passing** | MUST | Aggregate weekly | `passing_yards` |
| **Yards - Rushing** | MUST | Aggregate weekly | `rushing_yards` |
| **Pass Attempts** | MUST | Aggregate weekly | `attempts` |
| **Rush Attempts** | MUST | Aggregate weekly | `carries` |
| **Yards per Play** | MUST | Calculate | `total_yards / total_plays` |
| **Points Scored** | MUST | From schedules | `home_score` / `away_score` |
| **Points Allowed** | MUST | From schedules | Opponent's score |
| **Turnovers Committed** | MUST | Aggregate weekly | `interceptions + fumbles_lost` |
| **Sacks Allowed** | MUST | Aggregate weekly | `sacks` (offensive stat) |
| **Home/Away Indicator** | MUST | From schedules | `location` field |
| **Rest Days** | MUST | From schedules | `away_rest` / `home_rest` |
| **Spread Line** | MUST | From schedules | `spread_line` |
| **Total Line** | MUST | From schedules | `total_line` |
| **Moneyline** | MUST | From schedules | `home_moneyline` / `away_moneyline` |

#### Phase 2 Database Schema:

```sql
-- Team performance per game
CREATE TABLE team_game_stats (
    game_id TEXT,
    team_abbr TEXT,
    season INT,
    week INT,
    game_date DATE,
    opponent TEXT,
    is_home BOOLEAN,
    rest_days INT,
    
    -- Scoring
    points_scored INT,
    points_allowed INT,
    
    -- Volume
    total_plays INT,
    pass_attempts INT,
    rush_attempts INT,
    
    -- Production
    total_yards INT,
    passing_yards INT,
    rushing_yards INT,
    
    -- Efficiency
    yards_per_play DECIMAL(4,2),
    
    -- Turnovers
    turnovers INT,
    interceptions_thrown INT,
    fumbles_lost INT,
    
    -- Protection
    sacks_allowed INT,
    
    PRIMARY KEY (game_id, team_abbr),
    FOREIGN KEY (team_abbr) REFERENCES teams(team_abbr)
);

-- Betting lines per game
CREATE TABLE betting_lines (
    game_id TEXT PRIMARY KEY,
    season INT,
    week INT,
    game_date DATE,
    home_team TEXT,
    away_team TEXT,
    
    -- Spread
    spread_line DECIMAL(4,1),
    home_spread_odds INT,
    away_spread_odds INT,
    
    -- Total
    total_line DECIMAL(4,1),
    over_odds INT,
    under_odds INT,
    
    -- Moneyline
    home_moneyline INT,
    away_moneyline INT,
    
    -- Results (populated after game)
    home_score INT,
    away_score INT,
    spread_result TEXT,  -- 'home_covered', 'away_covered', 'push'
    total_result TEXT    -- 'over', 'under', 'push'
);

-- Game context
CREATE TABLE game_context (
    game_id TEXT PRIMARY KEY,
    season INT,
    week INT,
    game_date DATE,
    game_time TIME,
    
    -- Venue
    stadium TEXT,
    roof TEXT,          -- 'dome', 'outdoors', 'retractable'
    surface TEXT,       -- 'grass', 'sportturf'
    
    -- Weather
    temperature INT,
    wind_speed INT,
    
    -- Personnel
    home_qb TEXT,
    away_qb TEXT,
    referee TEXT,
    
    -- Situational
    is_division_game BOOLEAN,
    is_primetime BOOLEAN
);
```

#### Implementation Steps:
1. ✅ nflverse tested and working
2. Create Phase 2 tables in testbed database
3. Write `nflverse_data_loader.py`:
   - Load schedules (2022-2024 seasons)
   - Load weekly player stats (2022-2024)
   - Aggregate player stats to team-game level
   - Calculate derived stats (yards/play, turnovers)
   - Populate all three tables
4. Add API endpoints:
   - `/api/historical/team/{abbr}` - all games for team
   - `/api/historical/team/{abbr}/season/{year}` - single season
   - `/api/betting/lines/{game_id}` - betting lines for game
   - `/api/betting/upcoming` - next week's lines
5. Build UI page: "Historical Stats & Betting Lines"

---

### 🔍 **PHASE 3: VERY USEFUL STATS** (After Phase 2 Stable)
*Advanced efficiency metrics and momentum indicators*

**Timeline**: 2-3 weeks  
**Data Source**: `nfl.import_pbp_data()` (⚠️ LARGE - 372 columns, millions of rows)

#### Stats to Implement:

| Stat | Priority | How to Get | nflverse PBP Field(s) |
|------|----------|-----------|----------------------|
| **EPA Total** | NICE | Aggregate PBP | Sum of `epa` per team |
| **EPA per Play** | NICE | Calculate | `total_epa / total_plays` |
| **Success Rate** | NICE | Aggregate PBP | % where `success == 1` |
| **Red Zone Efficiency** | NICE | Filter PBP | TDs on drives starting inside 20 |
| **3rd Down %** | NICE | Aggregate PBP | `third_down_converted / attempts` |
| **4th Down %** | NICE | Aggregate PBP | `fourth_down_converted / attempts` |
| **Last 3 Game Avg** | NICE | Calculate | Rolling average key metrics |
| **Last 5 Game Avg** | NICE | Calculate | Rolling average key metrics |
| **Home/Away Splits** | NICE | Group by location | Separate stats per venue |
| **Injury Count** | NICE | From injuries API | Starters missing by position |

#### Phase 3 Additional Tables:

```sql
-- Advanced efficiency stats (from play-by-play)
CREATE TABLE team_advanced_stats (
    game_id TEXT,
    team_abbr TEXT,
    season INT,
    week INT,
    
    -- EPA
    epa_total DECIMAL(6,2),
    epa_per_play DECIMAL(4,2),
    epa_passing DECIMAL(6,2),
    epa_rushing DECIMAL(6,2),
    
    -- Success Rate
    success_rate DECIMAL(4,3),
    
    -- Situational
    redzone_trips INT,
    redzone_tds INT,
    redzone_efficiency DECIMAL(4,3),
    third_down_attempts INT,
    third_down_conversions INT,
    third_down_pct DECIMAL(4,3),
    fourth_down_attempts INT,
    fourth_down_conversions INT,
    fourth_down_pct DECIMAL(4,3),
    
    PRIMARY KEY (game_id, team_abbr)
);

-- Rolling averages (momentum indicators)
CREATE TABLE team_rolling_stats (
    team_abbr TEXT,
    season INT,
    week INT,
    
    -- Last 3 games
    last_3_avg_points DECIMAL(5,2),
    last_3_avg_points_allowed DECIMAL(5,2),
    last_3_avg_yards_per_play DECIMAL(4,2),
    last_3_avg_turnovers DECIMAL(4,2),
    
    -- Last 5 games
    last_5_avg_points DECIMAL(5,2),
    last_5_avg_points_allowed DECIMAL(5,2),
    last_5_avg_yards_per_play DECIMAL(4,2),
    last_5_avg_turnovers DECIMAL(4,2),
    
    PRIMARY KEY (team_abbr, season, week)
);

-- Home/Away performance splits
CREATE TABLE team_venue_splits (
    team_abbr TEXT,
    season INT,
    venue TEXT,  -- 'home' or 'away'
    
    games_played INT,
    wins INT,
    losses INT,
    avg_points DECIMAL(5,2),
    avg_points_allowed DECIMAL(5,2),
    avg_yards_per_play DECIMAL(4,2),
    
    PRIMARY KEY (team_abbr, season, venue)
);
```

**Warning**: Play-by-play is MASSIVE. Only download when needed, implement aggressive caching.

---

### 🗺 **PHASE 4: ADVANCED ANALYTICS** (Future - ChatGPT Schema)
*Opponent-adjusted metrics, matchup modeling, power ratings*

**Timeline**: Post-graduation / After production proven stable  
**Complexity**: HIGH - requires statistical modeling

This is where the complex ChatGPT schema comes in:
- Opponent-adjusted EPA (normalize for defensive strength)
- Matchup-specific variables (pass-heavy vs pass defense)
- Power ratings / team strength scores
- Materialized views for performance
- Predictive modeling algorithms
- Line movement analysis (requires external API)
- Sharp money indicators (requires external source)

**Save for Phase 4 - Don't overcomplicate MVP**

---

## 🎯 REALISTIC MVP SCOPE FOR BACHELOR'S PROJECT

### **NOW (Phase 2 - Next 2 weeks):**
- ✅ Basic team stats (points, yards, plays) per game
- ✅ Betting lines (spread, total, moneyline)
- ✅ Home/away context
- ✅ Rest days / short week indicators
- ✅ 3 seasons historical data (2022-2024)
- ✅ Simple UI showing team history + betting lines
- ✅ API endpoints for historical queries

**Deliverable**: Working historical stats database with betting lines

### **LATER (Phase 3 - If time allows before graduation):**
- EPA and success rate from play-by-play
- Rolling averages (last 3/5 games)
- Red zone efficiency
- Third/fourth down conversion rates
- Home/away performance splits

**Deliverable**: Advanced analytics dashboard

### **FUTURE (Phase 4 - After graduation):**
- Opponent-adjusted metrics
- Predictive modeling
- Line movement tracking (external API)
- Sharp money indicators
- Injury impact modeling
- Weather regression analysis

**Deliverable**: Professional-grade betting analytics platform

---

## 🚀 READY TO START PHASE 2?

**What we'll build:**
1. Three new tables: `team_game_stats`, `betting_lines`, `game_context`
2. Data loader: Pull 2022-2024 seasons from nflverse (~850 games)
3. API endpoints: Historical team stats + betting lines
4. Simple UI: Team history viewer with betting context

**Time estimate**: 2 weeks  
**Complexity**: Medium (aggregating player stats to team level)  
**Risk**: Low (nflverse proven working, data available)

**Shall I create the Phase 2 schema and start building the data loader?**

```
