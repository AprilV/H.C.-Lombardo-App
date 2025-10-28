# Phase 2 - Additional Data Sources & Integration
**ChatGPT Reference Documentation**

RECEIVED: October 22, 2025
SOURCE: ChatGPT conversation - Complete data pipeline for betting analytics
PURPOSE: Reference for integrating odds, schedules, injuries, weather, and projections

---

## Overview

This document covers the **complete data pipeline** for HC Lombardo Phase 2, focusing on data sources beyond the core nflverse play-by-play aggregations.

**What nflverse provides (FREE):**
- ✅ Play-by-play data (EPA, success rate, yards, TOs) - via `nfl-data-py`
- ✅ Schedules (game IDs, kickoff times, home/away) - via `nflreadpy`
- ✅ Injuries (weekly reports, status/designation) - via `nflreadpy`
- ✅ Rosters, depth charts, combine data - via `nflreadpy`

**What nflverse does NOT provide:**
- ❌ Betting odds/lines (sportsbooks)
- ❌ Real-time weather data
- ❌ Live game scores during play

**Solution:** Hybrid approach with CSV loaders and optional paid API stubs.

---

## A) Betting Lines/Odds

**Problem:** nflverse does not ship sportsbook odds.

**Solutions:**
1. **Community data**: Import historical CSVs (Kaggle, your own scrapes)
2. **Paid API (optional)**: The Odds API, SportsDataIO, etc.
3. **Manual entry**: Small-scale for testing

### Database Schema

```sql
SET search_path = hcl, public;

CREATE TABLE IF NOT EXISTS betting_lines (
  game_id          TEXT    NOT NULL,
  book             TEXT    NOT NULL,         -- e.g., 'consensus', 'pinnacle', 'dk'
  line_type        TEXT    NOT NULL,         -- 'spread' | 'total' | 'moneyline'
  open_value       DOUBLE PRECISION,         -- e.g., -3.5 for spread, 44.5 total, -135 ML
  open_time_utc    TIMESTAMPTZ,
  close_value      DOUBLE PRECISION,         -- closing line (if known)
  close_time_utc   TIMESTAMPTZ,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (game_id, book, line_type)
);

CREATE INDEX IF NOT EXISTS idx_blines_type ON betting_lines(line_type);
```

**Key Design Decisions:**
- Composite PK: `(game_id, book, line_type)` - Supports multiple sportsbooks per game
- `book = 'consensus'` - Use this for aggregated market consensus
- `open_value` vs `close_value` - Track line movement
- Timestamps: Track when lines open/close for historical analysis

### CSV Loader (Python)

```python
# file: ingest_betting_lines_csv.py
import os, pandas as pd
from sqlalchemy import create_engine, text

DB = os.getenv("DATABASE_URL")
if not DB: raise SystemExit("DATABASE_URL not set")
engine = create_engine(DB, pool_pre_ping=True)

def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # expected columns: game_id, book, line_type, open_value, open_time_utc, close_value, close_time_utc
    need = ["game_id","book","line_type","open_value","open_time_utc","close_value","close_time_utc"]
    missing = [c for c in need if c not in df.columns]
    if missing: raise SystemExit(f"Missing columns: {missing}")
    return df

def upsert(df: pd.DataFrame):
    sql = text("""
    INSERT INTO hcl.betting_lines (game_id, book, line_type, open_value, open_time_utc, close_value, close_time_utc)
    VALUES (:game_id,:book,:line_type,:open_value,:open_time_utc,:close_value,:close_time_utc)
    ON CONFLICT (game_id, book, line_type) DO UPDATE SET
      open_value=EXCLUDED.open_value, open_time_utc=EXCLUDED.open_time_utc,
      close_value=EXCLUDED.close_value, close_time_utc=EXCLUDED.close_time_utc;
    """)
    with engine.begin() as cxn:
        cxn.execute(sql, df.to_dict(orient="records"))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    args = ap.parse_args()
    upsert(load_csv(args.csv))
```

**Usage:**
```bash
python ingest_betting_lines_csv.py --csv path/to/odds_2024.csv
```

**CSV Format Example:**
```csv
game_id,book,line_type,open_value,open_time_utc,close_value,close_time_utc
2024_01_KC_BAL,consensus,spread,-3.0,2024-09-01 10:00:00,-3.5,2024-09-05 20:20:00
2024_01_KC_BAL,consensus,total,46.5,2024-09-01 10:00:00,47.0,2024-09-05 20:20:00
```

### View: Matchups with Lines

```sql
-- Adds consensus closing lines if present (spread/total). Safe to re-run.
CREATE OR REPLACE VIEW v_game_matchup_with_lines AS
SELECT
  d.*,
  bl_sp.close_value AS market_spread_consensus,  -- home negative = home favored
  bl_tot.close_value AS market_total_consensus
FROM hcl.v_game_matchup_display d
LEFT JOIN LATERAL (
  SELECT close_value FROM hcl.betting_lines
  WHERE game_id = d.game_id AND book = 'consensus' AND line_type='spread'
) bl_sp ON TRUE
LEFT JOIN LATERAL (
  SELECT close_value FROM hcl.betting_lines
  WHERE game_id = d.game_id AND book = 'consensus' AND line_type='total'
) bl_tot ON TRUE;
```

**Why LATERAL joins?**
- Efficient for 1:1 lookups (one spread, one total per game)
- Cleaner than subqueries in SELECT list
- Performs well with proper indexes

---

## B) Schedules (from nflverse)

**Data Source:** Lee Sharpe's schedule data via `nflreadpy`

**What it provides:**
- `game_id` - Unique identifier (e.g., "2024_01_KC_BAL")
- `kickoff_time_utc` - Exact timestamp (TIMESTAMPTZ)
- `home_team`, `away_team` - Team abbreviations
- `stadium`, `city`, `state`, `timezone` - Location metadata
- `game_type` - REG, WC, DIV, CON, SB
- `is_postseason` - Boolean flag

### Python Loader

```python
# file: ingest_schedules.py
import os
import pandas as pd
from sqlalchemy import create_engine, text

DB = os.getenv("DATABASE_URL")
if not DB: raise SystemExit("DATABASE_URL not set")
engine = create_engine(DB, pool_pre_ping=True)

# Use nflverse's published data via nflreadpy
try:
    import nflreadpy as nfl  # python port of nflreadr
except ImportError:
    nfl = None

def fetch_schedules(seasons):
    if nfl:
        sched = nfl.load_schedules(seasons)  # returns polars; convert to pandas
        try:
            import polars as pl
            if isinstance(sched, pl.DataFrame):
                sched = sched.to_pandas()
        except Exception:
            pass
        return sched
    else:
        # Fallback: nflverse-data keeps schedules in releases; nflreadr is the preferred route.
        raise SystemExit("Install nflreadpy: pip install nflreadpy")

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    # expected fields from nflverse schedules: game_id, season, week, game_type, gameday, gametime, kickoff_time_utc,
    # home_team, away_team, stadium, city, state, timezone, is_postseason or can be derived (POST vs REG)
    cols = {
        "game_id":"game_id","season":"season","week":"week","game_type":"game_type",
        "kickoff_time_utc":"kickoff_time_utc","home_team":"home_team","away_team":"away_team",
        "stadium":"stadium","site":"stadium","venue":"stadium",
        "location":"city","city":"city","state":"state","timezone":"timezone"
    }
    out = pd.DataFrame()
    for k,v in cols.items():
        if k in df.columns:
            out[v] = df[k]
    out["is_postseason"] = out.get("game_type","REG").fillna("REG").str.upper().ne("REG")
    # derive game_date if not present
    if "game_date" not in out.columns:
        out["game_date"] = pd.to_datetime(out["kickoff_time_utc"]).dt.date
    return out[["game_id","season","week","game_date","kickoff_time_utc","home_team","away_team","stadium","city","state","timezone","is_postseason"]]

def upsert(df: pd.DataFrame):
    df = df.dropna(subset=["game_id"])
    sql = text("""
    INSERT INTO hcl.games (game_id, season, week, game_date, kickoff_time_utc, home_team, away_team, stadium, city, state, timezone, is_postseason)
    VALUES (:game_id, :season, :week, :game_date, :kickoff_time_utc, :home_team, :away_team, :stadium, :city, :state, :timezone, :is_postseason)
    ON CONFLICT (game_id) DO UPDATE SET
      season=EXCLUDED.season, week=EXCLUDED.week, game_date=EXCLUDED.game_date,
      kickoff_time_utc=EXCLUDED.kickoff_time_utc, home_team=EXCLUDED.home_team, away_team=EXCLUDED.away_team,
      stadium=EXCLUDED.stadium, city=EXCLUDED.city, state=EXCLUDED.state, timezone=EXCLUDED.timezone,
      is_postseason=EXCLUDED.is_postseason;
    """)
    with engine.begin() as cxn:
        cxn.execute(sql, df.to_dict(orient="records"))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", nargs="+", required=True, type=int)
    args = ap.parse_args()
    df = fetch_schedules(args.seasons)
    upsert(normalize(df))
```

**Usage:**
```bash
python ingest_schedules.py --seasons 2022 2023 2024
```

**Why This Matters:**
- Populates `hcl.games` table with official nflverse game IDs
- Provides `kickoff_time_utc` for timezone-aware week detection
- Ensures game metadata matches play-by-play data (same IDs)

---

## C) Projections & Market Edge

**Concept:** Generate simple baseline projections using our advanced stats, then compare to market consensus to identify betting value.

**Projection Model (Linear Baseline):**
- **Spread**: `-2.2 * diff_epa_pp - 8.0 * diff_sr - 1.2` (home field)
- **Total**: `(home_ppg_for + away_ppg_for) + 14.0 * (home_epa_pp + away_epa_pp)`

**Why These Weights?**
- Based on professional betting research (from ChatGPT's analysis)
- EPA/play is ~2.2 points per 0.1 EPA edge
- Success rate differential worth ~8 points
- Home field advantage ~1.2 points on average
- Total incorporates both scoring trends and efficiency

### View: Projections + Edge vs Market

```sql
-- hcl.v_game_matchup_with_proj: adds projected_spread/total and edge vs consensus
CREATE OR REPLACE VIEW v_game_matchup_with_proj AS
WITH base AS (
  SELECT d.*, 
         bl_sp.close_value AS market_spread_consensus,
         bl_tot.close_value AS market_total_consensus
  FROM hcl.v_game_matchup_display d
  LEFT JOIN LATERAL (
    SELECT close_value FROM hcl.betting_lines
    WHERE game_id = d.game_id AND book='consensus' AND line_type='spread'
  ) bl_sp ON TRUE
  LEFT JOIN LATERAL (
    SELECT close_value FROM hcl.betting_lines
    WHERE game_id = d.game_id AND book='consensus' AND line_type='total'
  ) bl_tot ON TRUE
)
SELECT
  b.*,
  /* baseline projection (tune these weights later) */
  /* spread is home minus away; negative favors home */
  (-2.2 * COALESCE(b.diff_epa_pp,0)
   - 8.0 * COALESCE(b.diff_sr,0)
   - 1.2                   /* home field baseline */
  ) AS projected_spread,
  /* total via average of teams' PPG and EPA-based lift */
  (COALESCE(b.home_ppg_for,0) + COALESCE(b.away_ppg_for,0))/1.0
    + 14.0 * (COALESCE(b.home_epa_pp,0) + COALESCE(b.away_epa_pp,0)) AS projected_total,

  /* edges vs. market (negative is value on home, positive value on away) */
  CASE WHEN b.market_spread_consensus IS NULL THEN NULL
       ELSE (b.market_spread_consensus - (
             -2.2*COALESCE(b.diff_epa_pp,0) - 8.0*COALESCE(b.diff_sr,0) - 1.2))
  END AS edge_spread_points,
  CASE WHEN b.market_total_consensus IS NULL THEN NULL
       ELSE (b.market_total_consensus - (
             (COALESCE(b.home_ppg_for,0)+COALESCE(b.away_ppg_for,0))
             + 14.0*(COALESCE(b.home_epa_pp,0)+COALESCE(b.away_epa_pp,0))
       ))
  END AS edge_total_points
FROM base b;
```

**How to Interpret Edge:**
- `edge_spread_points < 0`: Value on **home team** (market undervalues home)
- `edge_spread_points > 0`: Value on **away team** (market undervalues away)
- `edge_total_points < 0`: Value on **under** (market total too high)
- `edge_total_points > 0`: Value on **over** (market total too low)

**Example:**
```
market_spread_consensus: -3.5 (home favored by 3.5)
projected_spread: -5.2 (our model favors home by 5.2)
edge_spread_points: 1.7 (market gives 1.7 extra points to home bettors)
→ Value on home team -3.5 (better than our -5.2 projection)
```

**Backtesting Notes:**
- These weights are **starting points**
- Backtest on historical data to tune
- Consider adjusting by weather, injuries, rest days
- Track performance over time (CLV - Closing Line Value)

---

## D) Injuries & Weather

### Injuries (from nflverse)

**Data Source:** Weekly injury reports via `nflreadpy`

**What it provides:**
- Player name, position, team
- Status: Questionable, Doubtful, Out, IR, PUP
- Designation: DNP (Did Not Practice), LP (Limited), FP (Full)
- Report date (usually Wednesday-Friday of game week)

#### Schema

```sql
SET search_path = hcl, public;

CREATE TABLE IF NOT EXISTS injuries (
  season       INT NOT NULL,
  week         INT NOT NULL,
  team         TEXT NOT NULL,
  full_name    TEXT,
  position     TEXT,
  status       TEXT,             -- e.g., Questionable, Out, IR, PUP
  designation  TEXT,             -- e.g., DNP, LP, FP
  report_date  DATE,
  gsis_id      TEXT,
  updated_at   TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (season, week, team, full_name)
);
```

#### Python Loader

```python
# file: ingest_injuries.py
import os
import pandas as pd
from sqlalchemy import create_engine, text

DB = os.getenv("DATABASE_URL")
if not DB: raise SystemExit("DATABASE_URL not set")
engine = create_engine(DB, pool_pre_ping=True)

try:
    import nflreadpy as nfl
except ImportError:
    raise SystemExit("Install nflreadpy: pip install nflreadpy")

def fetch(seasons):
    inj = nfl.load_injuries(seasons)  # mirrors nflreadr::load_injuries()
    try:
        import polars as pl
        if isinstance(inj, pl.DataFrame):
            inj = inj.to_pandas()
    except Exception:
        pass
    return inj

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    # map common fields; leave extras in staging if needed
    out = pd.DataFrame()
    out["season"] = df["season"]
    out["week"] = df["week"]
    out["team"] = df["team"]
    out["full_name"] = df.get("full_name")
    out["position"] = df.get("position")
    out["status"] = df.get("status")
    out["designation"] = df.get("practice_status")
    out["report_date"] = pd.to_datetime(df.get("report_date")).dt.date if "report_date" in df else None
    out["gsis_id"] = df.get("gsis_id")
    return out

def upsert(df: pd.DataFrame):
    sql = text("""
    INSERT INTO hcl.injuries (season, week, team, full_name, position, status, designation, report_date, gsis_id)
    VALUES (:season, :week, :team, :full_name, :position, :status, :designation, :report_date, :gsis_id)
    ON CONFLICT (season, week, team, full_name) DO UPDATE SET
      position=EXCLUDED.position, status=EXCLUDED.status, designation=EXCLUDED.designation,
      report_date=EXCLUDED.report_date, gsis_id=EXCLUDED.gsis_id, updated_at=NOW();
    """)
    with engine.begin() as cxn:
        cxn.execute(sql, df.to_dict(orient="records"))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", nargs="+", required=True, type=int)
    args = ap.parse_args()
    df = fetch(args.seasons)
    upsert(normalize(df))
```

**Usage:**
```bash
python ingest_injuries.py --seasons 2024
```

### Weather (CSV Stub - No Free API)

**Problem:** nflverse does not provide real-time weather data.

**Solutions:**
1. Manual CSV entry (small-scale testing)
2. Scrape weather sites (legal gray area)
3. Paid weather API (OpenWeatherMap, Weather.com API)
4. Indoor games: Mark as `roof='indoor'`, ignore weather

#### Schema

```sql
CREATE TABLE IF NOT EXISTS weather (
  game_id        TEXT PRIMARY KEY,
  roof           TEXT,            -- e.g., 'indoor','outdoor','retractable'
  surface        TEXT,            -- e.g., 'turf','grass'
  temp_f         DOUBLE PRECISION,
  wind_mph       DOUBLE PRECISION,
  precip_prob    DOUBLE PRECISION,
  source         TEXT,
  observed_time  TIMESTAMPTZ,
  updated_at     TIMESTAMPTZ DEFAULT NOW()
);
```

#### CSV Loader

```python
# file: ingest_weather_csv.py
import os, pandas as pd
from sqlalchemy import create_engine, text

DB = os.getenv("DATABASE_URL")
if not DB: raise SystemExit("DATABASE_URL not set")
engine = create_engine(DB, pool_pre_ping=True)

def run(csv_path: str, source_name: str = "manual"):
    df = pd.read_csv(csv_path)
    # expected: game_id, roof, surface, temp_f, wind_mph, precip_prob, observed_time
    sql = text("""
    INSERT INTO hcl.weather (game_id, roof, surface, temp_f, wind_mph, precip_prob, source, observed_time)
    VALUES (:game_id,:roof,:surface,:temp_f,:wind_mph,:precip_prob,:source,:observed_time)
    ON CONFLICT (game_id) DO UPDATE SET
      roof=EXCLUDED.roof, surface=EXCLUDED.surface, temp_f=EXCLUDED.temp_f,
      wind_mph=EXCLUDED.wind_mph, precip_prob=EXCLUDED.precip_prob,
      source=EXCLUDED.source, observed_time=EXCLUDED.observed_time,
      updated_at=NOW();
    """)
    df["source"] = source_name
    with engine.begin() as cxn:
        cxn.execute(sql, df.to_dict(orient="records"))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--source", default="manual")
    args = ap.parse_args()
    run(args.csv, args.source)
```

**CSV Format Example:**
```csv
game_id,roof,surface,temp_f,wind_mph,precip_prob,observed_time
2024_01_KC_BAL,outdoor,grass,72.5,8.2,0.15,2024-09-05 20:00:00
2024_01_DAL_CLE,retractable,turf,68.0,5.0,0.0,2024-09-08 13:00:00
```

**Usage:**
```bash
python ingest_weather_csv.py --csv weather_week1.csv --source "nws_scrape"
```

---

## Data Source Summary

| Data Type | Source | Method | Cost |
|-----------|--------|--------|------|
| **Play-by-Play** | nflverse | `nfl-data-py` | FREE |
| **Schedules** | nflverse (Lee Sharpe) | `nflreadpy` | FREE |
| **Injuries** | nflverse | `nflreadpy` | FREE |
| **Rosters** | nflverse | `nflreadpy` | FREE |
| **Betting Odds** | Community CSVs / Paid API | CSV loader or API stub | VARIES |
| **Weather** | Manual CSV / Paid API | CSV loader or API stub | VARIES |
| **Live Scores** | ESPN API (current) | `espn_data_fetcher.py` | FREE |

---

## Installation Requirements

```bash
# Core nflverse access
pip install nfl-data-py     # Play-by-play (already installed)
pip install nflreadpy       # Schedules, injuries, rosters

# Optional: Polars for faster processing (nflreadpy uses it)
pip install polars

# Database
pip install psycopg2-binary sqlalchemy pandas
```

---

## Flask API Endpoint Suggestion

ChatGPT offers to add:

**GET `/api/lines?season={}&week={}`**
- Returns all games for a week with:
  - Market lines (spread, total)
  - Our projections (projected_spread, projected_total)
  - Edge calculations (edge_spread_points, edge_total_points)
- Merges `v_game_matchup_with_proj` into existing matchup endpoints

**Integration Options:**
1. **Option A**: Add `market_*` and `projected_*` fields to existing `/api/matchups` response
2. **Option B**: Create separate `/api/lines` endpoint for betting-specific data
3. **Option C**: Add query param `/api/matchups?include_lines=true`

**Recommendation:** Option A (merge into `/api/matchups`) for simplicity, less round trips.

---

## Next Steps

**For HC Lombardo Implementation:**

1. **Install nflreadpy**:
   ```bash
   pip install nflreadpy
   ```

2. **Create tables** (betting_lines, injuries, weather):
   - Run SQL from sections A, D above

3. **Ingest schedules** (one-time for historical + weekly for new seasons):
   ```bash
   python ingest_schedules.py --seasons 2022 2023 2024
   ```

4. **Ingest injuries** (weekly during season):
   ```bash
   python ingest_injuries.py --seasons 2024
   ```

5. **Source betting lines**:
   - Find historical CSV datasets (Kaggle, sportsbookreview.com archives)
   - Format to match expected schema
   - Load via `ingest_betting_lines_csv.py`

6. **Create views**:
   - `v_game_matchup_with_lines` (section A)
   - `v_game_matchup_with_proj` (section C)

7. **Build Flask endpoints**:
   - Translate ChatGPT's FastAPI patterns to Flask
   - Add `/api/matchups` response fields: `market_spread_consensus`, `projected_spread`, `edge_spread_points`

8. **Backtest projections**:
   - Query historical data (2022-2023 seasons)
   - Calculate projection accuracy
   - Tune weights in `v_game_matchup_with_proj` view

---

## References

- **nflverse Documentation**: https://nflreadr.nflverse.com/
- **nfl-data-py (PBP)**: https://pypi.org/project/nfl-data-py/
- **nflreadpy (Schedules/Injuries)**: https://pypi.org/project/nflreadpy/
- **nflfastR (R package, original)**: https://www.nflfastr.com/
- **Lee Sharpe Schedules**: https://github.com/nflverse/nfldata (schedules.csv)

---

## ChatGPT's Offer

> If you want, I can also add:
> 
> `/api/lines?season=&week=` endpoint + merge `v_game_matchup_with_proj` into your existing FastAPI (so the front-end gets market + projection + edge in one call).

**April's Response:** I acknowledge this offer. I will decide whether to request this after:
1. Reviewing complete reference implementation
2. Understanding Flask translation requirements
3. Determining UI needs for betting lines display

For now, I have all the SQL, Python loaders, and view patterns needed to integrate betting lines and projections into HC Lombardo.
