import psycopg2

RENDER_DB_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

conn = psycopg2.connect(RENDER_DB_URL)
cur = conn.cursor()

print("RENDER hcl.games columns:")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'games' 
    ORDER BY ordinal_position
""")
for col, dtype in cur.fetchall():
    print(f"  {col}: {dtype}")

print("\nRENDER hcl.team_game_stats columns:")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats' 
    ORDER BY ordinal_position
""")
for col, dtype in cur.fetchall():
    print(f"  {col}: {dtype}")

conn.close()
