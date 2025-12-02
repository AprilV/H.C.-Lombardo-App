import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password='aprilv120'
)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Check what columns actually have data
cur.execute("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(points) as has_points,
        COUNT(total_yards) as has_total_yards,
        COUNT(passing_yards) as has_passing_yards,
        COUNT(rushing_yards) as has_rushing_yards,
        COUNT(result) as has_result,
        COUNT(completion_pct) as has_completion_pct,
        COUNT(third_down_pct) as has_third_down_pct
    FROM hcl.team_game_stats
    WHERE season IN (2023, 2024)
""")

stats = cur.fetchone()
print("Data availability for 2023-2024:")
print(dict(stats))

# Get actual sample record
cur.execute("""
    SELECT *
    FROM hcl.team_game_stats
    WHERE team = 'ATL' AND season = 2024
    LIMIT 1
""")

sample = cur.fetchone()
if sample:
    print("\nSample ATL 2024 record:")
    for key, value in dict(sample).items():
        print(f"  {key}: {value}")
else:
    print("\nNo ATL 2024 records found!")

conn.close()
