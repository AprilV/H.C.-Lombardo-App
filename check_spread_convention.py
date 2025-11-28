"""
Quick script to check spread convention in database
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'nfl_user'),
    password=os.getenv('DB_PASSWORD', 'nfl2024'),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432')
)

cursor = conn.cursor()

# Get KC@DAL game (2024 Week 13)
query = """
SELECT 
    game_id,
    away_team,
    home_team,
    away_score,
    home_score,
    (home_score - away_score) AS actual_margin,
    spread_line,
    CASE 
        WHEN spread_line < 0 THEN home_team || ' favored by ' || ABS(spread_line)
        WHEN spread_line > 0 THEN away_team || ' favored by ' || spread_line
        ELSE 'Pick ''em'
    END AS spread_interpretation
FROM hcl.games
WHERE season = 2024 
  AND week = 13
  AND away_team = 'KC'
  AND home_team = 'DAL'
LIMIT 1;
"""

cursor.execute(query)
result = cursor.fetchone()

print("\n" + "="*80)
print("SPREAD CONVENTION CHECK - KC @ DAL (2024 Week 13)")
print("="*80)

if result:
    game_id, away, home, away_score, home_score, margin, spread, interp = result
    
    print(f"\nGame: {away} @ {home}")
    print(f"Final Score: {away} {away_score}, {home} {home_score}")
    print(f"Actual Margin: {home} won by {margin}")
    print(f"\nDatabase spread_line value: {spread}")
    print(f"Interpretation: {interp}")
    
    print("\n" + "-"*80)
    print("ANALYSIS:")
    print("-"*80)
    
    # Reality check
    print(f"\nREALITY: Vegas had KC favored by 3.5")
    print(f"Expected database value: -3.5 (negative = home underdog)")
    print(f"OR: +3.5 (positive = home underdog)")
    
    if spread == -3.5:
        print(f"\n✅ CORRECT: Database uses standard convention")
        print(f"   Negative = home team favored")
        print(f"   Positive = away team favored")
        print(f"   {spread} means {home} favored by 3.5")
    elif spread == 3.5:
        print(f"\n✅ CORRECT: Database uses nflverse convention")
        print(f"   Positive = home team underdog (away favored)")
        print(f"   Negative = home team favored")
        print(f"   {spread} means {away} favored by 3.5")
    else:
        print(f"\n❌ UNEXPECTED VALUE: {spread}")
        print(f"   Expected -3.5 or +3.5")
        
else:
    print("❌ Game not found in database")

# Check a few more games for pattern
print("\n" + "="*80)
print("CHECKING MORE GAMES FOR PATTERN")
print("="*80 + "\n")

query2 = """
SELECT 
    away_team || ' @ ' || home_team AS matchup,
    away_score,
    home_score,
    (home_score - away_score) AS margin,
    spread_line
FROM hcl.games
WHERE season = 2024 
  AND week = 13
  AND spread_line IS NOT NULL
ORDER BY game_id
LIMIT 5;
"""

cursor.execute(query2)
results = cursor.fetchall()

for matchup, away_score, home_score, margin, spread in results:
    print(f"{matchup}")
    if away_score and home_score:
        print(f"  Final: Away {away_score}, Home {home_score} (Home {'+' if margin > 0 else ''}{margin})")
    print(f"  Spread: {spread}")
    if spread < 0:
        print(f"  → Home favored by {abs(spread)}")
    else:
        print(f"  → Away favored by {spread}")
    print()

cursor.close()
conn.close()
