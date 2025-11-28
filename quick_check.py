import psycopg2

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='nfl_user', 
    password='rzkKyzQq9pTas14pXDJU3fm8cCZObAh5',
    host='dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com'
)
cur = conn.cursor()

cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema='hcl' AND table_name='team_game_stats' 
    ORDER BY ordinal_position
""")
cols = [r[0] for r in cur.fetchall()]

print(f"\n✅ RENDER team_game_stats has {len(cols)} columns\n")

epa_cols = [c for c in cols if 'epa' in c.lower() or 'cpoe' in c.lower() or 'wpa' in c.lower()]
print(f"EPA-related columns: {epa_cols if epa_cols else '❌ NONE!'}\n")

conn.close()
