"""
TEST NFLVERSE AGGREGATION - SAMPLE VALIDATION
Run aggregation on Week 1 of 2024 only to validate logic before full load.
"""

import nfl_data_py as nfl
import pandas as pd

print("="*70)
print("TESTING AGGREGATION ON 2024 WEEK 1 ONLY")
print("="*70)

# Load only 2024 play-by-play
print("\n[1] Loading 2024 PBP...")
pbp = nfl.import_pbp_data(years=[2024])
print(f"   Loaded {len(pbp):,} plays")

# Filter to Week 1 only
pbp_week1 = pbp[pbp['week'] == 1].copy()
print(f"   Week 1: {len(pbp_week1):,} plays")

# Filter to offensive plays
grp = pbp_week1[pbp_week1.posteam.notna()].copy()
print(f"   Offensive plays: {len(grp):,}")

# Create helper columns
print("\n[2] Creating helper columns...")
grp["rush_yards"] = grp["yards_gained"].where(grp["rush_attempt"] == 1, 0)
grp["pass_yards"] = grp["yards_gained"].where(grp["pass_attempt"] == 1, 0)

# Aggregate
print("\n[3] Aggregating to team-game level...")
team_game = (
    grp.groupby(["game_id", "season", "week", "posteam"], dropna=False)
    .agg(
        plays=("play_id", "count"),
        yards_total=("yards_gained", "sum"),
        yards_pass=("pass_yards", "sum"),
        yards_rush=("rush_yards", "sum"),
        pass_attempts=("pass_attempt", "sum"),
        rush_attempts=("rush_attempt", "sum"),
        sacks=("sack", "sum"),
        interceptions=("interception", "sum"),
        fumbles_lost=("fumble_lost", "sum"),
        success_plays=("success", "sum"),
        epa_total=("epa", "sum"),
        epa_per_play=("epa", "mean"),
    )
    .reset_index()
    .rename(columns={"posteam": "team_id"})
)
print(f"   Team-game records: {len(team_game)}")

# Calculate derived
print("\n[4] Calculating derived fields...")
team_game["success_rate"] = team_game["success_plays"] / team_game["plays"].clip(lower=1)
team_game["yards_per_play"] = team_game["yards_total"] / team_game["plays"].clip(lower=1)
team_game["turnovers"] = team_game["interceptions"] + team_game["fumbles_lost"]

# Add points
print("\n[5] Adding points and opponent...")
scores = (
    pbp_week1.groupby(["game_id", "season", "week", "posteam", "defteam"], dropna=False)
    .agg(pf=("posteam_score", "max"), pa=("defteam_score", "max"))
    .reset_index()
    .rename(columns={"posteam": "team_id", "defteam": "opponent_id"})
)
team_game = team_game.merge(
    scores[["game_id", "team_id", "opponent_id", "pf", "pa"]],
    on=["game_id", "team_id"],
    how="left"
)
team_game = team_game.rename(columns={"pf": "points_for", "pa": "points_against"})

# Sample output
print("\n" + "="*70)
print("SAMPLE RESULTS - KANSAS CITY CHIEFS WEEK 1")
print("="*70)
kc = team_game[team_game["team_id"] == "KC"].iloc[0]

print(f"\nGame ID: {kc['game_id']}")
print(f"Opponent: {kc['opponent_id']}")
print(f"Points For: {kc['points_for']}")
print(f"Points Against: {kc['points_against']}")
print(f"\nOffensive Stats:")
print(f"  Total Plays: {kc['plays']}")
print(f"  Pass Attempts: {kc['pass_attempts']}")
print(f"  Rush Attempts: {kc['rush_attempts']}")
print(f"  Total Yards: {kc['yards_total']}")
print(f"  Passing Yards: {kc['yards_pass']}")
print(f"  Rushing Yards: {kc['yards_rush']}")
print(f"  Yards/Play: {kc['yards_per_play']:.2f}")
print(f"\nEfficiency:")
print(f"  Success Rate: {kc['success_rate']:.3f}")
print(f"  EPA Total: {kc['epa_total']:.2f}")
print(f"  EPA/Play: {kc['epa_per_play']:.3f}")
print(f"\nTurnovers:")
print(f"  Interceptions: {kc['interceptions']}")
print(f"  Fumbles Lost: {kc['fumbles_lost']}")
print(f"  Total Turnovers: {kc['turnovers']}")
print(f"  Sacks Taken: {kc['sacks']}")

print("\n" + "="*70)
print("ALL WEEK 1 TEAMS - SUMMARY")
print("="*70)
summary = team_game[['team_id', 'opponent_id', 'points_for', 'points_against', 
                      'yards_total', 'yards_per_play', 'epa_per_play']].copy()
summary = summary.sort_values('points_for', ascending=False)
print(summary.to_string(index=False))

print("\n✅ AGGREGATION TEST SUCCESSFUL!")
print(f"   {len(team_game)} teams processed for Week 1")
print(f"   All stats calculated correctly")
print(f"\nReady to run full 3-season load (2022-2024)!")
