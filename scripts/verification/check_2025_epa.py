import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)
cur = conn.cursor()

cur.execute("""
    SELECT game_id, team, points, total_yards, epa_per_play, pass_epa, rush_epa
    FROM hcl.team_game_stats 
    WHERE season = 2025 
    LIMIT 5
""")

print("\nSample 2025 team_game_stats:")
print("game_id | team | points | yards | epa_per_play | pass_epa | rush_epa")
print("-" * 80)
for row in cur.fetchall():
    print(f"{row[0][:20]:20} | {row[1]:4} | {row[2]:6} | {row[3]:5} | {row[4]} | {row[5]} | {row[6]}")

conn.close()
