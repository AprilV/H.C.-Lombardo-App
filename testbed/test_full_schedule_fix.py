"""
Test Full Schedule Fix - Testbed
================================
PROBLEM: Team detail page shows only 10 completed games
GOAL: Show all 17 regular season games (including future games)

Following BEST_PRACTICES.md: Testbed First, 100% Pass Rate Required
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Connect to production database"""
    return psycopg2.connect(
        dbname='nfl_analytics',
        user='postgres',
        password='aprilv120',
        host='localhost',
        port='5432'
    )

def test_current_query():
    """Test what the current query returns (should be 10 games)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Old query (FROM team_game_stats JOIN games)
    query_old = """
        SELECT 
            g.game_id, g.week, g.game_date,
            CASE WHEN g.home_team = %s THEN g.away_team ELSE g.home_team END as opponent,
            CASE WHEN g.home_team = %s THEN TRUE ELSE FALSE END as is_home,
            tgs.result, g.home_score, g.away_score
        FROM hcl.team_game_stats tgs
        JOIN hcl.games g ON tgs.game_id = g.game_id
        WHERE tgs.team = %s AND g.season = %s AND g.is_postseason = FALSE
        ORDER BY g.week ASC
    """
    
    team = 'KC'
    season = 2025
    cur.execute(query_old, (team, team, team, season))
    old_results = cur.fetchall()
    
    print(f"\n=== OLD QUERY (FROM team_game_stats JOIN games) ===")
    print(f"Total games: {len(old_results)}")
    for game in old_results[:5]:
        print(f"  Week {game['week']:2d}: {'vs' if game['is_home'] else '@'} {game['opponent']} - {game['result'] or 'TBD'}")
    if len(old_results) > 5:
        print(f"  ... and {len(old_results) - 5} more games")
    
    cur.close()
    conn.close()
    return len(old_results)

def test_new_query():
    """Test the new query with LEFT JOIN (should be 17 games)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # New query (FROM games LEFT JOIN team_game_stats)
    query_new = """
        SELECT 
            g.game_id, g.week, g.game_date,
            CASE WHEN g.home_team = %s THEN g.away_team ELSE g.home_team END as opponent,
            CASE WHEN g.home_team = %s THEN TRUE ELSE FALSE END as is_home,
            tgs.result, g.home_score, g.away_score,
            tgs.total_yards, tgs.passing_yards, tgs.rushing_yards
        FROM hcl.games g
        LEFT JOIN hcl.team_game_stats tgs ON g.game_id = tgs.game_id AND tgs.team = %s
        WHERE (g.home_team = %s OR g.away_team = %s) 
            AND g.season = %s 
            AND g.is_postseason = FALSE
        ORDER BY g.week ASC
    """
    
    team = 'KC'
    season = 2025
    cur.execute(query_new, (team, team, team, team, team, season))
    new_results = cur.fetchall()
    
    print(f"\n=== NEW QUERY (FROM games LEFT JOIN team_game_stats) ===")
    print(f"Total games: {len(new_results)}")
    print(f"\nFull schedule:")
    for game in new_results:
        result = game['result'] or 'TBD'
        loc = 'vs' if game['is_home'] else '@'
        score = f"{game['home_score'] or '-'}-{game['away_score'] or '-'}" if game['home_score'] else 'Not played'
        print(f"  Week {game['week']:2d}: {loc} {game['opponent']} - {result:3s} ({score})")
    
    cur.close()
    conn.close()
    return len(new_results)

def run_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("FULL SCHEDULE FIX - TESTBED VALIDATION")
    print("=" * 60)
    
    try:
        old_count = test_current_query()
        new_count = test_new_query()
        
        print(f"\n=== TEST RESULTS ===")
        print(f"Old query returned: {old_count} games (❌ Only completed)")
        print(f"New query returned: {new_count} games (✅ Full schedule)")
        
        if new_count == 17:
            print(f"\n✅ TEST PASSED: New query returns full 17-game schedule")
            print(f"✅ READY TO DEPLOY TO PRODUCTION")
            return True
        else:
            print(f"\n❌ TEST FAILED: Expected 17 games, got {new_count}")
            print(f"❌ NOT READY FOR PRODUCTION")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
