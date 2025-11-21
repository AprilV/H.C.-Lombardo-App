"""
Add Week 1 2025 predictions to tracking table
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
sys.path.insert(0, 'c:\\IS330\\H.C Lombardo App')

from ml.predict_week import WeeklyPredictor
from db_config import DATABASE_CONFIG

def add_week1():
    print("=" * 60)
    print("Adding Week 1 2025 Predictions to Tracking Table")
    print("=" * 60)
    
    predictor = WeeklyPredictor()
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if Week 1 already exists
    cur.execute("SELECT COUNT(*) as count FROM hcl.ml_predictions WHERE season = 2025 AND week = 1")
    existing = cur.fetchone()['count']
    
    if existing > 0:
        print(f"\n⚠️  Week 1 already has {existing} predictions. Skipping...")
        cur.close()
        conn.close()
        return
    
    print("\n[1/3] Generating Week 1 predictions...")
    try:
        predictions = predictor.predict_week(2025, 1)
        print(f"    ✅ Generated {len(predictions)} predictions")
    except Exception as e:
        print(f"    ❌ Error generating predictions: {e}")
        cur.close()
        conn.close()
        return
    
    print("\n[2/3] Saving predictions to tracking table...")
    saved = 0
    for p in predictions:
        try:
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
        except Exception as e:
            print(f"    ⚠️  Error saving prediction: {e}")
    
    conn.commit()
    print(f"    ✅ Saved {saved} predictions")
    
    print("\n[3/3] Updating with actual results...")
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
            home_score_prediction_error = ABS(p.predicted_home_score - g.home_score),
            away_score_prediction_error = ABS(p.predicted_away_score - g.away_score),
            result_recorded_at = NOW()
        FROM hcl.games g
        WHERE p.game_id = g.game_id
            AND p.season = 2025
            AND p.week = 1
            AND g.home_score IS NOT NULL
            AND g.away_score IS NOT NULL
    """
    
    cur.execute(update_sql)
    updated = cur.rowcount
    conn.commit()
    print(f"    ✅ Updated {updated} predictions with actual results")
    
    # Show summary
    print("\n" + "=" * 60)
    print("WEEK 1 SUMMARY")
    print("=" * 60)
    
    cur.execute("""
        SELECT 
            COUNT(*) as total_games,
            SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct,
            CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)) as accuracy,
            CAST(AVG(margin_prediction_error) AS NUMERIC(10,1)) as avg_margin_error
        FROM hcl.ml_predictions
        WHERE season = 2025 AND week = 1 AND result_recorded_at IS NOT NULL
    """)
    
    stats = cur.fetchone()
    if stats and stats['total_games'] > 0:
        print(f"Games: {stats['total_games']}")
        print(f"Correct: {stats['correct']}/{stats['total_games']}")
        print(f"Accuracy: {stats['accuracy']}%")
        print(f"Avg Margin Error: {stats['avg_margin_error']} pts")
    
    cur.close()
    conn.close()
    print("\n✅ Week 1 predictions added successfully!")

if __name__ == '__main__':
    add_week1()
