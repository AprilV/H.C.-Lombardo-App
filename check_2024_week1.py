import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Check 2024 season data
cur.execute("""
    SELECT week, 
           COUNT(*) as games,
           SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct
    FROM hcl.ml_predictions 
    WHERE season = 2024 
    AND result_recorded_at IS NOT NULL
    GROUP BY week 
    ORDER BY week
""")

rows = cur.fetchall()
print("2024 Season Week Data:")
for r in rows:
    print(f"  Week {r['week']}: {r['correct']}/{r['games']} games ({(r['correct']/r['games']*100):.1f}%)")

print(f"\nTotal weeks: {len(rows)}")

conn.close()
