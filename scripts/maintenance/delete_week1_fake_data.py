"""
Delete fake Week 1 predictions that were artificially created
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DATABASE_CONFIG

def delete_week1():
    print("=" * 70)
    print("Deleting Fake Week 1 Predictions")
    print("=" * 70)
    
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check current stats before deletion
    cur.execute("""
        SELECT 
            COUNT(*) as total_games,
            SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct,
            CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)) as accuracy
        FROM hcl.ml_predictions
        WHERE season = 2025 AND result_recorded_at IS NOT NULL
    """)
    
    before = cur.fetchone()
    print(f"\nBEFORE Deletion:")
    print(f"  Total Games: {before['total_games']}")
    print(f"  Correct: {before['correct']}")
    print(f"  Accuracy: {before['accuracy']}%")
    
    # Delete Week 1
    cur.execute("DELETE FROM hcl.ml_predictions WHERE season = 2025 AND week = 1")
    deleted = cur.rowcount
    conn.commit()
    
    print(f"\n✅ Deleted {deleted} fake Week 1 predictions")
    
    # Check stats after deletion
    cur.execute("""
        SELECT 
            COUNT(*) as total_games,
            SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct,
            CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)) as accuracy
        FROM hcl.ml_predictions
        WHERE season = 2025 AND result_recorded_at IS NOT NULL
    """)
    
    after = cur.fetchone()
    print(f"\nAFTER Deletion:")
    print(f"  Total Games: {after['total_games']}")
    print(f"  Correct: {after['correct']}")
    print(f"  Accuracy: {after['accuracy']}%")
    
    print(f"\n✅ Week 1 fake data removed! Only real ML predictions remain.")
    print(f"   Dashboard will now show accurate performance (Weeks 2-11)")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    delete_week1()
