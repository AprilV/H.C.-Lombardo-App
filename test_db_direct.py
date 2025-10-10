"""Quick database verification test"""
import psycopg2

try:
    conn = psycopg2.connect(
        dbname='nfl_analytics',
        user='postgres', 
        password='aprilv120',
        host='localhost'
    )
    cur = conn.cursor()
    
    # Check what's actually in the database
    cur.execute("SELECT name, wins, losses, ppg, pa FROM teams ORDER BY ppg DESC LIMIT 5")
    
    print("\n" + "="*70)
    print("DATABASE CONTENTS (Top 5 by PPG):")
    print("="*70)
    for row in cur.fetchall():
        print(f"{row[0]:30s} W:{row[1]:2d} L:{row[2]:2d} PPG:{row[3]:.1f} PA:{row[4]:.1f}")
    
    conn.close()
    print("\n✅ Database query successful")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
