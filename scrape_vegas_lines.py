#!/usr/bin/env python3
"""
Scrape Vegas betting lines for upcoming NFL games
Uses ESPN's odds API which aggregates Vegas lines
"""

import requests
import psycopg2
import argparse
from datetime import datetime
from db_config import DATABASE_CONFIG

def fetch_espn_odds(target_season=None, regular_season_only=True):
    """Fetch betting lines from ESPN odds API"""
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Pull scoreboard context and allow explicit season override.
        scoreboard_season = int(data.get('season', {}).get('year') or datetime.utcnow().year)
        scoreboard_type = int(data.get('season', {}).get('type') or 2)
        current_week = int(data.get('week', {}).get('number') or 0)
        season_to_use = int(target_season) if target_season is not None else scoreboard_season
        
        games = []
        for event in data.get('events', []):
            event_season = int(event.get('season', {}).get('year') or season_to_use)
            event_type = int(event.get('season', {}).get('type') or scoreboard_type)

            if event_season != season_to_use:
                continue
            if regular_season_only and event_type != 2:
                continue

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
            
            event_week = int(event.get('week', {}).get('number') or current_week)
            
            games.append({
                'game_id': game_id,
                'season': event_season,
                'season_type': event_type,
                'home_team': home_team,
                'away_team': away_team,
                'spread_line': spread_line,
                'total_line': total_line,
                'week': event_week,
                'status': status
            })
        
        return {
            'scoreboard_season': scoreboard_season,
            'scoreboard_season_type': scoreboard_type,
            'scoreboard_week': current_week,
            'target_season': season_to_use,
            'games': games
        }
        
    except Exception as e:
        print(f"❌ Error fetching odds from ESPN: {e}")
        return {
            'scoreboard_season': None,
            'scoreboard_season_type': None,
            'scoreboard_week': None,
            'target_season': target_season,
            'games': []
        }

def update_vegas_lines(games, season):
    """Update database with Vegas lines"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor()
    
    updated = 0
    skipped = 0
    missing = 0
    
    for game in games:
        try:
            if game['spread_line'] is None:
                skipped += 1
                continue

            # Find matching game in database
            cur.execute("""
                SELECT game_id 
                FROM hcl.games 
                WHERE season = %s 
                  AND week = %s
                  AND home_team = %s 
                  AND away_team = %s
            """, (season, game['week'], game['home_team'], game['away_team']))
            
            result = cur.fetchone()
            
            if result:
                # Update the game with Vegas lines
                cur.execute("""
                    UPDATE hcl.games 
                    SET spread_line = %s,
                        total_line = %s
                    WHERE season = %s 
                      AND week = %s
                      AND home_team = %s 
                      AND away_team = %s
                """, (
                    game['spread_line'],
                    game['total_line'],
                    season,
                    game['week'],
                    game['home_team'],
                    game['away_team']
                ))
                updated += 1
                print(f"✅ Updated {game['away_team']} @ {game['home_team']} (Week {game['week']}): {game['spread_line']} / O/U {game['total_line']}")
            else:
                missing += 1
                
        except Exception as e:
            print(f"❌ Error updating {game['away_team']} @ {game['home_team']}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return updated, skipped, missing

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape and persist ESPN Vegas lines')
    parser.add_argument('--season', type=int, default=None, help='Target season (defaults to ESPN scoreboard season)')
    parser.add_argument('--include-postseason', action='store_true', help='Include non-regular-season events')
    args = parser.parse_args()

    print("=" * 60)
    print("SCRAPING VEGAS BETTING LINES FROM ESPN")
    print("=" * 60)
    print()
    
    print("📥 Fetching current odds from ESPN...")
    payload = fetch_espn_odds(
        target_season=args.season,
        regular_season_only=not args.include_postseason
    )
    games = payload.get('games', [])
    
    if not games:
        print("❌ No games found!")
        exit(1)
    
    print(
        "✅ Scoreboard context: "
        f"season={payload.get('scoreboard_season')} "
        f"type={payload.get('scoreboard_season_type')} "
        f"week={payload.get('scoreboard_week')}"
    )
    print(f"✅ Found {len(games)} games for season {payload.get('target_season')}\n")
    
    print("💾 Updating database with Vegas lines...")
    updated, skipped, missing = update_vegas_lines(games, season=payload.get('target_season'))
    
    print()
    print("=" * 60)
    print(f"✅ COMPLETE: Updated {updated} games, skipped_no_odds {skipped}, missing_in_db {missing}")
    print("=" * 60)
