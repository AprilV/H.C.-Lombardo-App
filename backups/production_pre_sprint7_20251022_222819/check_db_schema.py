"""Quick script to check current database schema"""
import psycopg2
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()

# Get all tables
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
tables = cursor.fetchall()

print("=" * 60)
print("CURRENT POSTGRESQL DATABASE SCHEMA")
print("=" * 60)
print(f"\nTotal Tables: {len(tables)}")
print("\nTables:")
for table in tables:
    print(f"  - {table[0]}")

# Get teams table structure
print("\n" + "=" * 60)
print("TEAMS TABLE STRUCTURE")
print("=" * 60)
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'teams' 
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()
print(f"\nTotal Columns: {len(columns)}")
print("\nColumns:")
for col in columns:
    print(f"  - {col[0]}: {col[1]}")

# Count records
cursor.execute("SELECT COUNT(*) FROM teams")
count = cursor.fetchone()[0]
print(f"\nTotal Records: {count}")

conn.close()
