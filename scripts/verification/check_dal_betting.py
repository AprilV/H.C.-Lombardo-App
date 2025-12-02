import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_connection_string

conn = psycopg2.connect(get_connection_string())
cur = conn.cursor(cursor_factory=RealDictCursor)

print("DAL betting performance data:")
cur.execute("SELECT * FROM hcl.v_team_betting_performance WHERE team='DAL' AND season=2025")
row = cur.fetchone()
if row:
    for k, v in row.items():
        print(f"  {k:30} = {v}")
else:
    print("No data found for DAL")

cur.close()
conn.close()
