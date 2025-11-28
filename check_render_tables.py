#!/usr/bin/env python3
"""Check what tables exist in Render HCL schema"""

import psycopg2

RENDER_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

conn = psycopg2.connect(RENDER_URL)
cur = conn.cursor()

print("\n" + "="*80)
print("📊 RENDER DATABASE TABLES")
print("="*80)

# Check HCL schema tables
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'hcl'
    ORDER BY table_name
""")
hcl_tables = [row[0] for row in cur.fetchall()]

print(f"\n🗂️  HCL Schema Tables ({len(hcl_tables)}):")
for table in hcl_tables:
    cur.execute(f"SELECT COUNT(*) FROM hcl.{table}")
    count = cur.fetchone()[0]
    print(f"   • {table}: {count:,} rows")

# Check if team_info exists locally
print("\n🔍 Checking local database for team_info...")
local_conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password='aprilv120',
    host='localhost',
    port='5432'
)
local_cur = local_conn.cursor()

local_cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'hcl' AND table_name = 'team_info'
""")
if local_cur.fetchone():
    print("   ✅ team_info exists in local database")
    local_cur.execute("SELECT COUNT(*) FROM hcl.team_info")
    count = local_cur.fetchone()[0]
    print(f"   • Records: {count}")
    
    # Get schema
    local_cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'hcl' AND table_name = 'team_info'
        ORDER BY ordinal_position
    """)
    print("\n   Columns:")
    for col, dtype in local_cur.fetchall():
        print(f"      - {col}: {dtype}")
else:
    print("   ❌ team_info does NOT exist in local database")

local_conn.close()
conn.close()
print("="*80 + "\n")
