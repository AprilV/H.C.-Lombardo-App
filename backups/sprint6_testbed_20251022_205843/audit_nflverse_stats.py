"""
NFLVerse Available Stats Audit
Check what stats are actually available vs what we need
"""
import nfl_data_py as nfl
import pandas as pd

print("\n" + "="*70)
print("NFLVERSE AVAILABLE STATS AUDIT")
print("="*70)

# Test 1: What's in schedules (games + betting)
print("\n[1] SCHEDULE DATA (Games + Betting Lines)")
print("-" * 70)
try:
    schedule = nfl.import_schedules([2024])
    print(f"Available columns ({len(schedule.columns)} total):")
    for i, col in enumerate(schedule.columns, 1):
        print(f"  {i:2}. {col}")
    
    # Show sample game with all data
    print(f"\nSample game (Week 7) - ALL DATA:")
    game = schedule[schedule['week'] == 7].iloc[0]
    for col in schedule.columns:
        print(f"  {col}: {game[col]}")
    
except Exception as e:
    print(f"Error: {e}")

# Test 2: What's in weekly player stats (can we aggregate to team?)
print("\n" + "="*70)
print("[2] WEEKLY PLAYER STATS (Aggregate to Team)")
print("-" * 70)
try:
    weekly = nfl.import_weekly_data([2024])
    print(f"Available columns ({len(weekly.columns)} total):")
    for i, col in enumerate(weekly.columns, 1):
        print(f"  {i:2}. {col}")
    
    # Check if we can get team-level stats
    print(f"\nSample aggregation - Dallas Cowboys Week 7:")
    dal_w7 = weekly[(weekly['recent_team'] == 'DAL') & (weekly['week'] == 7)]
    
    team_stats = {
        'Passing Yards': dal_w7['passing_yards'].sum(),
        'Passing TDs': dal_w7['passing_tds'].sum(),
        'Interceptions': dal_w7['interceptions'].sum(),
        'Rushing Yards': dal_w7['rushing_yards'].sum(),
        'Rushing TDs': dal_w7['rushing_tds'].sum(),
        'Receiving Yards': dal_w7['receiving_yards'].sum(),
        'Receiving TDs': dal_w7['receiving_tds'].sum(),
        'Sacks Taken': dal_w7['sacks'].sum(),
        'Fumbles Lost': dal_w7['sack_fumbles_lost'].sum()
    }
    
    for stat, value in team_stats.items():
        print(f"  {stat}: {value}")
    
except Exception as e:
    print(f"Error: {e}")

# Test 3: Seasonal data
print("\n" + "="*70)
print("[3] SEASONAL PLAYER STATS")
print("-" * 70)
try:
    seasonal = nfl.import_seasonal_data([2024])
    print(f"Available columns ({len(seasonal.columns)} total):")
    for i, col in enumerate(seasonal.columns, 1):
        print(f"  {i:2}. {col}")
    
except Exception as e:
    print(f"Error: {e}")

# Test 4: Play-by-play (for advanced stats like EPA)
print("\n" + "="*70)
print("[4] PLAY-BY-PLAY DATA (Advanced Stats - EPA, Success Rate)")
print("-" * 70)
print("Testing if we can access play-by-play for EPA...")
try:
    # Get just a few columns to check what's available
    pbp_cols = nfl.see_pbp_cols()
    print(f"Available PBP columns ({len(pbp_cols)} total):")
    
    # Show relevant ones for betting analytics
    important = ['epa', 'success', 'yards_gained', 'play_type', 
                 'posteam_score', 'defteam_score', 'down', 'ydstogo',
                 'third_down_converted', 'fourth_down_converted',
                 'red_zone_play', 'goal_to_go']
    
    print("\nKey betting-relevant columns:")
    for col in important:
        if col in pbp_cols:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} (NOT AVAILABLE)")
    
    print(f"\nNote: Play-by-play has {len(pbp_cols)} columns total.")
    print("Downloading PBP is LARGE - only do when needed for advanced stats.")
    
except Exception as e:
    print(f"Error: {e}")

# Test 5: Team descriptive data
print("\n" + "="*70)
print("[5] TEAM DESCRIPTIVE DATA")
print("-" * 70)
try:
    teams = nfl.import_team_desc()
    print(f"Available columns: {list(teams.columns)}")
    
    dal = teams[teams['team_abbr'] == 'DAL'].iloc[0]
    print(f"\nSample (Dallas Cowboys):")
    for col in teams.columns:
        print(f"  {col}: {dal[col]}")
    
except Exception as e:
    print(f"Error: {e}")

# Test 6: Injuries (if available)
print("\n" + "="*70)
print("[6] INJURY REPORTS")
print("-" * 70)
try:
    injuries = nfl.import_injuries([2024])
    print(f"Available columns: {list(injuries.columns)}")
    print(f"Total injury records: {len(injuries)}")
    
    # Sample
    if len(injuries) > 0:
        print("\nSample injury record:")
        print(injuries.iloc[0])
    
except Exception as e:
    print(f"Error: {e}")

# Test 7: Depth charts
print("\n" + "="*70)
print("[7] DEPTH CHARTS")
print("-" * 70)
try:
    depth = nfl.import_depth_charts([2024])
    print(f"Available columns: {list(depth.columns)}")
    print(f"Total depth chart records: {len(depth)}")
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
print("SUMMARY: What Stats We Can Get")
print("="*70)

summary = """
BASIC STATS (Easy - From Schedules):
✅ Wins/Losses/Ties (calculate from game results)
✅ Points For/Against (home_score, away_score)
✅ Game dates, locations
✅ BETTING LINES (spread, moneyline, total, odds)

OFFENSIVE STATS (Medium - Aggregate from Weekly Player Data):
✅ Passing yards, TDs, INTs
✅ Rushing yards, TDs
✅ Receiving yards, TDs
✅ Sacks taken
✅ Fumbles lost
✅ Total yards (pass + rush)

ADVANCED STATS (Hard - Requires Play-by-Play):
✅ EPA (Expected Points Added)
✅ Success rate
✅ Third/Fourth down conversions
✅ Red zone efficiency
✅ Play-by-play detail
⚠️  Large downloads, slower processing

CONTEXTUAL DATA:
✅ Weather (temp, wind, roof type) - from schedules
✅ Injuries - separate endpoint
✅ Depth charts - separate endpoint
✅ Team info (colors, logos, division)

NOT AVAILABLE (Would need other sources):
❌ Defensive stats as team totals (need to calculate from opponent offense)
❌ Live line movement (only has final lines)
❌ Sharp vs public money percentages
❌ Team travel/rest days (need to calculate)
❌ Opponent-adjusted stats (need to calculate)

CONCLUSION:
We have PLENTY of stats for basic betting analytics:
- Team performance (W-L, points, yards)
- Betting lines (spread, totals, moneyline)
- Game context (weather, injuries)
- Can calculate: point differential, trends, home/away splits

For ADVANCED analytics (Phase 4):
- Can get EPA, success rate from play-by-play
- Need to calculate derived stats ourselves
- Need external sources for line movement tracking
"""

print(summary)
print("="*70 + "\n")
