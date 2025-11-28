#!/usr/bin/env python3
"""
EMERGENCY FIX: Load 2025 season to Render
Uses nflverse to get current 2025 season games and loads them to Render database
"""

import psycopg2
import nfl_data_py as nfl
from psycopg2.extras import execute_values
from datetime import datetime

RENDER_DB_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

def main():
    print("\n" + "="*80)
    print("🚨 EMERGENCY: LOADING 2025 SEASON TO RENDER")
    print("="*80)
    
    # Connect to Render
    print("\n🌐 Connecting to Render database...")
    try:
        conn = psycopg2.connect(RENDER_DB_URL)
        cur = conn.cursor()
        print("   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Get 2025 schedule from nflverse
    print("\n📥 Fetching 2025 season from nflverse...")
    try:
        schedules = nfl.import_schedules([2025])
        print(f"   ✅ Got {len(schedules)} games")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Clear existing 2025 games
    print("\n🗑️ Clearing old 2025 data...")
    cur.execute("DELETE FROM hcl.team_game_stats WHERE season = 2025")
    cur.execute("DELETE FROM hcl.games WHERE season = 2025")
    conn.commit()
    print(f"   ✅ Cleared")
    
    # Insert games
    print(f"\n1️⃣ Inserting {len(schedules)} games...")
    inserted = 0
    for _, row in schedules.iterrows():
        try:
            cur.execute("""
                INSERT INTO hcl.games (
                    game_id, season, week, game_date, kickoff_time_utc,
                    home_team, away_team, stadium, city, state,
                    is_postseason, home_score, away_score,
                    spread_line, total_line,
                    home_moneyline, away_moneyline,
                    roof, surface, temp, wind,
                    away_rest, home_rest, is_divisional_game,
                    overtime, referee, away_coach, home_coach
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s
                )
                ON CONFLICT (game_id) DO NOTHING
            """, (
                row['game_id'],
                int(row['season']),
                int(row['week']),
                row.get('gameday'),
                f"{row['gameday']} {row['gametime']}:00" if row.get('gameday') and row.get('gametime') else None,
                row['home_team'],
                row['away_team'],
                row.get('stadium'),
                None,  # city
                None,  # state
                row.get('game_type') != 'REG',
                int(row['home_score']) if row.get('home_score') and not pd.isna(row['home_score']) else None,
                int(row['away_score']) if row.get('away_score') and not pd.isna(row['away_score']) else None,
                float(row['spread_line']) if row.get('spread_line') and not pd.isna(row['spread_line']) else None,
                float(row['total_line']) if row.get('total_line') and not pd.isna(row['total_line']) else None,
                float(row['home_moneyline']) if row.get('home_moneyline') and not pd.isna(row['home_moneyline']) else None,
                float(row['away_moneyline']) if row.get('away_moneyline') and not pd.isna(row['away_moneyline']) else None,
                row.get('roof'),
                row.get('surface'),
                float(row['temp']) if row.get('temp') and not pd.isna(row['temp']) else None,
                float(row['wind']) if row.get('wind') and not pd.isna(row['wind']) else None,
                int(row['away_rest']) if row.get('away_rest') and not pd.isna(row['away_rest']) else None,
                int(row['home_rest']) if row.get('home_rest') and not pd.isna(row['home_rest']) else None,
                bool(row['div_game']) if row.get('div_game') and not pd.isna(row['div_game']) else None,
                int(row['overtime']) if row.get('overtime') and not pd.isna(row['overtime']) else 0,
                row.get('referee'),
                row.get('away_coach'),
                row.get('home_coach')
            ))
            inserted += 1
        except Exception as e:
            print(f"   ⚠️  Failed to insert {row['game_id']}: {e}")
    
    conn.commit()
    print(f"   ✅ Inserted {inserted} games")
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM hcl.games WHERE season = 2025")
    count = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM hcl.games 
        WHERE season = 2025 AND home_score IS NOT NULL
    """)
    completed = cur.fetchone()[0]
    
    print(f"\n✅ COMPLETE!")
    print(f"   • Total 2025 games: {count}")
    print(f"   • Completed games: {completed}")
    
    if completed > 0:
        cur.execute("""
            SELECT MIN(week), MAX(week)
            FROM hcl.games 
            WHERE season = 2025 AND home_score IS NOT NULL
        """)
        min_week, max_week = cur.fetchone()
        print(f"   • Weeks with scores: {min_week} to {max_week}")
    
    conn.close()
    return True


if __name__ == "__main__":
    import pandas as pd
    success = main()
    if success:
        print("\n🎉 Now refresh your website!")
        print("   https://h-c-lombardo-app.onrender.com")
    exit(0 if success else 1)
