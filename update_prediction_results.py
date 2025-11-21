"""
Update Prediction Results
========================

Automatically update ml_predictions table with actual game results
after new data is loaded into the games table.

Usage:
    python update_prediction_results.py

Run this after:
- Sunday night games complete
- Monday night games complete  
- Thursday night games complete
- Any time new game results are loaded

What it does:
1. Finds all predictions with corresponding completed games
2. Updates actual winner, scores, and margin
3. Calculates win_prediction_correct and margin_prediction_error
4. Sets result_recorded_at timestamp
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DB_CONFIG

def update_prediction_results():
    """Update predictions with actual results from completed games"""
    
    print("=" * 60)
    print("  UPDATE PREDICTION RESULTS")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Update all predictions that have results but haven't been scored yet
        update_sql = """
            UPDATE hcl.ml_predictions mp
            SET 
                actual_winner = CASE 
                    WHEN g.home_score > g.away_score THEN g.home_team
                    WHEN g.away_score > g.home_score THEN g.away_team
                    ELSE 'TIE'
                END,
                actual_home_score = g.home_score,
                actual_away_score = g.away_score,
                actual_margin = g.home_score - g.away_score,
                win_prediction_correct = CASE 
                    WHEN g.home_score > g.away_score THEN mp.predicted_winner = g.home_team
                    WHEN g.away_score > g.home_score THEN mp.predicted_winner = g.away_team
                    ELSE FALSE
                END,
                score_prediction_error_home = ABS(mp.predicted_home_score - g.home_score),
                score_prediction_error_away = ABS(mp.predicted_away_score - g.away_score),
                margin_prediction_error = ABS(mp.predicted_margin - (g.home_score - g.away_score)),
                result_recorded_at = NOW()
            FROM hcl.games g
            WHERE mp.game_id = g.game_id
              AND g.home_score IS NOT NULL
              AND g.away_score IS NOT NULL
              AND mp.result_recorded_at IS NULL
        """
        
        cur.execute(update_sql)
        updated_count = cur.rowcount
        
        conn.commit()
        
        if updated_count > 0:
            print(f"\n✅ Updated {updated_count} predictions with actual results")
            
            # Show summary stats
            stats_sql = """
                SELECT 
                    COUNT(*) as total_games,
                    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct_predictions,
                    ROUND(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END), 2) as win_accuracy,
                    ROUND(AVG(margin_prediction_error), 2) as avg_margin_error,
                    MAX(week) as latest_week
                FROM hcl.ml_predictions
                WHERE season = 2025
                  AND result_recorded_at IS NOT NULL
            """
            
            cur.execute(stats_sql)
            stats = cur.fetchone()
            
            if stats and stats['total_games'] > 0:
                print("\n📊 2025 Season Performance:")
                print(f"   Total Games: {stats['total_games']}")
                print(f"   Correct Picks: {stats['correct_predictions']}")
                print(f"   Win/Loss Accuracy: {stats['win_accuracy']}%")
                print(f"   Avg Margin Error: {stats['avg_margin_error']} points")
                print(f"   Latest Week: {stats['latest_week']}")
        else:
            print("\n⚠️  No new results to update")
            print("   All predictions are either:")
            print("   - Already updated with results")
            print("   - For games that haven't been played yet")
        
        # Check for pending predictions
        pending_sql = """
            SELECT COUNT(*) as pending
            FROM hcl.ml_predictions
            WHERE season = 2025
              AND result_recorded_at IS NULL
        """
        
        cur.execute(pending_sql)
        pending = cur.fetchone()
        
        if pending and pending['pending'] > 0:
            print(f"\n🔄 {pending['pending']} predictions waiting for results")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("  UPDATE COMPLETE")
        print("=" * 60)
        
        return updated_count
        
    except Exception as e:
        print(f"\n❌ Error updating predictions: {e}")
        return 0

if __name__ == '__main__':
    update_prediction_results()
