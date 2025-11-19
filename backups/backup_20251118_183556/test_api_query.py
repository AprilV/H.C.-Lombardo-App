import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password='aprilv120'
)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Check actual data for 2024
cur.execute("""
    SELECT team, game_id, result, points, total_yards, passing_yards, rushing_yards
    FROM hcl.team_game_stats
    WHERE team = 'KC' AND season = 2024
    LIMIT 3
""")

rows = cur.fetchall()
print("Sample KC 2024 raw data:")
for row in rows:
    print(dict(row))

# Now check what the API query returns
cur.execute("""
    SELECT 
        team,
        season,
        COUNT(*) as games_played,
        SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) as wins,
        ROUND(AVG(points)::numeric, 1) as ppg,
        ROUND(AVG(total_yards)::numeric, 1) as total_yards_per_game
    FROM hcl.team_game_stats
    WHERE team = 'KC' AND season = 2024
    GROUP BY team, season
""")

result = cur.fetchone()
print(f"\nAPI aggregated result:")
print(dict(result))

conn.close()
