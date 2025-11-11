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
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'hcl'
    AND table_name = 'games'
    ORDER BY ordinal_position;
""")

print("\nhcl.games columns:")
for row in cur.fetchall():
    print(f"  - {row[0]}: {row[1]}")

conn.close()
