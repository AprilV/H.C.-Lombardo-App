import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        dbname='nfl_analytics',
        user='postgres',
        password='aprilv120',
        host='localhost'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if HCL schema exists
    cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'hcl'")
    hcl_exists = cur.fetchone()
    
    if hcl_exists:
        print("✅ HCL schema exists")
        
        # Check team_game_stats table
        cur.execute("SELECT COUNT(*) as count FROM hcl.team_game_stats")
        total = cur.fetchone()['count']
        print(f"Total team_game_stats records: {total}")
        
        # Check by season
        cur.execute("SELECT season, COUNT(*) as count FROM hcl.team_game_stats GROUP BY season ORDER BY season DESC")
        seasons = cur.fetchall()
        print("\nRecords by season:")
        for s in seasons:
            print(f"  {s['season']}: {s['count']} records")
        
        # Check if we have 2025 data
        cur.execute("SELECT COUNT(*) as count FROM hcl.team_game_stats WHERE season = 2025")
        count_2025 = cur.fetchone()['count']
        
        if count_2025 > 0:
            # Test getting KC 2025 stats
            cur.execute("""
                SELECT team, season, COUNT(*) as games_played,
                       SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) as wins
                FROM hcl.team_game_stats
                WHERE team = 'KC' AND season = 2025
                GROUP BY team, season
            """)
            kc_stats = cur.fetchone()
            print(f"\n✅ KC 2025 data: {kc_stats}")
        else:
            print("\n❌ No 2025 data found")
            
    else:
        print("❌ HCL schema does NOT exist!")
        print("You need to create the HCL schema and load data.")
        
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
