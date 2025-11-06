"""
Quick database inventory check
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password=os.getenv('DB_PASSWORD'),
    host='localhost',
    port='5432'
)

cur = conn.cursor()

print("=" * 80)
print("CURRENT DATABASE INVENTORY")
print("=" * 80)

# Check seasons and games
cur.execute("SELECT MIN(season), MAX(season), COUNT(DISTINCT season), COUNT(*) FROM hcl.games")
result = cur.fetchone()
print(f"\n📊 Games Data:")
print(f"   Seasons: {result[0]}-{result[1]}")
print(f"   Total seasons: {result[2]}")
print(f"   Total games: {result[3]}")

# Check columns in team_game_stats
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' AND table_name = 'team_game_stats' 
    ORDER BY ordinal_position
""")
cols = cur.fetchall()
print(f"\n📈 Team Game Stats Columns ({len(cols)} total):")
for i, (col, dtype) in enumerate(cols, 1):
    print(f"   {i:2}. {col:30} ({dtype})")

# Check what we DON'T have
print("\n=" * 80)
print("CHECKING FOR KEY ML FEATURES...")
print("=" * 80)

# Check for betting data
cur.execute("""
    SELECT 
        COUNT(*) FILTER (WHERE spread_line IS NOT NULL) as has_spread,
        COUNT(*) FILTER (WHERE total_line IS NOT NULL) as has_total,
        COUNT(*) FILTER (WHERE home_moneyline IS NOT NULL) as has_moneyline,
        COUNT(*) as total_games
    FROM hcl.games
""")
result = cur.fetchone()
print(f"\n🎰 Betting Data:")
print(f"   Spread: {result[0]}/{result[3]} games ({result[0]/result[3]*100:.1f}%)")
print(f"   Total: {result[1]}/{result[3]} games ({result[1]/result[3]*100:.1f}%)")
print(f"   Moneyline: {result[2]}/{result[3]} games ({result[2]/result[3]*100:.1f}%)")

# Check for weather data
cur.execute("""
    SELECT 
        COUNT(*) FILTER (WHERE roof IS NOT NULL) as has_roof,
        COUNT(*) FILTER (WHERE temp IS NOT NULL) as has_temp,
        COUNT(*) FILTER (WHERE wind IS NOT NULL) as has_wind,
        COUNT(*) as total_games
    FROM hcl.games
""")
result = cur.fetchone()
print(f"\n🌤️  Weather Data:")
print(f"   Roof: {result[0]}/{result[3]} games ({result[0]/result[3]*100:.1f}%)")
print(f"   Temp: {result[1]}/{result[3]} games ({result[1]/result[3]*100:.1f}%)")
print(f"   Wind: {result[2]}/{result[3]} games ({result[2]/result[3]*100:.1f}%)")

# Check for advanced stats
cur.execute("""
    SELECT 
        COUNT(*) FILTER (WHERE epa_per_play IS NOT NULL) as has_epa,
        COUNT(*) FILTER (WHERE success_rate IS NOT NULL) as has_success_rate,
        COUNT(*) FILTER (WHERE yards_per_play IS NOT NULL) as has_ypp,
        COUNT(*) as total_records
    FROM hcl.team_game_stats
""")
result = cur.fetchone()
print(f"\n📊 Advanced Stats:")
print(f"   EPA/Play: {result[0]}/{result[3]} records ({result[0]/result[3]*100:.1f}%)")
print(f"   Success Rate: {result[1]}/{result[3]} records ({result[1]/result[3]*100:.1f}%)")
print(f"   Yards/Play: {result[2]}/{result[3]} records ({result[2]/result[3]*100:.1f}%)")

# Check sample of actual data
print("\n=" * 80)
print("SAMPLE DATA (Most Recent Game):")
print("=" * 80)
cur.execute("""
    SELECT game_id, season, week, home_team, away_team, 
           spread_line, total_line, roof, temp, wind
    FROM hcl.games
    ORDER BY season DESC, week DESC
    LIMIT 1
""")
result = cur.fetchone()
print(f"\nGame: {result[0]}")
print(f"Season: {result[1]}, Week: {result[2]}")
print(f"Matchup: {result[4]} @ {result[3]}")
print(f"Spread: {result[5]}, Total: {result[6]}")
print(f"Roof: {result[7]}, Temp: {result[8]}, Wind: {result[9]}")

cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ INVENTORY CHECK COMPLETE")
print("=" * 80)
