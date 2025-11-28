"""
Export local hcl schema and data, then import to AWS
"""
import psycopg2
import sys

print("=" * 80)
print("EXPORTING LOCAL DATABASE TO AWS")
print("=" * 80)

# Local database connection
local_conn = psycopg2.connect(
    dbname="nfl_analytics",
    user="postgres",
    password="aprilv120",
    host="localhost"
)

# AWS database connection
aws_conn = psycopg2.connect(
    dbname="nfl_analytics",
    user="nfl_user",
    password="aprilv120",
    host="3.239.85.206"
)

try:
    local_cur = local_conn.cursor()
    aws_cur = aws_conn.cursor()
    
    print("\n[1/4] Creating schemas on AWS...")
    aws_cur.execute("CREATE SCHEMA IF NOT EXISTS hcl")
    aws_conn.commit()
    print("✓ Schemas ready")
    
    print("\n[2/4] Getting table structure from local...")
    # Get all tables in hcl and public schemas
    local_cur.execute("""
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname IN ('hcl', 'public')
        ORDER BY schemaname, tablename
    """)
    tables = local_cur.fetchall()
    print(f"✓ Found {len(tables)} tables: {', '.join([f'{s}.{t}' for s, t in tables])}")
    
    print("\n[3/4] Creating tables on AWS...")
    for schema, table in tables:
        # Get column info
        local_cur.execute(f"""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
        """)
        columns_info = local_cur.fetchall()
        
        # Build CREATE TABLE
        col_defs = []
        for col_name, data_type, max_len, nullable in columns_info:
            col_def = f"{col_name} {data_type}"
            if max_len:
                col_def += f"({max_len})"
            if nullable == 'NO':
                col_def += " NOT NULL"
            col_defs.append(col_def)
        
        create_sql = f"CREATE TABLE {schema}.{table} ({', '.join(col_defs)})"
        
        try:
            aws_cur.execute(f"DROP TABLE IF EXISTS {schema}.{table} CASCADE")
            aws_cur.execute(create_sql)
            print(f"  ✓ Created {schema}.{table}")
        except Exception as e:
            print(f"  ⚠ Error creating {schema}.{table}: {e}")
    
    aws_conn.commit()
    
    print("\n[4/4] Copying data to AWS...")
    total_rows = 0
    BATCH_SIZE = 500
    
    for schema, table in tables:
        # Get row count
        local_cur.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
        count = local_cur.fetchone()[0]
        
        if count == 0:
            print(f"  - {schema}.{table}: 0 rows (skipped)")
            continue
        
        print(f"  → {schema}.{table}: Copying {count:,} rows...", end='', flush=True)
        
        # Get column names
        local_cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in local_cur.fetchall()]
        cols_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f"INSERT INTO {schema}.{table} ({cols_str}) VALUES ({placeholders})"
        
        # Use server-side cursor for large tables
        local_cur.execute(f"SELECT * FROM {schema}.{table}")
        rows_inserted = 0
        
        while True:
            batch = local_cur.fetchmany(BATCH_SIZE)
            if not batch:
                break
            aws_cur.executemany(insert_sql, batch)
            aws_conn.commit()
            rows_inserted += len(batch)
            print(f"\r  → {schema}.{table}: {rows_inserted:,}/{count:,} rows", end='', flush=True)
        
        total_rows += count
        print(f"\r  ✓ {schema}.{table}: {count:,} rows          ")
    
    print("\n" + "=" * 80)
    print(f"SUCCESS! Exported {total_rows:,} total rows to AWS")
    print("=" * 80)
    
    # Verify
    print("\n[VERIFICATION] Checking AWS database...")
    aws_cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats WHERE season = 2025")
    aws_2025_count = aws_cur.fetchone()[0]
    print(f"  ✓ AWS has {aws_2025_count} records for 2025 season")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    local_cur.close()
    local_conn.close()
    aws_cur.close()
    aws_conn.close()

print("\n✅ Database export complete!")
