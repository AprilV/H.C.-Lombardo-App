"""
HC Lombardo - Historical Data API
Sprint 6: Team analytics endpoints for betting insights

Endpoints:
- GET /api/teams - List all NFL teams
- GET /api/teams/<abbr> - Team season overview with stats
- GET /api/teams/<abbr>/games - Team game-by-game history
- GET /api/games?season=2024&week=7 - Games by week

Uses hcl schema in nfl_analytics_test database
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'nfl_analytics_test',
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# All 32 NFL teams
NFL_TEAMS = [
    'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
    'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
    'LAC', 'LAR', 'LV', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
    'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS'
]

def get_db_connection():
    """Get PostgreSQL database connection."""
    return psycopg2.connect(**DB_CONFIG)


@app.route('/')
def index():
    """API root - health check."""
    return jsonify({
        'service': 'HC Lombardo Historical Data API',
        'version': 'Sprint 6',
        'status': 'healthy',
        'endpoints': {
            'teams': '/api/teams',
            'team_overview': '/api/teams/<abbr>',
            'team_games': '/api/teams/<abbr>/games',
            'games_by_week': '/api/games?season=2024&week=7'
        }
    })


@app.route('/api/teams')
def get_teams():
    """
    Get list of all NFL teams with season stats.
    
    Query params:
        season (int, optional): Filter by season (default: 2024)
    
    Returns:
        {
            "season": 2024,
            "teams": [
                {
                    "team": "KC",
                    "games_played": 7,
                    "wins": 6,
                    "losses": 1,
                    "avg_ppg_for": 27.3,
                    "avg_epa_offense": 0.24,
                    ...
                },
                ...
            ]
        }
    """
    season = request.args.get('season', 2024, type=int)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    team,
                    season,
                    games_played,
                    wins,
                    losses,
                    avg_ppg_for,
                    avg_ppg_against,
                    avg_epa_offense,
                    avg_epa_defense,
                    avg_success_rate_offense,
                    avg_yards_per_play,
                    avg_third_down_rate,
                    total_turnover_diff,
                    home_wins,
                    home_losses,
                    away_wins,
                    away_losses
                FROM hcl.v_team_season_stats
                WHERE season = %s
                ORDER BY avg_epa_offense DESC NULLS LAST
            """, (season,))
            teams = cur.fetchall()
        
        # Convert to list of dicts
        teams_list = [dict(row) for row in teams]
        
        return jsonify({
            'season': season,
            'total_teams': len(teams_list),
            'teams': teams_list
        })
    
    finally:
        conn.close()


@app.route('/api/teams/<team_abbr>')
def get_team_overview(team_abbr):
    """
    Get team season overview with detailed stats.
    
    Path params:
        team_abbr (str): Team abbreviation (e.g., 'KC')
    
    Query params:
        season (int, optional): Season year (default: 2024)
    
    Returns:
        {
            "team": "KC",
            "season": 2024,
            "record": "6-1",
            "games_played": 7,
            "offense": {
                "avg_ppg": 27.3,
                "avg_epa_per_play": 0.24,
                "avg_success_rate": 0.52,
                "avg_yards_per_play": 5.8,
                ...
            },
            "defense": { ... },
            "splits": {
                "home": "4-0",
                "away": "2-1"
            }
        }
    """
    team_abbr = team_abbr.upper()
    season = request.args.get('season', 2024, type=int)
    
    if team_abbr not in NFL_TEAMS:
        return jsonify({'error': f'Invalid team: {team_abbr}'}), 404
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT *
                FROM hcl.v_team_season_stats
                WHERE team = %s AND season = %s
            """, (team_abbr, season))
            stats = cur.fetchone()
        
        if not stats:
            return jsonify({'error': f'No data found for {team_abbr} in {season}'}), 404
        
        # Format response
        stats_dict = dict(stats)
        response = {
            'team': team_abbr,
            'season': season,
            'record': f"{stats_dict.get('wins', 0)}-{stats_dict.get('losses', 0)}",
            'games_played': stats_dict.get('games_played', 0),
            'offense': {
                'avg_ppg': round(stats_dict.get('avg_ppg_for', 0), 1),
                'avg_epa_per_play': round(stats_dict.get('avg_epa_offense', 0), 3) if stats_dict.get('avg_epa_offense') else None,
                'avg_success_rate': round(stats_dict.get('avg_success_rate_offense', 0), 3) if stats_dict.get('avg_success_rate_offense') else None,
                'avg_yards_per_play': round(stats_dict.get('avg_yards_per_play', 0), 2) if stats_dict.get('avg_yards_per_play') else None,
                'avg_third_down_rate': round(stats_dict.get('avg_third_down_rate', 0), 3) if stats_dict.get('avg_third_down_rate') else None,
                'avg_red_zone_efficiency': round(stats_dict.get('avg_red_zone_efficiency', 0), 3) if stats_dict.get('avg_red_zone_efficiency') else None
            },
            'defense': {
                'avg_ppg_allowed': round(stats_dict.get('avg_ppg_against', 0), 1),
                'avg_epa_per_play': round(stats_dict.get('avg_epa_defense', 0), 3) if stats_dict.get('avg_epa_defense') else None
            },
            'turnovers': {
                'total_lost': stats_dict.get('total_turnovers_lost', 0),
                'total_gained': stats_dict.get('total_turnovers_gained', 0),
                'differential': stats_dict.get('total_turnover_diff', 0)
            },
            'splits': {
                'home': f"{stats_dict.get('home_wins', 0)}-{stats_dict.get('home_losses', 0)}",
                'away': f"{stats_dict.get('away_wins', 0)}-{stats_dict.get('away_losses', 0)}",
                'home_epa': round(stats_dict.get('avg_epa_home', 0), 3) if stats_dict.get('avg_epa_home') else None,
                'away_epa': round(stats_dict.get('avg_epa_away', 0), 3) if stats_dict.get('avg_epa_away') else None
            }
        }
        
        return jsonify(response)
    
    finally:
        conn.close()


@app.route('/api/teams/<team_abbr>/games')
def get_team_games(team_abbr):
    """
    Get team's game-by-game history.
    
    Path params:
        team_abbr (str): Team abbreviation (e.g., 'KC')
    
    Query params:
        season (int, optional): Season year (default: 2024)
        last (int, optional): Return only last N games
    
    Returns:
        {
            "team": "KC",
            "season": 2024,
            "total_games": 7,
            "games": [
                {
                    "game_id": "2024_07_KC_SF",
                    "week": 7,
                    "opponent": "SF",
                    "is_home": true,
                    "points_scored": 28,
                    "points_allowed": 18,
                    "won": true,
                    "epa_per_play": 0.31,
                    "success_rate": 0.54,
                    "yards_per_play": 6.8,
                    ...
                },
                ...
            ]
        }
    """
    team_abbr = team_abbr.upper()
    season = request.args.get('season', 2024, type=int)
    last_n = request.args.get('last', type=int)
    
    if team_abbr not in NFL_TEAMS:
        return jsonify({'error': f'Invalid team: {team_abbr}'}), 404
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Base query
            query = """
                SELECT 
                    tgs.game_id,
                    tgs.season,
                    tgs.week,
                    tgs.opponent,
                    tgs.is_home,
                    tgs.points_scored,
                    tgs.points_allowed,
                    tgs.won,
                    tgs.epa_per_play,
                    tgs.success_rate,
                    tgs.yards_per_play,
                    tgs.total_plays,
                    tgs.total_yards,
                    tgs.turnovers_lost,
                    tgs.third_down_rate,
                    tgs.red_zone_efficiency,
                    tgs.epa_last_3_games,
                    tgs.ppg_last_3_games,
                    g.game_date
                FROM hcl.team_game_stats tgs
                JOIN hcl.games g ON tgs.game_id = g.game_id
                WHERE tgs.team = %s AND tgs.season = %s
                ORDER BY g.game_date DESC
            """
            
            params = [team_abbr, season]
            
            # Add LIMIT if last_n specified
            if last_n:
                query += " LIMIT %s"
                params.append(last_n)
            
            cur.execute(query, params)
            games = cur.fetchall()
        
        if not games:
            return jsonify({'error': f'No games found for {team_abbr} in {season}'}), 404
        
        # Convert to list of dicts with formatting
        games_list = []
        for game in games:
            game_dict = dict(game)
            # Format floats
            for key in ['epa_per_play', 'success_rate', 'yards_per_play', 'third_down_rate', 
                       'red_zone_efficiency', 'epa_last_3_games', 'ppg_last_3_games']:
                if game_dict.get(key) is not None:
                    game_dict[key] = round(float(game_dict[key]), 3)
            # Convert date to string
            if game_dict.get('game_date'):
                game_dict['game_date'] = game_dict['game_date'].strftime('%Y-%m-%d')
            games_list.append(game_dict)
        
        return jsonify({
            'team': team_abbr,
            'season': season,
            'total_games': len(games_list),
            'games': games_list
        })
    
    finally:
        conn.close()


@app.route('/api/games')
def get_games_by_week():
    """
    Get all games for a specific week.
    
    Query params:
        season (int, required): Season year
        week (int, required): Week number
    
    Returns:
        {
            "season": 2024,
            "week": 7,
            "total_games": 15,
            "games": [
                {
                    "game_id": "2024_07_KC_SF",
                    "home_team": "SF",
                    "away_team": "KC",
                    "home_score": 18,
                    "away_score": 28,
                    "game_date": "2024-10-20",
                    ...
                },
                ...
            ]
        }
    """
    season = request.args.get('season', type=int)
    week = request.args.get('week', type=int)
    
    if not season or not week:
        return jsonify({'error': 'season and week parameters required'}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    game_id,
                    season,
                    week,
                    home_team,
                    away_team,
                    home_score,
                    away_score,
                    game_date,
                    stadium,
                    city,
                    state
                FROM hcl.games
                WHERE season = %s AND week = %s
                ORDER BY game_date, kickoff_time_utc
            """, (season, week))
            games = cur.fetchall()
        
        if not games:
            return jsonify({'error': f'No games found for season {season} week {week}'}), 404
        
        # Convert to list of dicts
        games_list = []
        for game in games:
            game_dict = dict(game)
            if game_dict.get('game_date'):
                game_dict['game_date'] = game_dict['game_date'].strftime('%Y-%m-%d')
            games_list.append(game_dict)
        
        return jsonify({
            'season': season,
            'week': week,
            'total_games': len(games_list),
            'games': games_list
        })
    
    finally:
        conn.close()


@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("HC LOMBARDO - HISTORICAL DATA API")
    print("Sprint 6: Team Analytics Endpoints")
    print("="*70)
    print(f"\nStarting server at http://127.0.0.1:8000")
    print(f"Database: {DB_CONFIG['database']}")
    print("\nEndpoints:")
    print("  GET  /api/teams")
    print("  GET  /api/teams/<abbr>")
    print("  GET  /api/teams/<abbr>/games")
    print("  GET  /api/games?season=2024&week=7")
    print("="*70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=8000)
