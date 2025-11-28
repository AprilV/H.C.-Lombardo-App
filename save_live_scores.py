#!/usr/bin/env python3
"""
Save Live Scores to Database
=============================
Fetches live NFL scores from ESPN API and saves them to the database.
Also locks the closing spread before games start.

This runs as a background service during game days to keep scores updated.
"""

import requests
import psycopg2
from datetime import datetime, timedelta
import time
import sys
import os
from dotenv import load_dotenv

load_dotenv()

class LiveScoreSaver:
    """Saves live NFL scores and locks spreads before kickoff"""
    
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'nfl_analytics'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
    def get_espn_scores(self):
        """Fetch current scores from ESPN API"""
        try:
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                competition = event['competitions'][0]
                
                # Get teams and scores
                home_team = None
                away_team = None
                home_score = None
                away_score = None
                
                for team in competition['competitors']:
                    abbrev = team['team']['abbreviation']
                    score = int(team['score']) if team.get('score') else None
                    
                    if team['homeAway'] == 'home':
                        home_team = abbrev
                        home_score = score
                    else:
                        away_team = abbrev
                        away_score = score
                
                # Get game status
                status = competition['status']['type']['name']
                game_date = event['date'][:10]  # YYYY-MM-DD
                
                # Get current spread if available
                current_spread = None
                if 'odds' in competition and len(competition['odds']) > 0:
                    odds = competition['odds'][0]
                    if 'spread' in odds:
                        # ESPN spread format: negative means home favored
                        current_spread = float(odds['spread'])
                
                games.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score,
                    'away_score': away_score,
                    'status': status,
                    'game_date': game_date,
                    'current_spread': current_spread
                })
            
            return games
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch ESPN scores: {e}")
            return []
    
    def save_scores_to_db(self, games):
        """Save scores and lock spreads in database"""
        if not games:
            return
        
        try:
            # Use Unix socket with peer authentication (no password needed)
            conn = psycopg2.connect(
                dbname=self.db_config['dbname'],
                user=self.db_config['user'],
                host='',  # Empty host = Unix socket
            )
            cur = conn.cursor()
            
            updates = 0
            spread_locks = 0
            
            for game in games:
                # Find matching game in database
                cur.execute("""
                    SELECT game_id, home_score, away_score, closing_spread, kickoff_time_utc
                    FROM hcl.games
                    WHERE home_team = %s 
                      AND away_team = %s
                      AND game_date = %s
                      AND season = EXTRACT(YEAR FROM CURRENT_DATE)
                """, (game['home_team'], game['away_team'], game['game_date']))
                
                result = cur.fetchone()
                if not result:
                    continue
                
                game_id, db_home_score, db_away_score, closing_spread, kickoff_time = result
                
                # Lock spread before kickoff (if not already locked)
                if closing_spread is None and game['current_spread'] is not None:
                    # Check if game is about to start (within 1 hour of kickoff)
                    if kickoff_time:
                        now = datetime.now(kickoff_time.tzinfo)
                        if now >= kickoff_time - timedelta(hours=1):
                            cur.execute("""
                                UPDATE hcl.games 
                                SET closing_spread = %s,
                                    updated_at = NOW()
                                WHERE game_id = %s
                            """, (game['current_spread'], game_id))
                            spread_locks += 1
                            print(f"  🔒 Locked spread for {game['away_team']}@{game['home_team']}: {game['current_spread']}")
                
                # Update scores if they've changed
                if game['home_score'] is not None and game['away_score'] is not None:
                    if db_home_score != game['home_score'] or db_away_score != game['away_score']:
                        cur.execute("""
                            UPDATE hcl.games 
                            SET home_score = %s,
                                away_score = %s,
                                updated_at = NOW()
                            WHERE game_id = %s
                        """, (game['home_score'], game['away_score'], game_id))
                        updates += 1
                        print(f"  ✅ Updated {game['away_team']} {game['away_score']} @ {game['home_team']} {game['home_score']}")
            
            conn.commit()
            
            if updates > 0 or spread_locks > 0:
                print(f"\n[SUCCESS] Updated {updates} scores, locked {spread_locks} spreads")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Database save failed: {e}")
    
    def run_once(self):
        """Run a single update cycle"""
        print("\n" + "="*70)
        print(f"LIVE SCORE UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        games = self.get_espn_scores()
        
        if games:
            print(f"\n[INFO] Found {len(games)} games from ESPN")
            self.save_scores_to_db(games)
        else:
            print("\n[INFO] No games found")
        
        print("="*70 + "\n")
    
    def run_continuous(self, interval_minutes=5):
        """Run continuous updates"""
        print(f"\n[CONTINUOUS] Starting live score updates (every {interval_minutes} minutes)")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_once()
                
                print(f"[WAITING] Next update in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n[STOPPED] Live score updates stopped by user")


if __name__ == "__main__":
    saver = LiveScoreSaver()
    
    # Check for continuous mode
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        saver.run_continuous(interval)
    else:
        saver.run_once()
        sys.exit(0)
