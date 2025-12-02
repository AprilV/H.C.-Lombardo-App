#!/usr/bin/env python3
"""
Create backup snapshot of testbed data before production migration
"""
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"testbed_backup_{timestamp}.txt"

print("=" * 80)
print("TESTBED DATA SNAPSHOT")
print("=" * 80)

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

with open(backup_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("TESTBED BACKUP SNAPSHOT\n")
    f.write(f"Created: {datetime.now()}\n")
    f.write(f"Database: nfl_analytics\n")
    f.write(f"Schema: hcl_test\n")
    f.write("=" * 80 + "\n\n")
    
    with conn.cursor() as cur:
        # Games table stats
        f.write("1. GAMES TABLE\n")
        f.write("-" * 40 + "\n")
        cur.execute("SELECT COUNT(*) FROM hcl_test.games")
        games_count = cur.fetchone()[0]
        f.write(f"Total games: {games_count}\n")
        
        cur.execute("""
            SELECT season, COUNT(*) 
            FROM hcl_test.games 
            GROUP BY season 
            ORDER BY season
        """)
        f.write("Games by season:\n")
        for row in cur.fetchall():
            f.write(f"  {row[0]}: {row[1]} games\n")
        
        # New columns coverage
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(spread_line) as with_spread,
                COUNT(roof) as with_roof,
                COUNT(referee) as with_referee
            FROM hcl_test.games
        """)
        row = cur.fetchone()
        f.write(f"\nNew columns coverage:\n")
        f.write(f"  Betting lines: {row[1]}/{row[0]} ({row[1]/row[0]*100:.1f}%)\n")
        f.write(f"  Weather (roof): {row[2]}/{row[0]} ({row[2]/row[0]*100:.1f}%)\n")
        f.write(f"  Referee: {row[3]}/{row[0]} ({row[3]/row[0]*100:.1f}%)\n")
        
        # Team-game stats
        f.write("\n2. TEAM_GAME_STATS TABLE\n")
        f.write("-" * 40 + "\n")
        cur.execute("SELECT COUNT(*) FROM hcl_test.team_game_stats")
        stats_count = cur.fetchone()[0]
        f.write(f"Total records: {stats_count}\n")
        
        # Sample games
        f.write("\n3. SAMPLE GAMES (2024 Week 1)\n")
        f.write("-" * 40 + "\n")
        cur.execute("""
            SELECT game_id, away_team, home_team, away_score, home_score,
                   spread_line, total_line, roof, temp
            FROM hcl_test.games
            WHERE season = 2024 AND week = 1
            ORDER BY game_date
            LIMIT 5
        """)
        for row in cur.fetchall():
            f.write(f"{row[0]}: {row[1]} @ {row[2]} ({row[3]}-{row[4]})\n")
            f.write(f"  Spread: {row[5]}, Total: {row[6]}, Roof: {row[7]}, Temp: {row[8]}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("BACKUP COMPLETE\n")
        f.write(f"Total games: {games_count}\n")
        f.write(f"Total team-game stats: {stats_count}\n")
        f.write("Ready for production migration\n")
        f.write("=" * 80 + "\n")

conn.close()

print(f"✓ Backup snapshot created: {backup_file}")
print(f"✓ Games: {games_count}")
print(f"✓ Team-game stats: {stats_count}")
print("\n" + "=" * 80)
print("BACKUP COMPLETE - SAFE TO PROCEED")
print("=" * 80)
