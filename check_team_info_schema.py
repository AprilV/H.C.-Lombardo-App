#!/usr/bin/env python3
"""Check team_info columns on Render"""

import psycopg2

RENDER_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

conn = psycopg2.connect(RENDER_URL)
cur = conn.cursor()

print("\n🔍 RENDER hcl.team_info schema:")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_info'
    ORDER BY ordinal_position
""")
cols = cur.fetchall()
for col, dtype in cols:
    print(f"   • {col}: {dtype}")

print("\n📋 Sample data:")
cur.execute("SELECT * FROM hcl.team_info LIMIT 3")
for row in cur.fetchall():
    print(f"   {row}")

conn.close()
