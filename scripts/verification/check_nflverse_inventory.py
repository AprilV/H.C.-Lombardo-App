"""
Complete inventory of what nflverse provides for FREE
"""
import nfl_data_py as nfl

print("=" * 80)
print("COMPLETE NFLVERSE DATA INVENTORY (ALL FREE)")
print("=" * 80)

print("\n📊 ALL AVAILABLE DATASETS:")
print("-" * 80)
funcs = [f for f in dir(nfl) if f.startswith('import_')]
for i, f in enumerate(funcs, 1):
    print(f"{i:2}. {f}")

print("\n" + "=" * 80)
print("WHAT WE'RE ALREADY GETTING:")
print("=" * 80)
print("✓ Schedules (game_id, teams, scores, dates)")
print("✓ Play-by-play data (for stat calculations)")

print("\n" + "=" * 80)
print("BETTING DATA AVAILABLE (FROM SCHEDULES):")
print("=" * 80)
schedules = nfl.import_schedules([2024])
betting_cols = [col for col in schedules.columns if any(x in col.lower() 
                for x in ['spread', 'line', 'odds', 'moneyline', 'total', 'over', 'under'])]
for col in betting_cols:
    print(f"   • {col}")

print("\n" + "=" * 80)
print("WEATHER DATA AVAILABLE (FROM SCHEDULES):")
print("=" * 80)
weather_cols = [col for col in schedules.columns if any(x in col.lower() 
                for x in ['roof', 'surface', 'temp', 'wind'])]
for col in weather_cols:
    print(f"   • {col}")

print("\n" + "=" * 80)
print("REST/CONTEXT DATA (FROM SCHEDULES):")
print("=" * 80)
context_cols = ['away_rest', 'home_rest', 'div_game', 'overtime', 'referee', 
                'away_coach', 'home_coach', 'away_qb_name', 'home_qb_name']
for col in context_cols:
    if col in schedules.columns:
        print(f"   • {col}")

print("\n" + "=" * 80)
print("SAMPLE BETTING DATA (WEEK 1, 2024):")
print("=" * 80)
sample = schedules[schedules['week'] == 1].head(3)
print(sample[['game_id', 'home_team', 'away_team', 'spread_line', 'total_line', 
              'home_moneyline', 'away_moneyline', 'roof', 'temp', 'wind']].to_string(index=False))

print("\n" + "=" * 80)
print("INJURY DATA CHECK:")
print("=" * 80)
try:
    injuries = nfl.import_injuries([2024])
    print(f"✓ Injuries available: {len(injuries)} records")
    if len(injuries) > 0:
        print(f"   Columns: {', '.join(injuries.columns)}")
        print(f"\n   Sample:")
        print(injuries.head(3).to_string(index=False))
except Exception as e:
    print(f"✗ Error loading injuries: {e}")

print("\n" + "=" * 80)
print("DEPTH CHART DATA CHECK:")
print("=" * 80)
try:
    depth = nfl.import_depth_charts([2024])
    print(f"✓ Depth charts available: {len(depth)} records")
    if len(depth) > 0:
        print(f"   Columns: {', '.join(depth.columns)}")
except Exception as e:
    print(f"✗ Error loading depth charts: {e}")

print("\n" + "=" * 80)
print("NEXT GEN STATS (NGS) CHECK:")
print("=" * 80)
try:
    ngs = nfl.import_ngs_data('passing', [2024])
    print(f"✓ NGS passing available: {len(ngs)} records")
    if len(ngs) > 0:
        print(f"   Columns: {', '.join(ngs.columns)}")
except Exception as e:
    print(f"✗ Error loading NGS: {e}")

print("\n" + "=" * 80)
print("SUMMARY - WHAT WE CAN ADD TO DATABASE:")
print("=" * 80)
print("🎯 HIGH VALUE (Already Downloaded, Not Stored):")
print("   1. Betting lines (spread, total, moneylines, odds)")
print("   2. Weather (roof, surface, temp, wind)")
print("   3. Rest days (away_rest, home_rest)")
print("   4. Context (div_game, overtime, referee, coaches)")
print("   5. QBs (away_qb_name, home_qb_name)")

print("\n🏈 MEDIUM VALUE (Need Separate Download):")
print("   6. Injuries (weekly injury reports)")
print("   7. Depth charts (position rankings)")
print("   8. Next Gen Stats (tracking data - speed, separation, etc)")
print("   9. QBR (ESPN quarterback ratings)")

print("\n📈 ALREADY HAVE (Via Play-by-Play):")
print("   10. EPA (Expected Points Added)")
print("   11. WPA (Win Probability Added)")
print("   12. Success rate")
print("   13. CPOE (Completion % Over Expected)")
print("   14. Air yards, YAC")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print("✅ PHASE 1: Add betting/weather/rest from schedules (ZERO extra download)")
print("✅ PHASE 2: Add EPA metrics from play-by-play (already downloaded)")
print("⏳ PHASE 3: Add injuries/depth charts (separate downloads)")
print("=" * 80)
