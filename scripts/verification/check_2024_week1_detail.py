import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Check if Week 1 predictions exist
cur.execute("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN result_recorded_at IS NOT NULL THEN 1 ELSE 0 END) as with_results
    FROM hcl.ml_predictions 
    WHERE season = 2024 
    AND week = 1
""")

result = cur.fetchone()
print(f"2024 Week 1 predictions: {result['total']} total, {result['with_results']} with results")

if result['total'] > 0:
    # Show the predictions
    cur.execute("""
        SELECT game_id, home_team, away_team, 
               predicted_winner, actual_winner,
               win_prediction_correct, result_recorded_at
        FROM hcl.ml_predictions 
        WHERE season = 2024 AND week = 1
        ORDER BY game_id
    """)
    
    preds = cur.fetchall()
    print("\nWeek 1 2024 predictions:")
    for p in preds:
        status = "✅" if p['win_prediction_correct'] else "❌" if p['actual_winner'] else "⏳"
        print(f"  {p['home_team']} vs {p['away_team']}: Predicted {p['predicted_winner']} → {status} (Actual: {p['actual_winner'] or 'TBD'})")

conn.close()
