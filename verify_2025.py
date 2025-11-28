import psycopg2

conn = psycopg2.connect('postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM hcl.team_game_stats WHERE season = 2025 AND epa_per_play IS NOT NULL')
epa = cur.fetchone()[0]

cur.execute('SELECT team, COUNT(*) as games FROM hcl.team_game_stats WHERE season = 2025 GROUP BY team ORDER BY team LIMIT 10')
teams = cur.fetchall()

print(f'\n✅ 2025 DATA VERIFICATION')
print(f'   Stats with EPA: {epa}')
print(f'\n   Sample teams:')
for team, count in teams:
    print(f'   {team}: {count} games')

conn.close()
