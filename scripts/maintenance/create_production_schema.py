#!/usr/bin/env python3
"""
Create production HCL schema
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("PRODUCTION SCHEMA CREATION")
print("=" * 80)

# Read SQL file
with open('production_hcl_schema.sql', 'r') as f:
    sql = f.read()

# Connect and execute
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

try:
    with conn.cursor() as cur:
        # Execute full schema
        cur.execute(sql)
        
        # Verify tables created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'hcl'
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        print("✓ Production schema 'hcl' created")
        print("\nTables created:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Verify materialized view
        cur.execute("""
            SELECT matviewname 
            FROM pg_matviews 
            WHERE schemaname = 'hcl'
        """)
        views = cur.fetchall()
        
        if views:
            print("\nMaterialized views created:")
            for view in views:
                print(f"  - {view[0]}")
    
    conn.commit()
    print("\n✓ Production schema ready for data load")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    raise
finally:
    conn.close()

print("=" * 80)
print("SCHEMA CREATION COMPLETE")
print("=" * 80)
