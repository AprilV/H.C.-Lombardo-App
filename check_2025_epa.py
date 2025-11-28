import psycopg2

conn = psycopg2.connect('postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics')
cur = conn.cursor()

cur.execute("""
    SELECT game_id, team, points, total_yards, epa_per_play, pass_epa, rush_epa
    FROM hcl.team_game_stats 
    WHERE season = 2025 
    LIMIT 5
""")

print("\nSample 2025 team_game_stats:")
print("game_id | team | points | yards | epa_per_play | pass_epa | rush_epa")
print("-" * 80)
for row in cur.fetchall():
    print(f"{row[0][:20]:20} | {row[1]:4} | {row[2]:6} | {row[3]:5} | {row[4]} | {row[5]} | {row[6]}")

conn.close()
