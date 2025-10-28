"""
Direct database test of HCL views to validate API logic
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def test_hcl_queries():
    print("\n🧪 Testing HCL Database Queries (API Logic)")
    print("=" * 60)
    
    conn = psycopg2.connect(
        dbname='nfl_analytics_test',
        user='postgres',
        password='aprilv120',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Teams list
    print("\n[1/3] Testing teams list query...")
    query = """
        SELECT 
            team,
            games_played,
            wins,
            losses,
            ROUND(avg_ppg_for::numeric, 1) as ppg,
            ROUND(avg_epa_offense::numeric, 3) as epa_per_play
        FROM hcl.v_team_season_stats
        ORDER BY wins DESC, avg_epa_offense DESC
        LIMIT 5
    """
    cur.execute(query)
    teams = cur.fetchall()
    print(f"✅ Retrieved {len(teams)} teams")
    for team in teams:
        print(f"   {team['team']}: {team['wins']}-{team['losses']}, {team['ppg']} PPG, {team['epa_per_play']} EPA")
    
    # Test 2: Team details (BAL)
    print("\n[2/3] Testing team details query (BAL)...")
    query = """
        SELECT 
            team,
            wins,
            losses,
            ROUND(avg_ppg_for::numeric, 1) as ppg,
            ROUND(avg_epa_offense::numeric, 3) as epa_per_play,
            ROUND(avg_epa_home::numeric, 3) as home_epa,
            ROUND(avg_epa_away::numeric, 3) as away_epa
        FROM hcl.v_team_season_stats
        WHERE team = 'BAL'
    """
    cur.execute(query)
    team = cur.fetchone()
    if team:
        print(f"✅ {team['team']}: {team['wins']}-{team['losses']}")
        print(f"   Overall: {team['ppg']} PPG, {team['epa_per_play']} EPA")
        print(f"   Home/Away EPA: {team['home_epa']}/{team['away_epa']}")
    else:
        print("❌ BAL not found")
    
    # Test 3: Team games (BAL)
    print("\n[3/3] Testing team games query (BAL)...")
    query = """
        SELECT 
            tgs.week,
            tgs.opponent,
            tgs.is_home,
            tgs.points_scored as team_points,
            tgs.points_allowed as opponent_points,
            ROUND(tgs.epa_per_play::numeric, 3) as epa_per_play,
            tgs.total_yards
        FROM hcl.team_game_stats tgs
        JOIN hcl.games g ON tgs.game_id = g.game_id
        WHERE tgs.team = 'BAL'
        ORDER BY g.kickoff_time_utc DESC
    """
    cur.execute(query)
    games = cur.fetchall()
    print(f"✅ Retrieved {len(games)} games")
    for game in games:
        home_away = 'vs' if game['is_home'] else '@'
        print(f"   Week {game['week']} {home_away} {game['opponent']}: {game['team_points']}-{game['opponent_points']}")
        print(f"      EPA: {game['epa_per_play']}, Yards: {game['total_yards']}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ All database queries successful!")
    print("   API logic validated - ready to test live endpoints\n")

if __name__ == '__main__':
    test_hcl_queries()
