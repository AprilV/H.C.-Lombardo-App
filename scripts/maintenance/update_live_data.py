"""
Continuous NFLverse Data Updater
Updates scores and stats from NFLverse every 5 minutes during game days
"""
import nfl_data_py as nfl
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import logging
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname='nfl_analytics',
        user='postgres',
        password='',
        host=''  # Unix socket
    )


def update_current_season_scores(season: int = 2025, schema: str = 'hcl'):
    """
    Update scores and stats for current season from NFLverse
    This runs every 5 minutes to keep data fresh
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info(f"Fetching latest data from NFLverse for {season} season...")
        
        # Get latest schedules with scores
        schedules = nfl.import_schedules([season])
        
        # Update games table with latest scores
        games_updated = 0
        for _, row in schedules.iterrows():
            game_id = row['game_id']
            home_score = row.get('home_score')
            away_score = row.get('away_score')
            
            # Only update if scores are available
            if home_score is not None and away_score is not None:
                update_query = f"""
                    UPDATE {schema}.games
                    SET home_score = %s, away_score = %s
                    WHERE game_id = %s
                """
                cur.execute(update_query, (home_score, away_score, game_id))
                if cur.rowcount > 0:
                    games_updated += 1
        
        conn.commit()
        logger.info(f"Updated {games_updated} games with latest scores")
        
        # Update team game stats
        logger.info("Updating team game stats...")
        weekly_stats = nfl.import_weekly_data([season])
        
        stats_updated = 0
        for _, row in weekly_stats.iterrows():
            # Build update query for team_game_stats
            update_query = f"""
                UPDATE {schema}.team_game_stats
                SET 
                    points = %s,
                    total_yards = %s,
                    passing_yards = %s,
                    rushing_yards = %s,
                    turnovers = %s,
                    result = %s
                WHERE game_id = %s AND team = %s
            """
            
            result = 'W' if row.get('result') == 1 else 'L' if row.get('result') == 0 else 'T'
            
            cur.execute(update_query, (
                row.get('points'),
                row.get('total_yards'),
                row.get('passing_yards'),
                row.get('rushing_yards'),
                row.get('turnovers'),
                result,
                row.get('game_id'),
                row.get('recent_team')
            ))
            
            if cur.rowcount > 0:
                stats_updated += 1
        
        conn.commit()
        logger.info(f"Updated {stats_updated} team game stats")
        
        cur.close()
        conn.close()
        
        return games_updated, stats_updated
        
    except Exception as e:
        logger.error(f"Error updating NFLverse data: {e}")
        return 0, 0


def run_continuous(interval_seconds: int = 300):
    """
    Run continuous updates every 5 minutes (300 seconds)
    """
    logger.info(f"Starting continuous NFLverse updater (every {interval_seconds} seconds)")
    
    while True:
        try:
            logger.info("=" * 50)
            logger.info(f"Update cycle started at {datetime.now()}")
            
            games_updated, stats_updated = update_current_season_scores()
            
            logger.info(f"Update complete: {games_updated} games, {stats_updated} stats updated")
            logger.info(f"Next update in {interval_seconds} seconds")
            logger.info("=" * 50)
            
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            logger.info("Shutting down updater...")
            break
        except Exception as e:
            logger.error(f"Error in update cycle: {e}")
            time.sleep(interval_seconds)


def run_once():
    """Run a single update"""
    logger.info("Running single NFLverse update...")
    games_updated, stats_updated = update_current_season_scores()
    logger.info(f"Update complete: {games_updated} games, {stats_updated} stats updated")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        run_once()
    else:
        run_continuous(300)  # 5 minutes
