import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT', '5432')
)

cur = conn.cursor()

# Check columns
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats' 
    ORDER BY ordinal_position
""")
cols = [row[0] for row in cur.fetchall()]
print('team_game_stats columns:')
print(', '.join(cols))

# Check 2025 count
cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats WHERE season = 2025")
count = cur.fetchone()[0]
print(f'\n2025 records in team_game_stats: {count}')

# Check Week 13 data
cur.execute("""
    SELECT team, week, points, total_yards, turnovers, pass_epa, rush_epa
    FROM hcl.team_game_stats 
    WHERE season = 2025 AND week = 13 
    LIMIT 5
""")
print('\nWeek 13 sample data:')
for row in cur.fetchall():
    print(f'  {row[0]} Week {row[1]}: {row[2]} pts, {row[3]} yds, {row[4]} TO, pass_epa={row[5]}, rush_epa={row[6]}')

conn.close()
