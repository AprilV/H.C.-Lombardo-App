"""
H.C. Lombardo NFL Analytics - Production API Server
Flask + PostgreSQL + CORS for React frontend
Serves both API endpoints and production React build
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import psycopg2
import sys
import os
from logging_config import setup_logging
from dashboard_api import register_dashboard_routes
from api_routes_hcl import hcl_bp
from api_routes_ml import ml_api
from api_routes_live_scores import live_scores_api
from background_updater import updater

# Initialize logger
loggers = setup_logging()
logger = loggers['api']

# Get build folder path
BUILD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'build')

# Initialize Flask with static files
app = Flask(__name__, static_folder=BUILD_FOLDER, static_url_path='')

# Enable CORS for React frontend and local HTML files
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000", 
            "http://127.0.0.1:3000", 
            "http://localhost:5000", 
            "http://127.0.0.1:5000", 
            "https://master.d2tamnlcbzo0d5.amplifyapp.com",
            "https://nfl.aprilsykes.dev",
            "null"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Register dashboard API routes
register_dashboard_routes(app)

# Register HCL API routes
app.register_blueprint(hcl_bp)

# Register ML API routes
# Register ML API routes
app.register_blueprint(ml_api)

# Register Live Scores API routes
app.register_blueprint(live_scores_api)

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'nfl_analytics'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'aprilv120'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

# API Routes (these must come before the React catch-all route)

@app.route('/health')
def health():
    """Health check including database connectivity"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        logger.info("Health check passed")
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "cors": "enabled"
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route('/api/teams')
def get_teams():
    """Get all NFL teams from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, abbreviation, wins, losses, ties, ppg, pa, games_played, last_updated 
            FROM teams 
            ORDER BY name
        """)
        teams = cursor.fetchall()
        cursor.close()
        conn.close()
        
        teams_list = [
            {
                "name": team[0],
                "abbreviation": team[1],
                "wins": team[2],
                "losses": team[3],
                "ties": team[4],
                "ppg": float(team[5]) if team[5] is not None else None,
                "pa": float(team[6]) if team[6] is not None else None,
                "games_played": team[7],
                "last_updated": team[8].isoformat() if team[8] else None
            }
            for team in teams
        ]
        
        logger.info(f"Retrieved {len(teams_list)} teams")
        return jsonify({
            "count": len(teams_list),
            "teams": teams_list
        })
    except Exception as e:
        logger.error(f"Failed to fetch teams: {e}")
        return jsonify({
            "error": str(e),
            "message": "Failed to fetch teams"
        }), 500

@app.route('/api/teams/count')
def get_teams_count():
    """Get count of teams in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        logger.info(f"Team count: {count}")
        return jsonify({
            "count": count,
            "expected": 32,
            "status": "correct" if count == 32 else "warning"
        })
    except Exception as e:
        logger.error(f"Failed to get team count: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/teams/<abbreviation>')
def get_team_by_abbr(abbreviation):
    """Get specific team by abbreviation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, abbreviation, wins, losses, ties, ppg, pa, games_played, last_updated 
            FROM teams 
            WHERE UPPER(abbreviation) = UPPER(%s)
        """, (abbreviation,))
        team = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if team:
            logger.info(f"Retrieved team: {abbreviation}")
            return jsonify({
                "name": team[0],
                "abbreviation": team[1],
                "wins": team[2],
                "losses": team[3],
                "ties": team[4],
                "ppg": float(team[5]) if team[5] is not None else None,
                "pa": float(team[6]) if team[6] is not None else None,
                "games_played": team[7],
                "last_updated": team[8].isoformat() if team[8] else None
            })
        else:
            logger.warning(f"Team not found: {abbreviation}")
            return jsonify({
                "error": "Team not found",
                "abbreviation": abbreviation
            }), 404
    except Exception as e:
        logger.error(f"Failed to fetch team {abbreviation}: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/game-statistics')
def get_game_statistics():
    """Get game statistics from team_game_stats table"""
    try:
        # Get query parameters
        season = request.args.get('season', type=int)
        week = request.args.get('week', type=int)
        team = request.args.get('team')
        game_id = request.args.get('game_id')
        limit = request.args.get('limit', default=100, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on filters
        query = """
            SELECT 
                game_id, team, opponent, is_home, season, week,
                points, touchdowns, field_goals_made, field_goals_att,
                total_yards, passing_yards, rushing_yards, plays, yards_per_play,
                completions, passing_att, completion_pct, passing_tds, interceptions,
                sacks_taken, sack_yards_lost, qb_rating,
                rushing_att, yards_per_carry, rushing_tds,
                third_down_conv, third_down_att, third_down_pct,
                fourth_down_conv, fourth_down_att, fourth_down_pct,
                red_zone_conv, red_zone_att, red_zone_pct,
                turnovers, fumbles_lost, penalties, penalty_yards,
                time_of_possession_sec, time_of_possession_pct,
                result, epa_per_play, success_rate, total_epa
            FROM hcl.team_game_stats
            WHERE 1=1
        """
        params = []
        
        if season:
            query += " AND season = %s"
            params.append(season)
        if week:
            query += " AND week = %s"
            params.append(week)
        if team:
            query += " AND UPPER(team) = UPPER(%s)"
            params.append(team)
        if game_id:
            query += " AND game_id = %s"
            params.append(game_id)
            
        query += " ORDER BY season DESC, week DESC, game_id LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        stats = cursor.fetchall()
        cursor.close()
        conn.close()
        
        stats_list = []
        for stat in stats:
            stats_list.append({
                "game_id": stat[0],
                "team": stat[1],
                "opponent": stat[2],
                "is_home": stat[3],
                "season": stat[4],
                "week": stat[5],
                "points": stat[6],
                "touchdowns": stat[7],
                "field_goals_made": stat[8],
                "field_goals_att": stat[9],
                "total_yards": stat[10],
                "passing_yards": stat[11],
                "rushing_yards": stat[12],
                "plays": stat[13],
                "yards_per_play": float(stat[14]) if stat[14] is not None else None,
                "completions": stat[15],
                "passing_att": stat[16],
                "completion_pct": float(stat[17]) if stat[17] is not None else None,
                "passing_tds": stat[18],
                "interceptions": stat[19],
                "sacks_taken": stat[20],
                "sack_yards_lost": stat[21],
                "qb_rating": float(stat[22]) if stat[22] is not None else None,
                "rushing_att": stat[23],
                "yards_per_carry": float(stat[24]) if stat[24] is not None else None,
                "rushing_tds": stat[25],
                "third_down_conv": stat[26],
                "third_down_att": stat[27],
                "third_down_pct": float(stat[28]) if stat[28] is not None else None,
                "fourth_down_conv": stat[29],
                "fourth_down_att": stat[30],
                "fourth_down_pct": float(stat[31]) if stat[31] is not None else None,
                "red_zone_conv": stat[32],
                "red_zone_att": stat[33],
                "red_zone_pct": float(stat[34]) if stat[34] is not None else None,
                "turnovers": stat[35],
                "fumbles_lost": stat[36],
                "penalties": stat[37],
                "penalty_yards": stat[38],
                "time_of_possession_sec": stat[39],
                "time_of_possession_pct": float(stat[40]) if stat[40] is not None else None,
                "result": stat[41],
                "epa_per_play": float(stat[42]) if stat[42] is not None else None,
                "success_rate": float(stat[43]) if stat[43] is not None else None,
                "total_epa": float(stat[44]) if stat[44] is not None else None
            })
        
        logger.info(f"Retrieved {len(stats_list)} game statistics")
        return jsonify({
            "count": len(stats_list),
            "statistics": stats_list,
            "filters": {
                "season": season,
                "week": week,
                "team": team,
                "game_id": game_id
            }
        })
    except Exception as e:
        logger.error(f"Failed to fetch game statistics: {e}")
        return jsonify({
            "error": str(e),
            "message": "Failed to fetch game statistics"
        }), 500

def run_server(host='127.0.0.1', port=5000, debug=False):
    """Run the Flask server"""
    logger.info("=" * 60)
    logger.info("H.C. LOMBARDO NFL ANALYTICS API - PRODUCTION")
    logger.info("=" * 60)
    logger.info(f"Server: http://{host}:{port}")
    logger.info(f"Process ID: {os.getpid()}")
    logger.info(f"CORS Enabled for: http://localhost:3000")
    logger.info("=" * 60)
    
    # Test database connection before starting
    try:
        logger.info("Testing database connection...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        logger.info(f"Database connected: {count} teams found")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error("Please check your PostgreSQL server and credentials")
        sys.exit(1)
    
    # Verify Flask-CORS is available
    try:
        from flask_cors import CORS
        logger.info("Flask-CORS verified")
    except ImportError:
        logger.error("Flask-CORS not installed. Run: pip install flask-cors")
        sys.exit(1)
    
    logger.info("Starting Flask server...")
    logger.info(f"Build folder: {BUILD_FOLDER}")
    if os.path.exists(BUILD_FOLDER):
        logger.info("[OK] React build folder found - serving production build")
    else:
        logger.warning("[!] React build folder not found - run 'npm run build' in frontend/")
    
    # Start background data updater
    try:
        updater.start()
        logger.info("🔄 Background NFL data updater started (updates every 30 minutes)")
    except Exception as e:
        logger.warning(f"Failed to start background updater: {e}")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        updater.stop()
        logger.info("Background updater stopped")
    except Exception as e:
        logger.error(f"Server error: {e}")
        updater.stop()
        import traceback
        traceback.print_exc()
        sys.exit(1)

# 404 Error handler for React Router
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors by serving React app (for client-side routing)"""
    # Get the requested path
    from flask import request
    path = request.path
    
    logger.info(f"404 handler: path='{path}'")
    
    # If it's an API route, return JSON error
    if path.startswith('/api/') or path.startswith('/health'):
        logger.warning(f"API route not found: {path}")
        return jsonify({"error": "Route not found", "path": path}), 404
    
    # For all other routes, serve index.html (React Router will handle it)
    logger.info(f"Serving index.html for React Router: path='{path}'")
    try:
        return send_from_directory(BUILD_FOLDER, 'index.html')
    except Exception as ex:
        logger.error(f"Error serving index.html: {ex}")
        return jsonify({"error": "Failed to load application"}), 500

# Serve React App (must be at the end, after all API routes)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React production build or index.html for client-side routing"""
    logger.info(f"Catch-all route hit: path='{path}'")
    
    # Don't intercept API routes
    if path.startswith('api/') or path.startswith('health'):
        logger.warning(f"API route in catch-all (should not happen): {path}")
        return jsonify({"error": "Route not found"}), 404
    
    # Check if it's a static file (has file extension)
    if path and '.' in path.split('/')[-1]:
        file_path = os.path.join(BUILD_FOLDER, path)
        if os.path.exists(file_path):
            logger.info(f"Serving static file: {path}")
            return send_from_directory(BUILD_FOLDER, path)
        else:
            logger.warning(f"Static file not found: {path}")
    
    # For all other routes, serve index.html (React Router handles them)
    logger.info(f"Serving index.html for React Router: path='{path}'")
    try:
        return send_from_directory(BUILD_FOLDER, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return jsonify({"error": "Failed to load application"}), 500

if __name__ == "__main__":
    run_server()
