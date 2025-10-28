"""
HC Lombardo - Matchup API Endpoints
FastAPI endpoints for game matchup data from v_game_matchup_display view

Endpoints:
- GET /api/matchups?season={year}&week={week} - All matchups for a week
- GET /api/matchups/{game_id} - Single game matchup detail
- GET /api/teams/{team_abbr}/matchups?season={year} - All matchups for a team

Requirements:
- pip install fastapi uvicorn psycopg2-binary python-dotenv
- PostgreSQL with hcl.v_game_matchup_display view
- DATABASE_URL environment variable
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="HC Lombardo Matchup API",
    description="NFL game matchup analytics with betting insights",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    """Get PostgreSQL database connection."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback to individual connection params
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "nfl_analytics"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
    return psycopg2.connect(db_url)

# Pydantic models for type-safe responses
class TeamStats(BaseModel):
    """Team statistics for a matchup."""
    games_played: Optional[int] = Field(None, alias="gp", description="Games played this season")
    ppg_for: Optional[float] = Field(None, description="Points per game scored")
    ppg_against: Optional[float] = Field(None, description="Points per game allowed")
    ypp: Optional[float] = Field(None, description="Yards per play")
    sr: Optional[float] = Field(None, description="Success rate")
    epa_pp: Optional[float] = Field(None, description="EPA per play")
    to_pg: Optional[float] = Field(None, description="Turnovers per game")
    third_down_rate: Optional[float] = Field(None, alias="3d_rate", description="3rd down conversion rate")
    fourth_down_rate: Optional[float] = Field(None, alias="4d_rate", description="4th down conversion rate")

class MomentumStats(BaseModel):
    """Last-3 game momentum indicators."""
    epa_l3: Optional[float] = Field(None, description="EPA/play last 3 games")
    ypp_l3: Optional[float] = Field(None, description="Yards/play last 3 games")
    ppg_l3: Optional[float] = Field(None, description="Points/game last 3 games")

class MatchupEdges(BaseModel):
    """Home vs Away statistical edges."""
    diff_epa_pp: Optional[float] = Field(None, description="EPA per play differential (home - away)")
    diff_ypp: Optional[float] = Field(None, description="Yards per play differential")
    diff_sr: Optional[float] = Field(None, description="Success rate differential")
    diff_ppg_for: Optional[float] = Field(None, description="Points per game differential")

class GameMatchup(BaseModel):
    """Complete game matchup with home/away stats."""
    # Game identifiers
    game_id: str
    season: int
    week: int
    game_date: Optional[date]
    home_team: str
    away_team: str
    stadium: Optional[str]
    city: Optional[str]
    state: Optional[str]
    timezone: Optional[str]
    
    # Home team stats
    home_stats: TeamStats
    home_momentum: MomentumStats
    
    # Away team stats
    away_stats: TeamStats
    away_momentum: MomentumStats
    
    # Matchup edges
    edges: MatchupEdges

    class Config:
        populate_by_name = True

class MatchupListResponse(BaseModel):
    """Response for multiple matchups."""
    season: int
    week: int
    total_games: int
    matchups: List[GameMatchup]

# Helper function to convert DB row to GameMatchup
def row_to_matchup(row: dict) -> GameMatchup:
    """Convert database row to GameMatchup model."""
    return GameMatchup(
        game_id=row["game_id"],
        season=row["season"],
        week=row["week"],
        game_date=row.get("game_date"),
        home_team=row["home_team"],
        away_team=row["away_team"],
        stadium=row.get("stadium"),
        city=row.get("city"),
        state=row.get("state"),
        timezone=row.get("timezone"),
        home_stats=TeamStats(
            gp=row.get("home_gp"),
            ppg_for=row.get("home_ppg_for"),
            ppg_against=row.get("home_ppg_against"),
            ypp=row.get("home_ypp"),
            sr=row.get("home_sr"),
            epa_pp=row.get("home_epa_pp"),
            to_pg=row.get("home_to_pg"),
            third_down_rate=row.get("home_3d_rate"),
            fourth_down_rate=row.get("home_4d_rate")
        ),
        home_momentum=MomentumStats(
            epa_l3=row.get("home_epa_l3"),
            ypp_l3=row.get("home_ypp_l3"),
            ppg_l3=row.get("home_ppg_l3")
        ),
        away_stats=TeamStats(
            gp=row.get("away_gp"),
            ppg_for=row.get("away_ppg_for"),
            ppg_against=row.get("away_ppg_against"),
            ypp=row.get("away_ypp"),
            sr=row.get("away_sr"),
            epa_pp=row.get("away_epa_pp"),
            to_pg=row.get("away_to_pg"),
            third_down_rate=row.get("away_3d_rate"),
            fourth_down_rate=row.get("away_4d_rate")
        ),
        away_momentum=MomentumStats(
            epa_l3=row.get("away_epa_l3"),
            ypp_l3=row.get("away_ypp_l3"),
            ppg_l3=row.get("away_ppg_l3")
        ),
        edges=MatchupEdges(
            diff_epa_pp=row.get("diff_epa_pp"),
            diff_ypp=row.get("diff_ypp"),
            diff_sr=row.get("diff_sr"),
            diff_ppg_for=row.get("diff_ppg_for")
        )
    )

# API Endpoints
@app.get("/")
def read_root():
    """API root - health check."""
    return {
        "service": "HC Lombardo Matchup API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "weekly_matchups": "/api/matchups?season={year}&week={week}",
            "single_matchup": "/api/matchups/{game_id}",
            "team_matchups": "/api/teams/{abbr}/matchups?season={year}"
        }
    }

@app.get("/api/matchups", response_model=MatchupListResponse)
def get_weekly_matchups(
    season: int = Query(..., description="Season year (e.g., 2024)"),
    week: int = Query(..., ge=1, le=18, description="Week number (1-18)")
):
    """
    Get all matchups for a specific week.
    
    Example: /api/matchups?season=2024&week=8
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM hcl.v_game_matchup_display
                WHERE season = %s AND week = %s
                ORDER BY game_date, home_team
            """, (season, week))
            rows = cur.fetchall()
            
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No matchups found for season {season}, week {week}"
            )
        
        matchups = [row_to_matchup(dict(row)) for row in rows]
        
        return MatchupListResponse(
            season=season,
            week=week,
            total_games=len(matchups),
            matchups=matchups
        )
    
    finally:
        conn.close()

@app.get("/api/matchups/{game_id}", response_model=GameMatchup)
def get_single_matchup(game_id: str):
    """
    Get detailed matchup for a specific game.
    
    Example: /api/matchups/2024_08_KC_BUF
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM hcl.v_game_matchup_display
                WHERE game_id = %s
            """, (game_id,))
            row = cur.fetchone()
            
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Matchup not found for game_id: {game_id}"
            )
        
        return row_to_matchup(dict(row))
    
    finally:
        conn.close()

@app.get("/api/teams/{team_abbr}/matchups")
def get_team_matchups(
    team_abbr: str,
    season: int = Query(..., description="Season year (e.g., 2024)")
):
    """
    Get all matchups for a specific team in a season.
    
    Example: /api/teams/KC/matchups?season=2024
    """
    team_abbr = team_abbr.upper()
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM hcl.v_game_matchup_display
                WHERE season = %s 
                  AND (home_team = %s OR away_team = %s)
                ORDER BY week
            """, (season, team_abbr, team_abbr))
            rows = cur.fetchall()
            
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No matchups found for team {team_abbr} in season {season}"
            )
        
        matchups = [row_to_matchup(dict(row)) for row in rows]
        
        return {
            "team": team_abbr,
            "season": season,
            "total_games": len(matchups),
            "matchups": matchups
        }
    
    finally:
        conn.close()

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
