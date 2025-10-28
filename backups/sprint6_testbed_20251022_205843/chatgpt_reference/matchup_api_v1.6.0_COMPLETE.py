"""
ChatGPT Reference Implementation - FastAPI Matchup API v1.6.0 COMPLETE
=======================================================================
Final production-grade API with all endpoints + fallback logic.

RECEIVED: October 22, 2025
SOURCE: ChatGPT conversation - Phase 2 implementation reference
PURPOSE: Study patterns for HC Lombardo Flask translation

VERSION HISTORY:
- v1.0.0: Basic matchup endpoints
- v1.3.0: Added /api/weeks, /api/seasons, timestamp-aware /api/next_week
- v1.5.0: Added /api/upcoming_matchups (single-call convenience)
- v1.6.0: Added include_last_completed fallback parameter

KEY FEATURES:
- Complete CRUD for matchups (weekly, single game, team-specific)
- Timezone-aware week detection using kickoff_time_utc
- Single-call upcoming matchups endpoint with graceful fallback
- CTE pattern for week aggregation
- IANA timezone support (optional, defaults to UTC)
- Graceful season-end handling

COMPLETE ENDPOINT LIST:
1. GET /healthz - Health check
2. GET /api/seasons - List all available seasons (DESC)
3. GET /api/weeks?season={} - Available weeks by season
4. GET /api/next_week?tz={} - Next upcoming or latest completed week
5. GET /api/matchups?season={}&week={}&team={} - Weekly matchups with filters
6. GET /api/matchups/{game_id} - Single game matchup detail
7. GET /api/upcoming_matchups?tz={}&include_last_completed={} - Convenience endpoint

DATABASE REQUIREMENTS:
- hcl.games table with kickoff_time_utc (TIMESTAMPTZ), season, week, is_postseason
- hcl.v_game_matchup_display view (43 columns, one-row-per-game)
- Index: CREATE INDEX idx_games_kickoff ON hcl.games(kickoff_time_utc)

TRANSLATION NOTES FOR FLASK:
- Replace SQLAlchemy with psycopg2 connection pool
- Replace Pydantic BaseModel with dict responses + jsonify
- Replace FastAPI Query() with request.args.get() + manual validation
- Replace constr() with custom validation functions
- Keep CTE pattern (works identically in psycopg2)
- Use psycopg2's AT TIME ZONE for timezone handling
- Replace HTTPException with Flask abort() or custom error handlers
- Add flask-cors for CORS middleware
- Integrate with existing db_config.py for connection management
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

app = FastAPI(title="HC in Lombardo API", version="1.6.0")

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
    PATTERN: Flat structure matching v_game_matchup_display columns
    
    43 total fields:
    - 10 game metadata (season, week, game_id, teams, location)
    - 9 home team stats (gp, ppg_for, ppg_against, ypp, sr, epa_pp, to_pg, 3d_rate, 4d_rate)
    - 9 away team stats (same metrics)
    - 3 home momentum (epa_l3, ypp_l3, ppg_l3)
    - 3 away momentum (same metrics)
    - 4 matchup edges (diff_epa_pp, diff_ypp, diff_sr, diff_ppg_for)
    - 5 game context (stadium, city, state, timezone, game_date)
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


class WeeksForSeason(BaseModel):
    """
    PATTERN: Structured response with PostgreSQL array aggregation
    Uses ARRAY_AGG(DISTINCT week ORDER BY week) for clean week lists
    """
    season: int
    weeks: List[int]


class NextWeek(BaseModel):
    """
    PATTERN: Status indicator for UI state management
    'upcoming' = games not yet kicked off
    'latest_completed' = most recent week with all games finished
    """
    season: int
    week: int
    status: str  # "upcoming" or "latest_completed"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def rows_to_dicts(rows, keys) -> List[Dict[str, Any]]:
    """
    PATTERN: Generic row-to-dict converter
    Works with any SQLAlchemy result set
    """
    return [dict(zip(keys, r)) for r in rows]


def select_next_or_latest_week(tz: Optional[str]) -> Tuple[int, int, str]:
    """
    PATTERN: Timezone-aware week detection using kickoff_time_utc
    
    Algorithm:
    1. Convert NOW() to user's timezone, then back to UTC for comparison
    2. Find earliest week with MIN(kickoff) >= now (upcoming)
    3. If none, find latest week with MAX(kickoff) < now (completed)
    4. Return (season, week, status)
    
    Uses CTE for clean week-level aggregation
    Regular season only (is_postseason = FALSE)
    """
    tz = tz or "UTC"

    # PATTERN: Validate timezone by attempting conversion
    # If invalid IANA name, PostgreSQL raises error -> catch and return 400
    sql_now = text("SELECT (NOW() AT TIME ZONE :tz) AT TIME ZONE 'UTC' AS now_ref_utc")
    with engine.begin() as cxn:
        try:
            now_ref_row = cxn.execute(sql_now, {"tz": tz}).fetchone()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid timezone. Use an IANA name like 'America/Los_Angeles'.")
        now_ref_utc = now_ref_row[0]

    # PATTERN: CTE for upcoming week (MIN kickoff >= now)
    sql_upcoming = text("""
        WITH weekly AS (
          SELECT season, week, MIN(kickoff_time_utc) AS first_kick
          FROM hcl.games
          WHERE COALESCE(is_postseason, FALSE) = FALSE
            AND kickoff_time_utc IS NOT NULL
          GROUP BY season, week
        )
        SELECT season, week
        FROM weekly
        WHERE first_kick >= :now_ref_utc
        ORDER BY first_kick ASC
        LIMIT 1
    """)

    # PATTERN: CTE for latest completed week (MAX kickoff < now)
    sql_latest = text("""
        WITH weekly AS (
          SELECT season, week, MAX(kickoff_time_utc) AS last_kick
          FROM hcl.games
          WHERE COALESCE(is_postseason, FALSE) = FALSE
            AND kickoff_time_utc IS NOT NULL
          GROUP BY season, week
        )
        SELECT season, week
        FROM weekly
        WHERE last_kick < :now_ref_utc
        ORDER BY last_kick DESC
        LIMIT 1
    """)

    # PATTERN: Try upcoming first, fallback to latest completed
    with engine.begin() as cxn:
        row = cxn.execute(sql_upcoming, {"now_ref_utc": now_ref_utc}).fetchone()
        if row:
            return int(row[0]), int(row[1]), "upcoming"
        row = cxn.execute(sql_latest, {"now_ref_utc": now_ref_utc}).fetchone()
        if row:
            return int(row[0]), int(row[1]), "latest_completed"

    raise HTTPException(status_code=404, detail="No regular-season weeks found (check games data).")


def select_matchups(season: int, week: int, team: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    """
    PATTERN: Flexible matchup query with optional team filter
    
    - Dynamic SQL with conditional team filter
    - Parameterized queries (SQL injection safe)
    - LIMIT/OFFSET for pagination
    - ORDER BY for consistent results
    """
    team_filter_sql = ""
    params = {"season": season, "week": week, "limit": limit, "offset": offset}
    if team:
        team_filter_sql = "AND (home_team = :team OR away_team = :team)"
        params["team"] = team

    sql = text(f"""
        SELECT *
        FROM hcl.v_game_matchup_display
        WHERE season = :season
          AND week = :week
          {team_filter_sql}
        ORDER BY game_date NULLS LAST, home_team, away_team
        LIMIT :limit OFFSET :offset
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, params)
        keys = result.keys()
        rows = result.fetchall()
    return rows_to_dicts(rows, keys)


def select_matchups_for(season: int, week: int) -> List[Dict[str, Any]]:
    """
    PATTERN: Simplified matchup query for known season/week
    Used by /api/upcoming_matchups for single-call convenience
    No filters, no pagination - just get all games for the week
    """
    sql = text("""
        SELECT *
        FROM hcl.v_game_matchup_display
        WHERE season = :season AND week = :week
        ORDER BY game_date NULLS LAST, home_team, away_team
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, {"season": season, "week": week})
        keys = result.keys()
        rows = result.fetchall()
    return rows_to_dicts(rows, keys)


def select_matchup_by_id(game_id: str) -> Optional[Dict[str, Any]]:
    """
    PATTERN: Single game lookup by game_id
    Returns None if not found (caller handles 404)
    """
    sql = text("""
        SELECT *
        FROM hcl.v_game_matchup_display
        WHERE game_id = :game_id
        LIMIT 1
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, {"game_id": game_id})
        row = result.fetchone()
        if not row:
            return None
        keys = result.keys()
    return dict(zip(keys, row))


def select_weeks(season: Optional[int]) -> List[Dict[str, Any]]:
    """
    PATTERN: Available weeks query with PostgreSQL array aggregation
    
    - Uses ARRAY_AGG(DISTINCT week ORDER BY week) for clean week lists
    - Optional season filter (if None, returns all seasons)
    - Grouped by season, ordered DESC for most recent first
    - Regular season only (is_postseason = FALSE)
    """
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
    """
    PATTERN: Simple distinct query for available seasons
    Returns list of integers, DESC for most recent first
    """
    sql = text("""
        SELECT DISTINCT season
        FROM hcl.games
        WHERE COALESCE(is_postseason, FALSE) = FALSE
        ORDER BY season DESC
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql)
        return [r[0] for r in result.fetchall()]

# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.get("/healthz")
def healthz():
    """
    ENDPOINT: Health check for monitoring/load balancers
    Simple SELECT 1 to verify database connectivity
    """
    with engine.begin() as cxn:
        cxn.execute(text("SELECT 1"))
    return {"ok": True}

@app.get("/api/seasons", response_model=List[int])
def get_seasons():
    """
    ENDPOINT: List all available seasons (DESC)
    
    Returns: [2025, 2024, 2023, ...]
    Use case: Season picker dropdown in UI
    """
    return select_seasons()

@app.get("/api/weeks", response_model=List[WeeksForSeason])
def get_weeks(
    season: Optional[int] = Query(None, ge=1999, description="Optional. If set, only that season.")
):
    """
    ENDPOINT: Available weeks by season
    
    Query params:
    - season (optional): Filter to single season
    
    Returns:
    - All seasons: [{"season": 2025, "weeks": [1,2,3,...]}, ...]
    - Single season: [{"season": 2024, "weeks": [1,2,3,...]}]
    
    Use case: Week picker dropdown, populated dynamically per season
    """
    return select_weeks(season)

@app.get("/api/next_week", response_model=NextWeek)
def get_next_week(
    tz: Optional[constr(strip_whitespace=True, min_length=2, max_length=64)] = Query(
        None, description="IANA timezone, e.g., 'America/Los_Angeles' (default UTC)"
    )
):
    """
    ENDPOINT: Next upcoming or latest completed week
    
    Query params:
    - tz (optional): IANA timezone name (e.g., "America/New_York")
    
    Returns:
    - {"season": 2025, "week": 8, "status": "upcoming"}
    - {"season": 2025, "week": 7, "status": "latest_completed"}
    
    Use case: 
    - Show "Next week: Week 8" or "Most recent: Week 7" in UI
    - Determine which week to query for matchups
    """
    season, week, status = select_next_or_latest_week(tz)
    return {"season": season, "week": week, "status": status}

@app.get("/api/matchups", response_model=List[Matchup])
def get_matchups(
    season: int = Query(..., ge=1999, description="Season year"),
    week: int = Query(..., ge=1, le=23, description="NFL week (regular season only in the view)"),
    team: Optional[str] = Query(None, description="Filter by team_id (e.g., KC, SF)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    ENDPOINT: Weekly matchups with filters
    
    Query params:
    - season (required): Year (e.g., 2024)
    - week (required): Week number (1-23)
    - team (optional): Filter to games involving this team
    - limit (optional, default 100): Max results
    - offset (optional, default 0): Pagination offset
    
    Returns: List of Matchup objects
    
    Use case:
    - GET /api/matchups?season=2024&week=8 → All Week 8 games
    - GET /api/matchups?season=2024&week=8&team=KC → KC's Week 8 game only
    """
    return select_matchups(season=season, week=week, team=team, limit=limit, offset=offset)

@app.get("/api/matchups/{game_id}", response_model=Matchup)
def get_matchup_by_id(game_id: str):
    """
    ENDPOINT: Single game matchup detail
    
    Path params:
    - game_id: Unique game identifier (e.g., "2024_08_KC_BUF")
    
    Returns: Single Matchup object
    Raises: 404 if game_id not found
    
    Use case: Deep-link to specific game detail page
    """
    row = select_matchup_by_id(game_id)
    if not row:
        raise HTTPException(status_code=404, detail="game_id not found")
    return row

@app.get("/api/upcoming_matchups", response_model=List[Matchup])
def get_upcoming_matchups(
    tz: Optional[constr(strip_whitespace=True, min_length=2, max_length=64)] = Query(
        None, description="IANA timezone, e.g., 'America/Los_Angeles' (default UTC)"
    ),
    include_last_completed: bool = Query(
        False,
        description="If true and no upcoming week exists, return latest completed week's matchups."
    )
):
    """
    ENDPOINT: Single-call convenience for upcoming week's matchups
    
    PATTERN: Combines week detection + matchup query internally
    Reduces frontend from 2 API calls to 1
    
    Query params:
    - tz (optional): IANA timezone name
    - include_last_completed (optional, default false): Fallback to latest completed if no upcoming
    
    Returns: List of Matchup objects for the next upcoming week
    
    Behavior:
    - Default: Raises 400 if no upcoming week (e.g., after Super Bowl)
    - With include_last_completed=true: Falls back to latest completed week
    
    Use case:
    - Homepage "This Week's Games" widget (one API call)
    - Mobile app home screen (reduce latency)
    - Off-season fallback (show most recent games)
    
    Examples:
    - GET /api/upcoming_matchups → Next week's games (or 400 if season over)
    - GET /api/upcoming_matchups?tz=America/New_York → Next week in ET
    - GET /api/upcoming_matchups?include_last_completed=true → Next week or fallback to latest
    """
    try:
        season, week, status = select_next_or_latest_week(tz)
        
        # PATTERN: Explicit error if no upcoming and fallback disabled
        if status == "latest_completed" and not include_last_completed:
            raise HTTPException(
                status_code=400, 
                detail="No upcoming week found. Set include_last_completed=true to get the latest completed week."
            )
        
        return select_matchups_for(season, week)
    
    except HTTPException as e:
        # PATTERN: Fallback handling for edge case (no data at all)
        if include_last_completed and e.status_code == 404:
            # Force fallback: call with tz but accept 'latest_completed'
            season, week, status = select_next_or_latest_week(tz)
            return select_matchups_for(season, week)
        raise


"""
REQUIRED INDEX (one-time setup):

SET search_path = hcl, public;
CREATE INDEX IF NOT EXISTS idx_games_kickoff ON games(kickoff_time_utc);

PURPOSE: Performance optimization for timestamp-based week queries
IMPACT: Transforms O(n) table scans to O(log n) index seeks
"""

"""
EXAMPLE API CALLS:

1. Health check:
   GET /healthz
   → {"ok": true}

2. Get all seasons:
   GET /api/seasons
   → [2025, 2024, 2023, ...]

3. Get weeks for 2024 season:
   GET /api/weeks?season=2024
   → [{"season": 2024, "weeks": [1,2,3,...,18]}]

4. Get next week (UTC):
   GET /api/next_week
   → {"season": 2025, "week": 8, "status": "upcoming"}

5. Get next week (Pacific time):
   GET /api/next_week?tz=America/Los_Angeles
   → {"season": 2025, "week": 8, "status": "upcoming"}

6. Get all Week 8 matchups:
   GET /api/matchups?season=2025&week=8
   → [{"game_id": "2025_08_KC_BUF", ...}, ...]

7. Get KC's Week 8 game:
   GET /api/matchups?season=2025&week=8&team=KC
   → [{"game_id": "2025_08_KC_BUF", ...}]

8. Get single game detail:
   GET /api/matchups/2025_08_KC_BUF
   → {"game_id": "2025_08_KC_BUF", "home_team": "BUF", ...}

9. Get upcoming matchups (one call):
   GET /api/upcoming_matchups
   → [{"game_id": "2025_08_KC_BUF", ...}, ...]

10. Get upcoming matchups (Eastern time):
    GET /api/upcoming_matchups?tz=America/New_York
    → Same data, week detection uses ET

11. Get upcoming or fallback to latest:
    GET /api/upcoming_matchups?include_last_completed=true
    → Next week's games, or latest completed if season over
"""

"""
FLASK TRANSLATION CHECKLIST:

DATABASE LAYER:
☐ Replace SQLAlchemy engine with psycopg2 connection pool from db_config.py
☐ Replace text() with raw SQL strings
☐ Replace engine.begin() with conn.cursor() pattern
☐ Replace result.keys() with cursor.description column names
☐ Keep parameterized queries (use %s placeholders instead of :param)

RESPONSE MODELS:
☐ Remove Pydantic BaseModel classes
☐ Return dict objects directly from helper functions
☐ Use jsonify() in Flask route handlers
☐ Manual type validation (or use marshmallow if preferred)

REQUEST VALIDATION:
☐ Replace Query() with request.args.get()
☐ Replace constr() with custom validation functions
☐ Add manual range checks (ge=1999, le=500, etc.)
☐ Convert string params to int/bool with error handling

ERROR HANDLING:
☐ Replace HTTPException with Flask abort()
☐ Or use @app.errorhandler() for custom error responses
☐ Return {"error": "message"} with appropriate status codes

MIDDLEWARE:
☐ Replace FastAPI CORS with flask-cors (pip install flask-cors)
☐ Add @cross_origin() decorator or CORS(app) initialization

INTEGRATION:
☐ Import db_config.py for database connection management
☐ Add endpoints to existing Flask app (not separate FastAPI app)
☐ Register blueprint if organizing by feature area
☐ Integrate with port_manager.py for coordinated startup
☐ Add routes to existing API documentation

TESTING:
☐ Test timezone validation with invalid IANA names
☐ Test pagination (limit/offset)
☐ Test team filter (home and away games)
☐ Test fallback logic (include_last_completed)
☐ Verify CTE queries work in psycopg2 (they should)
☐ Test NULL handling (NULLS LAST in ORDER BY)
☐ Performance test with index (should be <50ms for week queries)
"""
