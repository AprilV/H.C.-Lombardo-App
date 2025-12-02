#!/usr/bin/env python3
"""Check what 2025 weeks we have"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)
cur = conn.cursor()

print("\n📅 2025 Season Games by Week:")
print("="*80)

cur.execute("""
    SELECT week, 
           COUNT(*) as total_games,
           COUNT(home_score) as games_with_scores
    FROM hcl.games
    WHERE season = 2025
    GROUP BY week
    ORDER BY week
""")

for week, total, with_scores in cur.fetchall():
    print(f"  Week {week:2d}: {total:3d} games ({with_scores:3d} played)")

print("\n📊 Sample Week 13 game (if any):")
cur.execute("""
    SELECT game_id, home_team, away_team, game_date, home_score, away_score
    FROM hcl.games
    WHERE season = 2025 AND week = 13
    LIMIT 3
""")
games = cur.fetchall()
if games:
    for g in games:
        print(f"  {g}")
else:
    print("  ❌ NO WEEK 13 GAMES FOUND")

print("\n🔍 Checking max week in 2025:")
cur.execute("SELECT MAX(week) FROM hcl.games WHERE season = 2025")
max_week = cur.fetchone()[0]
print(f"  Max week: {max_week}")

conn.close()
print("="*80 + "\n")
