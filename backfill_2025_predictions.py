"""
Backfill 2025 Season Predictions
=================================

Generate and save predictions for all 2025 games (weeks 1-12)
then update with actual results for completed games.

This populates the tracking system with historical data.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DATABASE_CONFIG
from ml.predict_week import WeeklyPredictor

def backfill_predictions():
    """Generate predictions for all 2025 games and update with results"""
    
    print("=" * 70)
    print("  BACKFILL 2025 SEASON PREDICTIONS")
    print("=" * 70)
    
    # Initialize predictor
    print("\n[1/4] Loading ML models...")
    predictor = WeeklyPredictor()
    
    # Get all 2025 weeks with games
    print("\n[2/4] Finding 2025 games...")
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT DISTINCT week 
        FROM hcl.games 
        WHERE season = 2025 
        ORDER BY week
    """)
    weeks = [row['week'] for row in cur.fetchall()]
    print(f"    Found weeks: {weeks}")
    
    total_saved = 0
    
    # Generate predictions for each week
    print("\n[3/4] Generating predictions for each week...")
    for week in weeks:
        print(f"\n  Week {week}:")
        try:
            predictions = predictor.predict_week(2025, week)
            
            # Save each prediction
            for p in predictions:
                insert_sql = """
                    INSERT INTO hcl.ml_predictions (
                        game_id, season, week, home_team, away_team, game_date,
                        predicted_winner, win_confidence, home_win_prob, away_win_prob,
                        predicted_home_score, predicted_away_score, predicted_margin, ai_spread,
                        vegas_spread, vegas_total
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (game_id) DO NOTHING
                """
                
                cur.execute(insert_sql, (
                    p.get('game_id'),
                    p.get('season'),
                    p.get('week'),
                    p.get('home_team'),
                    p.get('away_team'),
                    p.get('game_date'),
                    p.get('predicted_winner'),
                    p.get('confidence'),
                    p.get('home_win_prob'),
                    p.get('away_win_prob'),
                    p.get('predicted_home_score'),
                    p.get('predicted_away_score'),
                    p.get('predicted_margin'),
                    p.get('ai_spread'),
                    p.get('vegas_spread'),
                    p.get('total_line')
                ))
            
            conn.commit()
            total_saved += len(predictions)
            print(f"    ✅ Saved {len(predictions)} predictions")
            
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
            continue
    
    print(f"\n  Total predictions saved: {total_saved}")
    
    # Update with actual results
    print("\n[4/4] Updating predictions with actual results...")
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
    
    print(f"    ✅ Updated {updated_count} predictions with actual results")
    
    # Show final statistics
    print("\n" + "=" * 70)
    print("  BACKFILL COMPLETE - 2025 SEASON SUMMARY")
    print("=" * 70)
    
    stats_sql = """
        SELECT 
            COUNT(*) as total_games,
            SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct_predictions,
            CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,2)) as win_accuracy,
            CAST(AVG(margin_prediction_error) AS NUMERIC(10,2)) as avg_margin_error,
            CAST(AVG(score_prediction_error_home) AS NUMERIC(10,2)) as avg_home_error,
            CAST(AVG(score_prediction_error_away) AS NUMERIC(10,2)) as avg_away_error,
            MIN(week) as first_week,
            MAX(week) as latest_week
        FROM hcl.ml_predictions
        WHERE season = 2025
          AND result_recorded_at IS NOT NULL
    """
    
    cur.execute(stats_sql)
    stats = cur.fetchone()
    
    if stats and stats['total_games'] > 0:
        print(f"\n📊 Overall Performance:")
        print(f"   Games: {stats['total_games']}")
        print(f"   Correct: {stats['correct_predictions']}")
        print(f"   Win/Loss Accuracy: {stats['win_accuracy']}%")
        print(f"   Avg Margin Error: {stats['avg_margin_error']} points")
        print(f"   Avg Score Error (Home): {stats['avg_home_error']} points")
        print(f"   Avg Score Error (Away): {stats['avg_away_error']} points")
        print(f"   Weeks Tracked: {stats['first_week']} - {stats['latest_week']}")
    
    # Week-by-week breakdown
    weekly_sql = """
        SELECT 
            week,
            COUNT(*) as games,
            SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct,
            CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)) as accuracy
        FROM hcl.ml_predictions
        WHERE season = 2025
          AND result_recorded_at IS NOT NULL
        GROUP BY week
        ORDER BY week
    """
    
    cur.execute(weekly_sql)
    weekly_stats = cur.fetchall()
    
    if weekly_stats:
        print(f"\n📈 Week-by-Week Results:")
        print(f"   {'Week':<6} {'Games':<8} {'Correct':<10} {'Accuracy'}")
        print(f"   {'-'*6} {'-'*8} {'-'*10} {'-'*10}")
        for week in weekly_stats:
            print(f"   {week['week']:<6} {week['games']:<8} {week['correct']:<10} {week['accuracy']}%")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("  Ready! Visit Admin page to see live performance tracking")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    backfill_predictions()
