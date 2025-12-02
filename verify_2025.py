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

cur.execute('SELECT COUNT(*) FROM hcl.team_game_stats WHERE season = 2025 AND epa_per_play IS NOT NULL')
epa = cur.fetchone()[0]

cur.execute('SELECT team, COUNT(*) as games FROM hcl.team_game_stats WHERE season = 2025 GROUP BY team ORDER BY team LIMIT 10')
teams = cur.fetchall()

print(f'\n✅ 2025 DATA VERIFICATION')
print(f'   Stats with EPA: {epa}')
print(f'\n   Sample teams:')
for team, count in teams:
    print(f'   {team}: {count} games')

conn.close()
