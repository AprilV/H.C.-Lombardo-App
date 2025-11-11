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
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema='hcl' 
      AND table_name='team_game_stats' 
    ORDER BY ordinal_position
""")

print("Columns in hcl.team_game_stats:")
print("="*50)
for row in cur.fetchall():
    print(row[0])

cur.close()
conn.close()
