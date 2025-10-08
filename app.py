"""
H.C. Lombardo - NFL Analytics Dashboard
Displays All 32 NFL Teams with Auto-Refresh from TeamRankings.com
Updates data automatically every 24 hours
"""
from flask import Flask, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)

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
            return True  # No metadata, need refresh
        
        # Get last update time
        cursor.execute("SELECT last_update FROM update_metadata ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return True
        
        last_update = result[0]
        time_diff = datetime.now() - last_update
        
        # Refresh if older than 24 hours
        return time_diff > timedelta(hours=24)
        
    except Exception as e:
        print(f"⚠️  Error checking data age: {e}")
        return False

def refresh_data_if_needed():
    """Refresh data from TeamRankings if needed"""
    if should_refresh_data():
        print("\n🔄 Data is stale (>24 hours old), refreshing from TeamRankings.com...")
        try:
            from scrape_teamrankings import update_database
            success = update_database()
            if success:
                print("✅ Data refreshed successfully!")
            else:
                print("⚠️  Data refresh failed, using existing data")
        except Exception as e:
            print(f"⚠️  Error during refresh: {e}")
    else:
        print("✅ Data is fresh (<24 hours old), no refresh needed")

def get_top_offense():
    """Get all offensive teams sorted by PPG"""
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
    
    return teams

def get_top_defense():
    """Get all defensive teams sorted by PA"""
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
    
    return teams

@app.route('/')
def home():
    """Homepage with all 32 teams"""
    # Check if data needs refresh (24-hour check)
    refresh_data_if_needed()
    
    offense = get_top_offense()
    defense = get_top_defense()
    
    # Debug: print first team to verify logo URL
    if offense:
        print(f"\n🔍 DEBUG - First offense team: {offense[0]['name']}")
        print(f"   Abbreviation: {offense[0]['abbreviation']}")
        print(f"   Logo URL: {offense[0].get('logo', 'NO LOGO')}\n")
    
    return render_template('index.html', offense=offense, defense=defense)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("H.C. LOMBARDO NFL DASHBOARD")
    print("Starting server at http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
