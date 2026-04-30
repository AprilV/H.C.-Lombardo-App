#!/usr/bin/env python3
"""Update database with Week 14-16 game data from NFLverse"""
import nfl_data_py as nfl
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'), 
    password=os.getenv('DB_PASSWORD', 'aprilv120'),
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', '5432'))
)
cur = conn.cursor()

# Get schedules and play-by-play
print('Fetching NFLverse data...')
schedules = nfl.import_schedules([2025])
pbp = nfl.import_pbp_data([2025])
pbp_14_16 = pbp[pbp['week'].isin([14,15,16])]

num_games = pbp_14_16['game_id'].nunique()
print(f'Processing {num_games} games...')

updated_stats = 0
for game_id in pbp_14_16['game_id'].unique():
    game_pbp = pbp_14_16[pbp_14_16['game_id'] == game_id]
    week = int(game_pbp['week'].iloc[0])
    
    # Get game info from schedule
    game_sched = schedules[schedules['game_id'] == game_id].iloc[0]
    home_team = game_sched['home_team']
    away_team = game_sched['away_team']
    
    # Process each team
    for team in [home_team, away_team]:
        opponent = away_team if team == home_team else home_team
        is_home = team == home_team
        
        team_pbp = game_pbp[game_pbp['posteam'] == team]
        
        if len(team_pbp) == 0:
            continue
            
        # Calculate stats
        total_yards = int(team_pbp['yards_gained'].fillna(0).sum())
        pass_yards = int(team_pbp[team_pbp['play_type'] == 'pass']['yards_gained'].fillna(0).sum())
        rush_yards = int(team_pbp[team_pbp['play_type'] == 'run']['yards_gained'].fillna(0).sum())
        turnovers = int(len(team_pbp[(team_pbp['interception'] == 1) | (team_pbp['fumble_lost'] == 1)]))
        points = int(team_pbp['posteam_score'].max())
        opponent_score = int(team_pbp['defteam_score'].max())
        result = 'W' if points > opponent_score else ('L' if points < opponent_score else 'T')
        
        cur.execute('''
            INSERT INTO hcl.team_game_stats
            (game_id, season, week, team, opponent, is_home, total_yards, passing_yards, rushing_yards, turnovers, points, result)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (game_id, team)
            DO UPDATE SET
                total_yards = EXCLUDED.total_yards,
                passing_yards = EXCLUDED.passing_yards,
                rushing_yards = EXCLUDED.rushing_yards,
                turnovers = EXCLUDED.turnovers,
                points = EXCLUDED.points,
                result = EXCLUDED.result
        ''', (str(game_id), 2025, week, team, opponent, is_home, total_yards, pass_yards, rush_yards, turnovers, points, result))
        
        updated_stats += 1
        print(f'  Inserted/updated {team} Week {week} vs {opponent}: {total_yards} yards, {points} pts')

conn.commit()
print(f'\n✅ Updated {updated_stats} team game stats for weeks 14-16')
print('Charts should now show data through Week 16!')

cur.close()
conn.close()
