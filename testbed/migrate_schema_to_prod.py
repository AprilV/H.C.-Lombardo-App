"""
Migrate HCL schema to production database
Sprint 7 - Production Integration
"""

import psycopg2

def migrate_schema():
    """Create HCL schema in production database (nfl_analytics)"""
    
    # Connect to production database
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='nfl_analytics',
        user='postgres',
        password='aprilv120'
    )
    
    cur = conn.cursor()
    
    # Read schema file
    with open('schema/hcl_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Execute schema creation
    print("Creating HCL schema in production database...")
    cur.execute(schema_sql)
    conn.commit()
    
    print("✅ HCL schema created successfully!\n")
    
    # Verify tables created
    cur.execute("""
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname='hcl' 
        ORDER BY tablename
    """)
    
    print("Tables created:")
    for row in cur.fetchall():
        print(f"  - {row[0]}.{row[1]}")
    
    # Verify views created
    cur.execute("""
        SELECT schemaname, viewname 
        FROM pg_views 
        WHERE schemaname='hcl' 
        ORDER BY viewname
    """)
    
    print("\nViews created:")
    for row in cur.fetchall():
        print(f"  - {row[0]}.{row[1]}")
    
    conn.close()
    print("\n✅ Migration complete!")

if __name__ == '__main__':
    migrate_schema()
