"""
Backfill predictions for 2023 and 2024 seasons
This will give us much more data to validate model performance
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DATABASE_CONFIG
from ml.predict_week import WeeklyPredictor

def backfill_historical_seasons():
    print("=" * 80)
    print("BACKFILLING 2023 & 2024 SEASON PREDICTIONS")
    print("=" * 80)
    
    predictor = WeeklyPredictor()
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    seasons_to_process = [2023, 2024]
    
    for season in seasons_to_process:
        print(f"\n{'='*80}")
        print(f"PROCESSING {season} SEASON")
        print(f"{'='*80}")
        
        # Get all weeks for this season
        cur.execute("""
            SELECT DISTINCT week 
            FROM hcl.games 
            WHERE season = %s 
            ORDER BY week
        """, (season,))
        
        weeks = [row['week'] for row in cur.fetchall()]
        print(f"\nFound {len(weeks)} weeks: {weeks}")
        
        # Skip Week 1 for 2023 (no prior data)
        if season == 2023:
            print(f"\n⚠️  Skipping 2023 Week 1 (no prior season data)")
            weeks = [w for w in weeks if w > 1]
        
        total_saved = 0
        total_updated = 0
        
        for week in weeks:
            print(f"\n  Week {week}:")
            
            try:
                # Generate predictions
                predictions = predictor.predict_week(season, week)
                print(f"    Generated {len(predictions)} predictions")
                
                # Save predictions
                saved = 0
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
                    saved += 1
                
                conn.commit()
                total_saved += saved
                print(f"    ✅ Saved {saved} predictions")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
        
        # Update with actual results for the entire season
        print(f"\n  Updating {season} predictions with actual results...")
        update_sql = """
            UPDATE hcl.ml_predictions p
            SET 
                actual_winner = CASE 
                    WHEN g.home_score > g.away_score THEN g.home_team
                    WHEN g.away_score > g.home_score THEN g.away_team
                    ELSE 'TIE'
                END,
                actual_home_score = g.home_score,
                actual_away_score = g.away_score,
                actual_margin = ABS(g.home_score - g.away_score),
                win_prediction_correct = (
                    (p.predicted_winner = g.home_team AND g.home_score > g.away_score) OR
                    (p.predicted_winner = g.away_team AND g.away_score > g.home_score)
                ),
                margin_prediction_error = ABS(p.predicted_margin - ABS(g.home_score - g.away_score)),
                score_prediction_error_home = ABS(p.predicted_home_score - g.home_score),
                score_prediction_error_away = ABS(p.predicted_away_score - g.away_score),
                result_recorded_at = NOW()
            FROM hcl.games g
            WHERE p.game_id = g.game_id
                AND p.season = %s
                AND g.home_score IS NOT NULL
                AND g.away_score IS NOT NULL
                AND p.result_recorded_at IS NULL
        """
        
        cur.execute(update_sql, (season,))
        updated = cur.rowcount
        conn.commit()
        total_updated += updated
        print(f"    ✅ Updated {updated} predictions with results")
        
        # Show season summary
        cur.execute("""
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct,
                CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)) as accuracy,
                CAST(AVG(margin_prediction_error) AS NUMERIC(10,1)) as avg_margin_error
            FROM hcl.ml_predictions
            WHERE season = %s AND result_recorded_at IS NOT NULL
        """, (season,))
        
        stats = cur.fetchone()
        if stats and stats['total_games'] > 0:
            print(f"\n  {season} SEASON SUMMARY:")
            print(f"    Games: {stats['total_games']}")
            print(f"    Correct: {stats['correct']}/{stats['total_games']}")
            print(f"    Accuracy: {stats['accuracy']}%")
            print(f"    Avg Margin Error: {stats['avg_margin_error']} pts")
    
    # Overall summary
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY - ALL SEASONS")
    print(f"{'='*80}")
    
    cur.execute("""
        SELECT 
            season,
            COUNT(*) as total_games,
            SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct,
            CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)) as accuracy
        FROM hcl.ml_predictions
        WHERE result_recorded_at IS NOT NULL
        GROUP BY season
        ORDER BY season
    """)
    
    all_seasons = cur.fetchall()
    for s in all_seasons:
        print(f"\n{s['season']}: {s['correct']}/{s['total_games']} correct ({s['accuracy']}%)")
    
    cur.close()
    conn.close()
    print(f"\n✅ Historical backfill complete!")

if __name__ == '__main__':
    backfill_historical_seasons()
