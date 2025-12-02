import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password='aprilv120'
)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Check data availability for each season 1999-2025
print("Checking data availability for seasons 1999-2025:\n")
print(f"{'Season':<8} {'Records':<10} {'Has Points':<12} {'Has Yards':<12} {'Has Passing':<12} {'Has Rushing':<12} {'Has Result':<12}")
print("-" * 90)

for year in range(1999, 2026):
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(points) as has_points,
            COUNT(total_yards) as has_yards,
            COUNT(passing_yards) as has_passing,
            COUNT(rushing_yards) as has_rushing,
            COUNT(result) as has_result
        FROM hcl.team_game_stats
        WHERE season = %s
    """, (year,))
    
    stats = cur.fetchone()
    
    status = "✅ FULL" if stats['has_passing'] == stats['total'] and stats['total'] > 0 else "❌ NULL" if stats['total'] > 0 else "⚠️ EMPTY"
    
    print(f"{year:<8} {stats['total']:<10} {stats['has_points']:<12} {stats['has_yards']:<12} {stats['has_passing']:<12} {stats['has_rushing']:<12} {stats['has_result']:<12} {status}")

conn.close()

print("\n✅ FULL = All stats populated")
print("❌ NULL = Records exist but stats are NULL")
print("⚠️ EMPTY = No records for this season")
