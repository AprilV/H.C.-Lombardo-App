# H.C. LOMBARDO SYSTEM ARCHITECTURE
**Current + Future State Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER (localhost:5000)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │   MAIN PAGE      │  │  HISTORICAL      │  │   BETTING        │        │
│  │   (Current)      │  │  PAGE (NEW)      │  │   PAGE (NEW)     │        │
│  │                  │  │                  │  │                  │        │
│  │ Current Week     │  │ Select Season:   │  │ Week 7 Lines     │        │
│  │ Standings        │  │ [2024 ▼]        │  │                  │        │
│  │                  │  │ Select Week:     │  │ DEN @ NO         │        │
│  │ DAL: 3-3-1      │  │ [5 ▼]           │  │ Spread: -3.5     │        │
│  │ PPG: 31.7       │  │                  │  │ Total: 47.5      │        │
│  │ PA: 29.4        │  │ [View Stats]     │  │ ML: -180/+150    │        │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘        │
│           │                     │                      │                   │
└───────────┼─────────────────────┼──────────────────────┼───────────────────┘
            │                     │                      │
            ▼                     ▼                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                           API SERVER (Flask)                              │
│                        api_server.py (Port 5000)                          │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  EXISTING ENDPOINTS:              NEW ENDPOINTS (Phase 2):               │
│  ┌─────────────────────┐          ┌──────────────────────────┐          │
│  │ GET /api/teams      │          │ GET /api/historical/     │          │
│  │ GET /api/teams/DAL  │          │     ?season=2024&week=5  │          │
│  │ GET /health         │          │                          │          │
│  └──────────┬──────────┘          │ GET /api/betting/current │          │
│             │                     │                          │          │
│             │                     │ GET /api/games/schedule  │          │
│             │                     └─────────────┬────────────┘          │
│             │                                   │                        │
└─────────────┼───────────────────────────────────┼────────────────────────┘
              │                                   │
              ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      POSTGRESQL DATABASE (localhost:5432)                   │
│                            Database: nfl_analytics                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ EXISTING TABLE: teams (32 rows - CURRENT SNAPSHOT)                 │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ id | name              | abbr | wins | losses | ties | ppg  | pa   │   │
│  │ 1  | Dallas Cowboys    | DAL  | 3    | 3      | 1    | 31.7 | 29.4 │   │
│  │ 2  | New York Giants   | NYG  | 2    | 4      | 0    | 18.5 | 24.1 │   │
│  │ ... (30 more teams)                                                  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ NEW TABLE: team_stats_weekly (THOUSANDS of rows - HISTORICAL)      │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ id | season | week | team | wins | losses | ties | pf  | pa | ...  │   │
│  │ 1  | 2024   | 1    | DAL  | 1    | 0      | 0    | 33  | 17 | ...  │   │
│  │ 2  | 2024   | 2    | DAL  | 1    | 1      | 0    | 63  | 44 | ...  │   │
│  │ 3  | 2024   | 3    | DAL  | 2    | 1      | 0    | 96  | 69 | ...  │   │
│  │ 4  | 2024   | 4    | DAL  | 2    | 2      | 0    | 116 | 89 | ...  │   │
│  │ 5  | 2024   | 5    | DAL  | 3    | 2      | 0    | 145 | 115| ...  │   │
│  │ 6  | 2024   | 6    | DAL  | 3    | 2      | 1    | 165 | 135| ...  │   │
│  │ 7  | 2024   | 7    | DAL  | 3    | 3      | 1    | 188 | 162| ...  │   │
│  │ ... (570+ rows per season × 32 teams × multiple seasons)            │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ NEW TABLE: games (285 rows per season - SCHEDULE & RESULTS)        │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ game_id        | season | week | home | away | h_score | a_score   │   │
│  │ 2024_07_DEN_NO | 2024   | 7    | NO   | DEN  | 10      | 33        │   │
│  │ 2024_07_DAL_SF | 2024   | 7    | SF   | DAL  | 30      | 24        │   │
│  │ ... (285 games per season)                                          │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │ NEW TABLE: betting_lines (285 rows per season - ODDS)              │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ game_id        | spread | home_ml | away_ml | total | over | under │   │
│  │ 2024_07_DEN_NO | -3.5   | -180    | +150    | 47.5  | -110 | -110  │   │
│  │ 2024_07_DAL_SF | -4.5   | -200    | +170    | 52.5  | -110 | -110  │   │
│  │ ... (285 games per season with betting lines)                       │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────▲───────────────────────────────────────────▲─────────────────┘
              │                                           │
              │                                           │
┌─────────────┴──────────────┐         ┌────────────────┴─────────────────┐
│   DATA UPDATER SYSTEM 1    │         │   DATA UPDATER SYSTEM 2 (NEW)    │
│   (EXISTING - KEEP)        │         │   (ADD - DON'T BREAK SYSTEM 1)   │
├────────────────────────────┤         ├──────────────────────────────────┤
│                            │         │                                  │
│ live_data_updater.py       │         │ nflverse_data_fetcher.py         │
│                            │         │                                  │
│ Runs: Every 15 minutes     │         │ Runs: Daily (or weekly)          │
│                            │         │                                  │
│ Updates: teams table       │         │ Inserts: team_stats_weekly       │
│ (overwrites 32 rows)       │         │          games                   │
│                            │         │          betting_lines           │
│                            │         │ (accumulates historical data)    │
└────────────▲───────────────┘         └──────────────▲───────────────────┘
             │                                        │
             │                                        │
┌────────────┴───────────────┐         ┌─────────────┴────────────────────┐
│  DATA SOURCE: CURRENT      │         │  DATA SOURCE: NFLVERSE           │
│                            │         │                                  │
│ ESPN API                   │         │ nfl-data-py (Python package)     │
│ - Standings (W-L-T)        │         │                                  │
│ - Real-time scores         │         │ import_schedules([2024, 2023])   │
│                            │         │ - Game results by week           │
│ TeamRankings.com (scrape)  │         │ - Betting lines (built-in!)      │
│ - PPG stats                │         │ - Historical data (1999+)        │
│ - PA stats                 │         │ - Weather, coaches, etc.         │
│                            │         │                                  │
│ Free, no rate limits       │         │ Free, no rate limits, no API key │
└────────────────────────────┘         └──────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════

KEY POINTS:

1. SYSTEM 1 (Left Side) = KEEP RUNNING, NO CHANGES
   - Updates teams table every 15 min
   - Serves main page /api/teams
   - Uses ESPN + TeamRankings

2. SYSTEM 2 (Right Side) = ADD NEW, DON'T INTERFERE
   - Populates new historical tables daily
   - Serves new pages (historical, betting)
   - Uses nflverse

3. BOTH RUN INDEPENDENTLY = "Parallel"
   - System 1 doesn't know System 2 exists
   - System 2 doesn't touch teams table
   - No conflicts, no breaking changes

4. USER EXPERIENCE:
   - Main page still works exactly the same
   - New historical page shows time-travel stats
   - New betting page shows odds/lines
   - Can compare "now" vs "then"

═══════════════════════════════════════════════════════════════════════════════
```
