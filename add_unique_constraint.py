"""
Add unique constraint to team_game_stats for data loader
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor()

print("Adding unique constraint to hcl.team_game_stats...")

# Add unique constraint on (game_id, team)
cur.execute("""
    ALTER TABLE hcl.team_game_stats 
    ADD CONSTRAINT team_game_stats_unique 
    UNIQUE (game_id, team)
""")

conn.commit()
print("✅ Constraint added successfully")

cur.close()
conn.close()
