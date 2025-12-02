import psycopg2
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor()

# Get all tables
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
tables = [row[0] for row in cur.fetchall()]

print("DATABASE SCHEMA")
print("=" * 60)

for table in tables:
    # Get columns
    cur.execute(f"""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns 
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    
    print(f"\nTable: {table}")
    print("-" * 60)
    for row in cur.fetchall():
        col_name, dtype, max_len, nullable = row
        length = f"({max_len})" if max_len else ""
        null = "NULL" if nullable == 'YES' else "NOT NULL"
        print(f"  {col_name:30s} {dtype}{length:20s} {null}")
    
    # Get primary keys
    cur.execute(f"""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = '{table}' AND tc.constraint_type = 'PRIMARY KEY'
    """)
    pks = [row[0] for row in cur.fetchall()]
    if pks:
        print(f"  PRIMARY KEY: {', '.join(pks)}")
    
    # Get foreign keys
    cur.execute(f"""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table}'
    """)
    fks = cur.fetchall()
    if fks:
        for fk in fks:
            print(f"  FOREIGN KEY: {fk[0]} -> {fk[1]}({fk[2]})")

conn.close()
