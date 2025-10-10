"""
H.C. Lombardo NFL Analytics - Production API Server
Flask + PostgreSQL + CORS for React frontend
Based on tested step-by-step methodology
"""
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import sys
import os
from logging_config import setup_logging

# Initialize logger
loggers = setup_logging()
logger = loggers['api']

app = Flask(__name__)

# Enable CORS for React frontend and local HTML files
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "null"],  # "null" allows file:// protocol
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

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

@app.route('/')
def index():
    """API root endpoint"""
    logger.info("API root endpoint accessed")
    return jsonify({
        "app": "H.C. Lombardo NFL Analytics API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "teams": "/api/teams",
            "teams_count": "/api/teams/count"
        }
    })

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
            SELECT name, abbreviation, wins, losses, ppg, pa, games_played 
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
                "ppg": float(team[4]) if team[4] is not None else None,
                "pa": float(team[5]) if team[5] is not None else None,
                "games_played": team[6]
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
            SELECT name, abbreviation, wins, losses, ppg, pa, games_played 
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
                "ppg": float(team[4]) if team[4] is not None else None,
                "pa": float(team[5]) if team[5] is not None else None,
                "games_played": team[6]
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

if __name__ == "__main__":
    run_server()
