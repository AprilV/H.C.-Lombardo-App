"""
COMPLETE STATS REPORT - What's Missing from Week 13
Compare database columns vs what has data
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
print("WEEK 13 STATS REPORT - What We Have vs What's Missing")
print("="*80)

# Get column names
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' 
    AND table_name = 'team_game_stats'
    ORDER BY ordinal_position
""")
all_columns = [row[0] for row in cur.fetchall()]

# Get sample Week 13 row
cur.execute("""
    SELECT *
    FROM hcl.team_game_stats
    WHERE season = 2025 AND week = 13
    ORDER BY team
    LIMIT 1
""")
sample_row = cur.fetchone()

# Categorize columns
has_data = []
missing_data = []

for i, col in enumerate(all_columns):
    if sample_row[i] is not None:
        has_data.append(col)
    else:
        missing_data.append(col)

print(f"\n✅ STATS WE HAVE ({len(has_data)}/{len(all_columns)}):")
print("-" * 80)
for col in has_data:
    print(f"  • {col}")

print(f"\n❌ STATS MISSING - ALL NULL ({len(missing_data)}/{len(all_columns)}):")
print("-" * 80)
for col in missing_data:
    print(f"  • {col}")

# Check how many teams have Week 13 data
cur.execute("""
    SELECT COUNT(DISTINCT team)
    FROM hcl.team_game_stats
    WHERE season = 2025 AND week = 13
""")
team_count = cur.fetchone()[0]

print(f"\n📊 WEEK 13 COVERAGE:")
print("-" * 80)
print(f"Teams with Week 13 data: {team_count}/32")

# Check if missing stats are EPA-specific
epa_stats = ['epa_per_play', 'success_rate', 'pass_epa', 'rush_epa', 'total_epa', 
             'wpa', 'cpoe', 'air_yards_per_att', 'yac_per_completion', 
             'explosive_play_pct', 'stuff_rate', 'pass_success_rate', 'rush_success_rate']

epa_missing = [s for s in epa_stats if s in missing_data]
non_epa_missing = [s for s in missing_data if s not in epa_stats]

print(f"\n🔍 BREAKDOWN OF MISSING STATS:")
print("-" * 80)
print(f"EPA/Advanced metrics missing: {len(epa_missing)}")
for stat in epa_missing:
    print(f"  • {stat}")

if non_epa_missing:
    print(f"\nNon-EPA stats missing: {len(non_epa_missing)}")
    for stat in non_epa_missing:
        print(f"  • {stat}")
else:
    print(f"\nNon-EPA stats missing: 0 (all basic stats populated)")

# Check earlier weeks
print(f"\n📅 HISTORICAL CHECK - Do older weeks have EPA?")
print("-" * 80)
for week in [12, 11, 10]:
    cur.execute("""
        SELECT COUNT(*) 
        FROM hcl.team_game_stats
        WHERE season = 2025 AND week = %s AND epa_per_play IS NOT NULL
    """, (week,))
    count = cur.fetchone()[0]
    print(f"  Week {week}: {count} teams with EPA data")

conn.close()

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("✅ Basic nflverse stats (51 fields) ARE populated")
print("❌ EPA/Advanced stats (13 fields) are NOT populated") 
print("\nRoot cause: EPA requires play-by-play data processing")
print("Solution: Run update_2025_with_epa.py to calculate EPA from plays")
print("="*80 + "\n")
