"""Check Week 14 schedule"""
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT', '5432')
)

cur = conn.cursor()

cur.execute("""
    SELECT game_id, game_date, home_team, away_team
    FROM hcl.games
    WHERE season = 2025 AND week = 14
    ORDER BY game_date
""")

week14_games = cur.fetchall()

print("\nWEEK 14 SCHEDULE (2025):")
print("="*80)
for game in week14_games:
    game_id, date, home, away = game
    print(f"{date} - {away} @ {home}")

print(f"\n{len(week14_games)} games scheduled for Week 14")
print(f"First game: {week14_games[0][1]}")
print(f"Today: {datetime.now().strftime('%Y-%m-%d')}")

conn.close()
