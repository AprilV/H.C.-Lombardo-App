import psycopg2

# LOCAL
conn = psycopg2.connect(dbname='nfl_analytics', user='postgres', password='aprilv120', host='localhost')
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='hcl' ORDER BY table_name")
local_tables = [r[0] for r in cur.fetchall()]
conn.close()

# RENDER  
conn = psycopg2.connect(dbname='nfl_analytics', user='nfl_user', password='rzkKyzQq9pTas14pXDJU3fm8cCZObAh5', host='dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com')
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='hcl' ORDER BY table_name")
render_tables = [r[0] for r in cur.fetchall()]
conn.close()

print(f"\nLOCAL tables:  {local_tables}")
print(f"RENDER tables: {render_tables}")
print(f"\nMissing on Render: {set(local_tables) - set(render_tables)}")
