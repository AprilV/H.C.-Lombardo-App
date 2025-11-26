import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_connection_string

try:
    conn = psycopg2.connect(get_connection_string())
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("Tables in hcl schema:")
    cur.execute("""
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = 'hcl'
        ORDER BY table_type, table_name
    """)
    tables = cur.fetchall()
    for t in tables:
        print(f"  {t['table_type']:10} - {t['table_name']}")
    
    print("\n\nLooking for tables with 'team' and 'season' in name:")
    cur.execute("""
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = 'hcl'
        AND (table_name LIKE '%team%' OR table_name LIKE '%season%')
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    for t in tables:
        print(f"  {t['table_type']:10} - {t['table_name']}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
