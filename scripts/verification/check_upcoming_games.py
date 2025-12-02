"""Check upcoming games in database vs actual NFL schedule"""
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, date

load_dotenv()

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password=os.getenv('DB_PASSWORD'),
    host='localhost'
)

cur = conn.cursor()

# Get upcoming games (from Nov 18 onwards)
cur.execute("""
    SELECT game_id, game_date, week, home_team, away_team, kickoff_time_utc
    FROM hcl.games 
    WHERE season=2025 AND game_date >= '2025-11-18'
    ORDER BY game_date, kickoff_time_utc
    LIMIT 20
""")

print("\n" + "="*80)
print("UPCOMING GAMES IN DATABASE (from Nov 18, 2025 onwards)")
print("="*80)
print(f"{'Week':<6} {'Date':<12} {'Kickoff':<10} {'Matchup':<35}")
print("-"*80)

rows = cur.fetchall()
for row in rows:
    game_id, game_date, week, home_team, away_team, kickoff = row
    matchup = f"{away_team} @ {home_team}"
    kickoff_str = str(kickoff)[:5] if kickoff else "TBD"
    print(f"{week:<6} {str(game_date):<12} {kickoff_str:<10} {matchup:<35}")

print("\n" + "="*80)
print("ACTUAL NFL SCHEDULE - Week 12 (Nov 21-25, 2025)")
print("="*80)
print("Thursday, Nov 21: CLE @ PIT")
print("Sunday, Nov 24:")
print("  - Multiple games at 1:00 PM ET")
print("  - DAL @ WAS (4:25 PM ET)")
print("  - PHI @ LA (8:20 PM ET)")
print("Monday, Nov 25: HOU @ DAL")
print("="*80)

# Now check what the API is returning
print("\n" + "="*80)
print("CHECKING WHAT /api/ml/predict-upcoming RETURNS")
print("="*80)

cur.execute("""
    SELECT game_id, game_date, week, home_team, away_team
    FROM hcl.games 
    WHERE season=2025 
    ORDER BY game_date DESC
    LIMIT 10
""")

print("\nMost recent games in database:")
print(f"{'Week':<6} {'Date':<12} {'Matchup':<35}")
print("-"*80)

for row in cur.fetchall():
    game_id, game_date, week, home_team, away_team = row
    matchup = f"{away_team} @ {home_team}"
    print(f"{week:<6} {str(game_date):<12} {matchup:<35}")

cur.close()
conn.close()

print("\n" + "="*80)
print("DIAGNOSIS")
print("="*80)
print("Current date: November 18, 2025")
print("Expected to see: Week 12 games (Nov 21-25)")
print("Actually seeing: ???")
print("\nNext step: Check what the predict-upcoming API endpoint returns")
print("="*80)
