"""
ChatGPT Reference Implementation - FastAPI Matchup API v1.7.0 COMPLETE
=======================================================================
Final production-grade API with all endpoints + week summary analytics.

RECEIVED: October 22, 2025
SOURCE: ChatGPT conversation - Phase 2 implementation reference
PURPOSE: Study patterns for HC Lombardo Flask translation

VERSION HISTORY:
- v1.0.0: Basic matchup endpoints
- v1.3.0: Added /api/weeks, /api/seasons, timestamp-aware /api/next_week
- v1.5.0: Added /api/upcoming_matchups (single-call convenience)
- v1.6.0: Added include_last_completed fallback parameter
- v1.7.0: Added /api/week_summary (analytics aggregates + top edges)

KEY FEATURES:
- Complete CRUD for matchups (weekly, single game, team-specific)
- Timezone-aware week detection using kickoff_time_utc
- Single-call upcoming matchups endpoint with graceful fallback
- Week-level analytics aggregates (avg/median EPA, YPP, PPG, etc.)
- Top 3 matchup edges by |diff_epa_pp| for UI highlights
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
8. GET /api/week_summary?season={}&week={}&tz={} - Week analytics aggregates

DATABASE REQUIREMENTS:
- hcl.games table with kickoff_time_utc (TIMESTAMPTZ), season, week, is_postseason
- hcl.v_game_matchup_display view (43 columns, one-row-per-game)
- Index: CREATE INDEX idx_games_kickoff ON hcl.games(kickoff_time_utc)

NEW IN v1.7.0 - WEEK SUMMARY ENDPOINT:
- Aggregate statistics for entire week (avg/median)
- Top 3 matchup edges by absolute diff_epa_pp
- Supports explicit season/week OR timezone inference
- Same fallback logic as /api/upcoming_matchups
- Perfect for "Week at a Glance" UI tile

TRANSLATION NOTES FOR FLASK:
- Replace SQLAlchemy with psycopg2 connection pool
- Replace Pydantic BaseModel with dict responses + jsonify
- Replace FastAPI Query() with request.args.get() + manual validation
- Keep CTE pattern (works identically in psycopg2)
- PostgreSQL aggregates (PERCENTILE_CONT, jsonb_agg) work in psycopg2
- Use psycopg2's AT TIME ZONE for timezone handling
- Replace HTTPException with Flask abort() or custom error handlers
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

app = FastAPI(title="HC in Lombardo API", version="1.7.0")

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
    """43-field matchup model (unchanged from v1.6.0)"""
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
    """Weeks grouped by season"""
    season: int
    weeks: List[int]


class NextWeek(BaseModel):
    """Next week metadata with status"""
    season: int
    week: int
    status: str  # "upcoming" or "latest_completed"


class TopEdge(BaseModel):
    """
    NEW IN v1.7.0: Individual matchup edge for top 3 highlights
    
    PATTERN: Lightweight model for UI "Featured Matchups" section
    Only includes essential fields (game identifiers + edge metrics)
    """
    game_id: str
    game_date: Optional[str] = None
    home_team: str
    away_team: str
    diff_epa_pp: Optional[float] = None
    diff_ypp: Optional[float] = None
    diff_sr: Optional[float] = None


class WeekSummary(BaseModel):
    """
    NEW IN v1.7.0: Week-level aggregate analytics
    
    PATTERN: Comprehensive summary for "Week at a Glance" UI tile
    
    Fields:
    - games: Count of matchups in the week
    - avg/median diff_epa_pp: Spread of matchup quality
    - avg/median diff_ypp, avg_diff_sr: Additional edge metrics
    - avg_home/away_epa_pp: Offensive efficiency by location
    - avg_home/away_ppg_for: Scoring by location
    - avg_combined_ppg: Expected total points (O/U insights)
    - avg_home/away_ypp: Yards efficiency by location
    - home_adv_epa: Home field advantage for the week
    - top_edges: Top 3 most lopsided matchups by |diff_epa_pp|
    
    Use cases:
    - "This week features high-scoring matchups (avg 45.5 PPG combined)"
    - "Home teams favored by +0.021 EPA/play this week"
    - "Top edge: KC vs DEN (+0.173 EPA/play)"
    """
    season: int
    week: int
    games: int
    avg_diff_epa_pp: Optional[float] = None
    median_diff_epa_pp: Optional[float] = None
    avg_diff_ypp: Optional[float] = None
    median_diff_ypp: Optional[float] = None
    avg_diff_sr: Optional[float] = None
    avg_home_epa_pp: Optional[float] = None
    avg_away_epa_pp: Optional[float] = None
    avg_home_ppg_for: Optional[float] = None
    avg_away_ppg_for: Optional[float] = None
    avg_combined_ppg: Optional[float] = None
    avg_home_ypp: Optional[float] = None
    avg_away_ypp: Optional[float] = None
    home_adv_epa: Optional[float] = None  # avg(home_epa_pp - away_epa_pp)
    top_edges: List[TopEdge] = []


# ------------------------------------------------------------------
# Helpers (v1.6.0 helpers unchanged, v1.7.0 adds select_week_summary)
# ------------------------------------------------------------------
def rows_to_dicts(rows, keys) -> List[Dict[str, Any]]:
    return [dict(zip(keys, r)) for r in rows]


def select_next_or_latest_week(tz: Optional[str]) -> Tuple[int, int, str]:
    """Timezone-aware week detection (unchanged from v1.6.0)"""
    tz = tz or "UTC"
    sql_now = text("SELECT (NOW() AT TIME ZONE :tz) AT TIME ZONE 'UTC' AS now_ref_utc")
    with engine.begin() as cxn:
        try:
            now_ref_row = cxn.execute(sql_now, {"tz": tz}).fetchone()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid timezone. Use an IANA name like 'America/Los_Angeles'.")
        now_ref_utc = now_ref_row[0]

    sql_upcoming = text("""
        WITH weekly AS (
          SELECT season, week, MIN(kickoff_time_utc) AS first_kick
          FROM hcl.games
          WHERE COALESCE(is_postseason, FALSE) = FALSE
            AND kickoff_time_utc IS NOT NULL
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
            AND kickoff_time_utc IS NOT NULL
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

    raise HTTPException(status_code=404, detail="No regular-season weeks found (check games data).")


def select_matchups(season: int, week: int, team: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    """Flexible matchup query (unchanged from v1.6.0)"""
    team_filter_sql = ""
    params = {"season": season, "week": week, "limit": limit, "offset": offset}
    if team:
        team_filter_sql = "AND (home_team = :team OR away_team = :team)"
        params["team"] = team

    sql = text(f"""
        SELECT * FROM hcl.v_game_matchup_display
        WHERE season = :season AND week = :week {team_filter_sql}
        ORDER BY game_date NULLS LAST, home_team, away_team
        LIMIT :limit OFFSET :offset
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, params)
        keys = result.keys()
        rows = result.fetchall()
    return rows_to_dicts(rows, keys)


def select_matchups_for(season: int, week: int) -> List[Dict[str, Any]]:
    """Simplified matchup query (unchanged from v1.6.0)"""
    sql = text("""
        SELECT * FROM hcl.v_game_matchup_display
        WHERE season = :season AND week = :week
        ORDER BY game_date NULLS LAST, home_team, away_team
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, {"season": season, "week": week})
        keys = result.keys()
        rows = result.fetchall()
    return rows_to_dicts(rows, keys)


def select_matchup_by_id(game_id: str) -> Optional[Dict[str, Any]]:
    """Single game lookup (unchanged from v1.6.0)"""
    sql = text("""
        SELECT * FROM hcl.v_game_matchup_display
        WHERE game_id = :game_id LIMIT 1
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, {"game_id": game_id})
        row = result.fetchone()
        if not row:
            return None
        keys = result.keys()
    return dict(zip(keys, row))


def select_weeks(season: Optional[int]) -> List[Dict[str, Any]]:
    """Available weeks query (unchanged from v1.6.0)"""
    params: Dict[str, Any] = {}
    where_season = ""
    if season is not None:
        where_season = "AND season = :season"
        params["season"] = season

    sql = text(f"""
        SELECT season, ARRAY_AGG(DISTINCT week ORDER BY week) AS weeks
        FROM hcl.games
        WHERE COALESCE(is_postseason, FALSE) = FALSE {where_season}
        GROUP BY season ORDER BY season DESC
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql, params)
        rows = result.fetchall()
        keys = result.keys()
    return rows_to_dicts(rows, keys)


def select_seasons() -> List[int]:
    """Available seasons (unchanged from v1.6.0)"""
    sql = text("""
        SELECT DISTINCT season FROM hcl.games
        WHERE COALESCE(is_postseason, FALSE) = FALSE
        ORDER BY season DESC
    """)
    with engine.begin() as cxn:
        result = cxn.execute(sql)
        return [r[0] for r in result.fetchall()]


def select_week_summary(season: int, week: int) -> Dict[str, Any]:
    """
    NEW IN v1.7.0: Week-level aggregate analytics
    
    PATTERN: Multi-CTE query for complex aggregations
    
    CTEs:
    1. wk: Filter to target week's matchups
    2. agg: Calculate week-level aggregates (AVG, PERCENTILE_CONT)
    3. edges: Rank matchups by |diff_epa_pp|, take top 3
    
    PostgreSQL Functions Used:
    - PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x): Median calculation
    - jsonb_agg(jsonb_build_object(...)): JSON aggregation for top_edges array
    - ABS(COALESCE(diff_epa_pp, 0)): Null-safe absolute value
    - ROW_NUMBER() OVER (ORDER BY ...): Window function for ranking
    - to_char(date, 'YYYY-MM-DD'): Date formatting
    
    Aggregates Calculated:
    - avg_diff_epa_pp: Mean matchup edge (home - away EPA/play)
    - median_diff_epa_pp: Median matchup edge (robust to outliers)
    - avg_diff_ypp, median_diff_ypp: Yards per play edges
    - avg_diff_sr: Success rate edges
    - avg_home_epa_pp, avg_away_epa_pp: Offensive efficiency by location
    - avg_home_ppg_for, avg_away_ppg_for: Scoring by location
    - avg_combined_ppg: Total expected points (home + away PPG)
    - avg_home_ypp, avg_away_ypp: Yards efficiency by location
    - home_adv_epa: Home field advantage (avg(home - away EPA/play))
    - top_edges: Top 3 matchups by absolute diff_epa_pp
    
    Use Cases:
    - "Week at a Glance" UI tile above matchup list
    - "Featured Matchups" section highlighting biggest edges
    - Week-level insights: "High-scoring week" / "Tight matchups"
    - Historical analysis: Track home field advantage trends
    """
    sql_summary = text("""
        WITH wk AS (
          SELECT *
          FROM hcl.v_game_matchup_display
          WHERE season = :season AND week = :week
        ),
        agg AS (
          SELECT
            COUNT(*)::int                                       AS games,
            AVG(diff_epa_pp)                                    AS avg_diff_epa_pp,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY diff_epa_pp) AS median_diff_epa_pp,
            AVG(diff_ypp)                                       AS avg_diff_ypp,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY diff_ypp)  AS median_diff_ypp,
            AVG(diff_sr)                                        AS avg_diff_sr,
            AVG(home_epa_pp)                                    AS avg_home_epa_pp,
            AVG(away_epa_pp)                                    AS avg_away_epa_pp,
            AVG(home_ppg_for)                                   AS avg_home_ppg_for,
            AVG(away_ppg_for)                                   AS avg_away_ppg_for,
            AVG(home_ppg_for + away_ppg_for)                    AS avg_combined_ppg,
            AVG(home_ypp)                                       AS avg_home_ypp,
            AVG(away_ypp)                                       AS avg_away_ypp,
            AVG(home_epa_pp - away_epa_pp)                      AS home_adv_epa
          FROM wk
        ),
        edges AS (
          SELECT
            game_id, game_date, home_team, away_team,
            diff_epa_pp, diff_ypp, diff_sr,
            ROW_NUMBER() OVER (ORDER BY ABS(COALESCE(diff_epa_pp,0)) DESC, game_date NULLS LAST) AS rk
          FROM wk
        )
        SELECT
          agg.games, agg.avg_diff_epa_pp, agg.median_diff_epa_pp,
          agg.avg_diff_ypp, agg.median_diff_ypp, agg.avg_diff_sr,
          agg.avg_home_epa_pp, agg.avg_away_epa_pp,
          agg.avg_home_ppg_for, agg.avg_away_ppg_for, agg.avg_combined_ppg,
          agg.avg_home_ypp, agg.avg_away_ypp, agg.home_adv_epa,
          (SELECT jsonb_agg(jsonb_build_object(
                    'game_id', e.game_id,
                    'game_date', to_char(e.game_date, 'YYYY-MM-DD'),
                    'home_team', e.home_team,
                    'away_team', e.away_team,
                    'diff_epa_pp', e.diff_epa_pp,
                    'diff_ypp', e.diff_ypp,
                    'diff_sr', e.diff_sr
                 ) ORDER BY e.rk)
           FROM edges e WHERE e.rk <= 3) AS top_edges
        FROM agg;
    """)
    
    with engine.begin() as cxn:
        row = cxn.execute(sql_summary, {"season": season, "week": week}).mappings().first()

    # PATTERN: Validate data exists before processing
    if not row or row["games"] is None or row["games"] == 0:
        raise HTTPException(status_code=404, detail="No matchups found for that season/week.")

    # PATTERN: Shape database row to response model
    summary = {
        "season": season,
        "week": week,
        "games": row["games"],
        "avg_diff_epa_pp": row["avg_diff_epa_pp"],
        "median_diff_epa_pp": row["median_diff_epa_pp"],
        "avg_diff_ypp": row["avg_diff_ypp"],
        "median_diff_ypp": row["median_diff_ypp"],
        "avg_diff_sr": row["avg_diff_sr"],
        "avg_home_epa_pp": row["avg_home_epa_pp"],
        "avg_away_epa_pp": row["avg_away_epa_pp"],
        "avg_home_ppg_for": row["avg_home_ppg_for"],
        "avg_away_ppg_for": row["avg_away_ppg_for"],
        "avg_combined_ppg": row["avg_combined_ppg"],
        "avg_home_ypp": row["avg_home_ypp"],
        "avg_away_ypp": row["avg_away_ypp"],
        "home_adv_epa": row["home_adv_epa"],
        "top_edges": row["top_edges"] or []
    }
    return summary


# ------------------------------------------------------------------
# Routes (v1.6.0 routes unchanged, v1.7.0 adds /api/week_summary)
# ------------------------------------------------------------------
@app.get("/healthz")
def healthz():
    """Health check (unchanged from v1.6.0)"""
    with engine.begin() as cxn:
        cxn.execute(text("SELECT 1"))
    return {"ok": True}


@app.get("/api/seasons", response_model=List[int])
def get_seasons():
    """List all available seasons (unchanged from v1.6.0)"""
    return select_seasons()


@app.get("/api/weeks", response_model=List[WeeksForSeason])
def get_weeks(
    season: Optional[int] = Query(None, ge=1999, description="Optional. If set, only that season.")
):
    """Available weeks by season (unchanged from v1.6.0)"""
    return select_weeks(season)


@app.get("/api/next_week", response_model=NextWeek)
def get_next_week(
    tz: Optional[constr(strip_whitespace=True, min_length=2, max_length=64)] = Query(
        None, description="IANA timezone, e.g., 'America/Los_Angeles' (default UTC)"
    )
):
    """Next upcoming or latest completed week (unchanged from v1.6.0)"""
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
    """Weekly matchups with filters (unchanged from v1.6.0)"""
    return select_matchups(season=season, week=week, team=team, limit=limit, offset=offset)


@app.get("/api/matchups/{game_id}", response_model=Matchup)
def get_matchup_by_id(game_id: str):
    """Single game matchup detail (unchanged from v1.6.0)"""
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
    """Single-call convenience endpoint (unchanged from v1.6.0)"""
    try:
        season, week, status = select_next_or_latest_week(tz)
        if status == "latest_completed" and not include_last_completed:
            raise HTTPException(
                status_code=400,
                detail="No upcoming week found. Set include_last_completed=true to get the latest completed week."
            )
        return select_matchups_for(season, week)
    except HTTPException as e:
        if include_last_completed and e.status_code == 404:
            season, week, status = select_next_or_latest_week(tz)
            return select_matchups_for(season, week)
        raise


@app.get("/api/week_summary", response_model=WeekSummary)
def get_week_summary(
    season: Optional[int] = Query(None, ge=1999, description="If omitted, inferred from tz via next upcoming or last completed."),
    week: Optional[int] = Query(None, ge=1, le=23),
    tz: Optional[constr(strip_whitespace=True, min_length=2, max_length=64)] = Query(
        None, description="IANA timezone for inference when season/week omitted (e.g., 'America/Los_Angeles')."
    ),
    include_last_completed: bool = Query(
        True,
        description="When inferring and there's no upcoming week, return latest completed."
    )
):
    """
    NEW IN v1.7.0: Week-level aggregate analytics
    
    PATTERN: Flexible endpoint with two modes:
    1. Explicit mode: season + week provided → direct query
    2. Inference mode: season/week omitted → use timezone logic
    
    Query params:
    - season (optional): Explicit season year
    - week (optional): Explicit week number
    - tz (optional): Timezone for inference mode (default UTC)
    - include_last_completed (optional, default true): Fallback behavior
    
    Returns: WeekSummary with aggregates + top 3 edges
    
    Behavior:
    - If season + week provided → query that week directly
    - Otherwise → infer week using select_next_or_latest_week(tz)
    - If inferred week is "latest_completed" and fallback disabled → 400 error
    
    Use cases:
    - GET /api/week_summary?season=2025&week=8 → Explicit week
    - GET /api/week_summary → Current/upcoming week (UTC)
    - GET /api/week_summary?tz=America/Los_Angeles → Current/upcoming week (PT)
    - GET /api/week_summary?include_last_completed=false → Force upcoming only
    
    UI Integration:
    - Render above /api/matchups results
    - Show "Week 8 at a Glance" tile with avg stats
    - Highlight top 3 edges: "Featured Matchups This Week"
    - Display insights: "High-scoring week (45.5 PPG avg)" or "Tight matchups (median edge 0.028)"
    """
    # PATTERN: Explicit mode takes precedence over inference
    if season is not None and week is not None:
        return select_week_summary(season, week)

    # PATTERN: Inference mode using same logic as /api/upcoming_matchups
    try:
        s, w, status = select_next_or_latest_week(tz)
        if status == "latest_completed" and not include_last_completed:
            raise HTTPException(
                status_code=400,
                detail="No upcoming week. Set include_last_completed=true or pass season/week."
            )
        return select_week_summary(s, w)
    except HTTPException as e:
        raise


"""
EXAMPLE API CALLS:

1. Get Week 8 summary explicitly:
   GET /api/week_summary?season=2025&week=8
   → {"season": 2025, "week": 8, "games": 14, "avg_diff_epa_pp": 0.035, ...}

2. Get current/upcoming week summary (UTC):
   GET /api/week_summary
   → {"season": 2025, "week": 8, "games": 14, ...}

3. Get current/upcoming week summary (Pacific time):
   GET /api/week_summary?tz=America/Los_Angeles
   → {"season": 2025, "week": 8, ...}

4. Force upcoming only (no fallback):
   GET /api/week_summary?tz=America/Los_Angeles&include_last_completed=false
   → 400 error if no upcoming week

RESPONSE SHAPE:
{
  "season": 2025,
  "week": 8,
  "games": 14,
  "avg_diff_epa_pp": 0.035,
  "median_diff_epa_pp": 0.028,
  "avg_diff_ypp": 0.22,
  "median_diff_ypp": 0.20,
  "avg_diff_sr": 0.018,
  "avg_home_epa_pp": 0.015,
  "avg_away_epa_pp": -0.006,
  "avg_home_ppg_for": 23.9,
  "avg_away_ppg_for": 21.6,
  "avg_combined_ppg": 45.5,
  "avg_home_ypp": 5.7,
  "avg_away_ypp": 5.4,
  "home_adv_epa": 0.021,
  "top_edges": [
    {
      "game_id": "2025_08_KC_DEN",
      "game_date": "2025-10-27",
      "home_team": "KC",
      "away_team": "DEN",
      "diff_epa_pp": 0.1729,
      "diff_ypp": 0.81,
      "diff_sr": 0.059
    },
    { "..." },
    { "..." }
  ]
}

UI IMPLEMENTATION EXAMPLE:

<div class="week-at-a-glance">
  <h2>Week 8 at a Glance</h2>
  <div class="stats-grid">
    <div class="stat">
      <label>Avg Total Points</label>
      <value>45.5</value>
    </div>
    <div class="stat">
      <label>Home Field Advantage</label>
      <value>+0.021 EPA/play</value>
    </div>
    <div class="stat">
      <label>Median Matchup Edge</label>
      <value>0.028 EPA/play</value>
    </div>
  </div>
  
  <h3>Featured Matchups</h3>
  <div class="top-edges">
    {top_edges.map(edge => (
      <div class="edge-card">
        <span class="teams">{edge.home_team} vs {edge.away_team}</span>
        <span class="edge">+{edge.diff_epa_pp} EPA/play</span>
      </div>
    ))}
  </div>
</div>
"""

"""
FLASK TRANSLATION NOTES FOR v1.7.0:

NEW PATTERNS TO TRANSLATE:

1. PERCENTILE_CONT aggregation:
   - Works identically in psycopg2
   - Returns float, handle None gracefully
   
2. jsonb_agg + jsonb_build_object:
   - PostgreSQL returns JSONB as dict in psycopg2
   - cursor.fetchone()['top_edges'] → already a Python list of dicts
   - No manual JSON parsing needed
   
3. ROW_NUMBER() window function:
   - Works identically in psycopg2
   - Used for top N ranking without LIMIT in subquery
   
4. Multi-CTE query:
   - Works identically in psycopg2
   - Keep structure exactly as is
   
5. .mappings().first():
   - SQLAlchemy method for dict-style row access
   - In psycopg2: Use RealDictCursor or manual zip(cursor.description, row)
   
6. Optional int type (int | None):
   - Python 3.10+ syntax
   - In Flask: Use Optional[int] or validate request.args.get() manually

FLASK IMPLEMENTATION:

@app.route('/api/week_summary')
def get_week_summary():
    season = request.args.get('season', type=int)
    week = request.args.get('week', type=int)
    tz = request.args.get('tz', default='UTC')
    include_last_completed = request.args.get('include_last_completed', default='true').lower() == 'true'
    
    # Explicit mode
    if season and week:
        summary = select_week_summary(season, week)
        return jsonify(summary)
    
    # Inference mode
    try:
        s, w, status = select_next_or_latest_week(tz)
        if status == 'latest_completed' and not include_last_completed:
            return jsonify({'error': 'No upcoming week'}), 400
        summary = select_week_summary(s, w)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def select_week_summary(season, week):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql_summary, {'season': season, 'week': week})
            row = cur.fetchone()
            
        if not row or row['games'] == 0:
            raise ValueError('No matchups found')
            
        return dict(row)  # RealDictCursor returns dict-like rows
    finally:
        conn.close()
"""
