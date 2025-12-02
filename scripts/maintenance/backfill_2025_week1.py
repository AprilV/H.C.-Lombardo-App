"""
Backfill 2025 Week 1 ML predictions using 2024 end-of-season data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DATABASE_CONFIG
from ml.predict_week import WeeklyPredictor
from datetime import datetime

def backfill_2025_week1():
    """Generate and save 2025 Week 1 predictions using 2024 data"""
    
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("=" * 80)
        print("BACKFILLING 2025 WEEK 1 PREDICTIONS")
        print("=" * 80)
        
        # Initialize predictor
        predictor = WeeklyPredictor()
        
        # Generate predictions for 2025 Week 1
        season = 2025
        week = 1
        
        print(f"\nGenerating predictions for Week {week}...")
        predictions = predictor.predict_week(season, week)
        
        if not predictions:
            print(f"No games found for Week {week}")
            return
        
        print(f"Generated {len(predictions)} predictions")
        
        # Save predictions to database
        saved_count = 0
        for pred in predictions:
            # Check if prediction already exists
            cur.execute("""
                SELECT prediction_id FROM hcl.ml_predictions
                WHERE game_id = %s
            """, (pred['game_id'],))
            
            existing = cur.fetchone()
            
            if existing:
                print(f"  ⚠️ Prediction already exists for game_id {pred['game_id']}, skipping")
                continue
            
            # Insert new prediction
            cur.execute("""
                INSERT INTO hcl.ml_predictions (
                    game_id, season, week, home_team, away_team,
                    predicted_winner, win_confidence, predicted_margin,
                    predicted_at
                ) VALUES (
                    %(game_id)s, %(season)s, %(week)s, %(home_team)s, %(away_team)s,
                    %(predicted_winner)s, %(confidence)s, %(predicted_margin)s,
                    NOW()
                )
            """, pred)
            saved_count += 1
        
        conn.commit()
        print(f"✅ Saved {saved_count} predictions")
        
        # Now update with actual results
        print(f"\nUpdating predictions with actual results...")
        
        cur.execute("""
            SELECT 
                mp.prediction_id,
                mp.game_id,
                mp.home_team,
                mp.away_team,
                mp.predicted_winner,
                mp.predicted_margin,
                g.home_score,
                g.away_score
            FROM hcl.ml_predictions mp
            JOIN hcl.games g ON mp.game_id = g.game_id
            WHERE mp.season = %s 
            AND mp.week = %s
            AND g.home_score IS NOT NULL
            AND g.away_score IS NOT NULL
        """, (season, week))
        
        predictions_to_update = cur.fetchall()
        print(f"Found {len(predictions_to_update)} games with results")
        
        correct_count = 0
        total_margin_error = 0
        
        for pred in predictions_to_update:
            home_score = pred['home_score']
            away_score = pred['away_score']
            
            # Determine actual winner
            if home_score > away_score:
                actual_winner = pred['home_team']
                actual_margin = home_score - away_score
            else:
                actual_winner = pred['away_team']
                actual_margin = away_score - home_score
            
            # Check if prediction was correct
            win_correct = (pred['predicted_winner'] == actual_winner)
            if win_correct:
                correct_count += 1
            
            # Calculate margin error
            margin_error = abs(pred['predicted_margin'] - actual_margin)
            total_margin_error += margin_error
            
            # Update database
            cur.execute("""
                UPDATE hcl.ml_predictions
                SET 
                    actual_winner = %s,
                    actual_margin = %s,
                    win_prediction_correct = %s,
                    margin_prediction_error = %s,
                    result_recorded_at = NOW()
                WHERE prediction_id = %s
            """, (actual_winner, actual_margin, win_correct, margin_error, pred['prediction_id']))
            
            # Display result
            status = "✅ CORRECT" if win_correct else "❌ WRONG"
            print(f"  {pred['home_team']} vs {pred['away_team']}: Predicted {pred['predicted_winner']} → {status} ({actual_winner} won)")
        
        conn.commit()
        
        # Calculate accuracy
        if predictions_to_update:
            accuracy = (correct_count / len(predictions_to_update)) * 100
            avg_margin_error = total_margin_error / len(predictions_to_update)
            
            print(f"\n" + "=" * 80)
            print(f"2025 WEEK 1 SUMMARY")
            print(f"=" * 80)
            print(f"Games: {len(predictions_to_update)}")
            print(f"Correct: {correct_count}/{len(predictions_to_update)}")
            print(f"Accuracy: {accuracy:.1f}%")
            print(f"Avg Margin Error: {avg_margin_error:.1f} pts")
            print(f"=" * 80)
        
        print(f"\n✅ 2025 Week 1 backfill complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    backfill_2025_week1()
