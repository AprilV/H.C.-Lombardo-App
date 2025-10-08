"""
H.C. Lombardo - Live Data Scraper
Scrapes REAL NFL stats from TeamRankings.com
"""
import requests
from bs4 import BeautifulSoup
import re

def scrape_offense_stats():
    """Scrape PPG from TeamRankings.com"""
    url = "https://www.teamrankings.com/nfl/stat/points-per-game"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    teams = []
    table = soup.find('table', class_='tr-table')
    
    if table:
        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                team_name = cells[1].get_text(strip=True)
                ppg = float(cells[2].get_text(strip=True))
                teams.append({'name': team_name, 'ppg': ppg})
    
    print(f"✓ Scraped {len(teams)} teams - Offense (PPG)")
    return teams

def scrape_defense_stats():
    """Scrape PA from TeamRankings.com"""
    url = "https://www.teamrankings.com/nfl/stat/opponent-points-per-game"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    teams = []
    table = soup.find('table', class_='tr-table')
    
    if table:
        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                team_name = cells[1].get_text(strip=True)
                pa = float(cells[2].get_text(strip=True))
                teams.append({'name': team_name, 'pa': pa})
    
    print(f"✓ Scraped {len(teams)} teams - Defense (PA)")
    return teams

def combine_stats():
    """Combine offense and defense stats"""
    print("\n" + "="*60)
    print("SCRAPING LIVE NFL DATA FROM TEAMRANKINGS.COM")
    print("="*60 + "\n")
    
    offense = scrape_offense_stats()
    defense = scrape_defense_stats()
    
    # Combine by team name
    combined = []
    for off_team in offense:
        # Find matching defense stats
        def_team = next((d for d in defense if d['name'] == off_team['name']), None)
        
        if def_team:
            combined.append({
                'name': off_team['name'],
                'ppg': off_team['ppg'],
                'pa': def_team['pa']
            })
    
    print(f"\n✓ Combined data for {len(combined)} teams")
    return combined

if __name__ == "__main__":
    teams = combine_stats()
    
    print("\n" + "="*60)
    print("SAMPLE DATA (First 5 teams):")
    print("="*60)
    for team in teams[:5]:
        print(f"{team['name']:30} PPG: {team['ppg']:5.1f}  PA: {team['pa']:5.1f}")
