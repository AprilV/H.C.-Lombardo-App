import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='nfl_analytics',
    user='postgres',
    password='aprilv120'
)

cursor = conn.cursor()

# Check ALL Week 12 games with day of week
print("ALL WEEK 12 GAMES (with day of week):")
cursor.execute("""
    SELECT game_id, game_date, away_team, home_team, kickoff_time_utc
    FROM hcl.games 
    WHERE season=2025 
    AND week = 12
    ORDER BY game_date, kickoff_time_utc
""")

for game in cursor.fetchall():
    date = game[1]
    day_name = datetime.strptime(str(date), '%Y-%m-%d').strftime('%A')
    print(f"  {day_name} {date} | {game[2]} @ {game[3]} | {game[0]}")

print("\n\nDALLAS THANKSGIVING GAME:")
cursor.execute("""
    SELECT game_id, game_date, away_team, home_team
    FROM hcl.games 
    WHERE season=2025 
    AND (home_team='DAL' OR away_team='DAL')
    AND game_date >= '2025-11-25'
    AND game_date <= '2025-11-28'
""")

for game in cursor.fetchall():
    date = game[1]
    day_name = datetime.strptime(str(date), '%Y-%m-%d').strftime('%A')
    print(f"  {day_name} {date} | {game[2]} @ {game[3]}")

print("\n\nNYJ GAMES Week 12:")
cursor.execute("""
    SELECT game_id, game_date, away_team, home_team
    FROM hcl.games 
    WHERE season=2025 
    AND week = 12
    AND (home_team='NYJ' OR away_team='NYJ')
""")

for game in cursor.fetchall():
    date = game[1]
    day_name = datetime.strptime(str(date), '%Y-%m-%d').strftime('%A')
    print(f"  {day_name} {date} | {game[2]} @ {game[3]}")

conn.close()
