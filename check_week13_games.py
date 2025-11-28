#!/usr/bin/env python3
"""Check what Week 13 games exist in Render database"""

import psycopg2

RENDER_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

conn = psycopg2.connect(RENDER_URL)
cur = conn.cursor()

print("\n🔍 Checking Week 13 games in Render database:")
print("="*80)

# Check exactly what the ML script is looking for
cur.execute("""
    SELECT game_id, home_team, away_team, home_score, away_score, 
           spread_line, is_postseason
    FROM hcl.games
    WHERE season = 2025 
    AND week = 13
    AND is_postseason = false
    ORDER BY game_id
""")
games = cur.fetchall()

print(f"\nQuery: season=2025, week=13, is_postseason=false")
print(f"Result: {len(games)} games found\n")

if len(games) > 0:
    for game in games[:5]:
        print(f"  {game[0]} | {game[1]} vs {game[2]} | Scores: {game[3]}-{game[4]} | Spread: {game[5]} | Postseason: {game[6]}")
else:
    # Check without is_postseason filter
    cur.execute("""
        SELECT game_id, home_team, away_team, home_score, away_score, 
               spread_line, is_postseason
        FROM hcl.games
        WHERE season = 2025 AND week = 13
        ORDER BY game_id
    """)
    games_no_filter = cur.fetchall()
    print(f"❌ No games with is_postseason=false")
    print(f"\nBut found {len(games_no_filter)} games WITHOUT that filter:")
    for game in games_no_filter[:5]:
        print(f"  {game[0]} | {game[1]} vs {game[2]} | Postseason: {game[6]}")
    
    # Check what is_postseason values exist
    cur.execute("""
        SELECT DISTINCT is_postseason, COUNT(*)
        FROM hcl.games
        WHERE season = 2025 AND week = 13
        GROUP BY is_postseason
    """)
    print(f"\nis_postseason values:")
    for val, count in cur.fetchall():
        print(f"  {val}: {count} games")

conn.close()
print("="*80 + "\n")
