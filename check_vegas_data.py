"""Quick check of Vegas spread data availability"""
import psycopg2
import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("\n=== CHECKING DATABASE ===")
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    database=os.getenv('DB_NAME', 'postgres'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
    port=os.getenv('DB_PORT', '5432')
)
cur = conn.cursor()

cur.execute("""
    SELECT 
        COUNT(*) as total_games,
        COUNT(spread_line) as with_spread_line,
        COUNT(total_line) as with_total_line
    FROM hcl.games 
    WHERE season = 2024 AND week = 16
""")
row = cur.fetchone()
print(f"2024 Week 16 in database:")
print(f"  Total games: {row[0]}")
print(f"  With spread_line: {row[1]}")
print(f"  With total_line: {row[2]}")

cur.execute("""
    SELECT away_team, home_team, spread_line, total_line
    FROM hcl.games 
    WHERE season = 2024 AND week = 16
    ORDER BY game_date
    LIMIT 3
""")
print("\nSample games:")
for r in cur.fetchall():
    print(f"  {r[0]} @ {r[1]}: spread_line={r[2]}, total_line={r[3]}")

conn.close()
