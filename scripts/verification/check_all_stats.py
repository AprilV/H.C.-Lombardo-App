import psycopg2
from datetime import datetime

# Connect to database
conn = psycopg2.connect(
    host='localhost',
    database='nfl_analytics',
    user='postgres',
    password='aprilv120'
)

cur = conn.cursor()

# Check all 11 columns for a sample of teams
print("=" * 80)
print("CHECKING ALL 11 STATS (Sample Teams)")
print("=" * 80)

sample_teams = ['BAL', 'BUF', 'DAL', 'KC', 'SF']

for abbr in sample_teams:
    cur.execute("""
        SELECT id, name, abbreviation, wins, losses, ties, ppg, pa, 
               games_played, stats, last_updated 
        FROM teams 
        WHERE abbreviation = %s
    """, (abbr,))
    
    result = cur.fetchone()
    if result:
        print(f"\n{result[1]} ({result[2]}):")
        print(f"  1. ID: {result[0]}")
        print(f"  2. Name: {result[1]}")
        print(f"  3. Abbreviation: {result[2]}")
        print(f"  4. Wins: {result[3]}")
        print(f"  5. Losses: {result[4]}")
        print(f"  6. Ties: {result[5]}")
        print(f"  7. PPG: {result[6]}")
        print(f"  8. PA: {result[7]}")
        print(f"  9. Games Played: {result[8]}")
        print(f"  10. Stats (JSONB): {result[9] if result[9] else 'NULL'}")
        print(f"  11. Last Updated: {result[10]}")

# Check all teams summary
print("\n" + "=" * 80)
print("ALL 32 TEAMS - STATS COMPLETENESS CHECK")
print("=" * 80)

cur.execute("""
    SELECT 
        COUNT(*) as total_teams,
        COUNT(CASE WHEN name IS NOT NULL THEN 1 END) as has_name,
        COUNT(CASE WHEN abbreviation IS NOT NULL THEN 1 END) as has_abbr,
        COUNT(CASE WHEN wins IS NOT NULL THEN 1 END) as has_wins,
        COUNT(CASE WHEN losses IS NOT NULL THEN 1 END) as has_losses,
        COUNT(CASE WHEN ties IS NOT NULL THEN 1 END) as has_ties,
        COUNT(CASE WHEN ppg IS NOT NULL THEN 1 END) as has_ppg,
        COUNT(CASE WHEN pa IS NOT NULL THEN 1 END) as has_pa,
        COUNT(CASE WHEN games_played IS NOT NULL THEN 1 END) as has_games,
        COUNT(CASE WHEN stats IS NOT NULL THEN 1 END) as has_stats_jsonb,
        COUNT(CASE WHEN last_updated IS NOT NULL THEN 1 END) as has_timestamp
    FROM teams
""")

summary = cur.fetchone()
print(f"\n{'Stat':<20} {'Teams with Data':<15} {'Status'}")
print("-" * 80)
print(f"{'Total Teams':<20} {summary[0]:<15} {'✅' if summary[0] == 32 else '❌'}")
print(f"{'1. ID':<20} {summary[0]:<15} {'✅'}")
print(f"{'2. Name':<20} {summary[1]:<15} {'✅' if summary[1] == 32 else '❌'}")
print(f"{'3. Abbreviation':<20} {summary[2]:<15} {'✅' if summary[2] == 32 else '❌'}")
print(f"{'4. Wins':<20} {summary[3]:<15} {'✅' if summary[3] == 32 else '❌'}")
print(f"{'5. Losses':<20} {summary[4]:<15} {'✅' if summary[4] == 32 else '❌'}")
print(f"{'6. Ties':<20} {summary[5]:<15} {'✅' if summary[5] == 32 else '❌'}")
print(f"{'7. PPG':<20} {summary[6]:<15} {'✅' if summary[6] == 32 else '❌'}")
print(f"{'8. PA':<20} {summary[7]:<15} {'✅' if summary[7] == 32 else '❌'}")
print(f"{'9. Games Played':<20} {summary[8]:<15} {'✅' if summary[8] == 32 else '❌'}")
print(f"{'10. Stats (JSONB)':<20} {summary[9]:<15} {'✅' if summary[9] == 32 else '⚠️  (Optional)'}")
print(f"{'11. Last Updated':<20} {summary[10]:<15} {'✅' if summary[10] == 32 else '❌'}")

# Check for any NULL values in critical stats
print("\n" + "=" * 80)
print("CHECKING FOR MISSING DATA")
print("=" * 80)

cur.execute("""
    SELECT name, abbreviation,
           CASE WHEN wins IS NULL THEN '❌ Wins' ELSE '' END ||
           CASE WHEN losses IS NULL THEN '❌ Losses' ELSE '' END ||
           CASE WHEN ppg IS NULL THEN '❌ PPG' ELSE '' END ||
           CASE WHEN pa IS NULL THEN '❌ PA' ELSE '' END ||
           CASE WHEN games_played IS NULL THEN '❌ Games' ELSE '' END ||
           CASE WHEN last_updated IS NULL THEN '❌ Timestamp' ELSE '' END as missing
    FROM teams
    WHERE wins IS NULL OR losses IS NULL OR ppg IS NULL OR pa IS NULL 
          OR games_played IS NULL OR last_updated IS NULL
""")

missing = cur.fetchall()
if missing:
    print(f"\n⚠️  Found {len(missing)} teams with missing data:")
    for team in missing:
        print(f"  {team[0]} ({team[1]}): {team[2]}")
else:
    print("\n✅ ALL TEAMS HAVE COMPLETE DATA!")

conn.close()
