import nfl_data_py as nfl
import pandas as pd

print("Checking what nflverse has for 2025 Week 1 NE game...\n")

# Load play-by-play data
pbp = nfl.import_pbp_data([2025])

# Filter to NE games
ne_games = pbp[(pbp['home_team'] == 'NE') | (pbp['away_team'] == 'NE')]

# Get Week 1
week1 = ne_games[ne_games['week'] == 1]

if len(week1) > 0:
    game_id = week1.iloc[0]['game_id']
    print(f"Game ID: {game_id}")
    print(f"Total plays: {len(week1)}")
    
    # Calculate passing yards
    pass_plays = week1[week1['play_type'] == 'pass']
    ne_pass_plays = pass_plays[(pass_plays['posteam'] == 'NE')]
    pass_yards = ne_pass_plays['yards_gained'].sum()
    
    # Calculate rushing yards  
    rush_plays = week1[week1['play_type'] == 'run']
    ne_rush_plays = rush_plays[(rush_plays['posteam'] == 'NE')]
    rush_yards = ne_rush_plays['yards_gained'].sum()
    
    print(f"\nNE Week 1 calculated from play-by-play:")
    print(f"  Passing yards: {pass_yards}")
    print(f"  Rushing yards: {rush_yards}")
    print(f"  Total yards: {pass_yards + rush_yards}")
else:
    print("No Week 1 data found!")

# Also check team stats view
print("\n\nChecking nflverse weekly team stats...")
try:
    weekly = nfl.import_weekly_data([2025])
    ne_weekly = weekly[(weekly['recent_team'] == 'NE') & (weekly['week'] == 1)]
    
    if len(ne_weekly) > 0:
        print("\nNE Week 1 from weekly stats:")
        cols = ['week', 'passing_yards', 'rushing_yards', 'opponent_team']
        print(ne_weekly[cols].to_string(index=False))
    else:
        print("No weekly stats found")
except Exception as e:
    print(f"Error loading weekly stats: {e}")
