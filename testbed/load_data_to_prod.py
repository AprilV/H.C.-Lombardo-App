"""
Load 2025 NFL data into PRODUCTION database
Sprint 7 - Production Integration
"""

import sys
import os

# Update database config to use production
sys.path.insert(0, os.path.dirname(__file__))

# Import the loader module
import nflverse_data_loader as loader

# Override database config to production
loader.DB_CONFIG['database'] = 'nfl_analytics'  # Production database

print("="*70)
print("LOADING DATA INTO PRODUCTION DATABASE")
print("="*70)
print(f"Database: {loader.DB_CONFIG['database']}")
print(f"Season: 2025, Weeks: 1-7")
print("="*70)

# Load the data
pbp_df = loader.load_play_by_play(years=[2025], weeks=list(range(1, 8)))

if pbp_df is not None and not pbp_df.empty:
    print(f"\n✅ Loaded {len(pbp_df):,} plays from nflverse")
    
    # Aggregate to team-game stats
    team_stats = loader.aggregate_team_game_stats(pbp_df)
    print(f"✅ Aggregated to {len(team_stats)} team-game records")
    
    # Load schedules for games table
    print("\nLoading schedules...")
    import nfl_data_py as nfl
    schedules = nfl.import_schedules([2025])
    schedules_filtered = schedules[schedules['week'].isin(list(range(1, 8)))].copy()
    print(f"✅ Loaded {len(schedules_filtered)} games")
    
    # Save to production database
    loader.save_to_database_hcl(team_stats, schedules_filtered, db_config=loader.DB_CONFIG)
    print("\n✅ DATA LOADED INTO PRODUCTION DATABASE!")
    print("="*70)
else:
    print("\n❌ Failed to load data from nflverse")
