import psycopg2
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)

cur = conn.cursor()

# Check Week 10 2025 games
cur.execute("""
    SELECT home_team, away_team, spread_line, total_line, home_moneyline, away_moneyline
    FROM hcl.games
    WHERE season = 2025 AND week = 10
    ORDER BY game_date
    LIMIT 5
""")

print("\n" + "="*70)
print("WEEK 10 2025 - VEGAS LINES IN DATABASE")
print("="*70)
print(f"{'Matchup':<20} | {'Spread':<8} | {'Total':<8} | {'ML Home':<10} | {'ML Away':<10}")
print("-"*70)

for row in cur.fetchall():
    home, away, spread, total, ml_home, ml_away = row
    matchup = f"{away} @ {home}"
    spread_str = str(spread) if spread is not None else "NULL"
    total_str = str(total) if total is not None else "NULL"
    ml_home_str = str(ml_home) if ml_home is not None else "NULL"
    ml_away_str = str(ml_away) if ml_away is not None else "NULL"
    
    print(f"{matchup:<20} | {spread_str:<8} | {total_str:<8} | {ml_home_str:<10} | {ml_away_str:<10}")

print("\n")

# Check if ANY games have Vegas lines
cur.execute("""
    SELECT 
        COUNT(*) as total_games,
        COUNT(spread_line) as games_with_spread,
        COUNT(total_line) as games_with_total,
        COUNT(home_moneyline) as games_with_moneyline
    FROM hcl.games
    WHERE season = 2025
""")

total, with_spread, with_total, with_ml = cur.fetchone()

print("="*70)
print("2025 SEASON - VEGAS LINE COVERAGE")
print("="*70)
print(f"Total Games: {total}")
print(f"Games with Spread Line: {with_spread} ({with_spread/total*100:.1f}%)")
print(f"Games with Total Line: {with_total} ({with_total/total*100:.1f}%)")
print(f"Games with Moneyline: {with_ml} ({with_ml/total*100:.1f}%)")
print("="*70)

conn.close()
