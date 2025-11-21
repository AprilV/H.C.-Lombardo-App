from db_config import DATABASE_CONFIG
import psycopg2

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor()

# Check total games in schedule for KC
cur.execute("SELECT COUNT(*) FROM hcl.games WHERE season = 2025 AND (home_team = 'KC' OR away_team = 'KC')")
total_games = cur.fetchone()[0]
print(f"Total KC games in schedule: {total_games}")

# Check how many have scores
cur.execute("SELECT COUNT(*) FROM hcl.games WHERE season = 2025 AND (home_team = 'KC' OR away_team = 'KC') AND home_score IS NOT NULL")
completed = cur.fetchone()[0]
print(f"Completed games: {completed}")
print(f"Future games: {total_games - completed}")

cur.close()
conn.close()
