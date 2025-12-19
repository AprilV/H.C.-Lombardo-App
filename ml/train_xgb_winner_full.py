"""
XGBoost Win/Loss Prediction Model Training - FULL FEATURE SET
Uses all 30+ advanced metrics including EPA from NFLverse
Date: December 18, 2025
"""

import psycopg2
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import DATABASE_CONFIG

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def load_data(schema='hcl'):
    """Load game data with ALL advanced metrics"""
    print(f"\nConnecting to database schema: {schema}")
    
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        dbname=DATABASE_CONFIG['dbname'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password']
    )
    
    query = f"""
        WITH game_stats AS (
            SELECT 
                tgs.game_id, tgs.team, g.season, g.week, g.game_date,
                tgs.points, tgs.total_yards, tgs.passing_yards, tgs.rushing_yards,
                tgs.yards_per_play, tgs.turnovers, tgs.third_down_pct, tgs.red_zone_pct,
                tgs.epa_per_play, tgs.success_rate, tgs.pass_epa, tgs.rush_epa,
                tgs.cpoe, tgs.pass_success_rate, tgs.rush_success_rate,
                tgs.completion_pct, tgs.qb_rating, tgs.interceptions, tgs.sacks_taken,
                tgs.yards_per_carry, tgs.explosive_play_pct, tgs.time_of_possession_pct
            FROM {schema}.team_game_stats tgs
            JOIN {schema}.games g ON tgs.game_id = g.game_id
            WHERE g.season >= 2020
        ),
        cumulative_stats AS (
            SELECT 
                game_id, team, season, week,
                AVG(points) OVER w as avg_ppg,
                AVG(total_yards) OVER w as avg_yards,
                AVG(passing_yards) OVER w as avg_pass_yards,
                AVG(rushing_yards) OVER w as avg_rush_yards,
                AVG(yards_per_play) OVER w as avg_ypp,
                AVG(turnovers) OVER w as avg_turnovers,
                AVG(third_down_pct) OVER w as avg_3rd_pct,
                AVG(red_zone_pct) OVER w as avg_rz_pct,
                AVG(epa_per_play) OVER w as avg_epa,
                AVG(success_rate) OVER w as avg_success,
                AVG(pass_epa) OVER w as avg_pass_epa,
                AVG(rush_epa) OVER w as avg_rush_epa,
                AVG(cpoe) OVER w as avg_cpoe,
                AVG(pass_success_rate) OVER w as avg_pass_success,
                AVG(rush_success_rate) OVER w as avg_rush_success,
                AVG(completion_pct) OVER w as avg_comp_pct,
                AVG(qb_rating) OVER w as avg_qb_rating,
                AVG(interceptions) OVER w as avg_ints,
                AVG(sacks_taken) OVER w as avg_sacks,
                AVG(yards_per_carry) OVER w as avg_ypc,
                AVG(explosive_play_pct) OVER w as avg_explosive,
                AVG(time_of_possession_pct) OVER w as avg_top
            FROM game_stats
            WINDOW w AS (PARTITION BY team, season ORDER BY week ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)
        )
        SELECT 
            g.game_id, g.season, g.week, g.home_team, g.away_team, g.home_score, g.away_score,
            COALESCE(h.avg_ppg, 20) as home_ppg,
            COALESCE(h.avg_yards, 320) as home_yards,
            COALESCE(h.avg_pass_yards, 220) as home_pass_yards,
            COALESCE(h.avg_rush_yards, 100) as home_rush_yards,
            COALESCE(h.avg_ypp, 5.0) as home_ypp,
            COALESCE(h.avg_turnovers, 1.0) as home_turnovers,
            COALESCE(h.avg_3rd_pct, 40.0) as home_3rd_pct,
            COALESCE(h.avg_rz_pct, 55.0) as home_rz_pct,
            COALESCE(h.avg_epa, 0.0) as home_epa,
            COALESCE(h.avg_success, 45.0) as home_success,
            COALESCE(h.avg_pass_epa, 0.0) as home_pass_epa,
            COALESCE(h.avg_rush_epa, 0.0) as home_rush_epa,
            COALESCE(h.avg_cpoe, 0.0) as home_cpoe,
            COALESCE(h.avg_pass_success, 45.0) as home_pass_success,
            COALESCE(h.avg_rush_success, 45.0) as home_rush_success,
            COALESCE(h.avg_comp_pct, 63.0) as home_comp_pct,
            COALESCE(h.avg_qb_rating, 90.0) as home_qb_rating,
            COALESCE(h.avg_ints, 0.8) as home_ints,
            COALESCE(h.avg_sacks, 2.0) as home_sacks,
            COALESCE(h.avg_ypc, 4.3) as home_ypc,
            COALESCE(h.avg_explosive, 10.0) as home_explosive,
            COALESCE(h.avg_top, 50.0) as home_top,
            COALESCE(a.avg_ppg, 20) as away_ppg,
            COALESCE(a.avg_yards, 320) as away_yards,
            COALESCE(a.avg_pass_yards, 220) as away_pass_yards,
            COALESCE(a.avg_rush_yards, 100) as away_rush_yards,
            COALESCE(a.avg_ypp, 5.0) as away_ypp,
            COALESCE(a.avg_turnovers, 1.0) as away_turnovers,
            COALESCE(a.avg_3rd_pct, 40.0) as away_3rd_pct,
            COALESCE(a.avg_rz_pct, 55.0) as away_rz_pct,
            COALESCE(a.avg_epa, 0.0) as away_epa,
            COALESCE(a.avg_success, 45.0) as away_success,
            COALESCE(a.avg_pass_epa, 0.0) as away_pass_epa,
            COALESCE(a.avg_rush_epa, 0.0) as away_rush_epa,
            COALESCE(a.avg_cpoe, 0.0) as away_cpoe,
            COALESCE(a.avg_pass_success, 45.0) as away_pass_success,
            COALESCE(a.avg_rush_success, 45.0) as away_rush_success,
            COALESCE(a.avg_comp_pct, 63.0) as away_comp_pct,
            COALESCE(a.avg_qb_rating, 90.0) as away_qb_rating,
            COALESCE(a.avg_ints, 0.8) as away_ints,
            COALESCE(a.avg_sacks, 2.0) as away_sacks,
            COALESCE(a.avg_ypc, 4.3) as away_ypc,
            COALESCE(a.avg_explosive, 10.0) as away_explosive,
            COALESCE(a.avg_top, 50.0) as away_top,
            COALESCE(g.spread_line, 0) as spread_line,
            COALESCE(g.total_line, 44) as total_line
        FROM {schema}.games g
        LEFT JOIN cumulative_stats h ON g.game_id = h.game_id AND g.home_team = h.team
        LEFT JOIN cumulative_stats a ON g.game_id = a.game_id AND g.away_team = a.team
        WHERE g.season >= 2020 
          AND g.home_score IS NOT NULL 
          AND g.away_score IS NOT NULL
          AND g.week >= 2
        ORDER BY g.season, g.week, g.game_id
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"Loaded {len(df):,} games from {df['season'].min()}-{df['season'].max()}")
    return df

def prepare_features(df):
    """Prepare features and target"""
    print("\nPreparing features...")
    
    # All feature columns (48 total)
    feature_cols = [col for col in df.columns if col not in 
                   ['game_id', 'season', 'week', 'home_team', 'away_team', 'home_score', 'away_score']]
    
    X = df[feature_cols].values
    y = (df['home_score'] > df['away_score']).astype(int).values
    
    print(f"Features: {len(feature_cols)} columns")
    print(f"Target: {np.sum(y == 1):,} home wins ({100*np.mean(y):.1f}%), {np.sum(y == 0):,} away wins")
    
    return X, y, feature_cols, df

def split_data(X, y, df):
    """Split by season"""
    print("\nSplitting data by season...")
    
    train_mask = df['season'] <= 2023
    val_mask = df['season'] == 2024
    test_mask = df['season'] == 2025
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_val, y_val = X[val_mask], y[val_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    
    print(f"  Training (2020-2023): {len(X_train):,} games")
    print(f"  Validation (2024):    {len(X_val):,} games")
    print(f"  Test (2025):          {len(X_test):,} games")
    
    return X_train, y_train, X_val, y_val, X_test, y_test

def train_model(X_train, y_train, X_val, y_val):
    """Train XGBoost classifier"""
    print_header("TRAINING XGBOOST WITH FULL FEATURE SET")
    
    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    
    print("Training model...")
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    print("Training complete")
    
    return model

def evaluate_model(model, X, y, dataset_name):
    """Evaluate model performance"""
    print(f"\n{dataset_name}:")
    print("-" * 40)
    
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    accuracy = accuracy_score(y, predictions)
    print(f"Accuracy: {accuracy:.1%}")
    
    cm = confusion_matrix(y, predictions)
    if cm.size > 0:
        print(f"\nConfusion Matrix:")
        print(f"             Predicted Away  |  Predicted Home")
        print(f"Actual Away:  {cm[0,0]:4d}          |  {cm[0,1]:4d}")
        print(f"Actual Home:  {cm[1,0]:4d}          |  {cm[1,1]:4d}")
    
    return accuracy

def main():
    print_header("XGBoost Winner Model - Full Feature Set (48 features)")
    print(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Features: Basic stats + EPA + Advanced metrics + Vegas lines")
    print("Data: 2020-2025 seasons, week 2+")
    
    # Load and prepare data
    df = load_data(schema='hcl')
    X, y, feature_cols, df = prepare_features(df)
    X_train, y_train, X_val, y_val, X_test, y_test = split_data(X, y, df)
    
    # Train model
    model = train_model(X_train, y_train, X_val, y_val)
    
    # Evaluate
    print_header("MODEL EVALUATION")
    train_acc = evaluate_model(model, X_train, y_train, "Training Set (2020-2023)")
    val_acc = evaluate_model(model, X_val, y_val, "Validation Set (2024)")
    test_acc = evaluate_model(model, X_test, y_test, "Test Set (2025)")
    
    # Feature importance
    print_header("TOP 15 FEATURE IMPORTANCE")
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:15]
    
    for i, idx in enumerate(indices, 1):
        print(f"  {feature_cols[idx]:30s}: {importances[idx]:.4f}")
    
    # Save model
    print_header("SAVING MODEL")
    os.makedirs('ml/models', exist_ok=True)
    
    model_path = 'ml/models/xgb_winner.pkl'
    features_path = 'ml/models/xgb_winner_features.txt'
    
    joblib.dump(model, model_path)
    with open(features_path, 'w') as f:
        f.write('\n'.join(feature_cols))
    
    print(f"Model saved: {model_path}")
    print(f"Features saved: {features_path}")
    
    # Summary
    print_header("SUMMARY")
    print(f"XGBoost Winner Model Complete - {len(feature_cols)} features")
    print(f"Test Accuracy: {test_acc:.1%}")
    print(f"Vegas baseline: ~52-55% (home team bias + point spread)")
    print(f"\nModel ready for predictions")

if __name__ == '__main__':
    main()
