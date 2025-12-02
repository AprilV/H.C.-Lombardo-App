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

# Only load .env if environment variables aren't already set
if not os.getenv('DB_HOST'):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Warning: python-dotenv not installed, using environment variables only")

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
    try:
        pbp = nfl.import_pbp_data([2025])
        print(f"   ✅ Downloaded {len(pbp):,} plays")
    except Exception as e:
        print(f"   ❌ Failed to download play-by-play data: {str(e)[:100]}")
        print("   ⚠️  Play-by-play data may not be available yet for 2025 season")
        print("   ℹ️  This is normal if games just finished - nflverse updates within 24-48 hours")
        print("   🔄 Exiting gracefully - will retry on next run")
        cur.close()
        conn.close()
        return
    
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
            pass_plays = home_plays[home_plays['play_type'] == 'pass']
            rush_plays = home_plays[home_plays['play_type'] == 'run']
            
            home_epa = {
                'game_id': game_id,
                'team': home_team,
                'epa_per_play': float(home_plays['epa'].mean()) if home_plays['epa'].notna().any() else None,
                'success_rate': float((home_plays['success'] == 1).mean() * 100) if 'success' in home_plays.columns and home_plays['success'].notna().any() else None,
                'pass_epa': float(pass_plays['epa'].sum()) if len(pass_plays) > 0 and pass_plays['epa'].notna().any() else None,
                'rush_epa': float(rush_plays['epa'].sum()) if len(rush_plays) > 0 and rush_plays['epa'].notna().any() else None,
                'total_epa': float(home_plays['epa'].sum()) if home_plays['epa'].notna().any() else None,
                'wpa': float(home_plays['wpa'].sum()) if 'wpa' in home_plays.columns and home_plays['wpa'].notna().any() else None,
                'cpoe': float(pass_plays['cpoe'].mean()) if 'cpoe' in pass_plays.columns and len(pass_plays) > 0 and pass_plays['cpoe'].notna().any() else None,
                'air_yards_per_att': float(pass_plays['air_yards'].mean()) if 'air_yards' in pass_plays.columns and len(pass_plays) > 0 and pass_plays['air_yards'].notna().any() else None,
                'yac_per_completion': float(pass_plays[pass_plays['complete_pass'] == 1]['yards_after_catch'].mean()) if 'yards_after_catch' in pass_plays.columns and len(pass_plays[pass_plays['complete_pass'] == 1]) > 0 else None,
                'explosive_play_pct': float(((home_plays['yards_gained'] >= 20) & (home_plays['play_type'].isin(['pass', 'run']))).mean() * 100) if 'yards_gained' in home_plays.columns else None,
                'stuff_rate': float(((rush_plays['yards_gained'] <= 0) & (rush_plays['play_type'] == 'run')).mean() * 100) if len(rush_plays) > 0 else None,
                'pass_success_rate': float((pass_plays['success'] == 1).mean() * 100) if 'success' in pass_plays.columns and len(pass_plays) > 0 and pass_plays['success'].notna().any() else None,
                'rush_success_rate': float((rush_plays['success'] == 1).mean() * 100) if 'success' in rush_plays.columns and len(rush_plays) > 0 and rush_plays['success'].notna().any() else None,
            }
            updates.append(home_epa)
        
        # Calculate for away team
        away_plays = game_plays[game_plays['posteam'] == away_team]
        if len(away_plays) > 0 and 'epa' in away_plays.columns:
            pass_plays = away_plays[away_plays['play_type'] == 'pass']
            rush_plays = away_plays[away_plays['play_type'] == 'run']
            
            away_epa = {
                'game_id': game_id,
                'team': away_team,
                'epa_per_play': float(away_plays['epa'].mean()) if away_plays['epa'].notna().any() else None,
                'success_rate': float((away_plays['success'] == 1).mean() * 100) if 'success' in away_plays.columns and away_plays['success'].notna().any() else None,
                'pass_epa': float(pass_plays['epa'].sum()) if len(pass_plays) > 0 and pass_plays['epa'].notna().any() else None,
                'rush_epa': float(rush_plays['epa'].sum()) if len(rush_plays) > 0 and rush_plays['epa'].notna().any() else None,
                'total_epa': float(away_plays['epa'].sum()) if away_plays['epa'].notna().any() else None,
                'wpa': float(away_plays['wpa'].sum()) if 'wpa' in away_plays.columns and away_plays['wpa'].notna().any() else None,
                'cpoe': float(pass_plays['cpoe'].mean()) if 'cpoe' in pass_plays.columns and len(pass_plays) > 0 and pass_plays['cpoe'].notna().any() else None,
                'air_yards_per_att': float(pass_plays['air_yards'].mean()) if 'air_yards' in pass_plays.columns and len(pass_plays) > 0 and pass_plays['air_yards'].notna().any() else None,
                'yac_per_completion': float(pass_plays[pass_plays['complete_pass'] == 1]['yards_after_catch'].mean()) if 'yards_after_catch' in pass_plays.columns and len(pass_plays[pass_plays['complete_pass'] == 1]) > 0 else None,
                'explosive_play_pct': float(((away_plays['yards_gained'] >= 20) & (away_plays['play_type'].isin(['pass', 'run']))).mean() * 100) if 'yards_gained' in away_plays.columns else None,
                'stuff_rate': float(((rush_plays['yards_gained'] <= 0) & (rush_plays['play_type'] == 'run')).mean() * 100) if len(rush_plays) > 0 else None,
                'pass_success_rate': float((pass_plays['success'] == 1).mean() * 100) if 'success' in pass_plays.columns and len(pass_plays) > 0 and pass_plays['success'].notna().any() else None,
                'rush_success_rate': float((rush_plays['success'] == 1).mean() * 100) if 'success' in rush_plays.columns and len(rush_plays) > 0 and rush_plays['success'].notna().any() else None,
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
                    wpa = %s,
                    cpoe = %s,
                    air_yards_per_att = %s,
                    yac_per_completion = %s,
                    explosive_play_pct = %s,
                    stuff_rate = %s,
                    pass_success_rate = %s,
                    rush_success_rate = %s,
                    updated_at = NOW()
                WHERE game_id = %s AND team = %s
            """, (
                stats['epa_per_play'],
                stats['success_rate'],
                stats['pass_epa'],
                stats['rush_epa'],
                stats['total_epa'],
                stats['wpa'],
                stats['cpoe'],
                stats['air_yards_per_att'],
                stats['yac_per_completion'],
                stats['explosive_play_pct'],
                stats['stuff_rate'],
                stats['pass_success_rate'],
                stats['rush_success_rate'],
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
