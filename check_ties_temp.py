import psycopg2
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor()

# Check teams with ties
cur.execute("""
    SELECT team, wins, losses, ties 
    FROM hcl_test.teams 
    WHERE season = 2025 AND ties > 0 
    ORDER BY team
""")

print("\nTeams with ties in 2025:")
print("="*40)
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}-{row[2]}-{row[3]}")

cur.close()
conn.close()
