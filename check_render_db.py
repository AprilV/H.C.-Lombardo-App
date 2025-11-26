"""Quick check of Render database contents"""
import psycopg2

DATABASE_URL = input("Paste External Database URL: ")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Check teams
cursor.execute("SELECT COUNT(*) FROM teams")
print(f"Total teams: {cursor.fetchone()[0]}")

cursor.execute("SELECT name, abbreviation FROM teams ORDER BY name LIMIT 5")
teams = cursor.fetchall()
print("\nFirst 5 teams:")
for team in teams:
    print(f"  - {team[0]} ({team[1]})")

# Check table structure
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'teams'
    ORDER BY ordinal_position
""")
print("\nTeams table columns:")
for col in cursor.fetchall():
    print(f"  - {col[0]}: {col[1]}")

cursor.close()
conn.close()
