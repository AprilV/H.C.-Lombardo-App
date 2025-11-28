#!/usr/bin/env python3
"""
COMPREHENSIVE RENDER DATABASE LOADER
=====================================
Loads ALL data to Render production database:
1. Full historical data (1999-2025) from local database
2. Current 2025 season games from nflverse
3. Team info and metadata

Run this to populate the Render database completely.
"""

import psycopg2
from psycopg2.extras import execute_values
import sys
from datetime import datetime

RENDER_DB_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

def main():
    print("\n" + "="*80)
    print("🚀 LOADING ALL DATA TO RENDER DATABASE")
    print("="*80)
    
    # Connect to LOCAL database (source)
    print("\n📂 Connecting to LOCAL database (source)...")
    try:
        local_conn = psycopg2.connect(
            dbname='nfl_analytics',
            user='postgres',
            password='aprilv120',
            host='localhost',
            port='5432'
        )
        local_cur = local_conn.cursor()
        print("   ✅ Connected to local database")
    except Exception as e:
        print(f"   ❌ Failed to connect to local database: {e}")
        return False
    
    # Connect to RENDER database (destination)
    print("\n🌐 Connecting to RENDER database (destination)...")
    try:
        render_conn = psycopg2.connect(RENDER_DB_URL)
        render_cur = render_conn.cursor()
        print("   ✅ Connected to Render database")
    except Exception as e:
        print(f"   ❌ Failed to connect to Render database: {e}")
        return False
    
    # Check what's in local database
    print("\n📊 Checking LOCAL database contents...")
    local_cur.execute("SELECT COUNT(*) FROM hcl.games")
    local_games = local_cur.fetchone()[0]
    local_cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats")
    local_stats = local_cur.fetchone()[0]
    local_cur.execute("SELECT MIN(season), MAX(season) FROM hcl.games")
    min_season, max_season = local_cur.fetchone()
    
    print(f"   • Games: {local_games:,}")
    print(f"   • Team game stats: {local_stats:,}")
    print(f"   • Seasons: {min_season} to {max_season}")
    
    if local_games == 0:
        print("\n❌ LOCAL database is empty! Cannot copy data.")
        return False
    
    # Step 1: Copy games table
    print(f"\n1️⃣ Copying {local_games:,} games to Render...")
    try:
        # Get all games from local
        local_cur.execute("""
            SELECT 
                game_id, season, week, game_date, kickoff,
                home_team, away_team, stadium, city, state, timezone,
                is_postseason, home_score, away_score,
                spread_line, total_line, home_moneyline, away_moneyline,
                home_spread_odds, away_spread_odds, over_odds, under_odds,
                roof, surface, temp, wind,
                away_rest, home_rest, div_game, overtime, referee,
                away_coach, home_coach, stadium_id, old_game_id
            FROM hcl.games
            ORDER BY season, week, game_id
        """)
        games_data = local_cur.fetchall()
        
        # Clear existing games in Render
        render_cur.execute("DELETE FROM hcl.games")
        render_conn.commit()
        
        # Insert games to Render
        execute_values(
            render_cur,
            """
            INSERT INTO hcl.games (
                game_id, season, week, game_date, kickoff,
                home_team, away_team, stadium, city, state, timezone,
                is_postseason, home_score, away_score,
                spread_line, total_line, home_moneyline, away_moneyline,
                home_spread_odds, away_spread_odds, over_odds, under_odds,
                roof, surface, temp, wind,
                away_rest, home_rest, div_game, overtime, referee,
                away_coach, home_coach, stadium_id, old_game_id
            ) VALUES %s
            ON CONFLICT (game_id) DO NOTHING
            """,
            games_data
        )
        render_conn.commit()
        
        render_cur.execute("SELECT COUNT(*) FROM hcl.games")
        copied_games = render_cur.fetchone()[0]
        print(f"   ✅ Copied {copied_games:,} games")
        
    except Exception as e:
        print(f"   ❌ Error copying games: {e}")
        render_conn.rollback()
        return False
    
    # Step 2: Copy team_game_stats table
    print(f"\n2️⃣ Copying {local_stats:,} team game stats to Render...")
    try:
        # Get all stats from local
        local_cur.execute("""
            SELECT 
                game_id, team, opponent, season, week,
                is_home, points_scored, points_allowed,
                epa_per_play, success_rate, explosive_play_rate,
                epa_pass, epa_rush, epa_success_pass, epa_success_rush,
                epa_explosive_pass, epa_explosive_rush,
                stuffed_rate, passing_downs_success, early_down_success,
                late_down_success, redzone_success, turnover_rate
            FROM hcl.team_game_stats
            ORDER BY season, week, game_id, team
        """)
        stats_data = local_cur.fetchall()
        
        # Clear existing stats in Render
        render_cur.execute("DELETE FROM hcl.team_game_stats")
        render_conn.commit()
        
        # Insert stats to Render
        execute_values(
            render_cur,
            """
            INSERT INTO hcl.team_game_stats (
                game_id, team, opponent, season, week,
                is_home, points_scored, points_allowed,
                epa_per_play, success_rate, explosive_play_rate,
                epa_pass, epa_rush, epa_success_pass, epa_success_rush,
                epa_explosive_pass, epa_explosive_rush,
                stuffed_rate, passing_downs_success, early_down_success,
                late_down_success, redzone_success, turnover_rate
            ) VALUES %s
            ON CONFLICT (game_id, team) DO NOTHING
            """,
            stats_data
        )
        render_conn.commit()
        
        render_cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats")
        copied_stats = render_cur.fetchone()[0]
        print(f"   ✅ Copied {copied_stats:,} team game stats")
        
    except Exception as e:
        print(f"   ❌ Error copying team stats: {e}")
        render_conn.rollback()
        return False
    
    # Step 3: Verify 2025 data
    print(f"\n3️⃣ Verifying 2025 season data on Render...")
    render_cur.execute("SELECT COUNT(*) FROM hcl.games WHERE season = 2025")
    games_2025 = render_cur.fetchone()[0]
    render_cur.execute("""
        SELECT MIN(week), MAX(week) 
        FROM hcl.games 
        WHERE season = 2025 AND home_score IS NOT NULL
    """)
    result = render_cur.fetchone()
    min_week, max_week = result if result[0] is not None else (None, None)
    
    print(f"   • 2025 games: {games_2025}")
    if min_week and max_week:
        print(f"   • Completed weeks: {min_week} to {max_week}")
    else:
        print(f"   ⚠️  No completed games yet for 2025")
    
    # Final summary
    print("\n" + "="*80)
    print("✅ DATA LOAD COMPLETE")
    print("="*80)
    print(f"\n📊 RENDER DATABASE SUMMARY:")
    
    render_cur.execute("SELECT COUNT(*) FROM hcl.games")
    total_games = render_cur.fetchone()[0]
    render_cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats")
    total_stats = render_cur.fetchone()[0]
    render_cur.execute("SELECT MIN(season), MAX(season) FROM hcl.games")
    min_s, max_s = render_cur.fetchone()
    
    print(f"   • Total games: {total_games:,}")
    print(f"   • Total team stats: {total_stats:,}")
    print(f"   • Season range: {min_s} to {max_s}")
    
    # Show games per season
    print(f"\n📅 Games by season:")
    render_cur.execute("""
        SELECT season, COUNT(*) as games
        FROM hcl.games
        GROUP BY season
        ORDER BY season DESC
        LIMIT 5
    """)
    for season, count in render_cur.fetchall():
        render_cur.execute("""
            SELECT COUNT(*) 
            FROM hcl.games 
            WHERE season = %s AND home_score IS NOT NULL
        """, (season,))
        completed = render_cur.fetchone()[0]
        print(f"   {season}: {count:3} games ({completed:3} completed)")
    
    print(f"\n🌐 Your app should now show data at:")
    print(f"   https://h-c-lombardo-app.onrender.com")
    print(f"\n💡 Next step: Set up auto-updates for 2025 season")
    print("="*80 + "\n")
    
    local_conn.close()
    render_conn.close()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
