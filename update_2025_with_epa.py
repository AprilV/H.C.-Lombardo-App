#!/usr/bin/env python3
"""
Update database with EPA calculations for 2025 season ONLY
Uses nflverse play-by-play data to calculate EPA stats
Updates existing team_game_stats records with EPA values
"""

import psycopg2
from psycopg2.extras import execute_values
import nfl_data_py as nfl
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("\n" + "="*80)
    print("📊 UPDATING DATABASE WITH EPA CALCULATIONS FOR 2025")
    print("="*80)
    
    # Connect to database
    print("\n🌐 Connecting to database...")
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    print("   ✅ Connected")
    
    # Get 2025 play-by-play data
    print("\n📥 Downloading 2025 play-by-play data from nflverse...")
    print("   (This may take 1-2 minutes)...")
    pbp = nfl.import_pbp_data([2025])
    print(f"   ✅ Downloaded {len(pbp):,} plays")
    
    # Get all games from database
    print("\n📋 Getting 2025 games from database...")
    cur.execute("""
        SELECT DISTINCT game_id, home_team, away_team, season, week
        FROM hcl.games
        WHERE season = 2025
        ORDER BY week, game_id
    """)
    games = cur.fetchall()
    print(f"   ✅ Found {len(games)} games")
    
    # Calculate EPA for each game
    print("\n🧮 Calculating EPA stats for each team-game...")
    updates = []
    
    for game_id, home_team, away_team, season, week in games:
        # Get plays for this game
        game_plays = pbp[pbp['game_id'] == game_id].copy()
        
        if len(game_plays) == 0:
            print(f"   ⚠️  No play-by-play data for {game_id}")
            continue
        
        # Calculate for home team
        home_plays = game_plays[game_plays['posteam'] == home_team]
        if len(home_plays) > 0 and 'epa' in home_plays.columns:
            home_epa = {
                'game_id': game_id,
                'team': home_team,
                'epa_per_play': float(home_plays['epa'].mean()) if home_plays['epa'].notna().any() else None,
                'success_rate': float((home_plays['epa'] > 0).mean()) if home_plays['epa'].notna().any() else None,
                'pass_epa': float(home_plays[home_plays['play_type'] == 'pass']['epa'].sum()) if 'epa' in home_plays else None,
                'rush_epa': float(home_plays[home_plays['play_type'] == 'run']['epa'].sum()) if 'epa' in home_plays else None,
                'total_epa': float(home_plays['epa'].sum()) if home_plays['epa'].notna().any() else None,
            }
            updates.append(home_epa)
        
        # Calculate for away team
        away_plays = game_plays[game_plays['posteam'] == away_team]
        if len(away_plays) > 0 and 'epa' in away_plays.columns:
            away_epa = {
                'game_id': game_id,
                'team': away_team,
                'epa_per_play': float(away_plays['epa'].mean()) if away_plays['epa'].notna().any() else None,
                'success_rate': float((away_plays['epa'] > 0).mean()) if away_plays['epa'].notna().any() else None,
                'pass_epa': float(away_plays[away_plays['play_type'] == 'pass']['epa'].sum()) if 'epa' in away_plays else None,
                'rush_epa': float(away_plays[away_plays['play_type'] == 'run']['epa'].sum()) if 'epa' in away_plays else None,
                'total_epa': float(away_plays['epa'].sum()) if away_plays['epa'].notna().any() else None,
            }
            updates.append(away_epa)
    
    print(f"   ✅ Calculated EPA for {len(updates)} team-game records")
    
    # Update database
    print("\n💾 Updating database with EPA stats...")
    count = 0
    for stats in updates:
        try:
            cur.execute("""
                UPDATE hcl.team_game_stats
                SET 
                    epa_per_play = %s,
                    success_rate = %s,
                    pass_epa = %s,
                    rush_epa = %s,
                    total_epa = %s,
                    updated_at = NOW()
                WHERE game_id = %s AND team = %s
            """, (
                stats['epa_per_play'],
                stats['success_rate'],
                stats['pass_epa'],
                stats['rush_epa'],
                stats['total_epa'],
                stats['game_id'],
                stats['team']
            ))
            count += cur.rowcount
        except Exception as e:
            print(f"   ⚠️  Error updating {stats['game_id']} {stats['team']}: {e}")
    
    conn.commit()
    print(f"   ✅ Updated {count} records")
    
    # Verify
    print("\n✅ Verifying EPA data...")
    cur.execute("""
        SELECT COUNT(*) 
        FROM hcl.team_game_stats 
        WHERE season = 2025 AND epa_per_play IS NOT NULL
    """)
    with_epa = cur.fetchone()[0]
    print(f"   • Records with EPA: {with_epa}")
    
    cur.execute("""
        SELECT team, AVG(epa_per_play) as avg_epa
        FROM hcl.team_game_stats
        WHERE season = 2025 AND epa_per_play IS NOT NULL
        GROUP BY team
        ORDER BY avg_epa DESC
        LIMIT 5
    """)
    print(f"\n   Top 5 teams by EPA/play:")
    for team, avg_epa in cur.fetchall():
        print(f"   {team}: {avg_epa:.4f}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ EPA UPDATE COMPLETE!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
