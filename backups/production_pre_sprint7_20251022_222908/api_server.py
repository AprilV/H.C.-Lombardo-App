"""
H.C. Lombardo NFL Analytics - Production API Server
Flask + PostgreSQL + CORS for React frontend
Serves both API endpoints and production React build
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import sys
import os
from logging_config import setup_logging
from dashboard_api import register_dashboard_routes

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
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000", "http://127.0.0.1:5000", "null"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Register dashboard API routes
register_dashboard_routes(app)

# Additional CORS headers for file:// protocol
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    return response

# Database configuration
DB_CONFIG = {
    'dbname': 'nfl_analytics',
    'user': 'postgres',
    'password': 'aprilv120',
    'host': 'localhost',
    'port': 5432
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
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Serve React App (must be at the end, after all API routes)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React production build or index.html for client-side routing"""
    if path != "" and os.path.exists(os.path.join(BUILD_FOLDER, path)):
        # Serve static file (JS, CSS, images, etc.)
        return send_from_directory(BUILD_FOLDER, path)
    else:
        # Serve index.html for all other routes (React Router handles them)
        return send_from_directory(BUILD_FOLDER, 'index.html')

if __name__ == "__main__":
    run_server()
