#!/usr/bin/env python3
"""
H.C. LOMBARDO APP - HISTORICAL GAME DATA LOADER
===============================================================================
Purpose: Load historical NFL game data (2022-2025) into HCL schema
Source: nflverse data via nfl_data_py library
Tables Populated: hcl.games, hcl.team_game_stats
Reference: PHASE2_IMPLEMENTATION_PLAN.md

Usage:
    python ingest_historical_games.py --testbed --seasons 2024
    python ingest_historical_games.py --testbed --seasons 2022 2023 2024 2025
    python ingest_historical_games.py --production --seasons 2022 2023 2024 2025

Author: April V. Sykes
Created: October 28, 2025
===============================================================================
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import nfl_data_py as nfl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('historical_data_load.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def get_db_connection(schema_prefix: str = 'hcl_test') -> psycopg2.extensions.connection:
    """
    Create database connection using environment variables.
    
    Args:
        schema_prefix: 'hcl_test' for testbed, 'hcl' for production
        
    Returns:
        psycopg2 connection object
    """
    import os
    
    # Only load .env file if environment variables aren't already set
    # (GitHub Actions sets them directly, local development uses .env)
    if not os.getenv('DB_HOST'):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            logger.warning("python-dotenv not installed, using environment variables only")
    
    try:
        # Connect to EC2 PostgreSQL database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'nfl_analytics'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD')
        )
        logger.info(f"Connected to database: {os.getenv('DB_NAME')}")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


def load_schedules(conn, seasons: List[int], schema: str = 'hcl_test') -> int:
    """
    Load game schedule data into games table.
    
    Args:
        conn: Database connection
        seasons: List of seasons to load (e.g., [2022, 2023, 2024])
        schema: Database schema ('hcl_test' or 'hcl')
        
    Returns:
        Number of games inserted
    """
    logger.info(f"Loading schedules for seasons: {seasons}")
    
    try:
        # Fetch schedule data from nflverse
        schedules = nfl.import_schedules(seasons)
        logger.info(f"Fetched {len(schedules)} games from nflverse")
        
        # Helper function to convert values safely
        def convert_val(val):
            """Convert numpy types to Python types, handle NaN"""
            import pandas as pd
            if pd.isna(val):
                return None
            if hasattr(val, 'item'):  # numpy type
                return val.item()
            return val
        
        # Prepare insert data
        games_data = []
        for _, row in schedules.iterrows():
            # Combine gameday and gametime to create proper timestamp
            kickoff = None
            if row.get('gameday') and row.get('gametime'):
                try:
                    kickoff = f"{row['gameday']} {row['gametime']}:00"
                except:
                    kickoff = None
            
            game_data = (
                row['game_id'],
                int(row['season']),
                int(row['week']),
                convert_val(row.get('gameday')),
                kickoff,
                row['home_team'],
                row['away_team'],
                convert_val(row.get('stadium')),
                None,  # city (not in nflverse)
                None,  # state (not in nflverse)
                None,  # timezone (not in nflverse)
                row.get('game_type') != 'REG',  # is_postseason
                convert_val(row.get('home_score')),
                convert_val(row.get('away_score')),
                
                # Betting Lines (10 columns)
                convert_val(row.get('spread_line')),
                convert_val(row.get('total_line')),
                convert_val(row.get('home_moneyline')),
                convert_val(row.get('away_moneyline')),
                convert_val(row.get('home_spread_odds')),
                convert_val(row.get('away_spread_odds')),
                convert_val(row.get('over_odds')),
                convert_val(row.get('under_odds')),
                
                # Weather (4 columns)
                convert_val(row.get('roof')),
                convert_val(row.get('surface')),
                convert_val(row.get('temp')),
                convert_val(row.get('wind')),
                
                # Context (9 columns)
                convert_val(row.get('away_rest')),
                convert_val(row.get('home_rest')),
                bool(convert_val(row.get('div_game'))) if convert_val(row.get('div_game')) is not None else None,  # Convert to boolean
                convert_val(row.get('overtime')),
                convert_val(row.get('referee')),
                convert_val(row.get('away_coach')),
                convert_val(row.get('home_coach')),
                convert_val(row.get('away_qb_name')),
                convert_val(row.get('home_qb_name'))
            )
            games_data.append(game_data)
        
        # Insert into database using UPSERT
        insert_sql = f"""
            INSERT INTO {schema}.games (
                game_id, season, week, game_date, kickoff_time_utc,
                home_team, away_team, stadium, city, state, timezone,
                is_postseason, home_score, away_score,
                spread_line, total_line, home_moneyline, away_moneyline,
                home_spread_odds, away_spread_odds, over_odds, under_odds,
                roof, surface, temp, wind,
                away_rest, home_rest, is_divisional_game, overtime,
                referee, away_coach, home_coach, away_qb_name, home_qb_name
            ) VALUES %s
            ON CONFLICT (game_id) DO UPDATE SET
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score,
                spread_line = EXCLUDED.spread_line,
                total_line = EXCLUDED.total_line,
                home_moneyline = EXCLUDED.home_moneyline,
                away_moneyline = EXCLUDED.away_moneyline,
                home_spread_odds = EXCLUDED.home_spread_odds,
                away_spread_odds = EXCLUDED.away_spread_odds,
                over_odds = EXCLUDED.over_odds,
                under_odds = EXCLUDED.under_odds,
                roof = EXCLUDED.roof,
                surface = EXCLUDED.surface,
                temp = EXCLUDED.temp,
                wind = EXCLUDED.wind,
                away_rest = EXCLUDED.away_rest,
                home_rest = EXCLUDED.home_rest,
                is_divisional_game = EXCLUDED.is_divisional_game,
                overtime = EXCLUDED.overtime,
                referee = EXCLUDED.referee,
                away_coach = EXCLUDED.away_coach,
                home_coach = EXCLUDED.home_coach,
                away_qb_name = EXCLUDED.away_qb_name,
                home_qb_name = EXCLUDED.home_qb_name,
                updated_at = NOW()
        """
        
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, games_data)
            conn.commit()
        
        logger.info(f"Inserted {len(games_data)} games into {schema}.games")
        return len(games_data)
        
    except Exception as e:
        logger.error(f"Failed to load schedules: {e}")
        conn.rollback()
        raise


def calculate_team_game_stats(pbp_data, game_id: str, team: str, opponent: str, 
                              is_home: bool, season: int, week: int) -> Dict[str, Any]:
    """
    Calculate comprehensive team statistics from play-by-play data for a single game.
    
    Args:
        pbp_data: Play-by-play DataFrame filtered for this game
        game_id: Unique game identifier
        team: Team abbreviation (e.g., 'KC', 'BAL')
        opponent: Opponent abbreviation
        is_home: True if team is home team
        season: Season year
        week: Week number
        
    Returns:
        Dictionary of statistics for this team in this game
    """
    # Filter plays for this team (possessing team)
    team_plays = pbp_data[pbp_data['posteam'] == team].copy()
    opp_plays = pbp_data[pbp_data['posteam'] == opponent].copy()
    
    # Initialize stats dictionary
    stats = {
        'game_id': game_id,
        'team': team,
        'opponent': opponent,
        'is_home': is_home,
        'season': season,
        'week': week
    }
    
    try:
        # Scoring
        stats['points'] = int(team_plays['total_home_score' if is_home else 'total_away_score'].iloc[-1]) if len(team_plays) > 0 else 0
        stats['touchdowns'] = len(team_plays[team_plays['touchdown'] == 1])
        
        # Field Goals
        fg_attempts = team_plays[(team_plays['play_type'] == 'field_goal')]
        stats['field_goals_att'] = len(fg_attempts)
        stats['field_goals_made'] = len(fg_attempts[fg_attempts['field_goal_result'] == 'made'])
        
        # Offensive Totals
        stats['total_yards'] = int(team_plays['yards_gained'].sum())
        stats['passing_yards'] = int(team_plays[team_plays['play_type'] == 'pass']['yards_gained'].sum())
        stats['rushing_yards'] = int(team_plays[team_plays['play_type'] == 'run']['yards_gained'].sum())
        stats['plays'] = len(team_plays[(team_plays['play_type'].isin(['pass', 'run']))])
        stats['yards_per_play'] = round(stats['total_yards'] / stats['plays'], 2) if stats['plays'] > 0 else 0.0
        
        # Passing Stats
        pass_plays = team_plays[team_plays['play_type'] == 'pass']
        stats['completions'] = len(pass_plays[pass_plays['complete_pass'] == 1])
        stats['passing_att'] = len(pass_plays[(pass_plays['pass_attempt'] == 1)])
        stats['completion_pct'] = round((stats['completions'] / stats['passing_att'] * 100), 1) if stats['passing_att'] > 0 else 0.0
        stats['passing_tds'] = len(pass_plays[(pass_plays['touchdown'] == 1)])
        stats['interceptions'] = len(pass_plays[pass_plays['interception'] == 1])
        stats['sacks_taken'] = len(pass_plays[pass_plays['sack'] == 1])
        stats['sack_yards_lost'] = abs(int(pass_plays[pass_plays['sack'] == 1]['yards_gained'].sum()))
        
        # QB Rating (NFL Passer Rating formula)
        if stats['passing_att'] > 0:
            a = ((stats['completions'] / stats['passing_att']) - 0.3) * 5
            b = ((stats['passing_yards'] / stats['passing_att']) - 3) * 0.25
            c = (stats['passing_tds'] / stats['passing_att']) * 20
            d = 2.375 - ((stats['interceptions'] / stats['passing_att']) * 25)
            
            # Clamp each component between 0 and 2.375
            a = max(0, min(a, 2.375))
            b = max(0, min(b, 2.375))
            c = max(0, min(c, 2.375))
            d = max(0, min(d, 2.375))
            
            stats['qb_rating'] = round(((a + b + c + d) / 6) * 100, 1)
        else:
            stats['qb_rating'] = None
        
        # Rushing Stats
        rush_plays = team_plays[team_plays['play_type'] == 'run']
        stats['rushing_att'] = len(rush_plays)
        stats['yards_per_carry'] = round(stats['rushing_yards'] / stats['rushing_att'], 2) if stats['rushing_att'] > 0 else 0.0
        stats['rushing_tds'] = len(rush_plays[rush_plays['touchdown'] == 1])
        
        # Third Down Efficiency
        third_down_plays = team_plays[team_plays['down'] == 3]
        stats['third_down_att'] = len(third_down_plays)
        stats['third_down_conv'] = len(third_down_plays[third_down_plays['first_down'] == 1])
        stats['third_down_pct'] = round((stats['third_down_conv'] / stats['third_down_att'] * 100), 1) if stats['third_down_att'] > 0 else 0.0
        
        # Fourth Down Efficiency
        fourth_down_plays = team_plays[team_plays['down'] == 4]
        stats['fourth_down_att'] = len(fourth_down_plays)
        stats['fourth_down_conv'] = len(fourth_down_plays[fourth_down_plays['first_down'] == 1])
        stats['fourth_down_pct'] = round((stats['fourth_down_conv'] / stats['fourth_down_att'] * 100), 1) if stats['fourth_down_att'] > 0 else 0.0
        
        # Red Zone Efficiency
        red_zone_plays = team_plays[team_plays['yardline_100'] <= 20]
        red_zone_drives = red_zone_plays['drive'].nunique()
        red_zone_tds = len(red_zone_plays[red_zone_plays['touchdown'] == 1])
        stats['red_zone_att'] = red_zone_drives
        stats['red_zone_conv'] = red_zone_tds
        stats['red_zone_pct'] = round((red_zone_tds / red_zone_drives * 100), 1) if red_zone_drives > 0 else 0.0
        
        # Special Teams
        punts = team_plays[team_plays['play_type'] == 'punt']
        stats['punt_count'] = len(punts)
        stats['punt_avg_yards'] = round(punts['kick_distance'].mean(), 1) if len(punts) > 0 else 0.0
        
        # Returns (opponent's kicks returned by this team)
        stats['kickoff_return_yards'] = int(opp_plays[opp_plays['play_type'] == 'kickoff']['return_yards'].sum())
        stats['punt_return_yards'] = int(opp_plays[opp_plays['play_type'] == 'punt']['return_yards'].sum())
        
        # Turnovers
        stats['fumbles_lost'] = len(team_plays[team_plays['fumble_lost'] == 1])
        stats['turnovers'] = stats['interceptions'] + stats['fumbles_lost']
        
        # Penalties
        penalties = team_plays[team_plays['penalty'] == 1]
        stats['penalties'] = len(penalties)
        stats['penalty_yards'] = int(penalties['penalty_yards'].sum())
        
        # Time of Possession
        stats['time_of_possession_sec'] = int(team_plays['game_seconds_remaining'].count() * 40)  # Approximate
        total_game_seconds = 3600  # 60 minutes
        stats['time_of_possession_pct'] = round((stats['time_of_possession_sec'] / total_game_seconds * 100), 1)
        
        # Advanced Metrics
        stats['drives'] = team_plays['drive'].nunique()
        
        # Early Down Success Rate (1st/2nd down plays gaining 50%+ of needed yards)
        early_downs = team_plays[team_plays['down'].isin([1, 2])]
        if len(early_downs) > 0:
            successful_early = early_downs[early_downs['yards_gained'] >= (early_downs['ydstogo'] * 0.5)]
            stats['early_down_success_rate'] = round((len(successful_early) / len(early_downs) * 100), 1)
        else:
            stats['early_down_success_rate'] = 0.0
        
        # Starting Field Position (average)
        drive_starts = team_plays.groupby('drive')['yardline_100'].first()
        stats['starting_field_pos_yds'] = round(100 - drive_starts.mean(), 1) if len(drive_starts) > 0 else 50.0
        
        # Game Result
        if stats['points'] > opp_plays['total_home_score' if not is_home else 'total_away_score'].iloc[-1] if len(opp_plays) > 0 else 0:
            stats['result'] = 'W'
        elif stats['points'] < opp_plays['total_home_score' if not is_home else 'total_away_score'].iloc[-1] if len(opp_plays) > 0 else 0:
            stats['result'] = 'L'
        else:
            stats['result'] = 'T'
            
    except Exception as e:
        logger.warning(f"Error calculating stats for {team} in {game_id}: {e}")
        # Fill in default values for failed calculations
        for key in stats:
            if key not in ['game_id', 'team', 'opponent', 'is_home', 'season', 'week', 'result']:
                if stats.get(key) is None:
                    stats[key] = 0 if isinstance(stats.get(key, 0), int) else 0.0
    
    return stats


def load_team_game_stats(conn, seasons: List[int], schema: str = 'hcl_test') -> int:
    """
    Load team-game statistics from play-by-play data.
    
    Args:
        conn: Database connection
        seasons: List of seasons to load
        schema: Database schema ('hcl_test' or 'hcl')
        
    Returns:
        Number of team-game records inserted
    """
    logger.info(f"Loading team-game stats for seasons: {seasons}")
    total_records = 0
    
    try:
        # Fetch play-by-play data from nflverse
        logger.info("Fetching play-by-play data from nflverse... (this may take a few minutes)")
        pbp_data = nfl.import_pbp_data(seasons)
        logger.info(f"Fetched {len(pbp_data)} plays")
        
        # Get unique games
        games = pbp_data[['game_id', 'season', 'week', 'home_team', 'away_team']].drop_duplicates()
        logger.info(f"Processing {len(games)} unique games")
        
        # Process each game
        all_stats = []
        for idx, game in games.iterrows():
            game_id = game['game_id']
            season = game['season']
            week = game['week']
            home_team = game['home_team']
            away_team = game['away_team']
            
            # Filter play-by-play for this game
            game_pbp = pbp_data[pbp_data['game_id'] == game_id]
            
            # Calculate stats for home team
            home_stats = calculate_team_game_stats(
                game_pbp, game_id, home_team, away_team, True, season, week
            )
            all_stats.append(home_stats)
            
            # Calculate stats for away team
            away_stats = calculate_team_game_stats(
                game_pbp, game_id, away_team, home_team, False, season, week
            )
            all_stats.append(away_stats)
            
            if (idx + 1) % 50 == 0:
                logger.info(f"Processed {idx + 1}/{len(games)} games...")
        
        logger.info(f"Calculated stats for {len(all_stats)} team-game records")
        
        # Prepare insert data (convert numpy types to Python types)
        insert_data = []
        for stats in all_stats:
            def convert_val(val, default):
                """Convert numpy types to Python types"""
                if val is None:
                    return default
                # Handle numpy types
                if hasattr(val, 'item'):
                    return val.item()
                return val
            
            record = (
                stats['game_id'], stats['team'], stats['opponent'], stats['is_home'],
                stats['season'], stats['week'],
                convert_val(stats.get('points'), 0), convert_val(stats.get('touchdowns'), 0),
                convert_val(stats.get('field_goals_made'), 0), convert_val(stats.get('field_goals_att'), 0),
                convert_val(stats.get('total_yards'), 0), convert_val(stats.get('passing_yards'), 0),
                convert_val(stats.get('rushing_yards'), 0), convert_val(stats.get('plays'), 0),
                convert_val(stats.get('yards_per_play'), 0.0),
                convert_val(stats.get('completions'), 0), convert_val(stats.get('passing_att'), 0),
                convert_val(stats.get('completion_pct'), 0.0), convert_val(stats.get('passing_tds'), 0),
                convert_val(stats.get('interceptions'), 0), convert_val(stats.get('sacks_taken'), 0),
                convert_val(stats.get('sack_yards_lost'), 0), convert_val(stats.get('qb_rating'), None),
                convert_val(stats.get('rushing_att'), 0), convert_val(stats.get('yards_per_carry'), 0.0),
                convert_val(stats.get('rushing_tds'), 0),
                convert_val(stats.get('third_down_conv'), 0), convert_val(stats.get('third_down_att'), 0),
                convert_val(stats.get('third_down_pct'), 0.0),
                convert_val(stats.get('fourth_down_conv'), 0), convert_val(stats.get('fourth_down_att'), 0),
                convert_val(stats.get('fourth_down_pct'), 0.0),
                convert_val(stats.get('red_zone_conv'), 0), convert_val(stats.get('red_zone_att'), 0),
                convert_val(stats.get('red_zone_pct'), 0.0),
                convert_val(stats.get('punt_count'), 0), convert_val(stats.get('punt_avg_yards'), 0.0),
                convert_val(stats.get('kickoff_return_yards'), 0), convert_val(stats.get('punt_return_yards'), 0),
                convert_val(stats.get('turnovers'), 0), convert_val(stats.get('fumbles_lost'), 0),
                convert_val(stats.get('penalties'), 0), convert_val(stats.get('penalty_yards'), 0),
                convert_val(stats.get('time_of_possession_sec'), 0), convert_val(stats.get('time_of_possession_pct'), 0.0),
                convert_val(stats.get('drives'), 0), convert_val(stats.get('early_down_success_rate'), 0.0),
                convert_val(stats.get('starting_field_pos_yds'), 50.0),
                stats.get('result', 'L')
            )
            insert_data.append(record)
        
        # Insert into database using UPSERT
        insert_sql = f"""
            INSERT INTO {schema}.team_game_stats (
                game_id, team, opponent, is_home, season, week,
                points, touchdowns, field_goals_made, field_goals_att,
                total_yards, passing_yards, rushing_yards, plays, yards_per_play,
                completions, passing_att, completion_pct, passing_tds, interceptions,
                sacks_taken, sack_yards_lost, qb_rating,
                rushing_att, yards_per_carry, rushing_tds,
                third_down_conv, third_down_att, third_down_pct,
                fourth_down_conv, fourth_down_att, fourth_down_pct,
                red_zone_conv, red_zone_att, red_zone_pct,
                punt_count, punt_avg_yards, kickoff_return_yards, punt_return_yards,
                turnovers, fumbles_lost, penalties, penalty_yards,
                time_of_possession_sec, time_of_possession_pct,
                drives, early_down_success_rate, starting_field_pos_yds,
                result
            ) VALUES %s
            ON CONFLICT (game_id, team) DO UPDATE SET
                opponent = EXCLUDED.opponent,
                is_home = EXCLUDED.is_home,
                points = EXCLUDED.points,
                touchdowns = EXCLUDED.touchdowns,
                field_goals_made = EXCLUDED.field_goals_made,
                field_goals_att = EXCLUDED.field_goals_att,
                total_yards = EXCLUDED.total_yards,
                passing_yards = EXCLUDED.passing_yards,
                rushing_yards = EXCLUDED.rushing_yards,
                plays = EXCLUDED.plays,
                yards_per_play = EXCLUDED.yards_per_play,
                completions = EXCLUDED.completions,
                passing_att = EXCLUDED.passing_att,
                completion_pct = EXCLUDED.completion_pct,
                passing_tds = EXCLUDED.passing_tds,
                interceptions = EXCLUDED.interceptions,
                sacks_taken = EXCLUDED.sacks_taken,
                sack_yards_lost = EXCLUDED.sack_yards_lost,
                qb_rating = EXCLUDED.qb_rating,
                rushing_att = EXCLUDED.rushing_att,
                yards_per_carry = EXCLUDED.yards_per_carry,
                rushing_tds = EXCLUDED.rushing_tds,
                third_down_conv = EXCLUDED.third_down_conv,
                third_down_att = EXCLUDED.third_down_att,
                third_down_pct = EXCLUDED.third_down_pct,
                fourth_down_conv = EXCLUDED.fourth_down_conv,
                fourth_down_att = EXCLUDED.fourth_down_att,
                fourth_down_pct = EXCLUDED.fourth_down_pct,
                red_zone_conv = EXCLUDED.red_zone_conv,
                red_zone_att = EXCLUDED.red_zone_att,
                red_zone_pct = EXCLUDED.red_zone_pct,
                punt_count = EXCLUDED.punt_count,
                punt_avg_yards = EXCLUDED.punt_avg_yards,
                kickoff_return_yards = EXCLUDED.kickoff_return_yards,
                punt_return_yards = EXCLUDED.punt_return_yards,
                turnovers = EXCLUDED.turnovers,
                fumbles_lost = EXCLUDED.fumbles_lost,
                penalties = EXCLUDED.penalties,
                penalty_yards = EXCLUDED.penalty_yards,
                time_of_possession_sec = EXCLUDED.time_of_possession_sec,
                time_of_possession_pct = EXCLUDED.time_of_possession_pct,
                drives = EXCLUDED.drives,
                early_down_success_rate = EXCLUDED.early_down_success_rate,
                starting_field_pos_yds = EXCLUDED.starting_field_pos_yds,
                result = EXCLUDED.result,
                updated_at = NOW()
        """
        
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, insert_data, page_size=100)
            conn.commit()
        
        total_records = len(insert_data)
        logger.info(f"Inserted {total_records} team-game records into {schema}.team_game_stats")
        return total_records
        
    except Exception as e:
        logger.error(f"Failed to load team-game stats: {e}")
        conn.rollback()
        raise


def load_team_game_stats_simple(conn, seasons: List[int], schema: str = 'hcl_test') -> int:
    """
    Load basic team-game stats from games table (simplified version without pbp data).
    
    Args:
        conn: Database connection
        seasons: List of seasons to load
        schema: Database schema
        
    Returns:
        Number of team-game records inserted
    """
    logger.info(f"Loading team-game stats (simple) for seasons: {seasons}")
    
    try:
        with conn.cursor() as cur:
            # Insert home team stats
            cur.execute(f"""
                INSERT INTO {schema}.team_game_stats 
                (game_id, team, opponent, is_home, season, week, points, result, created_at, updated_at)
                SELECT 
                    game_id,
                    home_team,
                    away_team,
                    true,
                    season,
                    week,
                    home_score,
                    CASE 
                        WHEN home_score > away_score THEN 'W'
                        WHEN home_score < away_score THEN 'L'
                        ELSE 'T'
                    END,
                    NOW(),
                    NOW()
                FROM {schema}.games
                WHERE season = ANY(%s) AND home_score IS NOT NULL
                ON CONFLICT (game_id, team) DO UPDATE SET
                    points = EXCLUDED.points,
                    result = EXCLUDED.result,
                    updated_at = NOW()
            """, (seasons,))
            home_count = cur.rowcount
            
            # Insert away team stats
            cur.execute(f"""
                INSERT INTO {schema}.team_game_stats 
                (game_id, team, opponent, is_home, season, week, points, result, created_at, updated_at)
                SELECT 
                    game_id,
                    away_team,
                    home_team,
                    false,
                    season,
                    week,
                    away_score,
                    CASE 
                        WHEN away_score > home_score THEN 'W'
                        WHEN away_score < home_score THEN 'L'
                        ELSE 'T'
                    END,
                    NOW(),
                    NOW()
                FROM {schema}.games
                WHERE season = ANY(%s) AND away_score IS NOT NULL
                ON CONFLICT (game_id, team) DO UPDATE SET
                    points = EXCLUDED.points,
                    result = EXCLUDED.result,
                    updated_at = NOW()
            """, (seasons,))
            away_count = cur.rowcount
            
            conn.commit()
            total = home_count + away_count
            logger.info(f"Inserted {total} team-game records into {schema}.team_game_stats")
            return total
            
    except Exception as e:
        logger.error(f"Failed to load team-game stats: {e}")
        conn.rollback()
        raise


def refresh_views(conn, schema: str = 'hcl_test'):
    """
    Refresh materialized views after data load.
    
    Args:
        conn: Database connection
        schema: Database schema
    """
    logger.info("Refreshing materialized views...")
    try:
        with conn.cursor() as cur:
            cur.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {schema}.v_game_matchup_display")
            conn.commit()
        logger.info("Views refreshed successfully")
    except Exception as e:
        logger.error(f"Failed to refresh views: {e}")
        conn.rollback()


def verify_data_load(conn, schema: str = 'hcl_test'):
    """
    Run verification queries to check data integrity.
    
    Args:
        conn: Database connection
        schema: Database schema
    """
    logger.info("Running verification queries...")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check table counts
            cur.execute(f"SELECT COUNT(*) as count FROM {schema}.games")
            games_count = cur.fetchone()['count']
            logger.info(f"  Games table: {games_count} records")
            
            cur.execute(f"SELECT COUNT(*) as count FROM {schema}.team_game_stats")
            stats_count = cur.fetchone()['count']
            logger.info(f"  Team-game stats table: {stats_count} records")
            
            # Check by season
            cur.execute(f"""
                SELECT season, COUNT(*) as game_count 
                FROM {schema}.games 
                GROUP BY season 
                ORDER BY season DESC
            """)
            season_counts = cur.fetchall()
            logger.info("  Games by season:")
            for row in season_counts:
                logger.info(f"    {row['season']}: {row['game_count']} games")
            
            # Check for data quality issues
            cur.execute(f"""
                SELECT COUNT(*) as count 
                FROM {schema}.team_game_stats 
                WHERE points IS NULL OR total_yards IS NULL
            """)
            null_count = cur.fetchone()['count']
            if null_count > 0:
                logger.warning(f"  Found {null_count} records with NULL critical stats")
            else:
                logger.info("  No NULL critical stats found (good!)")
                
    except Exception as e:
        logger.error(f"Verification failed: {e}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Load historical NFL game data into HCL schema')
    parser.add_argument('--testbed', action='store_true', help='Load into testbed schema (hcl_test)')
    parser.add_argument('--production', action='store_true', help='Load into production schema (hcl)')
    parser.add_argument('--seasons', nargs='+', type=int, required=True, help='Seasons to load (e.g., 2022 2023 2024)')
    parser.add_argument('--skip-schedules', action='store_true', help='Skip schedule loading (if already loaded)')
    parser.add_argument('--skip-stats', action='store_true', help='Skip stats loading (if already loaded)')
    
    args = parser.parse_args()
    
    # Determine schema
    if args.testbed and args.production:
        logger.error("Cannot specify both --testbed and --production")
        sys.exit(1)
    
    schema = 'hcl_test' if args.testbed else 'hcl'
    
    logger.info("="*80)
    logger.info("H.C. LOMBARDO APP - HISTORICAL DATA LOADER")
    logger.info("="*80)
    logger.info(f"Schema: {schema}")
    logger.info(f"Seasons: {args.seasons}")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("="*80)
    
    # Connect to database
    conn = get_db_connection(schema)
    
    try:
        # Load schedules (game metadata)
        if not args.skip_schedules:
            games_loaded = load_schedules(conn, args.seasons, schema)
            logger.info(f"✓ Loaded {games_loaded} games")
        else:
            logger.info("Skipped schedule loading")
        
        # Load team-game statistics (using simple method from games table)
        if not args.skip_stats:
            try:
                stats_loaded = load_team_game_stats_simple(conn, args.seasons, schema)
                logger.info(f"✓ Loaded {stats_loaded} team-game records")
            except Exception as e:
                logger.warning(f"Stats loading failed: {e}")
                logger.info("Continuing without team stats...")
        else:
            logger.info("Skipped stats loading")
        
        # Refresh materialized views
        refresh_views(conn, schema)
        logger.info("✓ Refreshed materialized views")
        
        # Verify data
        verify_data_load(conn, schema)
        
        logger.info("="*80)
        logger.info("DATA LOAD COMPLETE!")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"Data load failed: {e}")
        sys.exit(1)
    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == '__main__':
    main()
