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

# Check Week 13 EPA data
cur.execute('''
    SELECT team, week, epa_per_play, pass_epa, rush_epa 
    FROM hcl.team_game_stats 
    WHERE season = 2025 AND week = 13 
    ORDER BY team 
    LIMIT 10
''')

rows = cur.fetchall()
print(f'\nWeek 13 2025 - First 10 teams:')
print(f'Total teams: {len(rows)}')

for row in rows:
    epa = row[2] if row[2] is not None else 'NULL'
    pass_epa = row[3] if row[3] is not None else 'NULL'
    rush_epa = row[4] if row[4] is not None else 'NULL'
    print(f'  {row[0]} Week {row[1]}: epa={epa}, pass_epa={pass_epa}, rush_epa={rush_epa}')

conn.close()
