"""
TESTBED: Add EPA columns and test data loading (1999-2025)
Sprint 9 - Phase 1: Enhanced Data Pipeline

Testing Strategy:
1. Create testbed schema with EPA columns
2. Load sample data (1 season first)
3. Verify EPA calculations
4. Then scale to full 1999-2025 load
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to testbed database
conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password=os.getenv('DB_PASSWORD'),
    host='localhost',
    port='5432'
)

cur = conn.cursor()

print("=" * 80)
print("TESTBED: ADD EPA COLUMNS TO SCHEMA")
print("=" * 80)

# Step 1: Add EPA columns to team_game_stats
print("\n📊 Step 1: Adding EPA columns to hcl.team_game_stats...")

epa_columns = """
ALTER TABLE hcl.team_game_stats 
  ADD COLUMN IF NOT EXISTS epa_per_play            DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS success_rate            DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS pass_epa                DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS rush_epa                DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS total_epa               DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS wpa                     DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS cpoe                    DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS air_yards_per_att       DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS yac_per_completion      DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS explosive_play_pct      DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS stuff_rate              DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS pass_success_rate       DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS rush_success_rate       DOUBLE PRECISION
"""

try:
    cur.execute(epa_columns)
    conn.commit()
    print("✅ EPA columns added successfully!")
except Exception as e:
    print(f"❌ Error adding columns: {e}")
    conn.rollback()

# Step 2: Verify columns were added
print("\n📋 Step 2: Verifying new columns...")

cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' 
      AND table_name = 'team_game_stats'
      AND (column_name LIKE '%epa%' 
           OR column_name LIKE '%success%' 
           OR column_name LIKE '%wpa%'
           OR column_name LIKE '%cpoe%'
           OR column_name LIKE '%air_yards%'
           OR column_name LIKE '%yac%'
           OR column_name LIKE '%explosive%'
           OR column_name LIKE '%stuff%')
    ORDER BY column_name
""")

new_cols = cur.fetchall()
print(f"\n✅ Found {len(new_cols)} new EPA/advanced stat columns:")
for col, dtype in new_cols:
    print(f"   • {col:30} ({dtype})")

# Step 3: Check current data stats
print("\n📊 Step 3: Current database stats...")

cur.execute("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT season) as seasons,
        MIN(season) as first_season,
        MAX(season) as last_season,
        COUNT(DISTINCT team) as teams,
        COUNT(*) FILTER (WHERE epa_per_play IS NOT NULL) as has_epa
    FROM hcl.team_game_stats
""")

result = cur.fetchone()
print(f"\n   Total records: {result[0]}")
print(f"   Seasons: {result[1]} ({result[2]}-{result[3]})")
print(f"   Teams: {result[4]}")
print(f"   Records with EPA: {result[5]} ({result[5]/result[0]*100:.1f}%)")

# Step 4: Add indexes for better query performance
print("\n🔍 Step 4: Adding indexes for EPA columns...")

indexes = """
CREATE INDEX IF NOT EXISTS idx_tgs_epa ON hcl.team_game_stats(epa_per_play);
CREATE INDEX IF NOT EXISTS idx_tgs_success_rate ON hcl.team_game_stats(success_rate);
CREATE INDEX IF NOT EXISTS idx_tgs_season_team_epa ON hcl.team_game_stats(season, team, epa_per_play);
"""

try:
    cur.execute(indexes)
    conn.commit()
    print("✅ Indexes created successfully!")
except Exception as e:
    print(f"⚠️  Warning creating indexes: {e}")

cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ TESTBED SCHEMA UPDATE COMPLETE")
print("=" * 80)
print("\nNext Steps:")
print("1. Test load 2024 season with EPA (quick test)")
print("2. Verify EPA calculations are correct")
print("3. Then load full 1999-2025 dataset")
print("=" * 80)
