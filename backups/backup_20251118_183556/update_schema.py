#!/usr/bin/env python3
"""
Update testbed schema to add betting/weather/context columns
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Read SQL file
with open('update_testbed_schema_betting.sql', 'r') as f:
    sql = f.read()

# Connect and execute
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )
    
    with conn.cursor() as cur:
        cur.execute(sql)
        
        # Fetch verification results
        results = cur.fetchall()
        for row in results:
            print(row)
    
    conn.commit()
    print("\n✓ Schema update complete!")
    print("✓ 23 new columns added to hcl_test.games table")
    
except Exception as e:
    print(f"Error: {e}")
    raise
finally:
    if conn:
        conn.close()
