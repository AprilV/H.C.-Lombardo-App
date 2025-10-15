import psycopg2

# Connect to database
conn = psycopg2.connect(
    host='localhost',
    database='nfl_analytics',
    user='postgres',
    password='aprilv120'
)

cur = conn.cursor()

# Check Baltimore Ravens
print("=" * 60)
print("BALTIMORE RAVENS:")
cur.execute("SELECT name, abbreviation, wins, losses, ppg, pa, games_played FROM teams WHERE abbreviation = 'BAL'")
result = cur.fetchone()
if result:
    print(f"  Name: {result[0]}")
    print(f"  Abbreviation: {result[1]}")
    print(f"  Record: {result[2]}-{result[3]}")
    print(f"  PPG: {result[4]}")
    print(f"  PA: {result[5]}")
    print(f"  Games Played: {result[6]}")
else:
    print("  NOT FOUND!")

# Check all teams with 0 wins and 0 losses
print("\n" + "=" * 60)
print("TEAMS WITH 0-0 RECORD:")
cur.execute("SELECT name, abbreviation, wins, losses, ppg, pa, games_played FROM teams WHERE wins = 0 AND losses = 0 ORDER BY name")
zero_teams = cur.fetchall()
print(f"Found {len(zero_teams)} teams with 0-0 record:")
for team in zero_teams:
    print(f"  {team[1]}: {team[0]} | PPG: {team[4]} | PA: {team[5]} | Games: {team[6]}")

# Check all teams stats summary
print("\n" + "=" * 60)
print("ALL TEAMS SUMMARY:")
cur.execute("""
    SELECT 
        COUNT(*) as total_teams,
        COUNT(CASE WHEN wins = 0 AND losses = 0 THEN 1 END) as zero_record_teams,
        COUNT(CASE WHEN ppg IS NULL OR ppg = 0 THEN 1 END) as missing_ppg,
        COUNT(CASE WHEN pa IS NULL OR pa = 0 THEN 1 END) as missing_pa
    FROM teams
""")
summary = cur.fetchone()
print(f"  Total Teams: {summary[0]}")
print(f"  Teams with 0-0 record: {summary[1]}")
print(f"  Teams missing PPG: {summary[2]}")
print(f"  Teams missing PA: {summary[3]}")

conn.close()
