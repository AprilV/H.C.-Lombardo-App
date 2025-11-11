"""
H.C. Lombardo - NFL Analytics Dashboard
Displays All 32 NFL Teams with Auto-Refresh from TeamRankings.com
Updates data automatically every 24 hours
"""
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import sys
from datetime import datetime, timedelta
from logging_config import setup_logging, log_activity

# Load environment variables
load_dotenv()

# Initialize logging
loggers = setup_logging()

app = Flask(__name__)
CORS(app)  # Enable CORS for React dev server

# Register HCL API blueprint for historical data
from api_routes_hcl import hcl_bp
app.register_blueprint(hcl_bp)

# Register ML API blueprint for predictions
from api_routes_ml import ml_api
app.register_blueprint(ml_api)

# Log application startup
log_activity('app', 'info', 'Flask application starting', 
            version='2.0', database='PostgreSQL', features='auto-refresh,logos,all-teams')

def get_espn_logo_url(abbreviation):
    """Generate ESPN CDN logo URL from team abbreviation"""
    # ESPN uses lowercase abbreviations
    abbr_lower = abbreviation.lower()
    return f"https://a.espncdn.com/i/teamlogos/nfl/500/{abbr_lower}.png"

def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

def should_refresh_data():
    """Check if data needs refresh (older than 24 hours)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if metadata table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'update_metadata'
            )
        """)
        
        if not cursor.fetchone()[0]:
            conn.close()
            log_activity('database', 'warning', 'Update metadata table not found', action='should_refresh_data')
            return True  # No metadata, need refresh
        
        # Get last update time
        cursor.execute("SELECT last_update FROM update_metadata ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            log_activity('database', 'warning', 'No update metadata found', action='should_refresh_data')
            return True
        
        last_update = result[0]
        time_diff = datetime.now() - last_update
        hours_old = time_diff.total_seconds() / 3600
        
        log_activity('database', 'info', 'Checked data age', 
                    last_update=last_update.strftime('%Y-%m-%d %H:%M:%S'), 
                    hours_old=round(hours_old, 2))
        
        # Refresh if older than 24 hours
        return time_diff > timedelta(hours=24)
        
    except Exception as e:
        log_activity('database', 'error', f'Error checking data age: {e}', action='should_refresh_data')
        return False

def refresh_data_if_needed():
    """Refresh data from TeamRankings if needed"""
    if should_refresh_data():
        log_activity('scraper', 'info', 'Starting data refresh - data is stale', threshold_hours=24)
        try:
            from scrape_teamrankings import update_database
            success = update_database()
            if success:
                log_activity('scraper', 'info', 'Data refresh completed successfully', source='TeamRankings.com')
            else:
                log_activity('scraper', 'warning', 'Data refresh failed, using existing data', source='TeamRankings.com')
        except Exception as e:
            log_activity('scraper', 'error', f'Error during refresh: {e}', source='TeamRankings.com')
    else:
        log_activity('scraper', 'info', 'Data is fresh, no refresh needed', threshold_hours=24)

def get_top_offense():
    """Get all offensive teams sorted by PPG"""
    log_activity('database', 'info', 'Fetching offensive rankings', action='get_top_offense')
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT name, abbreviation, ppg, wins, losses 
        FROM teams 
        ORDER BY ppg DESC
    """)
    
    teams = cursor.fetchall()
    conn.close()
    
    # Add logo URLs to each team
    for team in teams:
        team['logo'] = get_espn_logo_url(team['abbreviation'])
    
    log_activity('database', 'info', 'Offensive rankings retrieved', 
                teams_count=len(teams), top_team=teams[0]['name'] if teams else 'None')
    
    return teams

def get_top_defense():
    """Get all defensive teams sorted by PA"""
    log_activity('database', 'info', 'Fetching defensive rankings', action='get_top_defense')
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT name, abbreviation, pa, wins, losses 
        FROM teams 
        ORDER BY pa ASC
    """)
    
    teams = cursor.fetchall()
    conn.close()
    
    # Add logo URLs to each team
    for team in teams:
        team['logo'] = get_espn_logo_url(team['abbreviation'])
    
    log_activity('database', 'info', 'Defensive rankings retrieved', 
                teams_count=len(teams), top_team=teams[0]['name'] if teams else 'None')
    
    return teams

# API Routes for React frontend
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
            "database": "connected",
            "cors": "enabled"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route('/api/teams')
def api_get_teams():
    """Get all NFL teams from database as JSON"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT name, abbreviation, wins, losses, ties, ppg, pa, games_played, last_updated 
            FROM teams 
            ORDER BY name
        """)
        teams = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Add logo URLs
        for team in teams:
            team['logo'] = get_espn_logo_url(team['abbreviation'])
        
        return jsonify({"teams": teams, "count": len(teams)})
    except Exception as e:
        log_activity('api', 'error', f'Failed to get teams: {e}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams/<abbreviation>')
def api_get_team_details(abbreviation):
    """Get detailed stats for a specific team"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get team details with stats
        cursor.execute("""
            SELECT t.*, 
                   COALESCE(t.ppg, 0) as points_per_game,
                   COALESCE(t.pa, 0) as points_against,
                   COALESCE(t.wins, 0) as wins,
                   COALESCE(t.losses, 0) as losses,
                   COALESCE(t.ties, 0) as ties,
                   NOW() as last_updated
            FROM teams t
            WHERE UPPER(t.abbreviation) = UPPER(%s)
        """, (abbreviation,))
        
        team = cursor.fetchone()
        
        if not team:
            cursor.close()
            conn.close()
            return jsonify({"error": "Team not found"}), 404
        
        # Add logo URL
        team['logo'] = get_espn_logo_url(team['abbreviation'])
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "team": dict(team)})
    except Exception as e:
        log_activity('api', 'error', f'Failed to get team {abbreviation}: {e}')
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    """Homepage with all 32 teams"""
    log_activity('app', 'info', 'Homepage accessed', route='/', user_agent='browser')
    
    # Check if data needs refresh (24-hour check)
    refresh_data_if_needed()
    
    offense = get_top_offense()
    defense = get_top_defense()
    
    log_activity('app', 'info', 'Homepage data prepared', 
                offense_teams=len(offense), defense_teams=len(defense))
    
    return render_template('index.html', offense=offense, defense=defense)

@app.route('/team/<team_abbr>')
def team_detail(team_abbr):
    """Team detail page with historical stats"""
    log_activity('app', 'info', f'Team detail accessed: {team_abbr}', route='/team/<team_abbr>')
    return render_template('team_detail.html', team_abbr=team_abbr.upper())

@app.route('/ml-test')
def ml_test():
    """ML Predictions test page"""
    log_activity('app', 'info', 'ML test page accessed', route='/ml-test')
    return render_template('ml_test.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory('frontend/build', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    log_activity('app', 'info', 'Starting H.C. Lombardo NFL Dashboard', 
                host='127.0.0.1', port=5000, debug=True)
    
    print("\n" + "="*60)
    print("H.C. LOMBARDO NFL DASHBOARD")
    print("Starting server at http://127.0.0.1:5000")
    print("All activity logged to logs/ directory")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
