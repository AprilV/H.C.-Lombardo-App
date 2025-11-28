"""
Populate Render Database with 2024 Season Games
Quick data load to make the app functional
"""
import nfl_data_py as nfl
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

RENDER_DB_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

print("=" * 80)
print("POPULATE RENDER DATABASE - 2024 SEASON GAMES")
print("=" * 80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

try:
    conn = psycopg2.connect(RENDER_DB_URL)
    cursor = conn.cursor()
    
    print("✅ Connected to Render database\n")
    
    # Step 1: Download 2024 schedule
    print("📅 Step 1: Downloading 2024 schedule...")
    schedules = nfl.import_schedules([2024])
    print(f"✅ Downloaded {len(schedules)} games\n")
    
    # Step 2: Insert games
    print("🏈 Step 2: Inserting games into hcl.games...")
    
    games_data = []
    for _, row in schedules.iterrows():
        games_data.append((
            row['game_id'],
            int(row['season']),
            int(row['week']),
            row.get('gameday'),
            row['home_team'],
            row['away_team'],
            row.get('stadium'),
            row.get('home_score'),
            row.get('away_score'),
            row.get('spread_line'),
            row.get('total_line'),
            row.get('roof'),
            row.get('surface'),
            row.get('temp'),
            row.get('wind')
        ))
    
    # Delete existing 2024 games
    cursor.execute("DELETE FROM hcl.team_game_stats WHERE season = 2024")
    cursor.execute("DELETE FROM hcl.games WHERE season = 2024")
    conn.commit()
    
    # Insert new games
    execute_values(cursor, """
        INSERT INTO hcl.games (
            game_id, season, week, game_date,
            home_team, away_team, stadium,
            home_score, away_score,
            spread_line, total_line,
            roof, surface, temp, wind
        ) VALUES %s
    """, games_data)
    
    conn.commit()
    print(f"✅ Inserted {len(games_data)} games\n")
    
    # Step 3: Calculate basic team stats from completed games
    print("📊 Step 3: Calculating team stats from completed games...")
    
    cursor.execute("""
        SELECT game_id, week, home_team, away_team, home_score, away_score
        FROM hcl.games
        WHERE season = 2024 
        AND home_score IS NOT NULL 
        AND away_score IS NOT NULL
    """)
    completed_games = cursor.fetchall()
    
    print(f"Found {len(completed_games)} completed games\n")
    
    team_game_stats = []
    for game_id, week, home_team, away_team, home_score, away_score in completed_games:
        # Home team stats
        team_game_stats.append((
            game_id,
            2024,
            week,
            home_team,
            away_team,  # opponent
            True,  # is_home
            home_score,
            'W' if home_score > away_score else ('L' if home_score < away_score else 'T'),
            0, 0, 0, 0, 0, 0, 0, 0  # placeholder stats
        ))
        
        # Away team stats
        team_game_stats.append((
            game_id,
            2024,
            week,
            away_team,
            home_team,  # opponent
            False,  # is_home
            away_score,
            'W' if away_score > home_score else ('L' if away_score < home_score else 'T'),
            0, 0, 0, 0, 0, 0, 0, 0  # placeholder stats
        ))
    
    if team_game_stats:
        execute_values(cursor, """
            INSERT INTO hcl.team_game_stats (
                game_id, season, week, team, opponent, is_home, points, result,
                total_yards, passing_yards, rushing_yards, plays,
                yards_per_play, completion_pct, turnovers, touchdowns
            ) VALUES %s
        """, team_game_stats)
        
        conn.commit()
        print(f"✅ Inserted {len(team_game_stats)} team-game records\n")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM hcl.games WHERE season = 2024")
    games_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hcl.team_game_stats WHERE season = 2024")
    stats_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hcl.team_info")
    teams_count = cursor.fetchone()[0]
    
    print("=" * 80)
    print("SUCCESS! Database populated:")
    print(f"  - {teams_count} teams in hcl.team_info")
    print(f"  - {games_count} games in hcl.games (2024)")
    print(f"  - {stats_count} team-game records in hcl.team_game_stats (2024)")
    print("=" * 80)
    print("\nNow refresh the website - team dropdowns should work!")
    print("You'll see 2024 season data with basic stats.")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
