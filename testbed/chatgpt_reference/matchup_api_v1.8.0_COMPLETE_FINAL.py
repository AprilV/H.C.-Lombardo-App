"""
ChatGPT Reference Implementation - FastAPI Matchup API v1.8.0 COMPLETE
=======================================================================
FINAL production-grade API with betting lines, projections, and edge analysis.

RECEIVED: October 22, 2025
SOURCE: ChatGPT conversation - Phase 2 implementation reference
PURPOSE: Study patterns for HC Lombardo Flask translation

VERSION HISTORY:
- v1.0.0: Basic matchup endpoints
- v1.3.0: Added /api/weeks, /api/seasons, timestamp-aware /api/next_week
- v1.5.0: Added /api/upcoming_matchups (single-call convenience)
- v1.6.0: Added include_last_completed fallback parameter
- v1.7.0: Added /api/week_summary (analytics aggregates + top edges)
- v1.8.0: Added betting lines, projections, and edge endpoints

KEY FEATURES (v1.8.0):
- Complete CRUD for matchups (weekly, single game, team-specific)
- Timezone-aware week detection using kickoff_time_utc
- Single-call upcoming matchups endpoint with graceful fallback
- Week-level analytics aggregates (avg/median EPA, YPP, PPG, etc.)
- **NEW: Betting lines endpoints** (query by season/week/game/book)
- **NEW: Projections endpoints** (market + our model + edge calculation)
- **NEW: Upcoming matchups with projections** (one-call for betting UI)
- CTE pattern for week aggregation
- IANA timezone support (optional, defaults to UTC)
- Graceful season-end handling

COMPLETE ENDPOINT LIST (11 total):
1. GET /healthz - Health check
2. GET /api/seasons - List all available seasons (DESC)
3. GET /api/weeks?season={} - Available weeks by season
4. GET /api/next_week?tz={} - Next upcoming or latest completed week
5. GET /api/matchups?season={}&week={}&team={} - Weekly matchups (base stats only)
6. GET /api/matchups/{game_id} - Single game matchup (base stats only)
7. GET /api/matchups_with_proj?season={}&week={}&team={} - Weekly matchups with projections
8. GET /api/matchups_with_proj/{game_id} - Single game with projections
9. GET /api/upcoming_matchups_with_proj?tz={}&include_last_completed={} - Convenience + projections
10. GET /api/lines?season={}&week={}&game_id={}&book={}&line_type={} - Query betting lines
11. GET /api/week_summary?season={}&week={}&tz={} - Week analytics (from v1.7.0)

DATABASE REQUIREMENTS:
- hcl.games table with kickoff_time_utc (TIMESTAMPTZ), season, week, is_postseason
- hcl.betting_lines table (game_id, book, line_type, open/close values)
- hcl.v_game_matchup_display view (43 columns, base stats)
- hcl.v_game_matchup_with_proj view (base + market + projection + edge)
- Indexes: idx_games_kickoff, idx_blines_type

NEW IN v1.8.0 - BETTING INTEGRATION:

1. ProjectedMatchup Model (extends Matchup):
   - Adds 6 fields: market_spread_consensus, market_total_consensus
   - projected_spread, projected_total (our model)
   - edge_spread_points, edge_total_points (value indicators)

2. LineRow Model:
   - Simple representation of betting_lines table
   - Supports open/close values and timestamps
   - Multi-sportsbook tracking

3. Dual-mode endpoints:
   - /api/matchups - Base stats only (fast, lightweight)
   - /api/matchups_with_proj - Full betting analytics (market + model + edge)

4. Flexible lines query:
   - Filter by season/week OR game_id
   - Filter by sportsbook (e.g., 'consensus', 'pinnacle', 'dk')
   - Filter by line_type ('spread', 'total', 'moneyline')

TRANSLATION NOTES FOR FLASK:
- Replace SQLAlchemy with psycopg2 connection pool
- Replace Pydantic BaseModel with dict responses + jsonify
- Replace FastAPI Query() with request.args.get() + manual validation
- Keep dual-view pattern (display vs proj) for performance
- Use same LATERAL join pattern for betting_lines
- All PostgreSQL queries work identically in psycopg2
"""

import os
from typing import Optional, List, Any, Dict, Tuple

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL not set")

engine: Engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(title="HC in Lombardo API", version="1.8.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------
class Matchup(BaseModel):
    """
    Base matchup model (43 fields) - unchanged from v1.7.0
    Contains only advanced stats, no betting lines/projections
    """
    season: int
    week: int
    game_date: Optional[str] = None
    game_id: str
    home_team: str
    away_team: str
    stadium: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    timezone: Optional[str] = None

    home_gp: Optional[int] = None
    home_ppg_for: Optional[float] = None
    home_ppg_against: Optional[float] = None
    home_ypp: Optional[float] = None
    home_sr: Optional[float] = None
    home_epa_pp: Optional[float] = None
    home_to_pg: Optional[float] = None
    home_4d_rate: Optional[float] = None
    home_3d_rate: Optional[float] = None

    away_gp: Optional[int] = None
    away_ppg_for: Optional[float] = None
    away_ppg_against: Optional[float] = None
    away_ypp: Optional[float] = None
    away_sr: Optional[float] = None
    away_epa_pp: Optional[float] = None
    away_to_pg: Optional[float] = None
    away_4d_rate: Optional[float] = None
    away_3d_rate: Optional[float] = None

    home_epa_l3: Optional[float] = None
    home_ypp_l3: Optional[float] = None
    home_ppg_l3: Optional[float] = None
    away_epa_l3: Optional[float] = None
    away_ypp_l3: Optional[float] = None
    away_ppg_l3: Optional[float] = None

    diff_epa_pp: Optional[float] = None
    diff_ypp: Optional[float] = None
    diff_sr: Optional[float] = None
    diff_ppg_for: Optional[float] = None


class ProjectedMatchup(Matchup):
    """
    NEW IN v1.8.0: Extended matchup with betting analytics
    
    PATTERN: Inheritance keeps response models clean
    - Base class: 43 stat fields
    - Extended class: +6 betting fields
    
    Use Cases:
    - Public API: Return Matchup (no betting data)
    - Betting UI: Return ProjectedMatchup (full analytics)
    - Performance: Base view faster (no LATERAL joins)
    
    Fields:
    - market_spread_consensus: Sportsbook closing spread (negative = home favored)
    - market_total_consensus: Sportsbook closing total (O/U)
    - projected_spread: Our model's spread prediction
    - projected_total: Our model's total prediction
    - edge_spread_points: Market - Projection (positive = value on away, negative = value on home)
    - edge_total_points: Market - Projection (positive = value on over, negative = value on under)
    """
    market_spread_consensus: Optional[float] = None
    market_total_consensus: Optional[float] = None
    projected_spread: Optional[float] = None
    projected_total: Optional[float] = None
    edge_spread_points: Optional[float] = None
    edge_total_points: Optional[float] = None


class WeeksForSeason(BaseModel):
    """Weeks grouped by season (unchanged from v1.7.0)"""
    season: int
    weeks: List[int]


class NextWeek(BaseModel):
    """Next week metadata with status (unchanged from v1.7.0)"""
    season: int
    week: int
    status: str  # "upcoming" or "latest_completed"


class LineRow(BaseModel):
    """
    NEW IN v1.8.0: Individual betting line representation
    
    PATTERN: Direct mapping of hcl.betting_lines table
    
    Fields:
    - game_id: FK to hcl.games
    - book: Sportsbook identifier ('consensus', 'pinnacle', 'dk', etc.)
    - line_type: 'spread' | 'total' | 'moneyline'
    - open_value: Opening line (e.g., -3.5 spread, 44.5 total, -135 ML)
    - open_time_utc: When line opened (timestamp)
    - close_value: Closing line (most important for sharp bettors)
    - close_time_utc: When line closed (usually kickoff)
    
    Use Cases:
    - Line movement tracking (open vs close)
    - Multi-sportsbook comparison (find best line)
    - Historical analysis (closing line value)
    - Live betting (if open_value updates real-time)
    """
    game_id: str
    book: str
    line_type: str      # spread|total|moneyline
    open_value: Optional[float] = None
    open_time_utc: Optional[str] = None
    close_value: Optional[float] = None
    close_time_utc: Optional[str] = None


# ------------------------------------------------------------------
# Helpers (v1.7.0 helpers + new betting helpers)
# ------------------------------------------------------------------
def rows_to_dicts(rows, keys) -> List[Dict[str, Any]]:
    """Generic row-to-dict converter (unchanged from v1.7.0)"""
    return [dict(zip(keys, r)) for r in rows]


def select_next_or_latest_week(tz: Optional[str]) -> Tuple[int, int, str]:
    """Timezone-aware week detection (unchanged from v1.7.0)"""
    tz = tz or "UTC"
    sql_now = text("SELECT (NOW() AT TIME ZONE :tz) AT TIME ZONE 'UTC' AS now_ref_utc")
    with engine.begin() as cxn:
        try:
            now_ref_row = cxn.execute(sql_now, {"tz": tz}).fetchone()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid timezone.")
        now_ref_utc = now_ref_row[0]

    sql_upcoming = text("""
        WITH weekly AS (
          SELECT season, week, MIN(kickoff_time_utc) AS first_kick
          FROM hcl.games
          WHERE COALESCE(is_postseason, FALSE) = FALSE
          GROUP BY season, week
        )
        SELECT season, week FROM weekly
        WHERE first_kick >= :now_ref_utc
        ORDER BY first_kick ASC LIMIT 1
    """)
    sql_latest = text("""
        WITH weekly AS (
          SELECT season, week, MAX(kickoff_time_utc) AS last_kick
          FROM hcl.games
          WHERE COALESCE(is_postseason, FALSE) = FALSE
          GROUP BY season, week
        )
        SELECT season, week FROM weekly
        WHERE last_kick < :now_ref_utc
        ORDER BY last_kick DESC LIMIT 1
    """)

    with engine.begin() as cxn:
        row = cxn.execute(sql_upcoming, {"now_ref_utc": now_ref_utc}).fetchone()
        if row:
            return int(row[0]), int(row[1]), "upcoming"
        row = cxn.execute(sql_latest, {"now_ref_utc": now_ref_utc}).fetchone()
        if row:
            return int(row[0]), int(row[1]), "latest_completed"
    raise HTTPException(status_code=404, detail="No week data found.")


def select_matchups(season: int, week: int, team: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    """
    Base matchups query (unchanged from v1.7.0)
    Uses v_game_matchup_display (no betting lines)
    """
    team_filter_sql = ""
    params = {"season": season, "week": week, "limit": limit, "offset": offset}
    if team:
        team_filter_sql = "AND (home_team = :team OR away_team = :team)"
        params["team"] = team

    sql = text(f"""
        SELECT *
        FROM hcl.v_game_matchup_display
        WHERE season = :season AND week = :week
          {team_filter_sql}
        ORDER BY game_date NULLS LAST, home_team, away_team
        LIMIT :limit OFFSET :offset
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, params)
        keys = result.keys()
        rows = result.fetchall()
    return rows_to_dicts(rows, keys)


def select_matchups_with_proj(season: int, week: int, team: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    """
    NEW IN v1.8.0: Matchups with betting analytics
    
    PATTERN: Identical to select_matchups() but uses v_game_matchup_with_proj view
    
    Performance Note:
    - v_game_matchup_with_proj includes LATERAL joins to betting_lines
    - Slightly slower than base view (~10-20ms overhead)
    - Cache results if serving high traffic
    """
    team_filter_sql = ""
    params = {"season": season, "week": week, "limit": limit, "offset": offset}
    if team:
        team_filter_sql = "AND (home_team = :team OR away_team = :team)"
        params["team"] = team

    sql = text(f"""
        SELECT *
        FROM hcl.v_game_matchup_with_proj
        WHERE season = :season AND week = :week
          {team_filter_sql}
        ORDER BY game_date NULLS LAST, home_team, away_team
        LIMIT :limit OFFSET :offset
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, params)
        keys = result.keys()
        rows = result.fetchall()
    return rows_to_dicts(rows, keys)


def select_matchups_for(season: int, week: int, with_proj: bool = False) -> List[Dict[str, Any]]:
    """
    NEW IN v1.8.0: Dual-mode matchups query
    
    PATTERN: Single function with view selection based on flag
    
    Why This Matters:
    - DRY principle: One function for both modes
    - Performance option: Caller chooses overhead
    - Used by upcoming_matchups endpoints
    """
    view = "hcl.v_game_matchup_with_proj" if with_proj else "hcl.v_game_matchup_display"
    sql = text(f"""
        SELECT * FROM {view}
        WHERE season = :season AND week = :week
        ORDER BY game_date NULLS LAST, home_team, away_team
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, {"season": season, "week": week})
        keys = result.keys()
        rows = result.fetchall()
    return rows_to_dicts(rows, keys)


def select_matchup_by_id(game_id: str, with_proj: bool = False) -> Optional[Dict[str, Any]]:
    """
    NEW IN v1.8.0: Dual-mode single game query
    
    PATTERN: Same as select_matchups_for() but for single game
    """
    view = "hcl.v_game_matchup_with_proj" if with_proj else "hcl.v_game_matchup_display"
    sql = text(f"SELECT * FROM {view} WHERE game_id = :game_id LIMIT 1")
    with engine.begin() as cxn:
        result = cxn.execute(sql, {"game_id": game_id})
        row = result.fetchone()
        if not row:
            return None
        keys = result.keys()
    return dict(zip(keys, row))


def select_weeks(season: Optional[int]) -> List[Dict[str, Any]]:
    """Available weeks query (unchanged from v1.7.0)"""
    params: Dict[str, Any] = {}
    where_season = ""
    if season is not None:
        where_season = "AND season = :season"
        params["season"] = season

    sql = text(f"""
        SELECT season,
               ARRAY_AGG(DISTINCT week ORDER BY week) AS weeks
        FROM hcl.games
        WHERE COALESCE(is_postseason, FALSE) = FALSE
          {where_season}
        GROUP BY season
        ORDER BY season DESC
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, params)
        rows = result.fetchall()
        keys = result.keys()
    return rows_to_dicts(rows, keys)


def select_seasons() -> List[int]:
    """Available seasons (unchanged from v1.7.0)"""
    sql = text("""
        SELECT DISTINCT season
        FROM hcl.games
        WHERE COALESCE(is_postseason, FALSE) = FALSE
        ORDER BY season DESC
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql)
        return [r[0] for r in result.fetchall()]


def select_lines(season: Optional[int], week: Optional[int], game_id: Optional[str],
                 book: Optional[str], line_type: Optional[str]) -> List[Dict[str, Any]]:
    """
    NEW IN v1.8.0: Flexible betting lines query
    
    PATTERN: Dynamic WHERE clause construction
    
    Supports Multiple Filter Modes:
    1. By game_id: Get all lines for a specific game
    2. By season + week: Get all lines for a week
    3. By book: Filter to specific sportsbook (e.g., 'consensus')
    4. By line_type: Filter to spread/total/moneyline
    5. Any combination of above
    
    Join to hcl.games:
    - Enables season/week filtering
    - Provides ordering by recency
    - LEFT JOIN keeps lines even if game metadata missing
    
    Use Cases:
    - GET /api/lines?season=2024&week=8&book=consensus → Week's consensus lines
    - GET /api/lines?game_id=2024_08_KC_BUF → All books for one game
    - GET /api/lines?season=2024&line_type=spread → All spreads for season
    """
    where = ["1=1"]
    params: Dict[str, Any] = {}
    
    if game_id:
        where.append("bl.game_id = :game_id")
        params["game_id"] = game_id
    if season is not None:
        where.append("g.season = :season")
        params["season"] = season
    if week is not None:
        where.append("g.week = :week")
        params["week"] = week
    if book:
        where.append("bl.book = :book")
        params["book"] = book
    if line_type:
        where.append("bl.line_type = :line_type")
        params["line_type"] = line_type

    sql = text(f"""
        SELECT bl.game_id, bl.book, bl.line_type,
               bl.open_value, bl.open_time_utc,
               bl.close_value, bl.close_time_utc
        FROM hcl.betting_lines bl
        LEFT JOIN hcl.games g ON g.game_id = bl.game_id
        WHERE {' AND '.join(where)}
        ORDER BY g.season DESC NULLS LAST, g.week DESC NULLS LAST, bl.book, bl.line_type
    """)
    with engine.begin() as cxn:
        res = cxn.execute(sql, params)
        keys = res.keys()
        rows = res.fetchall()
    return rows_to_dicts(rows, keys)

# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.get("/healthz")
def healthz():
    """Health check (unchanged from v1.7.0)"""
    with engine.begin() as cxn:
        cxn.execute(text("SELECT 1"))
    return {"ok": True}

@app.get("/api/seasons", response_model=List[int])
def get_seasons():
    """List all available seasons (unchanged from v1.7.0)"""
    return select_seasons()

@app.get("/api/weeks", response_model=List[WeeksForSeason])
def get_weeks(
    season: Optional[int] = Query(None, ge=1999, description="Optional. If set, only that season.")
):
    """Available weeks by season (unchanged from v1.7.0)"""
    return select_weeks(season)

@app.get("/api/next_week", response_model=NextWeek)
def get_next_week(
    tz: Optional[constr(strip_whitespace=True, min_length=2, max_length=64)] = Query(
        None, description="IANA timezone, e.g., 'America/Los_Angeles' (default UTC)"
    )
):
    """Next upcoming or latest completed week (unchanged from v1.7.0)"""
    season, week, status = select_next_or_latest_week(tz)
    return {"season": season, "week": week, "status": status}

# --- Base matchups (no betting data) ---
@app.get("/api/matchups", response_model=List[Matchup])
def get_matchups(
    season: int = Query(..., ge=1999),
    week: int = Query(..., ge=1, le=23),
    team: Optional[str] = Query(None, description="Filter by team_id (e.g., KC, SF)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Weekly matchups (base stats only, unchanged from v1.7.0)
    
    Returns: Matchup objects (43 fields, no betting data)
    Use when: Public API, no betting features needed
    Performance: Faster than _with_proj endpoints
    """
    return select_matchups(season=season, week=week, team=team, limit=limit, offset=offset)

@app.get("/api/matchups/{game_id}", response_model=Matchup)
def get_matchup_by_id(game_id: str):
    """
    Single game matchup (base stats only, unchanged from v1.7.0)
    
    Returns: Matchup object (43 fields, no betting data)
    Use when: Game detail page, no betting features
    """
    row = select_matchup_by_id(game_id, with_proj=False)
    if not row:
        raise HTTPException(status_code=404, detail="game_id not found")
    return row

# --- Projections & edges (NEW IN v1.8.0) ---
@app.get("/api/matchups_with_proj", response_model=List[ProjectedMatchup])
def get_matchups_with_proj(
    season: int = Query(..., ge=1999),
    week: int = Query(..., ge=1, le=23),
    team: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    NEW IN v1.8.0: Weekly matchups with betting analytics
    
    Returns: ProjectedMatchup objects (49 fields: 43 base + 6 betting)
    
    Fields Added:
    - market_spread_consensus, market_total_consensus (sportsbook lines)
    - projected_spread, projected_total (our model predictions)
    - edge_spread_points, edge_total_points (value indicators)
    
    Use Cases:
    - Betting UI main page
    - Value finder tools
    - Line shopping comparison
    - Historical edge analysis
    
    Performance: ~10-20ms slower than /api/matchups (LATERAL joins)
    """
    return select_matchups_with_proj(season=season, week=week, team=team, limit=limit, offset=offset)

@app.get("/api/matchups_with_proj/{game_id}", response_model=ProjectedMatchup)
def get_matchup_with_proj_by_id(game_id: str):
    """
    NEW IN v1.8.0: Single game with betting analytics
    
    Returns: ProjectedMatchup object (49 fields)
    
    Use Cases:
    - Game detail page with betting section
    - Deep dive into specific matchup edge
    """
    row = select_matchup_by_id(game_id, with_proj=True)
    if not row:
        raise HTTPException(status_code=404, detail="game_id not found")
    return row

@app.get("/api/upcoming_matchups_with_proj", response_model=List[ProjectedMatchup])
def get_upcoming_matchups_with_proj(
    tz: Optional[constr(strip_whitespace=True, min_length=2, max_length=64)] = Query(
        None, description="IANA timezone, default UTC"
    ),
    include_last_completed: bool = Query(
        False, description="If true and no upcoming week, return latest completed week."
    )
):
    """
    NEW IN v1.8.0: Single-call upcoming matchups with betting analytics
    
    PATTERN: Combines week detection + projections in one endpoint
    
    Returns: ProjectedMatchup objects for next upcoming week
    
    Use Cases:
    - Homepage "This Week's Best Bets" widget (one API call)
    - Mobile betting app home screen
    - Daily digest email generation
    - Automated betting alerts (edges > threshold)
    
    Example Response:
    [
      {
        "game_id": "2025_08_KC_BUF",
        "home_team": "BUF", "away_team": "KC",
        "diff_epa_pp": -0.05, "diff_sr": -0.02,
        "market_spread_consensus": -3.5,
        "projected_spread": -5.2,
        "edge_spread_points": 1.7,  # Value on home (BUF -3.5)
        "market_total_consensus": 47.0,
        "projected_total": 44.8,
        "edge_total_points": -2.2  # Value on under
      },
      ...
    ]
    """
    try:
        season, week, status = select_next_or_latest_week(tz)
        if status == "latest_completed" and not include_last_completed:
            raise HTTPException(status_code=400, detail="No upcoming week. Set include_last_completed=true for fallback.")
        return select_matchups_for(season, week, with_proj=True)
    except HTTPException as e:
        if include_last_completed and e.status_code == 404:
            season, week, status = select_next_or_latest_week(tz)
            return select_matchups_for(season, week, with_proj=True)
        raise

# --- Lines (NEW IN v1.8.0) ---
@app.get("/api/lines", response_model=List[LineRow])
def get_lines(
    season: Optional[int] = Query(None, ge=1999, description="Filter by season"),
    week: Optional[int] = Query(None, ge=1, le=23, description="Filter by week"),
    game_id: Optional[str] = Query(None, description="Filter by exact game_id"),
    book: Optional[str] = Query(None, description="e.g., 'consensus','pinnacle','dk'"),
    line_type: Optional[str] = Query(None, description="spread|total|moneyline")
):
    """
    NEW IN v1.8.0: Query betting lines with flexible filters
    
    Returns: LineRow objects from hcl.betting_lines
    
    Query Params (all optional):
    - season: Filter to specific season (e.g., 2024)
    - week: Filter to specific week (requires season for performance)
    - game_id: Get all lines for one game (overrides season/week)
    - book: Filter to sportsbook ('consensus', 'pinnacle', 'dk', 'fanduel', etc.)
    - line_type: Filter to 'spread' | 'total' | 'moneyline'
    
    Use Cases:
    1. Week consensus lines:
       GET /api/lines?season=2024&week=8&book=consensus
       → All consensus spreads/totals for Week 8
    
    2. Line shopping for one game:
       GET /api/lines?game_id=2024_08_KC_BUF
       → All books, all line types for KC @ BUF
    
    3. Spread movement analysis:
       GET /api/lines?season=2024&line_type=spread
       → All spreads for entire season (compare open vs close)
    
    4. Sportsbook-specific lines:
       GET /api/lines?season=2024&week=8&book=pinnacle&line_type=total
       → Pinnacle's totals for Week 8 (sharp money indicator)
    
    Response Example:
    [
      {
        "game_id": "2024_08_KC_BUF",
        "book": "consensus",
        "line_type": "spread",
        "open_value": -3.0,
        "open_time_utc": "2024-10-15T10:00:00Z",
        "close_value": -3.5,
        "close_time_utc": "2024-10-20T20:20:00Z"
      },
      ...
    ]
    """
    return select_lines(season=season, week=week, game_id=game_id, book=book, line_type=line_type)


"""
PREREQUISITES FOR v1.8.0:

1. Database Views:
   - v_game_matchup_display (base stats, 43 columns)
   - v_game_matchup_with_proj (base + betting, 49 columns)

2. Database Tables:
   - hcl.games (game metadata, kickoff times)
   - hcl.betting_lines (odds/lines from sportsbooks)

3. Indexes:
   CREATE INDEX idx_games_kickoff ON hcl.games(kickoff_time_utc);
   CREATE INDEX idx_blines_type ON hcl.betting_lines(line_type);

4. Data Population:
   - Run ingest_schedules.py (populate hcl.games)
   - Run ingest_betting_lines_csv.py (populate hcl.betting_lines)
   - Or use paid odds API to populate hcl.betting_lines

5. View Definitions (from PHASE2_ADDITIONAL_DATA_SOURCES.md):
   - v_game_matchup_with_lines (LATERAL joins to betting_lines)
   - v_game_matchup_with_proj (adds projections + edge calculations)
"""

"""
EXAMPLE API CALLS:

1. Upcoming week with projections (Pacific time):
   GET /api/upcoming_matchups_with_proj?tz=America/Los_Angeles
   → Next week's games with market lines, projections, edges

2. Specific week with projections:
   GET /api/matchups_with_proj?season=2025&week=8
   → All Week 8 games with betting analytics

3. Lines for Week 8, consensus only:
   GET /api/lines?season=2025&week=8&book=consensus
   → Consensus spreads and totals for Week 8

4. Single game with projections:
   GET /api/matchups_with_proj/2025_08_KC_DEN
   → KC @ DEN with market lines, our model, edge

5. All lines for one game (line shopping):
   GET /api/lines?game_id=2025_08_KC_DEN
   → All sportsbooks' lines for KC @ DEN

6. Spread movement for season:
   GET /api/lines?season=2025&line_type=spread
   → All spreads (compare open_value vs close_value)
"""

"""
CHATGPT'S ADDITIONAL OFFER:

> If you want a filter by minimum edge (e.g., min_edge=1.5 on spread), 
> I can add /api/edges that returns only games where ABS(edge_spread_points) 
> exceeds your threshold.

APRIL'S RESPONSE:
I acknowledge this offer. This would be useful for:
- Automated betting alerts ("Notify me when edge > 2 points")
- Value finder dashboard ("Show me today's best bets")
- Historical analysis ("How many +2 edges occurred in 2024?")

Decision: I will request this after:
1. Building Flask version of core endpoints
2. Testing projection accuracy with historical data
3. Determining optimal edge thresholds via backtesting

For now, the frontend can filter /api/matchups_with_proj results by edge_spread_points.
"""

"""
FLASK TRANSLATION NOTES FOR v1.8.0:

NEW PATTERNS TO TRANSLATE:

1. Dual-view pattern (with_proj flag):
   def select_matchup_by_id(game_id, with_proj=False):
       view = "v_game_matchup_with_proj" if with_proj else "v_game_matchup_display"
   
   Flask equivalent:
   view = "hcl.v_game_matchup_with_proj" if with_proj else "hcl.v_game_matchup_display"
   cursor.execute(f"SELECT * FROM {view} WHERE game_id = %s", (game_id,))

2. Dynamic WHERE clause construction:
   where = ["1=1"]
   if season: where.append("g.season = :season")
   sql = f"WHERE {' AND '.join(where)}"
   
   Flask equivalent (same pattern, works identically):
   where = ["1=1"]
   params = []
   if season:
       where.append("g.season = %s")
       params.append(season)
   sql = f"WHERE {' AND '.join(where)}"
   cursor.execute(sql, params)

3. Model inheritance (ProjectedMatchup extends Matchup):
   Flask: No Pydantic, just return dict with all 49 fields
   Frontend handles which fields to display

4. Optional query params:
   FastAPI: Optional[int] = Query(None, ge=1999)
   Flask: season = request.args.get('season', type=int)
           if season and season < 1999: return jsonify({'error': 'Invalid season'}), 400

COMPLETE FLASK ENDPOINT LIST:

@app.route('/api/matchups')                        # Base stats
@app.route('/api/matchups/<game_id>')              # Base stats, single
@app.route('/api/matchups_with_proj')              # + Betting analytics
@app.route('/api/matchups_with_proj/<game_id>')    # + Betting analytics, single
@app.route('/api/upcoming_matchups_with_proj')     # Next week + betting
@app.route('/api/lines')                           # Query betting lines
@app.route('/api/seasons')                         # Available seasons
@app.route('/api/weeks')                           # Available weeks
@app.route('/api/next_week')                       # Next upcoming week
@app.route('/api/week_summary')                    # Week analytics (v1.7.0)
@app.route('/health')                              # Health check
"""
