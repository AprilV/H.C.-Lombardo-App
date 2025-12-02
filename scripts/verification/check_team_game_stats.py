import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)

cur = conn.cursor(cursor_factory=RealDictCursor)

query = """
SELECT game_id, week, team, opponent, 
       passing_yards, rushing_yards, total_yards
FROM hcl.team_game_stats
WHERE team = 'NE' AND season = 2025
ORDER BY week
"""

cur.execute(query)
rows = cur.fetchall()

print("NE 2025 Data in hcl.team_game_stats:\n")
for row in rows:
    print(f"Week {row['week']:2d}: Pass={row['passing_yards'] or 'NULL':>7}, Rush={row['rushing_yards'] or 'NULL':>7}, Total={row['total_yards'] or 'NULL':>7}")

cur.close()
conn.close()
