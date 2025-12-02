import psycopg2
from db_config import DATABASE_CONFIG

try:
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'hcl' 
        AND table_name = 'ml_predictions' 
        ORDER BY ordinal_position
    """)

    print("ML_PREDICTIONS TABLE COLUMNS:")
    columns = cur.fetchall()
    if columns:
        for row in columns:
            print(f"  {row[0]}: {row[1]}")
    else:
        print("  No columns found!")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
