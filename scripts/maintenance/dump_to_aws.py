"""Fast data dump to AWS using COPY"""
import psycopg2
import sys

print("=" * 80)
print("FAST DATA DUMP TO AWS")
print("=" * 80)

local_conn = psycopg2.connect(
    dbname="nfl_analytics",
    user="postgres",
    password="aprilv120",
    host="localhost"
)

aws_conn = psycopg2.connect(
    dbname="nfl_analytics",
    user="nfl_user",
    password="aprilv120",
    host="3.239.85.206"
)

try:
    local_cur = local_conn.cursor()
    aws_cur = aws_conn.cursor()
    
    # Just copy team_game_stats - the critical table
    table = 'hcl.team_game_stats'
    
    print(f"\nGetting {table} data...")
    local_cur.execute(f"SELECT COUNT(*) FROM {table}")
    total = local_cur.fetchone()[0]
    print(f"Total rows: {total:,}")
    
    print(f"\nClearing {table} on AWS...")
    aws_cur.execute(f"TRUNCATE {table}")
    aws_conn.commit()
    
    print(f"\nCopying data in batches of 1000...")
    
    # Get columns
    local_cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'hcl' AND table_name = 'team_game_stats'
        ORDER BY ordinal_position
    """)
    columns = [row[0] for row in local_cur.fetchall()]
    cols_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
    
    # Stream data
    local_cur.execute(f"SELECT * FROM {table}")
    rows_done = 0
    
    while True:
        batch = local_cur.fetchmany(1000)
        if not batch:
            break
        
        aws_cur.executemany(insert_sql, batch)
        aws_conn.commit()
        
        rows_done += len(batch)
        pct = (rows_done / total) * 100
        print(f"  {rows_done:,}/{total:,} rows ({pct:.1f}%)", end='\r')
    
    print(f"\n\n✅ SUCCESS! Copied {total:,} rows to AWS")
    
    # Verify
    aws_cur.execute(f"SELECT COUNT(*) FROM {table} WHERE season = 2025")
    count_2025 = aws_cur.fetchone()[0]
    print(f"✅ AWS now has {count_2025} records for 2025 season")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)
finally:
    local_cur.close()
    local_conn.close()
    aws_cur.close()
    aws_conn.close()

print("\n" + "=" * 80)
print("DONE!")
print("=" * 80)
