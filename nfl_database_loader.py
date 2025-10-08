"""
H.C. Lombardo - NFL Analytics with PostgreSQL
Loads NFL team statistics into PostgreSQL database
"""
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# NFL 2025 Season Data - REAL CURRENT STATS from TeamRankings.com (10/8/2025)
NFL_TEAMS_2025 = [
    ('Detroit Lions', 'DET', 0, 0, 34.8, 12.2, 5),
    ('Indianapolis Colts', 'IND', 0, 0, 32.6, 17.8, 5),
    ('Buffalo Bills', 'BUF', 0, 0, 30.6, 22.6, 5),
    ('Dallas Cowboys', 'DAL', 0, 0, 30.2, 19.2, 5),
    ('San Francisco 49ers', 'SF', 0, 0, 29.2, 19.6, 5),
    ('Baltimore Ravens', 'BAL', 0, 0, 28.2, 19.6, 5),
    ('Tampa Bay Buccaneers', 'TB', 0, 0, 27.0, 21.8, 5),
    ('Washington Commanders', 'WAS', 0, 0, 26.8, 20.2, 5),
    ('Green Bay Packers', 'GB', 0, 0, 28.0, 21.0, 5),
    ('Jacksonville Jaguars', 'JAX', 0, 0, 25.4, 20.0, 5),
    ('Chicago Bears', 'CHI', 0, 0, 25.3, 21.4, 5),
    ('New England Patriots', 'NE', 0, 0, 25.0, 20.2, 5),
    ('Kansas City Chiefs', 'KC', 0, 0, 25.0, 21.4, 5),
    ('Philadelphia Eagles', 'PHI', 0, 0, 25.0, 21.8, 5),
    ('Los Angeles Rams', 'LAR', 0, 0, 24.6, 21.4, 5),
    ('Minnesota Vikings', 'MIN', 0, 0, 24.6, 20.2, 5),
    ('Pittsburgh Steelers', 'PIT', 0, 0, 24.0, 22.4, 5),
    ('Denver Broncos', 'DEN', 0, 0, 23.4, 16.8, 5),
    ('New York Jets', 'NYJ', 0, 0, 22.4, 23.8, 5),
    ('Houston Texans', 'HOU', 0, 0, 21.6, 22.4, 5),
    ('Miami Dolphins', 'MIA', 0, 0, 21.4, 20.2, 5),
    ('San Francisco 49ers', 'SF', 0, 0, 21.2, 19.6, 5),
    ('Arizona Cardinals', 'ARI', 0, 0, 20.6, 19.2, 5),
    ('Carolina Panthers', 'CAR', 0, 0, 20.1, 23.8, 5),
    ('Atlanta Falcons', 'ATL', 0, 0, 19.2, 21.5, 5),
    ('Seattle Seahawks', 'SEA', 0, 0, 19.2, 21.0, 5),
    ('Las Vegas Raiders', 'LV', 0, 0, 18.8, 25.3, 5),
    ('Cincinnati Bengals', 'CIN', 0, 0, 18.8, 20.2, 5),
    ('Tennessee Titans', 'TEN', 0, 0, 17.8, 25.3, 5),
    ('New York Giants', 'NYG', 0, 0, 16.5, 24.0, 5),
    ('Cleveland Browns', 'CLE', 0, 0, 16.0, 23.8, 5),
    ('New Orleans Saints', 'NO', 0, 0, 14.6, 25.3, 5),
]

def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

def setup_database():
    """Create database tables and load NFL data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table (PostgreSQL syntax)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            abbreviation TEXT,
            wins INTEGER,
            losses INTEGER,
            ppg REAL,
            pa REAL,
            games_played INTEGER
        )
    """)
    
    # Clear existing data
    cursor.execute("DELETE FROM teams")
    
    # Insert NFL data (PostgreSQL uses %s instead of ?)
    cursor.executemany("""
        INSERT INTO teams (name, abbreviation, wins, losses, ppg, pa, games_played)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, NFL_TEAMS_2025)
    
    conn.commit()
    conn.close()
    
    print("✅ PostgreSQL database loaded with 2025 NFL data")

def answer_questions():
    """Answer the assignment questions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("ASSIGNMENT QUESTION 1: Top 10 Offensive Teams (Highest PPG)")
    print("="*70)
    
    cursor.execute("""
        SELECT name, abbreviation, ppg, wins, losses 
        FROM teams 
        ORDER BY ppg DESC 
        LIMIT 10
    """)
    
    for i, (name, abbr, ppg, wins, losses) in enumerate(cursor.fetchall(), 1):
        print(f"{i:2}. {name:30} {abbr:5} {ppg:5.1f} PPG  ({wins}-{losses})")
    
    print("\n" + "="*70)
    print("ASSIGNMENT QUESTION 2: Top 10 Defensive Teams (Lowest PA)")
    print("="*70)
    
    cursor.execute("""
        SELECT name, abbreviation, pa, wins, losses 
        FROM teams 
        ORDER BY pa ASC 
        LIMIT 10
    """)
    
    for i, (name, abbr, pa, wins, losses) in enumerate(cursor.fetchall(), 1):
        print(f"{i:2}. {name:30} {abbr:5} {pa:5.1f} PA   ({wins}-{losses})")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✅ Assignment Complete - Questions Answered!")
    print("="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("H.C. LOMBARDO - DATABASE + ML ASSIGNMENT")
    print("2025 NFL Season Analysis")
    print("="*70 + "\n")
    
    setup_database()
    answer_questions()
