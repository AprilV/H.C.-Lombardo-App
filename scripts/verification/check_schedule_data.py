"""Check what seasons have game-by-game schedule data"""
import psycopg2
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor()

# Check games per season
print("=" * 70)
print("GAME-BY-GAME DATA AVAILABILITY")
print("=" * 70)
cur.execute("""
    SELECT 
        season, 
        COUNT(DISTINCT game_id) as total_games,
        COUNT(DISTINCT team) as teams_with_data,
        MIN(week) as first_week,
        MAX(week) as last_week
    FROM hcl.team_game_stats 
    GROUP BY season 
    ORDER BY season DESC
""")

print(f"\n{'Season':<8} {'Games':<8} {'Teams':<8} {'Weeks':<15}")
print("-" * 70)
for row in cur.fetchall():
    season, games, teams, first_week, last_week = row
    week_range = f"Week {first_week}-{last_week}" if first_week and last_week else "N/A"
    print(f"{season:<8} {games:<8} {teams:<8} {week_range:<15}")

# Check 2025 specifically
print("\n" + "=" * 70)
print("2025 SEASON DETAIL")
print("=" * 70)
cur.execute("""
    SELECT 
        week,
        COUNT(DISTINCT game_id) as games,
        COUNT(DISTINCT team) as teams
    FROM hcl.team_game_stats 
    WHERE season = 2025
    GROUP BY week
    ORDER BY week
""")

print(f"\n{'Week':<6} {'Games':<8} {'Teams':<8}")
print("-" * 70)
for row in cur.fetchall():
    print(f"{row[0]:<6} {row[1]:<8} {row[2]:<8}")

# Sample game data from 2025
print("\n" + "=" * 70)
print("SAMPLE 2025 GAME DATA (First 5 games)")
print("=" * 70)
cur.execute("""
    SELECT 
        week,
        game_date,
        team,
        opponent,
        is_home,
        result,
        points
    FROM hcl.team_game_stats
    WHERE season = 2025
    ORDER BY week, team
    LIMIT 10
""")

print(f"\n{'Week':<6} {'Date':<12} {'Team':<6} {'Opp':<6} {'H/A':<5} {'Result':<6} {'Pts':<5}")
print("-" * 70)
for row in cur.fetchall():
    week, date, team, opp, is_home, result, pts = row
    home_away = "Home" if is_home else "Away"
    print(f"{week:<6} {str(date):<12} {team:<6} {opp:<6} {home_away:<5} {result or 'N/A':<6} {pts or 'N/A':<5}")

# Check older seasons
print("\n" + "=" * 70)
print("SAMPLE DATA FROM OLDER SEASONS")
print("=" * 70)
cur.execute("""
    SELECT 
        season,
        COUNT(DISTINCT game_id) as games,
        COUNT(DISTINCT week) as weeks,
        MIN(game_date) as first_game,
        MAX(game_date) as last_game
    FROM hcl.team_game_stats
    WHERE season < 2025
    GROUP BY season
    ORDER BY season DESC
    LIMIT 5
""")

print(f"\n{'Season':<8} {'Games':<8} {'Weeks':<8} {'First Game':<15} {'Last Game':<15}")
print("-" * 70)
for row in cur.fetchall():
    season, games, weeks, first, last = row
    print(f"{season:<8} {games:<8} {weeks:<8} {str(first):<15} {str(last):<15}")

cur.close()
conn.close()

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)
print("✓ If you see game_id, week, opponent data for seasons 1999-2024,")
print("  then we HAVE full schedules for those seasons!")
print("✓ If older seasons show NULL/0 for weeks, we only have aggregated stats")
print("=" * 70)
