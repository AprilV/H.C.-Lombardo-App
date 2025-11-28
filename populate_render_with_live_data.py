"""
Populate Render database with LIVE NFL data
Fetches current standings, stats, and game data
"""
import psycopg2
import os
import sys

# Import the data fetcher
sys.path.insert(0, os.path.dirname(__file__))
from multi_source_data_fetcher import MultiSourceDataFetcher

def main():
    DATABASE_URL = input("Paste External Database URL: ")
    
    print("🚀 Connecting to Render database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        
        print("✅ Connected! Fetching live NFL data...")
        
        # Create and run the data fetcher
        fetcher = MultiSourceDataFetcher()
        
        # Set database connection for the fetcher
        fetcher.conn = conn
        fetcher.cursor = conn.cursor()
        
        # Run the update
        print("\n📊 Fetching from ESPN, TeamRankings, and other sources...")
        fetcher.run_full_update()
        
        conn.commit()
        
        # Verify the data
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teams WHERE wins > 0 OR losses > 0")
        teams_with_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT name, wins, losses, ppg FROM teams WHERE wins > 0 ORDER BY wins DESC LIMIT 5")
        top_teams = cursor.fetchall()
        
        print(f"\n✅ Success! {teams_with_records} teams have updated records")
        print("\nTop 5 teams by wins:")
        for team in top_teams:
            print(f"  {team[0]}: {team[1]}-{team[2]} ({team[3]} PPG)")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Live data populated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
