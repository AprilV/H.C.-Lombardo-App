import psycopg2
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor()

# Check 2025 data
cur.execute("""
    SELECT 
        season,
        COUNT(*) as total_records,
        COUNT(points) as has_points,
        COUNT(total_yards) as has_yards,
        COUNT(passing_yards_per_game) as has_passing,
        COUNT(rushing_yards_per_game) as has_rushing,
        COUNT(result) as has_result
    FROM hcl.team_game_stats 
    WHERE season = 2025
    GROUP BY season
""")

print("2025 Season Data Check:")
print("=" * 80)
row = cur.fetchone()
if row:
    print(f"Season: {row[0]}")
    print(f"Total Records: {row[1]}")
    print(f"Has Points: {row[2]}")
    print(f"Has Total Yards: {row[3]}")
    print(f"Has Passing Stats: {row[4]}")
    print(f"Has Rushing Stats: {row[5]}")
    print(f"Has Result: {row[6]}")
    
    if row[1] > 0 and row[4] < row[1]:
        print("\n⚠️ WARNING: Some stats are NULL!")
        
        # Get a sample record
        cur.execute("""
            SELECT team, game_id, points, total_yards, 
                   passing_yards_per_game, rushing_yards_per_game, result
            FROM hcl.team_game_stats
            WHERE season = 2025
            LIMIT 5
        """)
        print("\nSample records:")
        for r in cur.fetchall():
            print(f"  Team: {r[0]}, Points: {r[2]}, Total Yards: {r[3]}, "
                  f"Pass Yards/G: {r[4]}, Rush Yards/G: {r[5]}, Result: {r[6]}")
else:
    print("No 2025 data found!")

conn.close()
