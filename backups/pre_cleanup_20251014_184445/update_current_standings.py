"""
Quick update script for current NFL standings (Oct 10, 2025)
Updates wins/losses with actual current records including tonight's games
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Current standings as of Oct 10, 2025 (after Giants beat Eagles)
CURRENT_RECORDS = {
    # NFC East
    'WAS': (4, 1),  # Washington Commanders
    'PHI': (4, 2),  # Philadelphia Eagles (LOST tonight)
    'DAL': (3, 2),  # Dallas Cowboys
    'NYG': (2, 4),  # New York Giants (WON tonight)
    
    # NFC North
    'DET': (4, 1),  # Detroit Lions
    'MIN': (5, 0),  # Minnesota Vikings
    'GB': (4, 2),   # Green Bay Packers
    'CHI': (4, 2),  # Chicago Bears
    
    # NFC South
    'TB': (4, 2),   # Tampa Bay Buccaneers
    'ATL': (4, 2),  # Atlanta Falcons
    'NO': (2, 4),   # New Orleans Saints
    'CAR': (1, 5),  # Carolina Panthers
    
    # NFC West
    'SEA': (4, 2),  # Seattle Seahawks
    'SF': (3, 3),   # San Francisco 49ers
    'ARI': (2, 4),  # Arizona Cardinals
    'LAR': (2, 4),  # Los Angeles Rams
    
    # AFC East
    'BUF': (4, 2),  # Buffalo Bills
    'NYJ': (2, 4),  # New York Jets
    'MIA': (2, 3),  # Miami Dolphins
    'NE': (1, 5),   # New England Patriots
    
    # AFC North
    'PIT': (4, 2),  # Pittsburgh Steelers
    'BAL': (4, 2),  # Baltimore Ravens
    'CLE': (1, 5),  # Cleveland Browns
    'CIN': (1, 4),  # Cincinnati Bengals
    
    # AFC South
    'HOU': (5, 1),  # Houston Texans
    'IND': (3, 3),  # Indianapolis Colts
    'TEN': (1, 4),  # Tennessee Titans
    'JAX': (1, 5),  # Jacksonville Jaguars
    
    # AFC West
    'KC': (5, 0),   # Kansas City Chiefs
    'DEN': (3, 3),  # Denver Broncos
    'LV': (2, 4),   # Las Vegas Raiders
    'LAC': (2, 3),  # Los Angeles Chargers (missing from original data)
}

def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'aprilv120')
    )

def update_standings():
    """Update team records with current standings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("UPDATING NFL STANDINGS - October 10, 2025")
    print("Including: Giants 2-4 (beat Eagles tonight)")
    print("="*70 + "\n")
    
    updated_count = 0
    for abbr, (wins, losses) in CURRENT_RECORDS.items():
        games_played = wins + losses
        cursor.execute("""
            UPDATE teams 
            SET wins = %s, losses = %s, games_played = %s
            WHERE abbreviation = %s
        """, (wins, losses, games_played, abbr))
        
        if cursor.rowcount > 0:
            updated_count += 1
            cursor.execute("SELECT name FROM teams WHERE abbreviation = %s", (abbr,))
            team_name = cursor.fetchone()
            if team_name:
                print(f"✅ {team_name[0]:30s} {abbr:3s}  {wins}-{losses}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*70}")
    print(f"✅ Updated {updated_count} teams with current standings")
    print(f"{'='*70}\n")
    
    # Verify Giants and Eagles
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, wins, losses, games_played 
        FROM teams 
        WHERE abbreviation IN ('NYG', 'PHI')
        ORDER BY name
    """)
    
    print("🏈 Tonight's Game Verification:")
    print("="*70)
    for row in cursor.fetchall():
        print(f"  {row[0]:30s}  {row[1]}-{row[2]} ({row[3]} games)")
    print()
    
    conn.close()

if __name__ == "__main__":
    update_standings()
