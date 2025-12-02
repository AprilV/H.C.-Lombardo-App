"""Quick check - count total NULL fields per team"""
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

# Get one row to count total NULLs
cur.execute("""
    SELECT * FROM hcl.team_game_stats
    WHERE season = 2025 AND week = 13 AND team = 'KC'
""")
row = cur.fetchone()

cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' 
    AND table_name = 'team_game_stats'
    ORDER BY ordinal_position
""")
columns = [r[0] for r in cur.fetchall()]

null_count = sum(1 for val in row if val is None)
populated_count = len(row) - null_count

print(f"\n✅ KC Week 13: {populated_count}/{len(columns)} fields populated ({null_count} NULL)")
print(f"\n64 total columns in database")
print(f"{populated_count} have data")
print(f"{null_count} are NULL")

if null_count == 0:
    print("\n🎉 PERFECT - ALL 64 STATS ARE POPULATED!")
else:
    # Show which are NULL
    null_fields = [columns[i] for i, val in enumerate(row) if val is None]
    print(f"\nNULL fields: {', '.join(null_fields)}")

conn.close()
