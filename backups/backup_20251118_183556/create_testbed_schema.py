#!/usr/bin/env python3
"""
Quick script to create testbed schema
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Read SQL file
with open('testbed_hcl_schema.sql', 'r') as f:
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
        cur.execute(sql)
        conn.commit()
    print("✓ Testbed schema created successfully!")
except Exception as e:
    print(f"✗ Error creating schema: {e}")
    conn.rollback()
finally:
    conn.close()
