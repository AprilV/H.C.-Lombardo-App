"""Check all table structures"""
import psycopg2
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()

print("="*70)
print("DATABASE SCHEMA - ALL TABLES")
print("="*70)

# Get all tables
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    print(f"\n{'='*70}")
    print(f"TABLE: {table.upper()}")
    print(f"{'='*70}")
    
    # Get columns
    cursor.execute(f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = '{table}' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    
    print(f"\nColumns ({len(columns)}):")
    for col_name, data_type, nullable in columns:
        null_str = "NULL" if nullable == 'YES' else "NOT NULL"
        print(f"  - {col_name:25} {data_type:20} {null_str}")
    
    # Get primary keys
    cursor.execute(f"""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = '{table}'::regclass AND i.indisprimary
    """)
    pks = cursor.fetchall()
    if pks:
        print(f"\nPrimary Key: {', '.join(pk[0] for pk in pks)}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Total Records: {count}")

# Check for foreign keys
print(f"\n{'='*70}")
print("FOREIGN KEY RELATIONSHIPS")
print(f"{'='*70}")

cursor.execute("""
    SELECT
        tc.table_name, 
        kcu.column_name, 
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
""")
fks = cursor.fetchall()

if fks:
    for table_name, col, foreign_table, foreign_col in fks:
        print(f"  {table_name}.{col} → {foreign_table}.{foreign_col}")
else:
    print("  No foreign key relationships found")

conn.close()
