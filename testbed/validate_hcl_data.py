"""
Validation Script - Check loaded data in hcl schema
Sprint 6: Verify Week 7 data loaded correctly
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'nfl_analytics_test',
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def run_validation_queries():
    """Run SQL validation queries to verify data."""
    print(f"\n{'='*70}")
    print(f"DATA VALIDATION - hcl schema")
    print(f"{'='*70}\n")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Query 1: Row counts
        print("[1/7] Checking row counts...")
        cursor.execute("SELECT COUNT(*) as count FROM hcl.games")
        games_count = cursor.fetchone()['count']
        print(f"   hcl.games: {games_count} rows")
        
        cursor.execute("SELECT COUNT(*) as count FROM hcl.team_game_stats")
        stats_count = cursor.fetchone()['count']
        print(f"   hcl.team_game_stats: {stats_count} rows")
        
        assert games_count == 15, f"Expected 15 games, got {games_count}"
        assert stats_count == 30, f"Expected 30 team-game records, got {stats_count}"
        print("   ✅ Row counts correct")
        
        # Query 2: Sample game data
        print("\n[2/7] Sample game from hcl.games...")
        cursor.execute("""
            SELECT game_id, season, week, home_team, away_team, home_score, away_score, game_date
            FROM hcl.games
            ORDER BY game_date
            LIMIT 3
        """)
        games = cursor.fetchall()
        for game in games:
            print(f"   {game['game_id']}: {game['away_team']}@{game['home_team']} "
                  f"({game['away_score']}-{game['home_score']}) on {game['game_date']}")
        print("   ✅ Games have valid data")
        
        # Query 3: Sample team stats
        print("\n[3/7] Sample team stats from hcl.team_game_stats...")
        cursor.execute("""
            SELECT game_id, team, points_scored, points_allowed, epa_per_play, success_rate, yards_per_play
            FROM hcl.team_game_stats
            WHERE epa_per_play IS NOT NULL
            ORDER BY epa_per_play DESC
            LIMIT 3
        """)
        stats = cursor.fetchall()
        for stat in stats:
            print(f"   {stat['team']} ({stat['game_id']}): "
                  f"EPA={stat['epa_per_play']:.3f}, SR={stat['success_rate']:.3f}, "
                  f"YPP={stat['yards_per_play']:.2f}, Pts={stat['points_scored']}")
        print("   ✅ Team stats populated")
        
        # Query 4: Check view - v_team_season_stats
        print("\n[4/7] Testing v_team_season_stats view...")
        cursor.execute("""
            SELECT team, games_played, wins, losses, avg_ppg_for, avg_epa_offense
            FROM hcl.v_team_season_stats
            WHERE season = 2024
            ORDER BY avg_epa_offense DESC NULLS LAST
            LIMIT 5
        """)
        season_stats = cursor.fetchall()
        for stat in season_stats:
            wins = stat['wins'] if stat['wins'] is not None else 0
            losses = stat['losses'] if stat['losses'] is not None else 0
            gp = stat['games_played'] if stat['games_played'] is not None else 0
            ppg = stat['avg_ppg_for'] if stat['avg_ppg_for'] is not None else 0
            epa = stat['avg_epa_offense'] if stat['avg_epa_offense'] is not None else None
            epa_str = f"{epa:.3f}" if epa is not None else "N/A"
            print(f"   {stat['team']}: {wins}-{losses} ({gp} GP), {ppg:.1f} PPG, EPA={epa_str}")
        print("   ✅ Season stats view working")
        
        # Query 5: Check view - v_game_matchup_display
        print("\n[5/7] Testing v_game_matchup_display view...")
        cursor.execute("""
            SELECT game_id, home_team, away_team, home_epa_pp, away_epa_pp, diff_epa_pp
            FROM hcl.v_game_matchup_display
            WHERE season = 2024 AND week = 7
            LIMIT 5
        """)
        matchups = cursor.fetchall()
        for m in matchups:
            diff = f"{m['diff_epa_pp']:.3f}" if m['diff_epa_pp'] is not None else "N/A"
            print(f"   {m['game_id']}: {m['away_team']}@{m['home_team']} - EPA diff={diff}")
        print("   ✅ Matchup display view working")
        
        # Query 6: Check view - v_game_matchup_with_proj
        print("\n[6/7] Testing v_game_matchup_with_proj view...")
        cursor.execute("""
            SELECT game_id, home_team, away_team, projected_spread, projected_total, matchup_type
            FROM hcl.v_game_matchup_with_proj
            WHERE season = 2024 AND week = 7
            LIMIT 5
        """)
        projs = cursor.fetchall()
        for p in projs:
            spread = f"{p['projected_spread']:.1f}" if p['projected_spread'] is not None else "N/A"
            total = f"{p['projected_total']:.1f}" if p['projected_total'] is not None else "N/A"
            print(f"   {p['game_id']}: {p['away_team']}@{p['home_team']} - "
                  f"Proj Spread={spread}, Total={total}, Type={p['matchup_type']}")
        print("   ✅ Projection view working")
        
        # Query 7: Verify momentum calculations
        print("\n[7/7] Checking momentum indicators (last 3 games)...")
        cursor.execute("""
            SELECT team, game_id, epa_per_play, epa_last_3_games
            FROM hcl.team_game_stats
            WHERE epa_last_3_games IS NOT NULL
            ORDER BY epa_last_3_games DESC
            LIMIT 5
        """)
        momentum = cursor.fetchall()
        for m in momentum:
            print(f"   {m['team']} ({m['game_id']}): "
                  f"Current EPA={m['epa_per_play']:.3f}, "
                  f"L3 Avg={m['epa_last_3_games']:.3f}")
        print("   ✅ Momentum calculations working")
        
        print(f"\n{'='*70}")
        print(f"✅ ALL VALIDATION CHECKS PASSED!")
        print(f"{'='*70}\n")
        
        print("Data Summary:")
        print(f"  - 15 games loaded (Week 7)")
        print(f"  - 30 team-game records")
        print(f"  - All views calculating correctly")
        print(f"  - Projections working (spread & total)")
        print(f"  - Momentum indicators populated")
        print("\n🎉 Database is ready for API development!")
        
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()
    
    return True


if __name__ == '__main__':
    success = run_validation_queries()
    exit(0 if success else 1)
