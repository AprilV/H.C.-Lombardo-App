#!/usr/bin/env python3
"""
Standalone Background Updater Service
Run this as a separate process from the API server
Updates NFL data every 30 minutes
"""
import logging
import time
import sys
import os
from datetime import datetime

# Add scripts/maintenance to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts', 'maintenance'))
from multi_source_data_fetcher import MultiSourceDataFetcher
import nfl_data_py as nfl
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/H.C.-Lombardo-App/logs/background_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def update_nflverse_data(season: int = 2025):
    """Update game scores and team stats from NFLverse"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'nfl_analytics'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'aprilv120')
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get latest schedules with scores
        schedules = nfl.import_schedules([season])
        
        # Update games table with latest scores  
        games_updated = 0
        for _, row in schedules.iterrows():
            game_id = str(row['game_id'])  # Convert to string to avoid integer overflow
            home_score = row.get('home_score')
            away_score = row.get('away_score')
            
            if home_score is not None and away_score is not None and not (isinstance(home_score, float) and home_score != home_score):  # Check for NaN
                try:
                    cur.execute("""
                        UPDATE hcl.games
                        SET home_score = %s, away_score = %s
                        WHERE game_id = %s
                    """, (int(home_score), int(away_score), game_id))
                    if cur.rowcount > 0:
                        games_updated += 1
                except Exception as e:
                    logger.warning(f"Could not update game {game_id}: {e}")
                    continue
        
        conn.commit()
        
        # Update team game stats
        weekly_stats = nfl.import_weekly_data([season])
        
        stats_updated = 0
        for _, row in weekly_stats.iterrows():
            game_id = str(row.get('game_id', ''))
            team = row.get('recent_team')
            
            if not game_id or not team:
                continue
                
            try:
                result = 'W' if row.get('result') == 1 else 'L' if row.get('result') == 0 else 'T'
                
                cur.execute("""
                    UPDATE hcl.team_game_stats
                    SET 
                        points = %s,
                        total_yards = %s,
                        passing_yards = %s,
                        rushing_yards = %s,
                        turnovers = %s,
                        result = %s
                    WHERE game_id = %s AND team = %s
                """, (
                    row.get('points'),
                    row.get('total_yards'),
                    row.get('passing_yards'),
                    row.get('rushing_yards'),
                    row.get('turnovers'),
                    result,
                    game_id,
                    team
                ))
                
                if cur.rowcount > 0:
                    stats_updated += 1
            except Exception as e:
                logger.warning(f"Could not update stats for {team} game {game_id}: {e}")
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        return games_updated, stats_updated
        
    except Exception as e:
        logger.error(f"Error updating NFLverse data: {e}", exc_info=True)
        return 0, 0

def main():
    """Main update loop"""
    update_interval_minutes = 30
    
    logger.info("=" * 70)
    logger.info("🏈 NFL BACKGROUND DATA UPDATER SERVICE STARTED")
    logger.info(f"⏰ Update interval: {update_interval_minutes} minutes")
    logger.info("=" * 70)
    
    # Wait 60 seconds before first update (let API server fully start)
    logger.info("⏳ Waiting 60 seconds before first update...")
    time.sleep(60)
    
    while True:
        try:
            logger.info("=" * 70)
            logger.info(f"🔄 AUTOMATIC DATA UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 70)
            
            # 1. Update team standings (ESPN + TeamRankings)
            logger.info("📊 Updating team standings...")
            fetcher = MultiSourceDataFetcher()
            fetcher.run_full_update()
            
            # 2. Update game scores and stats (NFLverse)
            logger.info("🏈 Updating game scores and stats...")
            games_updated, stats_updated = update_nflverse_data()
            logger.info(f"   - Updated {games_updated} game scores")
            logger.info(f"   - Updated {stats_updated} team game stats")
            
            logger.info("✅ Automatic update complete")
            logger.info(f"⏰ Next update in {update_interval_minutes} minutes")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Background update failed: {e}", exc_info=True)
            
        # Sleep until next update
        time.sleep(update_interval_minutes * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Background updater stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        raise
