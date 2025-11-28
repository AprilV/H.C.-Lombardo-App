import psycopg2

# LOCAL database
print("LOCAL DATABASE (hcl.team_game_stats) columns:")
conn = psycopg2.connect(dbname='nfl_analytics', user='postgres', password='aprilv120', host='localhost')
cur = conn.cursor()
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats' 
    ORDER BY ordinal_position
""")
for col, dtype in cur.fetchall():
    print(f"  {col}: {dtype}")
conn.close()
