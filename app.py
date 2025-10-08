"""
H.C. Lombardo - NFL Analytics Dashboard
Displays Top 10 NFL Offense and Defense using PostgreSQL
"""
from flask import Flask, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

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
