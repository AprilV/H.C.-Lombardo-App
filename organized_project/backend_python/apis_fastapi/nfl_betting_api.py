#!/usr/bin/env python3
"""
NFL Betting Database REST API
FastAPI-based API for NFL betting predictions and database operations
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import sys
import os
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime, date
import logging

# Add parent directory to path to import NFL utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'nfl_betting_database'))

try:
    from nfl_database_utils import NFLDatabaseManager
except ImportError:
    print("Error: Could not import NFL database utilities")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="H.C. Lombardo NFL Betting API",
    description="Professional NFL betting predictions and database operations by H.C. Lombardo",
    version="1.0.0"
)

# Initialize database manager
db_path = os.path.join(os.path.dirname(__file__), '..', 'nfl_betting_database', 'sports_betting.db')
db_manager = NFLDatabaseManager(db_path)

# Homepage route
@app.get("/", response_class=HTMLResponse)
async def homepage():
    """
    HTML homepage with navigation menu to all API endpoints
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>H.C. Lombardo - NFL Betting API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                line-height: 1.6;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            h1 {
                text-align: center;
                font-size: 3rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .subtitle {
                text-align: center;
                font-size: 1.2rem;
                margin-bottom: 40px;
                opacity: 0.9;
            }
            .nav-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .nav-card {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 25px;
                text-decoration: none;
                color: white;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(5px);
            }
            .nav-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.25);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                color: #FFD700;
            }
            .nav-card h3 {
                margin-top: 0;
                font-size: 1.3rem;
                color: #FFD700;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .nav-card p {
                margin-bottom: 0;
                opacity: 0.9;
                font-size: 0.95rem;
            }
            .icon {
                font-size: 1.5rem;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                opacity: 0.7;
                font-size: 0.9rem;
            }
            .api-status {
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: bold;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="api-status">🟢 API Active</div>
            <h1>🏈 H.C. Lombardo - NFL Betting API</h1>
            <p class="subtitle">Professional REST API for NFL betting predictions by H.C. Lombardo</p>
            
            <div class="nav-grid">
                <a href="/docs" class="nav-card">
                    <h3><span class="icon">📚</span> Swagger UI</h3>
                    <p>Interactive API documentation with request/response examples and testing interface</p>
                </a>
                
                <a href="/redoc" class="nav-card">
                    <h3><span class="icon">📖</span> ReDoc UI</h3>
                    <p>Beautiful API documentation with detailed schemas and comprehensive endpoint descriptions</p>
                </a>
                
                <a href="/teams" class="nav-card">
                    <h3><span class="icon">🏟️</span> Teams API</h3>
                    <p>Access all 32 NFL teams with conference, division, and performance statistics</p>
                </a>
                
                <a href="/games?season=2024&week=1" class="nav-card">
                    <h3><span class="icon">⚡</span> Games API</h3>
                    <p>Retrieve game schedules, scores, and matchup data for current and past seasons</p>
                </a>
                
                <a href="/docs#/default/predict_game_predict_post" class="nav-card">
                    <h3><span class="icon">🎯</span> Predictions API</h3>
                    <p>Generate betting line predictions using advanced algorithms and team analytics</p>
                </a>
                
                <a href="/database/stats" class="nav-card">
                    <h3><span class="icon">📊</span> Database Stats</h3>
                    <p>View comprehensive database statistics and system performance metrics</p>
                </a>
            </div>
            
            <div class="footer">
                <p>🚀 Built by H.C. Lombardo with FastAPI • Powered by NFL Database • Version 1.0.0</p>
                <p>📡 Real-time NFL data integration with betting line predictions</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# Pydantic models
class Team(BaseModel):
    team_id: int
    name: str
    abbreviation: str
    division: str
    conference: str
    city: Optional[str] = None

class Game(BaseModel):
    game_id: int
    week: int
    season: int
    home_team: str
    away_team: str
    game_date: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    game_status: str

class TeamStats(BaseModel):
    team_name: str
    abbreviation: str
    avg_offense: float
    avg_defense: float
    avg_turnovers: float
    avg_passing: float
    avg_rushing: float
    games_played: int

class BettingLine(BaseModel):
    line_id: int
    game_id: int
    spread: float
    total: float
    home_moneyline: Optional[int] = None
    away_moneyline: Optional[int] = None
    sportsbook: Optional[str] = None
    prediction_confidence: Optional[float] = None

class PredictionRequest(BaseModel):
    home_team_id: int
    away_team_id: int
    season: int

class PredictionResult(BaseModel):
    home_team: str
    away_team: str
    predicted_spread: float
    predicted_total: float
    confidence: float
    home_stats: TeamStats
    away_stats: TeamStats

class NewTeam(BaseModel):
    name: str
    abbreviation: str
    division: str
    conference: str
    city: Optional[str] = None

class NewGame(BaseModel):
    week: int
    season: int
    home_team_id: int
    away_team_id: int
    game_date: str
    game_time: Optional[str] = None

# Simple prediction class (copied from betting_predictor_example.py)
class BettingPredictor:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def analyze_team_performance(self, team_id: int, season: int) -> Optional[Dict]:
        """Analyze team performance for the season"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    AVG(ts.offense_yards) as avg_offense,
                    AVG(ts.defense_yards) as avg_defense,
                    AVG(ts.turnovers) as avg_turnovers,
                    AVG(ts.passing_yards) as avg_passing,
                    AVG(ts.rushing_yards) as avg_rushing,
                    COUNT(*) as games_played,
                    t.name, t.abbreviation
                FROM TeamStats ts
                JOIN Games g ON ts.game_id = g.game_id
                JOIN Teams t ON ts.team_id = t.team_id
                WHERE ts.team_id = ? AND g.season = ?
                GROUP BY ts.team_id, t.name, t.abbreviation
            ''', (team_id, season))
            
            result = cursor.fetchone()
            if result:
                return {
                    'team_name': result['name'],
                    'abbreviation': result['abbreviation'],
                    'avg_offense': round(result['avg_offense'] or 0, 1),
                    'avg_defense': round(result['avg_defense'] or 0, 1),
                    'avg_turnovers': round(result['avg_turnovers'] or 0, 1),
                    'avg_passing': round(result['avg_passing'] or 0, 1),
                    'avg_rushing': round(result['avg_rushing'] or 0, 1),
                    'games_played': result['games_played']
                }
            return None
    
    def predict_spread(self, home_team_id: int, away_team_id: int, season: int) -> Dict:
        """Predict spread for a game"""
        home_stats = self.analyze_team_performance(home_team_id, season)
        away_stats = self.analyze_team_performance(away_team_id, season)
        
        if not home_stats or not away_stats:
            return {'error': 'Insufficient data for prediction'}
        
        # Simple prediction algorithm
        home_advantage = 3.0
        home_off_diff = home_stats['avg_offense'] - away_stats['avg_defense']
        away_off_diff = away_stats['avg_offense'] - home_stats['avg_defense']
        
        predicted_spread = (home_off_diff - away_off_diff) / 25.0 + home_advantage
        predicted_spread = round(predicted_spread * 2) / 2
        
        predicted_total = (home_stats['avg_offense'] + away_stats['avg_offense']) / 15.0 + 42.0
        predicted_total = round(predicted_total * 2) / 2
        
        return {
            'home_team': home_stats['team_name'],
            'away_team': away_stats['team_name'],
            'predicted_spread': predicted_spread,
            'predicted_total': predicted_total,
            'home_stats': home_stats,
            'away_stats': away_stats,
            'confidence': min(0.95, max(0.55, abs(predicted_spread) / 10.0 + 0.6))
        }

# Initialize predictor
predictor = BettingPredictor(db_manager)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = db_manager.get_database_stats()
        return {
            "status": "healthy",
            "database_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/teams", response_model=List[Team])
async def get_teams():
    """Get all teams"""
    try:
        teams = db_manager.get_teams()
        return [Team(**dict(team)) for team in teams]
    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch teams")

@app.post("/teams", response_model=dict)
async def add_team(team: NewTeam):
    """Add a new team"""
    try:
        team_id = db_manager.add_team(
            team.name, team.abbreviation, team.division, team.conference, team.city
        )
        return {"message": "Team added successfully", "team_id": team_id}
    except Exception as e:
        logger.error(f"Error adding team: {e}")
        raise HTTPException(status_code=500, detail="Failed to add team")

@app.get("/games")
async def get_games(
    season: int = Query(..., description="NFL season year"),
    week: int = Query(..., description="NFL week (1-22)")
):
    """Get games for a specific week"""
    try:
        games = db_manager.get_games_by_week(season, week)
        return [dict(game) for game in games]
    except Exception as e:
        logger.error(f"Error fetching games: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch games")

@app.post("/games", response_model=dict)
async def add_game(game: NewGame):
    """Add a new game"""
    try:
        game_id = db_manager.add_game(
            game.week, game.season, game.home_team_id, 
            game.away_team_id, game.game_date, game.game_time
        )
        return {"message": "Game added successfully", "game_id": game_id}
    except Exception as e:
        logger.error(f"Error adding game: {e}")
        raise HTTPException(status_code=500, detail="Failed to add game")

@app.post("/predict", response_model=PredictionResult)
async def predict_game(request: PredictionRequest):
    """Predict betting lines for a game"""
    try:
        prediction = predictor.predict_spread(
            request.home_team_id, request.away_team_id, request.season
        )
        
        if 'error' in prediction:
            raise HTTPException(status_code=400, detail=prediction['error'])
        
        return PredictionResult(
            home_team=prediction['home_team'],
            away_team=prediction['away_team'],
            predicted_spread=prediction['predicted_spread'],
            predicted_total=prediction['predicted_total'],
            confidence=prediction['confidence'],
            home_stats=TeamStats(**prediction['home_stats']),
            away_stats=TeamStats(**prediction['away_stats'])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.get("/betting-lines/{game_id}", response_model=List[BettingLine])
async def get_betting_lines(game_id: int):
    """Get betting lines for a specific game"""
    try:
        lines = db_manager.get_betting_lines(game_id)
        return [BettingLine(**dict(line)) for line in lines]
    except Exception as e:
        logger.error(f"Error fetching betting lines: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch betting lines")

@app.get("/stats/team/{team_id}")
async def get_team_stats(team_id: int, season: int = Query(..., description="Season year")):
    """Get team statistics for a season"""
    try:
        stats = predictor.analyze_team_performance(team_id, season)
        if not stats:
            raise HTTPException(status_code=404, detail="No statistics found for this team/season")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch team statistics")

@app.get("/database/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        return db_manager.get_database_stats()
    except Exception as e:
        logger.error(f"Error fetching database stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch database statistics")

if __name__ == "__main__":
    print("Starting NFL Betting API...")
    print("API Documentation: http://localhost:8001/docs")
    print("API Interface: http://localhost:8001/redoc")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)