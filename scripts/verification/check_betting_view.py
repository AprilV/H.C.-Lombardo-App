import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_connection_string

try:
    conn_str = get_connection_string()
    print(f"Connecting to database...")
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if view exists
    cur.execute("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = 'hcl' 
        AND table_name = 'v_team_betting_performance'
    """)
    view_exists = cur.fetchone()
    print(f"View exists: {view_exists}")
    
    if not view_exists:
        print("\n❌ View v_team_betting_performance does NOT exist!")
        print("\nChecking what views DO exist in hcl schema:")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'hcl'
            ORDER BY table_name
        """)
        views = cur.fetchall()
        for v in views:
            print(f"  - {v['table_name']}")
    else:
        # Try to query the view
        print("\n✅ View exists! Testing query...")
        cur.execute("""
            SELECT team, season, total_games, ats_wins, ats_losses 
            FROM hcl.v_team_betting_performance 
            WHERE season = 2025 
            LIMIT 5
        """)
        results = cur.fetchall()
        print(f"\nSample data ({len(results)} rows):")
        for row in results:
            print(f"  {row}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
