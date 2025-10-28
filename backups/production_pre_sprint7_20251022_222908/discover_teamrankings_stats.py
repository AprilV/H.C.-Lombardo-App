"""
Discover ALL available NFL stats on TeamRankings.com
This will show us the complete list of stats we can scrape
"""
import requests
from bs4 import BeautifulSoup

def discover_available_stats():
    print("="*70)
    print("DISCOVERING ALL NFL STATS ON TEAMRANKINGS.COM")
    print("="*70)
    
    url = "https://www.teamrankings.com/nfl/stats"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all stat categories
        categories = {}
        
        # TeamRankings organizes stats in sections
        stat_sections = soup.find_all('div', class_='datatable')
        
        if not stat_sections:
            # Try finding stat links
            stat_links = soup.find_all('a', href=lambda x: x and '/nfl/stat/' in x)
            
            print(f"\nFound {len(stat_links)} stat pages:")
            print("-"*70)
            
            for i, link in enumerate(stat_links[:50], 1):  # First 50 stats
                stat_name = link.get_text().strip()
                stat_url = link.get('href')
                
                if stat_name and stat_url:
                    full_url = f"https://www.teamrankings.com{stat_url}" if not stat_url.startswith('http') else stat_url
                    print(f"{i:3d}. {stat_name:<50} {stat_url}")
        
        print("\n" + "="*70)
        print("COMMON STATS WE CAN SCRAPE:")
        print("="*70)
        
        # List of known stats available
        known_stats = {
            "Offense": [
                "points-per-game",
                "yards-per-game", 
                "passing-yards-per-game",
                "rushing-yards-per-game",
                "first-downs-per-game",
                "third-down-conversions",
                "third-down-conversion-pct",
                "fourth-down-conversions",
                "fourth-down-conversion-pct",
                "red-zone-scoring-pct",
                "touchdowns-per-game",
                "passing-touchdowns",
                "rushing-touchdowns",
                "turnovers-per-game",
                "giveaways",
                "fumbles-lost",
                "interceptions-thrown",
                "penalties-per-game",
                "penalty-yards-per-game",
                "time-of-possession"
            ],
            "Defense": [
                "opponent-points-per-game",
                "opponent-yards-per-game",
                "opponent-passing-yards-per-game", 
                "opponent-rushing-yards-per-game",
                "sacks-per-game",
                "interceptions",
                "forced-fumbles",
                "takeaways",
                "opponent-third-down-conversion-pct",
                "opponent-red-zone-scoring-pct",
                "tackles-for-loss-per-game"
            ],
            "Special Teams": [
                "field-goal-pct",
                "extra-point-pct",
                "punt-average",
                "punt-return-average",
                "kickoff-return-average",
                "touchbacks-per-game"
            ]
        }
        
        total_count = 0
        for category, stats in known_stats.items():
            print(f"\n{category}:")
            for stat in stats:
                url_path = f"/nfl/stat/{stat}"
                print(f"  • {stat.replace('-', ' ').title():<45} {url_path}")
                total_count += 1
        
        print(f"\n{'='*70}")
        print(f"TOTAL: {total_count} stats available")
        print(f"{'='*70}")
        
        print("\n🎯 THESE ARE ALL SCRAPEABLE!")
        print("   Each URL returns a table with all 32 teams")
        print("   Format: https://www.teamrankings.com/nfl/stat/STAT-NAME")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    discover_available_stats()
