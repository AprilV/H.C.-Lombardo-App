"""
H.C. Lombardo - Simple Web Dashboard
Displays Top 10 NFL Offense and Defense
"""
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_top_offense():
    """Get top 10 offensive teams"""
    conn = sqlite3.connect('data/nfl_teams.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, abbreviation, ppg, wins, losses 
        FROM teams 
        ORDER BY ppg DESC 
        LIMIT 10
    """)
    
    teams = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return teams

def get_top_defense():
    """Get top 10 defensive teams"""
    conn = sqlite3.connect('data/nfl_teams.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, abbreviation, pa, wins, losses 
        FROM teams 
        ORDER BY pa ASC 
        LIMIT 10
    """)
    
    teams = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return teams

@app.route('/')
def home():
    """Homepage with top 10 lists"""
    offense = get_top_offense()
    defense = get_top_defense()
    return render_template('index.html', offense=offense, defense=defense)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("H.C. LOMBARDO NFL DASHBOARD")
    print("Starting server at http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
