"""
XGBoost Point Spread Prediction Model Training
Trains XGBRegressor to predict NFL game point differentials
Using 2020-2025 season data only (modern NFL)
"""

import sys
import os

# Add parent directory to path for db_config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Import database configuration
from db_config import DATABASE_CONFIG

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def load_data(schema='hcl'):
    """Load game data from database"""
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
                tgs.game_id,
                tgs.team,
                g.season,
                g.week,
                g.game_date,
                tgs.points,
                tgs.total_yards,
                tgs.passing_yards,
                tgs.rushing_yards,
                tgs.yards_per_play,
                tgs.turnovers,
                tgs.third_down_pct,
                tgs.red_zone_pct
            FROM {schema}.team_game_stats tgs
            JOIN {schema}.games g ON tgs.game_id = g.game_id
            WHERE g.season >= 2020
              AND g.is_postseason = FALSE
        ),
        cumulative_stats AS (
            SELECT 
                game_id,
                team,
                season,
                week,
                -- Calculate averages from PRIOR games only (exclude current game)
                AVG(points) OVER (
                    PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as avg_ppg,
                AVG(total_yards) OVER (
                    PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as avg_yards,
                AVG(passing_yards) OVER (
                    PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as avg_pass_yards,
                AVG(rushing_yards) OVER (
                    PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as avg_rush_yards,
                AVG(yards_per_play) OVER (
                    PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as avg_yards_per_play,
                AVG(turnovers) OVER (
                    PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as avg_turnovers,
                AVG(third_down_pct) OVER (
                    PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as avg_third_down_pct,
                AVG(red_zone_pct) OVER (
                    PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as avg_red_zone_pct
            FROM game_stats
        )
        SELECT 
            g.game_id,
            g.season,
            g.week,
            g.home_team,
            g.away_team,
            g.home_score,
            g.away_score,
            (g.home_score - g.away_score) as point_differential,
            
            -- Home team cumulative stats (NULL for week 1)
            COALESCE(h.avg_ppg, 20) as home_ppg,
            COALESCE(h.avg_yards, 320) as home_yards_pg,
            COALESCE(h.avg_pass_yards, 220) as home_pass_yards_pg,
            COALESCE(h.avg_rush_yards, 100) as home_rush_yards_pg,
            COALESCE(h.avg_yards_per_play, 5) as home_yards_per_play,
            COALESCE(h.avg_turnovers, 1) as home_turnovers,
            COALESCE(h.avg_third_down_pct, 40) as home_third_down_pct,
            COALESCE(h.avg_red_zone_pct, 50) as home_red_zone_pct,
            
            -- Away team cumulative stats (NULL for week 1)
            COALESCE(a.avg_ppg, 20) as away_ppg,
            COALESCE(a.avg_yards, 320) as away_yards_pg,
            COALESCE(a.avg_pass_yards, 220) as away_pass_yards_pg,
            COALESCE(a.avg_rush_yards, 100) as away_rush_yards_pg,
            COALESCE(a.avg_yards_per_play, 5) as away_yards_per_play,
            COALESCE(a.avg_turnovers, 1) as away_turnovers,
            COALESCE(a.avg_third_down_pct, 40) as away_third_down_pct,
            COALESCE(a.avg_red_zone_pct, 50) as away_red_zone_pct,
            
            -- Vegas lines
            COALESCE(g.spread_line, 0) as spread_line,
            COALESCE(g.total_line, 44) as total_line
            
        FROM {schema}.games g
        LEFT JOIN cumulative_stats h ON g.game_id = h.game_id AND g.home_team = h.team
        LEFT JOIN cumulative_stats a ON g.game_id = a.game_id AND g.away_team = a.team
        WHERE g.season >= 2020
          AND g.is_postseason = FALSE
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          AND g.week >= 2  -- Skip week 1 (no prior data)
        ORDER BY g.season, g.week, g.game_id
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"✓ Loaded {len(df):,} games from {df['season'].min()}-{df['season'].max()}")
    return df

def prepare_features(df):
    """Prepare features and target variable"""
    print("\nPreparing features...")
    
    # Feature columns (all stats plus Vegas lines)
    feature_cols = [
        'home_ppg', 'home_yards_pg', 'home_pass_yards_pg', 'home_rush_yards_pg',
        'home_yards_per_play', 'home_turnovers',
        'home_third_down_pct', 'home_red_zone_pct',
        'away_ppg', 'away_yards_pg', 'away_pass_yards_pg', 'away_rush_yards_pg',
        'away_yards_per_play', 'away_turnovers',
        'away_third_down_pct', 'away_red_zone_pct',
        'spread_line', 'total_line'
    ]
    
    X = df[feature_cols].values
    y = df['point_differential'].values  # Home score - Away score
    
    print(f"✓ Features: {len(feature_cols)} columns")
    print(f"✓ Target range: {y.min():.0f} to {y.max():.0f} points")
    print(f"✓ Mean differential: {y.mean():.2f} points (home field advantage)")
    
    return X, y, feature_cols

def split_data(df, X, y):
    """Split data by season: ≤2023 train, 2024 validation, 2025 test"""
    print("\nSplitting data by season...")
    
    train_mask = df['season'] <= 2023
    val_mask = df['season'] == 2024
    test_mask = df['season'] == 2025
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_val, y_val = X[val_mask], y[val_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    
    df_train = df[train_mask]
    df_val = df[val_mask]
    df_test = df[test_mask]
    
    print(f"  Training (≤2023):   {len(X_train):,} games")
    print(f"  Validation (2024):  {len(X_val):,} games")
    print(f"  Test (2025):        {len(X_test):,} games")
    
    return X_train, y_train, X_val, y_val, X_test, y_test, df_train, df_val, df_test

def train_model(X_train, y_train, X_val, y_val):
    """Train XGBoost regressor"""
    print_header("TRAINING XGBOOST REGRESSOR")
    
    model = xgb.XGBRegressor(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='mae'
    )
    
    print("Training model...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    print("✓ Training complete")
    return model

def evaluate_model(model, X, y, name, df):
    """Evaluate model performance"""
    print(f"\n{name}:")
    print("-" * 40)
    
    y_pred = model.predict(X)
    
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    
    print(f"MAE:  {mae:.2f} points")
    print(f"RMSE: {rmse:.2f} points")
    print(f"R²:   {r2:.4f}")
    
    # Winner accuracy (correct side of spread)
    actual_winners = (y > 0).astype(int)
    pred_winners = (y_pred > 0).astype(int)
    winner_acc = np.mean(actual_winners == pred_winners)
    print(f"Winner Accuracy: {100*winner_acc:.1f}%")
    
    # Show some example predictions
    print(f"\nSample Predictions:")
    for i in range(min(5, len(df))):
        row = df.iloc[i]
        actual = y[i]
        predicted = y_pred[i]
        print(f"  {row['away_team']} @ {row['home_team']}: Predicted {predicted:+.1f}, Actual {actual:+.1f}")
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2, 'winner_accuracy': winner_acc}

def main():
    print_header("XGBoost Spread Prediction Model Training")
    print(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target: Predict NFL game point differentials (spread)")
    print("Data: 2020-2025 seasons from hcl_test schema")
    
    # Load data
    df = load_data(schema='hcl_test')
    
    # Prepare features
    X, y, feature_cols = prepare_features(df)
    
    # Split data
    X_train, y_train, X_val, y_val, X_test, y_test, df_train, df_val, df_test = split_data(df, X, y)
    
    # Train model
    model = train_model(X_train, y_train, X_val, y_val)
    
    # Evaluate
    print_header("MODEL EVALUATION")
    train_metrics = evaluate_model(model, X_train, y_train, "Training Set (2020-2023)", df_train)
    val_metrics = evaluate_model(model, X_val, y_val, "Validation Set (2024)", df_val)
    test_metrics = evaluate_model(model, X_test, y_test, "Test Set (2025)", df_test)
    
    # Feature importance
    print_header("TOP 10 FEATURE IMPORTANCE")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']:30s}: {row['importance']:.4f}")
    
    # Save model
    print_header("SAVING MODEL")
    output_dir = 'ml/models'
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = f'{output_dir}/xgb_spread.pkl'
    features_path = f'{output_dir}/xgb_spread_features.txt'
    
    joblib.dump(model, model_path)
    with open(features_path, 'w') as f:
        for feature in feature_cols:
            f.write(f"{feature}\n")
    
    print(f"✓ Model saved: {model_path}")
    print(f"✓ Features saved: {features_path}")
    
    # Summary
    print_header("FINAL SUMMARY")
    print(f"✓ XGBoost Spread Model Complete")
    print(f"\nTest MAE: {test_metrics['mae']:.2f} points")
    print(f"Vegas typical MAE: ~10.5 points")
    
    if test_metrics['mae'] < 10.5:
        print(f"✓ We beat Vegas by {10.5 - test_metrics['mae']:.2f} points!")
    else:
        print(f"  Vegas is {test_metrics['mae'] - 10.5:.2f} points better")
    
    print(f"\nWinner Accuracy: {100*test_metrics['winner_accuracy']:.1f}%")
    print("\nModel ready for predictions.")

if __name__ == "__main__":
    main()
