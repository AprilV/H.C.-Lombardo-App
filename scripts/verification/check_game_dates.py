"""Quick script to check game_date values in database"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password=os.getenv('DB_PASSWORD'),
    host='localhost'
)

cur = conn.cursor()

# Check upcoming games
cur.execute("""
    SELECT game_id, game_date, week, home_team, away_team 
    FROM hcl.games 
    WHERE season=2025 AND week IN (11, 12)
    ORDER BY game_date 
    LIMIT 15
""")

print("\n=== Upcoming Games in Database ===")
print(f"{'Game ID':<15} {'Date':<12} {'Week':<6} {'Matchup':<30}")
print("-" * 70)

for row in cur.fetchall():
    game_id, game_date, week, home_team, away_team = row
    matchup = f"{away_team} @ {home_team}"
    print(f"{game_id:<15} {str(game_date):<12} {week:<6} {matchup:<30}")

cur.close()
conn.close()

print("\n✅ Current date: November 18, 2025")
print("Question: Are these dates correct for upcoming NFL games?")
