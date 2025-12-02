"""CHECK NFLVERSE DIRECTLY - What 2025 data exists right now"""
import nfl_data_py as nfl
import pandas as pd

print("\n" + "="*100)
print("DIRECT NFLVERSE CHECK - December 2, 2025")
print("="*100)

# 1. Check what seasons have play-by-play data
print("\n1. TESTING PLAY-BY-PLAY DATA AVAILABILITY:")
print("   Attempting to download 2025 season...")

try:
    pbp_2025 = nfl.import_pbp_data([2025])
    print(f"   ✅ SUCCESS - Downloaded {len(pbp_2025):,} plays for 2025")
    
    # Check what weeks exist
    weeks = sorted(pbp_2025['week'].unique())
    print(f"   Weeks available: {weeks}")
    
    # Check latest game
    latest = pbp_2025.sort_values('game_id', ascending=False).iloc[0]
    print(f"   Latest game: {latest['game_id']}")
    
except Exception as e:
    print(f"   ❌ FAILED - {type(e).__name__}: {str(e)[:200]}")
    print("\n   Trying 2024 to verify nflverse is working...")
    try:
        pbp_2024 = nfl.import_pbp_data([2024])
        print(f"   ✅ 2024 works - {len(pbp_2024):,} plays")
        print(f"   → 2025 data not uploaded yet by nflverse")
    except Exception as e2:
        print(f"   ❌ 2024 also fails - nflverse might be down")

# 2. Check schedules (separate from play-by-play)
print("\n2. TESTING SCHEDULE DATA:")
try:
    schedules = nfl.import_schedules([2025])
    print(f"   ✅ Schedule data available - {len(schedules)} games")
    
    # Check latest completed game
    completed = schedules[schedules['home_score'].notna()]
    if len(completed) > 0:
        latest_week = completed['week'].max()
        latest_games = completed[completed['week'] == latest_week]
        print(f"   Latest completed week: Week {latest_week} ({len(latest_games)} games)")
    
except Exception as e:
    print(f"   ❌ FAILED - {e}")

# 3. Check weekly data (team stats)
print("\n3. TESTING WEEKLY TEAM DATA:")
try:
    weekly = nfl.import_weekly_data([2025])
    print(f"   ✅ Weekly data available - {len(weekly)} team-week records")
    
    weeks = sorted(weekly['week'].unique())
    print(f"   Weeks with data: {weeks}")
    
    # Check if EPA exists in weekly data
    if 'epa' in weekly.columns or 'total_epa' in weekly.columns:
        print(f"   ✅ EPA data exists in weekly stats")
    else:
        print(f"   ❌ No EPA in weekly data - columns: {list(weekly.columns[:20])}")
    
except Exception as e:
    print(f"   ❌ FAILED - {e}")

print("\n" + "="*100)
print("CONCLUSION:")
print("="*100)
