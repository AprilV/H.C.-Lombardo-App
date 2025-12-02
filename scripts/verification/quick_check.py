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
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema='hcl' AND table_name='team_game_stats' 
    ORDER BY ordinal_position
""")
cols = [r[0] for r in cur.fetchall()]

print(f"\n✅ team_game_stats has {len(cols)} columns\n")

epa_cols = [c for c in cols if 'epa' in c.lower() or 'cpoe' in c.lower() or 'wpa' in c.lower()]
print(f"EPA-related columns: {epa_cols if epa_cols else '❌ NONE!'}\n")

conn.close()
