#!/usr/bin/env python3
"""
Scrape Vegas betting lines for upcoming NFL games
Uses ESPN's odds API which aggregates Vegas lines
"""

import requests
import psycopg2
from datetime import datetime
from db_config import DATABASE_CONFIG

def fetch_espn_odds():
    """Fetch betting lines from ESPN odds API"""
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Get current week from the scoreboard
        current_week = data.get('week', {}).get('number', 17)  # Default to 17 if not found
        
        games = []
        for event in data.get('events', []):
            # Get game info
            game_id = event.get('id')
            status = event.get('status', {}).get('type', {}).get('name', '')
            
            competitions = event.get('competitions', [])
            if not competitions:
                continue
                
            comp = competitions[0]
            
            # Get teams
            home_team = None
            away_team = None
            for team in comp.get('competitors', []):
                abbr = team.get('team', {}).get('abbreviation')
                if team.get('homeAway') == 'home':
                    home_team = abbr
                else:
                    away_team = abbr
            
            if not home_team or not away_team:
                continue
            
            # Get odds (spread and total)
            odds = comp.get('odds', [])
            spread_line = None
            total_line = None
            
            if odds:
                # ESPN provides Caesars or consensus lines
                for odd in odds:
                    details = odd.get('details', '')
                    over_under = odd.get('overUnder')
                    
                    # Parse spread (e.g., "HOU -3.5")
                    if details and ('-' in details or '+' in details):
                        parts = details.split()
                        if len(parts) >= 2:
                            try:
                                spread_val = float(parts[1].replace('+', ''))
                                team_abbr = parts[0]
                                # Normalize to home team perspective
                                if team_abbr == home_team:
                                    spread_line = spread_val
                                else:
                                    spread_line = -spread_val
                            except ValueError:
                                pass
                    
                    # Get total
                    if over_under:
                        try:
                            total_line = float(over_under)
                        except (ValueError, TypeError):
                            pass
            
            # Use current_week from scoreboard data
            week = current_week
            
            games.append({
                'game_id': game_id,
                'home_team': home_team,
                'away_team': away_team,
                'spread_line': spread_line,
                'total_line': total_line,
                'week': week,
                'status': status
            })
        
        return games
        
    except Exception as e:
        print(f"❌ Error fetching odds from ESPN: {e}")
        return []

def update_vegas_lines(games):
    """Update database with Vegas lines"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor()
    
    updated = 0
    skipped = 0
    
    for game in games:
        try:
            # Find matching game in database
            cur.execute("""
                SELECT game_id 
                FROM hcl.games 
                WHERE season = 2025 
                  AND week = %s
                  AND home_team = %s 
                  AND away_team = %s
                  AND spread_line IS NULL
            """, (game['week'], game['home_team'], game['away_team']))
            
            result = cur.fetchone()
            
            if result and game['spread_line'] is not None:
                # Update the game with Vegas lines
                cur.execute("""
                    UPDATE hcl.games 
                    SET spread_line = %s,
                        total_line = %s
                    WHERE season = 2025 
                      AND week = %s
                      AND home_team = %s 
                      AND away_team = %s
                """, (
                    game['spread_line'],
                    game['total_line'],
                    game['week'],
                    game['home_team'],
                    game['away_team']
                ))
                updated += 1
                print(f"✅ Updated {game['away_team']} @ {game['home_team']} (Week {game['week']}): {game['spread_line']} / O/U {game['total_line']}")
            else:
                skipped += 1
                
        except Exception as e:
            print(f"❌ Error updating {game['away_team']} @ {game['home_team']}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return updated, skipped

if __name__ == '__main__':
    print("=" * 60)
    print("SCRAPING VEGAS BETTING LINES FROM ESPN")
    print("=" * 60)
    print()
    
    print("📥 Fetching current odds from ESPN...")
    games = fetch_espn_odds()
    
    if not games:
        print("❌ No games found!")
        exit(1)
    
    print(f"✅ Found {len(games)} games with odds\n")
    
    print("💾 Updating database with Vegas lines...")
    updated, skipped = update_vegas_lines(games)
    
    print()
    print("=" * 60)
    print(f"✅ COMPLETE: Updated {updated} games, skipped {skipped}")
    print("=" * 60)
