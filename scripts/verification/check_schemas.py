import psycopg2
import os

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432')
)
cur = conn.cursor()

# Get all schemas
cur.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name")
schemas = cur.fetchall()
print("Available schemas:")
for s in schemas:
    print(f"  - {s[0]}")

# Check for tables in public schema
cur.execute("""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public' 
    AND tablename LIKE '%team%'
    ORDER BY tablename
""")
tables = cur.fetchall()
print("\nTables with 'team' in public schema:")
for t in tables:
    print(f"  - {t[0]}")

conn.close()
