"""
STEP 3: Flask Server with PostgreSQL Connection
Add database connectivity and test querying NFL teams
"""
from flask import Flask, jsonify
import psycopg2
import sys
import os

app = Flask(__name__)

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
        print(f"Database connection error: {e}", file=sys.stderr)
        raise

@app.route('/')
def hello():
    return jsonify({
        "message": "Flask + PostgreSQL Server",
        "status": "running",
        "database": "nfl_analytics"
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
        
        return jsonify({
            "status": "healthy",
            "port": 5002,
            "database": "connected"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "port": 5002,
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route('/teams')
def get_teams():
    """Get all NFL teams from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, abbreviation, wins, losses, ppg FROM teams ORDER BY name")
        teams = cursor.fetchall()
        cursor.close()
        conn.close()
        
        teams_list = [
            {
                "name": team[0],
                "abbreviation": team[1],
                "wins": team[2],
                "losses": team[3],
                "ppg": float(team[4]) if team[4] is not None else None
            }
            for team in teams
        ]
        
        return jsonify({
            "count": len(teams_list),
            "teams": teams_list
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to fetch teams"
        }), 500

@app.route('/teams/count')
def get_teams_count():
    """Get count of teams in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            "count": count,
            "expected": 32,
            "status": "correct" if count == 32 else "incorrect"
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

def run_server():
    """Run the server"""
    print("=" * 60, flush=True)
    print("STEP 3: FLASK + POSTGRESQL SERVER", flush=True)
    print("=" * 60, flush=True)
    print(f"Server: http://127.0.0.1:5002", flush=True)
    print(f"Process ID: {os.getpid()}", flush=True)
    print(f"\nEndpoints:", flush=True)
    print(f"  GET /            - Server info", flush=True)
    print(f"  GET /health      - Health check", flush=True)
    print(f"  GET /teams       - All teams", flush=True)
    print(f"  GET /teams/count - Team count", flush=True)
    print("=" * 60, flush=True)
    
    sys.stdout.flush()
    
    # Test database connection before starting
    try:
        print("\nTesting database connection...", flush=True)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✓ Database connected: {count} teams found\n", flush=True)
    except Exception as e:
        print(f"✗ Database connection failed: {e}", flush=True)
        print("Please check your PostgreSQL server and credentials\n", flush=True)
        sys.exit(1)
    
    try:
        app.run(
            host='127.0.0.1',
            port=5002,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n✓ Server stopped by user", flush=True)
    except Exception as e:
        print(f"\n✗ Server error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_server()
