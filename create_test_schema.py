#!/usr/bin/env python3
"""
Create test schema on database using existing credentials.
"""
import psycopg2
from db_config import DATABASE_CONFIG

def create_test_schema():
    """Execute testbed_hcl_schema.sql to create test schema"""
    try:
        # Connect using existing config
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        
        # Read and execute schema SQL
        with open('testbed_hcl_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Test schema (hcl_test) created successfully")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating test schema: {e}")
        raise

if __name__ == "__main__":
    create_test_schema()
