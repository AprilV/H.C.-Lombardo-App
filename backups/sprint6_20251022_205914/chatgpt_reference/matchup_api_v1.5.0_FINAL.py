"""
ChatGPT Reference Implementation - FastAPI Matchup API v1.5.0 FINAL
====================================================================
Complete production-grade API with all endpoints.

RECEIVED: October 22, 2025
SOURCE: ChatGPT conversation - Phase 2 implementation reference
PURPOSE: Study patterns for HC Lombardo Flask translation

KEY FEATURES:
- Timezone-aware week detection using kickoff_time_utc
- Single-call upcoming matchups endpoint
- CTE pattern for week aggregation
- Graceful fallback handling
- IANA timezone support (optional)

ENDPOINTS:
1. GET /api/next_week?tz={timezone}
   - Returns next upcoming or latest completed week
   - Uses kickoff_time_utc and NOW() comparison
   - Status: "upcoming" or "latest_completed"

2. GET /api/upcoming_matchups?tz={timezone}
   - Single-call convenience endpoint
   - Returns full matchup list for next week
   - Raises 400 if no upcoming week found

DATABASE REQUIREMENTS:
- hcl.games table with kickoff_time_utc (TIMESTAMPTZ)
- hcl.v_game_matchup_display view (43 columns)
- Index: CREATE INDEX idx_games_kickoff ON hcl.games(kickoff_time_utc)

TRANSLATION NOTES FOR FLASK:
- Replace SQLAlchemy with psycopg2
- Replace Pydantic with dict responses + jsonify
- Replace FastAPI Query with request.args.get()
- Keep CTE pattern (works identically in psycopg2)
- Timezone handling: psycopg2 supports AT TIME ZONE natively
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

app = FastAPI(title="HC in Lombardo API", version="1.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------
class Matchup(BaseModel):
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


class NextWeek(BaseModel):
    season: int
    week: int
    status: str


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def rows_to_dicts(rows, keys) -> List[Dict[str, Any]]:
    return [dict(zip(keys, r)) for r in rows]


def select_next_or_latest_week(tz: Optional[str]) -> Tuple[int, int, str]:
    """
    PATTERN: Timezone-aware week detection using kickoff_time_utc
    
    Uses AT TIME ZONE to convert NOW() to user's timezone, then back to UTC
    for fair comparison. This ensures "upcoming" logic respects local time.
    
    Returns: (season, week, status)
    - status = "upcoming" if any games with kickoff >= now
    - status = "latest_completed" if all recent games kicked off before now
    """
    tz = tz or "UTC"
    
    # PATTERN: Validate timezone by attempting conversion
    sql_now = text("""
        SELECT (NOW() AT TIME ZONE :tz) AT TIME ZONE 'UTC' AS now_ref_utc
    """)
    with engine.begin() as cxn:
        try:
            now_ref_row = cxn.execute(sql_now, {"tz": tz}).fetchone()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid timezone name.")
        now_ref_utc = now_ref_row[0]

    # PATTERN: CTE for week-level aggregation (MIN/MAX kickoff times)
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

    # PATTERN: Try upcoming first, fallback to latest completed
    with engine.begin() as cxn:
        row = cxn.execute(sql_upcoming, {"now_ref_utc": now_ref_utc}).fetchone()
        if row:
            return int(row[0]), int(row[1]), "upcoming"
        row = cxn.execute(sql_latest, {"now_ref_utc": now_ref_utc}).fetchone()
        if row:
            return int(row[0]), int(row[1]), "latest_completed"
    
    raise HTTPException(status_code=404, detail="No week data found.")


def select_matchups_for(season: int, week: int) -> List[Dict[str, Any]]:
    """
    PATTERN: Simple view query for matchup data
    
    Uses v_game_matchup_display which pre-joins and pivots home/away stats.
    No complex joins needed in application code.
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


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.get("/api/next_week", response_model=NextWeek)
def get_next_week(
    tz: Optional[constr(strip_whitespace=True, min_length=2, max_length=64)] = Query(
        None, description="IANA timezone, e.g., 'America/Los_Angeles'"
    )
):
    """
    ENDPOINT: Next upcoming or latest completed week
    
    Query params:
    - tz (optional): IANA timezone name (e.g., "America/New_York")
    
    Returns:
    - season, week, status ("upcoming" or "latest_completed")
    
    Use case: UI can show "Next week" or "Most recent week" label
    """
    season, week, status = select_next_or_latest_week(tz)
    return {"season": season, "week": week, "status": status}


@app.get("/api/upcoming_matchups", response_model=List[Matchup])
def get_upcoming_matchups(
    tz: Optional[str] = Query(None, description="IANA timezone, e.g., 'America/New_York'")
):
    """
    ENDPOINT: Single-call convenience for upcoming week's matchups
    
    PATTERN: Combines week detection + matchup query in one endpoint
    
    Query params:
    - tz (optional): IANA timezone name
    
    Returns:
    - List of Matchup objects for the next upcoming week
    - Raises 400 if no upcoming week (e.g., after Super Bowl)
    
    Use case: Homepage "This Week's Games" widget with one API call
    """
    season, week, status = select_next_or_latest_week(tz)
    
    # PATTERN: Explicit error if no upcoming games
    if status == "latest_completed":
        raise HTTPException(
            status_code=400, 
            detail="No upcoming week found (season likely complete)."
        )
    
    data = select_matchups_for(season, week)
    return data


# ------------------------------------------------------------------
# Additional Endpoints (from v1.3.0)
# ------------------------------------------------------------------
# NOTE: These endpoints were in previous versions but not shown in v1.5.0
# ChatGPT focused on the new /api/upcoming_matchups endpoint
# Full API likely includes:
# - GET /api/matchups?season={}&week={}&team={}
# - GET /api/matchups/{game_id}
# - GET /api/weeks?season={}
# - GET /api/seasons
# - GET /healthz

"""
EXAMPLE CALLS:

1. Get next week (UTC):
   GET /api/next_week
   → {"season": 2025, "week": 8, "status": "upcoming"}

2. Get next week (Pacific time):
   GET /api/next_week?tz=America/Los_Angeles
   → {"season": 2025, "week": 8, "status": "upcoming"}

3. Get upcoming matchups (one call):
   GET /api/upcoming_matchups
   → [{"game_id": "2025_08_KC_BUF", "home_team": "BUF", ...}, ...]

4. Get upcoming matchups (Eastern time):
   GET /api/upcoming_matchups?tz=America/New_York
   → Same data, but week detection uses ET

FLASK TRANSLATION CHECKLIST:
☐ Replace SQLAlchemy engine with psycopg2 connection pool
☐ Replace Pydantic models with dict/jsonify responses
☐ Replace Query() validators with request.args.get() + manual validation
☐ Keep CTE pattern (works identically)
☐ Use psycopg2's cursor.execute() with parameterized queries
☐ Handle timezone errors with try/except (same logic)
☐ Return Flask Response objects with proper status codes
☐ Add CORS via flask-cors
☐ Integrate with existing db_config.py connection logic
☐ Add to existing port_manager.py for coordinated startup
"""
