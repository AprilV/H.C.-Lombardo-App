"""
Complete verification - do we have ALL stats for ALL 32 teams Week 13
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT', '5432')
)

cur = conn.cursor()

print("\n" + "="*80)
print("WEEK 13 COMPLETE VERIFICATION")
print("="*80)

# Check team count
cur.execute("""
    SELECT COUNT(DISTINCT team)
    FROM hcl.team_game_stats
    WHERE season = 2025 AND week = 13
""")
team_count = cur.fetchone()[0]
print(f"\n1. Team Coverage: {team_count}/32 teams")
if team_count < 32:
    cur.execute("""
        SELECT team FROM hcl.team_game_stats 
        WHERE season = 2025 AND week = 13
        ORDER BY team
    """)
    teams_present = [r[0] for r in cur.fetchall()]
    all_teams = ['ARI','ATL','BAL','BUF','CAR','CHI','CIN','CLE','DAL','DEN','DET','GB','HOU','IND','JAX','KC','LAC','LAR','LV','MIA','MIN','NE','NO','NYG','NYJ','PHI','PIT','SEA','SF','TB','TEN','WAS']
    missing = [t for t in all_teams if t not in teams_present]
    print(f"   Missing teams: {', '.join(missing)}")

# Check EPA data
cur.execute("""
    SELECT COUNT(*)
    FROM hcl.team_game_stats
    WHERE season = 2025 AND week = 13 AND epa_per_play IS NOT NULL
""")
epa_count = cur.fetchone()[0]
print(f"\n2. EPA Data: {epa_count}/32 teams have EPA stats")

# Check all 64 columns for a sample team
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' 
    AND table_name = 'team_game_stats'
    ORDER BY ordinal_position
""")
all_columns = [row[0] for row in cur.fetchall()]

cur.execute("""
    SELECT * FROM hcl.team_game_stats
    WHERE season = 2025 AND week = 13 AND team = 'KC'
""")
kc_row = cur.fetchone()

null_count = sum(1 for val in kc_row if val is None)
populated_count = len(kc_row) - null_count

print(f"\n3. KC Week 13 Stats: {populated_count}/{len(all_columns)} fields populated")
print(f"   NULL fields: {null_count}")

# List what's still NULL
if null_count > 0:
    null_fields = [all_columns[i] for i, val in enumerate(kc_row) if val is None]
    print(f"   Still NULL: {', '.join(null_fields)}")

# Check current week
cur.execute("""
    SELECT MAX(week) FROM hcl.games
    WHERE season = 2025 AND home_score IS NOT NULL
""")
latest_week = cur.fetchone()[0]
print(f"\n4. Latest Completed Week: Week {latest_week}")

# Check if Week 14 data exists
cur.execute("""
    SELECT COUNT(*) FROM hcl.games
    WHERE season = 2025 AND week = 14
""")
week14_count = cur.fetchone()[0]
print(f"\n5. Week 14 Games: {week14_count} games scheduled")

cur.execute("""
    SELECT COUNT(*) FROM hcl.games
    WHERE season = 2025 AND week = 14 AND home_score IS NOT NULL
""")
week14_complete = cur.fetchone()[0]
print(f"   Week 14 Completed: {week14_complete} games")

conn.close()

print("\n" + "="*80)
print("STATUS:")
if team_count == 32 and epa_count == 32 and null_count == 0:
    print("✅ PERFECT - All 32 teams, all 64 stats for Week 13")
else:
    print("❌ INCOMPLETE")
    if team_count < 32:
        print(f"   - Missing {32-team_count} teams")
    if epa_count < 32:
        print(f"   - Missing EPA for {32-epa_count} teams")
    if null_count > 0:
        print(f"   - {null_count} NULL fields remain")
print("="*80 + "\n")
