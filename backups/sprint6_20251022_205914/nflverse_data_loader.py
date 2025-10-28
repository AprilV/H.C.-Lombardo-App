"""
NFLVERSE DATA LOADER - SPRINT 6
Load play-by-play data from nflverse and aggregate to team-game level stats.

All 47 columns for betting analytics MVP:
- Identifiers (7)
- Base Volume & Splits (8)
- Scoring & Pressure/TOs (8)
- Efficiency Advanced (8)
- Situational Red Zone/3rd/4th (6)
- Context (4)
- Rolling Form (6)

Data Source: nfl-data-py (nflfastR play-by-play)
Output: PostgreSQL hcl.games + hcl.team_game_stats tables

Usage:
    python testbed/nflverse_data_loader.py --seasons 2024 --weeks 7 --output database
    python testbed/nflverse_data_loader.py --seasons 2022 2023 2024 --output csv
"""

import nfl_data_py as nfl
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import sys
import argparse
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'nfl_analytics_test',  # Default to test database
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def load_play_by_play(years=[2022, 2023, 2024], weeks=None):
    """Load play-by-play data from nflverse."""
    print(f"\n{'='*70}")
    print(f"LOADING PLAY-BY-PLAY DATA")
    print(f"{'='*70}")
    print(f"Seasons: {years}")
    if weeks:
        print(f"Weeks: {weeks}")
    print("This may take 2-3 minutes (large dataset)...\n")
    
    try:
        pbp = nfl.import_pbp_data(years=years)
        print(f"✅ Loaded {len(pbp):,} play-by-play records")
        
        # Filter to specific weeks if requested
        if weeks:
            pbp = pbp[pbp['week'].isin(weeks)]
            print(f"   Filtered to weeks {weeks}: {len(pbp):,} records")
        
        print(f"   Columns: {len(pbp.columns)}")
        print(f"   Memory: {pbp.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        return pbp
    except Exception as e:
        print(f"❌ Error loading PBP: {e}")
        sys.exit(1)


def aggregate_team_game_stats(pbp):
    """Aggregate play-by-play to team-game level with all 47 columns."""
    print(f"\n{'='*70}")
    print(f"AGGREGATING TO TEAM-GAME LEVEL")
    print(f"{'='*70}")
    
    # Step 1: Filter to offensive plays only
    print("\n[1/9] Filtering to offensive plays...")
    grp = pbp[pbp.posteam.notna()].copy()
    print(f"   {len(grp):,} offensive plays")
    
    # Step 2: Create helper columns
    print("[2/9] Creating helper columns...")
    grp["rush_yards"] = grp["yards_gained"].where(grp["rush_attempt"] == 1, 0)
    grp["pass_yards"] = grp["yards_gained"].where(grp["pass_attempt"] == 1, 0)
    
    # Step 3: Main aggregation
    print("[3/9] Aggregating base stats...")
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
    print(f"   {len(team_game):,} team-game records")
    
    # Step 4: Calculate derived fields
    print("[4/9] Calculating efficiency metrics...")
    team_game["success_rate"] = team_game["success_plays"] / team_game["plays"].clip(lower=1)
    team_game["yards_per_play"] = team_game["yards_total"] / team_game["plays"].clip(lower=1)
    team_game["turnovers"] = team_game["interceptions"] + team_game["fumbles_lost"]
    
    # Step 5: Add points & opponent
    print("[5/9] Adding points and opponent...")
    scores = (
        pbp.groupby(["game_id", "season", "week", "posteam", "defteam"], dropna=False)
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
    
    # Step 6: Pass/Rush EPA per play
    print("[6/9] Calculating EPA splits...")
    rush = (
        grp[grp["rush_attempt"] == 1]
        .groupby(["game_id", "posteam"])
        .epa.mean()
        .reset_index()
        .rename(columns={"posteam": "team_id", "epa": "rush_epa_per_play"})
    )
    pas = (
        grp[grp["pass_attempt"] == 1]
        .groupby(["game_id", "posteam"])
        .epa.mean()
        .reset_index()
        .rename(columns={"posteam": "team_id", "epa": "pass_epa_per_play"})
    )
    team_game = (
        team_game
        .merge(rush, on=["game_id", "team_id"], how="left")
        .merge(pas, on=["game_id", "team_id"], how="left")
    )
    
    # Step 7: Situational stats (3rd/4th down & red zone)
    print("[7/9] Calculating situational stats...")
    
    # 3rd down
    third_down = (
        grp[grp["down"] == 3]
        .groupby(["game_id", "posteam"])
        .agg(
            third_down_att=("play_id", "count"),
            third_down_conv=("third_down_converted", "sum")
        )
        .reset_index()
        .rename(columns={"posteam": "team_id"})
    )
    
    # 4th down
    fourth_down = (
        grp[grp["down"] == 4]
        .groupby(["game_id", "posteam"])
        .agg(
            fourth_down_att=("play_id", "count"),
            fourth_down_conv=("fourth_down_converted", "sum")
        )
        .reset_index()
        .rename(columns={"posteam": "team_id"})
    )
    
    # Red zone
    red_zone = (
        grp[grp["yardline_100"] <= 20]
        .groupby(["game_id", "posteam"])
        .agg(
            red_zone_trips=("fixed_drive", "nunique"),
            red_zone_tds=("touchdown", "sum")
        )
        .reset_index()
        .rename(columns={"posteam": "team_id"})
    )
    red_zone["red_zone_td_rate"] = red_zone["red_zone_tds"] / red_zone["red_zone_trips"].clip(lower=1)
    
    # Merge situational stats
    team_game = (
        team_game
        .merge(third_down, on=["game_id", "team_id"], how="left")
        .merge(fourth_down, on=["game_id", "team_id"], how="left")
        .merge(red_zone[["game_id", "team_id", "red_zone_trips", "red_zone_td_rate"]], 
               on=["game_id", "team_id"], how="left")
    )
    
    # Fill NaN with 0 for teams with no attempts
    team_game[["third_down_att", "third_down_conv", "fourth_down_att", "fourth_down_conv", "red_zone_trips"]] = \
        team_game[["third_down_att", "third_down_conv", "fourth_down_att", "fourth_down_conv", "red_zone_trips"]].fillna(0)
    team_game["red_zone_td_rate"] = team_game["red_zone_td_rate"].fillna(0)
    
    # Step 8: Add context from schedules
    print("[8/9] Adding game context (home/away, rest)...")
    years = team_game["season"].unique().tolist()
    schedules = nfl.import_schedules(years=years)
    
    # Home context
    home_context = schedules[["game_id", "home_team", "home_rest", "gameday"]].copy()
    home_context["is_home"] = True
    home_context = home_context.rename(columns={
        "home_team": "team_id",
        "home_rest": "days_rest",
        "gameday": "game_date"
    })
    
    # Away context
    away_context = schedules[["game_id", "away_team", "away_rest", "gameday"]].copy()
    away_context["is_home"] = False
    away_context = away_context.rename(columns={
        "away_team": "team_id",
        "away_rest": "days_rest",
        "gameday": "game_date"
    })
    
    # Combine and merge
    context = pd.concat([home_context, away_context])
    team_game = team_game.merge(context, on=["game_id", "team_id"], how="left")
    
    # Derive short_week and off_bye
    team_game["short_week"] = team_game["days_rest"] < 6
    team_game["off_bye"] = team_game["days_rest"] >= 13
    team_game["home_field"] = team_game["is_home"]  # Alias
    
    # Step 9: Rolling averages (momentum)
    print("[9/9] Calculating rolling averages (momentum)...")
    team_game = team_game.sort_values(["team_id", "season", "week"])
    
    # Last 3 games
    team_game["epa_l3"] = team_game.groupby("team_id")["epa_per_play"].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    team_game["ppg_for_l3"] = team_game.groupby("team_id")["points_for"].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    team_game["ppg_against_l3"] = team_game.groupby("team_id")["points_against"].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    team_game["ypp_l3"] = team_game.groupby("team_id")["yards_per_play"].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    team_game["sr_l3"] = team_game.groupby("team_id")["success_rate"].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    
    # Last 5 games
    team_game["epa_l5"] = team_game.groupby("team_id")["epa_per_play"].transform(
        lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
    )
    
    print(f"\n✅ Aggregation complete!")
    print(f"   Final columns: {len(team_game.columns)}")
    print(f"   Team-game records: {len(team_game):,}")
    
    return team_game


def verify_data_quality(team_game):
    """Check for data quality issues."""
    print(f"\n{'='*70}")
    print(f"DATA QUALITY CHECKS")
    print(f"{'='*70}\n")
    
    issues = []
    
    # Check for zero plays
    zero_plays = team_game[team_game["plays"] == 0]
    if len(zero_plays) > 0:
        issues.append(f"⚠️  {len(zero_plays)} games with 0 plays")
    else:
        print("✅ No games with 0 plays")
    
    # Check for missing points
    missing_points = team_game[team_game["points_for"].isna()]
    if len(missing_points) > 0:
        issues.append(f"⚠️  {len(missing_points)} games with missing points")
    else:
        print("✅ All games have points_for")
    
    # Check for missing opponent
    missing_opp = team_game[team_game["opponent_id"].isna()]
    if len(missing_opp) > 0:
        issues.append(f"⚠️  {len(missing_opp)} games with missing opponent_id")
    else:
        print("✅ All games have opponent_id")
    
    # Check for extreme EPA values (> 1000 or < -1000)
    extreme_epa = team_game[(team_game["epa_total"] > 1000) | (team_game["epa_total"] < -1000)]
    if len(extreme_epa) > 0:
        issues.append(f"⚠️  {len(extreme_epa)} games with extreme EPA values")
    else:
        print("✅ No extreme EPA values")
    
    # Check date coverage
    print(f"\n📅 Date Coverage:")
    print(f"   First game: {team_game['game_date'].min()}")
    print(f"   Last game: {team_game['game_date'].max()}")
    
    # Season breakdown
    print(f"\n📊 Games per Season:")
    season_counts = team_game.groupby("season").size()
    for season, count in season_counts.items():
        print(f"   {season}: {count:,} team-games")
    
    # Sample stats
    print(f"\n📈 Sample Stats (Averages):")
    print(f"   Points/game: {team_game['points_for'].mean():.1f}")
    print(f"   Yards/game: {team_game['yards_total'].mean():.1f}")
    print(f"   Yards/play: {team_game['yards_per_play'].mean():.2f}")
    print(f"   EPA/play: {team_game['epa_per_play'].mean():.3f}")
    print(f"   Success rate: {team_game['success_rate'].mean():.3f}")
    
    if issues:
        print(f"\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"\n✅ ALL DATA QUALITY CHECKS PASSED!")
    
    return len(issues) == 0


def save_to_csv(team_game, output_file="team_game_stats.csv"):
    """Save aggregated data to CSV."""
    print(f"\n{'='*70}")
    print(f"SAVING TO CSV")
    print(f"{'='*70}\n")
    
    # Select final columns in correct order
    final_columns = [
        'game_id', 'team_id', 'season', 'week', 'opponent_id', 'is_home', 'game_date',
        'plays', 'pass_attempts', 'rush_attempts', 'yards_total', 'yards_pass', 
        'yards_rush', 'points_for', 'points_against', 'sacks', 'interceptions', 
        'fumbles_lost', 'turnovers', 'yards_per_play', 'success_plays', 'success_rate', 
        'epa_total', 'epa_per_play', 'rush_epa_per_play', 'pass_epa_per_play',
        'red_zone_trips', 'red_zone_td_rate', 'third_down_att', 'third_down_conv',
        'home_field', 'days_rest', 'short_week', 'off_bye',
        'epa_l3', 'epa_l5', 'ppg_for_l3', 'ppg_against_l3', 'ypp_l3', 'sr_l3'
    ]
    
    # Select only columns that exist
    available_cols = [col for col in final_columns if col in team_game.columns]
    df_to_save = team_game[available_cols].copy()
    
    # Convert data types
    df_to_save['game_date'] = pd.to_datetime(df_to_save['game_date'])
    
    df_to_save.to_csv(output_file, index=False)
    print(f"✅ Saved to {output_file}")
    print(f"   {len(df_to_save):,} rows × {len(df_to_save.columns)} columns")
    
    return True


def save_to_database_hcl(team_game, schedules, db_config=None):
    """
    Save aggregated data to PostgreSQL hcl schema.
    Populates both hcl.games and hcl.team_game_stats tables with UPSERT.
    """
    print(f"\n{'='*70}")
    print(f"SAVING TO DATABASE (hcl schema)")
    print(f"{'='*70}\n")
    
    if db_config is None:
        db_config = DB_CONFIG
    
    print(f"Connecting to {db_config['database']}...")
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # ====================================================================
        # STEP 1: Populate hcl.games table
        # ====================================================================
        print("\n[1/2] Populating hcl.games table...")
        
        # Get unique games from schedules
        games_data = schedules[[
            'game_id', 'season', 'week', 'game_type', 'gameday', 
            'gametime', 'home_team', 'away_team', 'home_score', 'away_score',
            'stadium', 'location'
        ]].copy()
        
        # Parse location into city, state
        games_data['city'] = games_data['location'].apply(lambda x: x.split(',')[0].strip() if pd.notna(x) and ',' in x else None)
        games_data['state'] = games_data['location'].apply(lambda x: x.split(',')[-1].strip() if pd.notna(x) and ',' in x else None)
        
        # Combine gameday + gametime for kickoff_time_utc
        games_data['kickoff_time_utc'] = pd.to_datetime(
            games_data['gameday'].astype(str) + ' ' + games_data['gametime'].fillna('00:00:00')
        )
        
        # Determine if postseason
        games_data['is_postseason'] = games_data['game_type'] != 'REG'
        
        # UPSERT into hcl.games
        games_insert_sql = """
            INSERT INTO hcl.games (
                game_id, season, week, game_type, game_date, kickoff_time_utc,
                home_team, away_team, home_score, away_score, stadium, city, state, is_postseason
            ) VALUES %s
            ON CONFLICT (game_id) 
            DO UPDATE SET
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score,
                updated_at = CURRENT_TIMESTAMP
        """
        
        games_values = [
            (
                row['game_id'], row['season'], row['week'], row['game_type'],
                row['gameday'], row['kickoff_time_utc'],
                row['home_team'], row['away_team'], row['home_score'], row['away_score'],
                row['stadium'], row['city'], row['state'], row['is_postseason']
            )
            for _, row in games_data.iterrows()
        ]
        
        execute_values(cursor, games_insert_sql, games_values)
        print(f"   ✅ Upserted {len(games_values)} games")
        
        # ====================================================================
        # STEP 2: Populate hcl.team_game_stats table
        # ====================================================================
        print("\n[2/2] Populating hcl.team_game_stats table...")
        
        # Map columns from team_game to hcl.team_game_stats schema
        stats_insert_sql = """
            INSERT INTO hcl.team_game_stats (
                game_id, team, season, week, opponent, is_home,
                points_scored, points_allowed, won,
                epa_per_play, epa_per_play_defense, success_rate, success_rate_defense,
                total_plays, total_yards, yards_per_play,
                passing_yards, passing_attempts, passing_completions, passing_touchdowns, interceptions,
                rushing_yards, rushing_attempts, rushing_touchdowns,
                first_downs, third_down_attempts, third_down_conversions, third_down_rate,
                fourth_down_attempts, fourth_down_conversions, fourth_down_rate,
                red_zone_attempts, red_zone_scores, red_zone_touchdowns, red_zone_efficiency,
                turnovers_lost, turnovers_gained, turnover_differential,
                penalties, penalty_yards,
                time_of_possession_seconds, explosive_plays,
                epa_last_3_games, yards_per_play_last_3, ppg_last_3_games,
                touchdowns, field_goals_made, field_goals_attempted,
                extra_points_made, two_point_conversions
            ) VALUES %s
            ON CONFLICT (game_id, team)
            DO UPDATE SET
                points_scored = EXCLUDED.points_scored,
                points_allowed = EXCLUDED.points_allowed,
                epa_per_play = EXCLUDED.epa_per_play,
                success_rate = EXCLUDED.success_rate,
                yards_per_play = EXCLUDED.yards_per_play,
                updated_at = CURRENT_TIMESTAMP
        """
        
        # Prepare values (handle missing columns gracefully)
        stats_values = []
        for _, row in team_game.iterrows():
            stats_values.append((
                row['game_id'],
                row['team_id'],
                row['season'],
                row['week'],
                row['opponent_id'],
                row['is_home'],
                # Points
                row.get('points_for', 0),
                row.get('points_against', 0),
                row.get('points_for', 0) > row.get('points_against', 0),  # won
                # EPA
                row.get('epa_per_play', 0),
                None,  # epa_per_play_defense - TODO from defensive stats
                row.get('success_rate', 0),
                None,  # success_rate_defense - TODO
                # Volume
                row.get('plays', 0),
                row.get('yards_total', 0),
                row.get('yards_per_play', 0),
                # Passing
                row.get('yards_pass', 0),
                row.get('pass_attempts', 0),
                None,  # completions - TODO
                None,  # pass TDs - TODO
                row.get('interceptions', 0),
                # Rushing
                row.get('yards_rush', 0),
                row.get('rush_attempts', 0),
                None,  # rush TDs - TODO
                # Conversions
                None,  # first_downs - TODO
                row.get('third_down_att', 0),
                row.get('third_down_conv', 0),
                row.get('third_down_conv', 0) / max(row.get('third_down_att', 1), 1),
                row.get('fourth_down_att', 0),
                row.get('fourth_down_conv', 0),
                row.get('fourth_down_conv', 0) / max(row.get('fourth_down_att', 1), 1),
                # Red zone
                row.get('red_zone_trips', 0),
                None,  # red_zone_scores - TODO
                None,  # red_zone_tds - TODO
                row.get('red_zone_td_rate', 0),
                # Turnovers
                row.get('turnovers', 0),
                None,  # turnovers_gained - TODO (defensive stat)
                None,  # turnover_differential - TODO
                # Penalties
                None,  # penalties - TODO
                None,  # penalty_yards - TODO
                # Misc
                None,  # time_of_possession - TODO
                None,  # explosive_plays - TODO
                # Momentum
                row.get('epa_l3', None),
                row.get('ypp_l3', None),
                row.get('ppg_for_l3', None),
                # Scoring breakdown
                None,  # touchdowns - TODO
                None,  # FG made - TODO
                None,  # FG att - TODO
                None,  # XP made - TODO
                None   # 2pt conv - TODO
            ))
        
        execute_values(cursor, stats_insert_sql, stats_values)
        print(f"   ✅ Upserted {len(stats_values)} team-game records")
        
        conn.commit()
        print(f"\n✅ Database save complete!")
        
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
    
    return True


def main():
    """Main execution flow."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Load NFL play-by-play data and save to database or CSV'
    )
    parser.add_argument(
        '--seasons',
        type=int,
        nargs='+',
        default=[2024],
        help='Seasons to load (e.g., --seasons 2022 2023 2024)'
    )
    parser.add_argument(
        '--weeks',
        type=int,
        nargs='+',
        default=None,
        help='Specific weeks to load (e.g., --weeks 7 8) - optional'
    )
    parser.add_argument(
        '--output',
        choices=['database', 'csv', 'both'],
        default='csv',
        help='Output destination (default: csv)'
    )
    parser.add_argument(
        '--db-name',
        type=str,
        default='nfl_analytics_test',
        help='Database name (default: nfl_analytics_test)'
    )
    parser.add_argument(
        '--csv-file',
        type=str,
        default='team_game_stats.csv',
        help='CSV output filename (default: team_game_stats.csv)'
    )
    
    args = parser.parse_args()
    
    # Update database config with custom db name
    db_config = DB_CONFIG.copy()
    db_config['database'] = args.db_name
    
    print(f"\n{'#'*70}")
    print(f"# NFLVERSE DATA LOADER - SPRINT 6")
    print(f"# Betting Analytics - Historical Data Storage")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}")
    print(f"\nConfiguration:")
    print(f"  Seasons: {args.seasons}")
    print(f"  Weeks: {args.weeks if args.weeks else 'All'}")
    print(f"  Output: {args.output}")
    print(f"  Database: {args.db_name}")
    
    try:
        # Load play-by-play
        pbp = load_play_by_play(years=args.seasons, weeks=args.weeks)
        
        # Aggregate to team-game level
        team_game = aggregate_team_game_stats(pbp)
        
        # Verify data quality
        quality_ok = verify_data_quality(team_game)
        
        if not quality_ok:
            print("\n⚠️  Data quality issues detected. Review before saving.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        # Load schedules for database save (need game metadata)
        schedules = nfl.import_schedules(years=args.seasons)
        if args.weeks:
            schedules = schedules[schedules['week'].isin(args.weeks)]
        
        # Save based on output option
        if args.output in ['database', 'both']:
            save_to_database_hcl(team_game, schedules, db_config)
        
        if args.output in ['csv', 'both']:
            save_to_csv(team_game, args.csv_file)
        
        print(f"\n{'#'*70}")
        print(f"# DATA LOAD COMPLETE!")
        print(f"# Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
