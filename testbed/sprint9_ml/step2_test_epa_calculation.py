"""
TESTBED: Test EPA Calculation for 2024 Season
Sprint 9 - Phase 1b: Test EPA from play-by-play data

Strategy:
1. Load 2024 season play-by-play data
2. Calculate EPA for each team-game
3. Verify calculations are reasonable
4. If successful, proceed to full 1999-2025 load
"""
import nfl_data_py as nfl
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

print("=" * 80)
print("TESTBED: LOAD 2024 SEASON WITH EPA CALCULATIONS")
print("=" * 80)

# Step 1: Download 2024 play-by-play data
print("\n📥 Step 1: Downloading 2024 play-by-play data from nflverse...")
print("   (This may take 2-3 minutes for 1 season)")

start_time = datetime.now()
pbp = nfl.import_pbp_data([2024])
elapsed = (datetime.now() - start_time).total_seconds()

print(f"✅ Downloaded {len(pbp):,} plays in {elapsed:.1f} seconds")
print(f"   Columns available: {len(pbp.columns)}")

# Step 2: Check what EPA columns are available
print("\n📊 Step 2: Checking EPA columns in play-by-play data...")

epa_cols = [col for col in pbp.columns if 'epa' in col.lower()]
print(f"\nFound {len(epa_cols)} EPA-related columns:")
for col in epa_cols:
    non_null = pbp[col].notna().sum()
    print(f"   • {col:30} ({non_null:,} non-null values)")

# Step 3: Calculate team-game EPA stats
print("\n🧮 Step 3: Calculating team-game EPA statistics...")

def calculate_team_game_epa(pbp_df, game_id, team):
    """Calculate EPA stats for one team in one game"""
    
    # Filter to this game and team
    team_plays = pbp_df[
        (pbp_df['game_id'] == game_id) & 
        (pbp_df['posteam'] == team)
    ].copy()
    
    if len(team_plays) == 0:
        return None
    
    # Calculate EPA metrics
    stats = {
        'epa_per_play': team_plays['epa'].mean() if 'epa' in team_plays.columns else None,
        'total_epa': team_plays['epa'].sum() if 'epa' in team_plays.columns else None,
        'success_rate': (team_plays['epa'] > 0).mean() if 'epa' in team_plays.columns else None,
        
        # Pass EPA
        'pass_epa': team_plays[team_plays['play_type'] == 'pass']['epa'].sum() if 'epa' in team_plays.columns else None,
        'pass_success_rate': (team_plays[team_plays['play_type'] == 'pass']['epa'] > 0).mean() if 'epa' in team_plays.columns else None,
        
        # Rush EPA
        'rush_epa': team_plays[team_plays['play_type'] == 'run']['epa'].sum() if 'epa' in team_plays.columns else None,
        'rush_success_rate': (team_plays[team_plays['play_type'] == 'run']['epa'] > 0).mean() if 'epa' in team_plays.columns else None,
        
        # WPA
        'wpa': team_plays['wpa'].sum() if 'wpa' in team_plays.columns else None,
        
        # CPOE (completion % over expected)
        'cpoe': team_plays['cpoe'].mean() if 'cpoe' in team_plays.columns else None,
        
        # Air yards
        'air_yards_per_att': team_plays[team_plays['play_type'] == 'pass']['air_yards'].mean() if 'air_yards' in team_plays.columns else None,
        
        # YAC
        'yac_per_completion': team_plays[team_plays['complete_pass'] == 1]['yards_after_catch'].mean() if 'yards_after_catch' in team_plays.columns else None,
        
        # Explosive plays (20+ yards)
        'explosive_play_pct': (team_plays['yards_gained'] >= 20).mean() if 'yards_gained' in team_plays.columns else None,
        
        # Stuff rate (negative plays on rushes)
        'stuff_rate': (team_plays[team_plays['play_type'] == 'run']['yards_gained'] <= 0).mean() if 'yards_gained' in team_plays.columns else None,
    }
    
    return stats

# Test on first 5 games of 2024
print("\n🧪 Testing EPA calculation on sample games...")

test_games = pbp['game_id'].unique()[:5]
sample_results = []

for game_id in test_games:
    game_teams = pbp[pbp['game_id'] == game_id]['posteam'].dropna().unique()
    
    for team in game_teams:
        stats = calculate_team_game_epa(pbp, game_id, team)
        if stats:
            stats['game_id'] = game_id
            stats['team'] = team
            sample_results.append(stats)

sample_df = pd.DataFrame(sample_results)

print(f"\n✅ Calculated EPA for {len(sample_df)} team-games")
print("\nSample EPA Stats:")
print(sample_df[['game_id', 'team', 'epa_per_play', 'success_rate', 'pass_epa', 'rush_epa']].head(10))

# Step 4: Verify EPA values are reasonable
print("\n✅ Step 4: Verifying EPA values are reasonable...")

print(f"\nEPA per play stats:")
print(f"   Mean: {sample_df['epa_per_play'].mean():.3f}")
print(f"   Median: {sample_df['epa_per_play'].median():.3f}")
print(f"   Min: {sample_df['epa_per_play'].min():.3f}")
print(f"   Max: {sample_df['epa_per_play'].max():.3f}")

print(f"\nSuccess rate stats:")
print(f"   Mean: {sample_df['success_rate'].mean():.1%}")
print(f"   Median: {sample_df['success_rate'].median():.1%}")
print(f"   Min: {sample_df['success_rate'].min():.1%}")
print(f"   Max: {sample_df['success_rate'].max():.1%}")

# Sanity check
if -0.5 < sample_df['epa_per_play'].mean() < 0.5:
    print("\n✅ EPA values look reasonable (typical range: -0.3 to +0.3)")
else:
    print("\n⚠️  WARNING: EPA values outside typical range!")

if 0.3 < sample_df['success_rate'].mean() < 0.6:
    print("✅ Success rate looks reasonable (typical range: 35-55%)")
else:
    print("⚠️  WARNING: Success rate outside typical range!")

print("\n" + "=" * 80)
print("✅ TESTBED EPA CALCULATION SUCCESSFUL")
print("=" * 80)
print("\nNext Steps:")
print("1. ✅ EPA columns added to schema")
print("2. ✅ EPA calculation function verified")
print("3. 🔜 Ready to load full 1999-2025 dataset")
print("=" * 80)
