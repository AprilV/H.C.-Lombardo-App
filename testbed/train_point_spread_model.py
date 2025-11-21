"""
NFL Point Spread Prediction Model - TESTBED
============================================
Train neural network to predict point differentials (home_score - away_score)

Sprint 11: Point Spread & Score Predictions
Date: November 20, 2025

Training Strategy: Option C - Weighted All Data
- Uses all games 1999-2025 (14,312 games)
- Recent years weighted more heavily (2019-2025 = 2x weight)
- Prevents data leakage (only uses stats from BEFORE each game)

Author: April V. Sykes
Course: IS330 - Database Management
"""

import psycopg2
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime

# Database connection
DB_CONFIG = {
    'dbname': 'nfl_analytics',
    'user': 'postgres',
    'password': 'aprilv120',
    'host': 'localhost',
    'port': '5432'
}

def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_subheader(title):
    """Print formatted subsection"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)

def calculate_sample_weights(years):
    """
    Calculate sample weights based on recency
    Recent games (2019+) get 2x weight
    Middle era (2011-2018) gets 1x weight
    Older games (1999-2010) get 0.5x weight
    """
    weights = np.ones(len(years))
    
    # Older era: 1999-2010 (pre-rule changes)
    weights[years < 2011] = 0.5
    
    # Middle era: 2011-2018 (transition)
    weights[(years >= 2011) & (years < 2019)] = 1.0
    
    # Modern era: 2019-2025 (current NFL)
    weights[years >= 2019] = 2.0
    
    return weights

def fetch_training_data():
    """
    Fetch all games with rolling features
    Target: home_score - away_score (point differential)
    """
    print_header("LOADING TRAINING DATA FROM DATABASE")
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
        WITH team_rolling_stats AS (
            SELECT 
                tgs.game_id,
                tgs.team,
                g.season,
                g.week,
                g.home_team,
                g.away_team,
                g.home_score,
                g.away_score,
                
                -- Rolling season stats (all games BEFORE this one)
                AVG(tgs2.points) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as ppg_season,
                
                AVG(tgs2.total_yards) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as ypg_season,
                
                AVG(tgs2.touchdowns) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as tpg_season,
                
                AVG(tgs2.epa_per_play) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as epa_season,
                
                AVG(tgs2.success_rate) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as success_season,
                
                AVG(tgs2.yards_per_play) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as ypp_season,
                
                AVG(tgs2.third_down_pct) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as third_down_season,
                
                AVG(tgs2.pass_epa) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as pass_epa_season,
                
                AVG(tgs2.rush_epa) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as rush_epa_season,
                
                AVG(tgs2.cpoe) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) as cpoe_season,
                
                -- Last 3 games
                AVG(tgs2.points) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
                ) as ppg_l3,
                
                AVG(tgs2.epa_per_play) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
                ) as epa_l3,
                
                AVG(tgs2.success_rate) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
                ) as success_l3,
                
                -- Last 5 games
                AVG(tgs2.points) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
                ) as ppg_l5,
                
                AVG(tgs2.epa_per_play) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
                ) as epa_l5,
                
                AVG(tgs2.success_rate) OVER (
                    PARTITION BY tgs.team, tgs.season 
                    ORDER BY g2.week 
                    ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
                ) as success_l5,
                
                -- Vegas lines
                g.spread_line,
                g.total_line
                
            FROM hcl.team_game_stats tgs
            JOIN hcl.games g ON tgs.game_id = g.game_id
            JOIN hcl.team_game_stats tgs2 ON tgs2.team = tgs.team AND tgs2.season = tgs.season
            JOIN hcl.games g2 ON tgs2.game_id = g2.game_id
            WHERE g.season >= 1999 
            AND g.is_postseason = FALSE
            AND g.home_score IS NOT NULL  -- Only completed games
            AND g.away_score IS NOT NULL
        )
        
        SELECT 
            home.game_id,
            home.season,
            home.week,
            home.home_team,
            home.away_team,
            home.home_score,
            home.away_score,
            (home.home_score - home.away_score) as point_differential,
            
            -- Home team features
            COALESCE(home.ppg_season, 20) as home_ppg_season,
            COALESCE(home.ypg_season, 320) as home_ypg_season,
            COALESCE(home.tpg_season, 2.5) as home_tpg_season,
            COALESCE(home.epa_season, 0) as home_epa_season,
            COALESCE(home.success_season, 0.40) as home_success_season,
            COALESCE(home.ypp_season, 5.5) as home_ypp_season,
            COALESCE(home.third_down_season, 38) as home_third_down_season,
            COALESCE(home.pass_epa_season, 0) as home_pass_epa_season,
            COALESCE(home.rush_epa_season, 0) as home_rush_epa_season,
            COALESCE(home.cpoe_season, 0) as home_cpoe_season,
            COALESCE(home.ppg_l3, home.ppg_season, 20) as home_ppg_l3,
            COALESCE(home.epa_l3, home.epa_season, 0) as home_epa_l3,
            COALESCE(home.success_l3, home.success_season, 0.40) as home_success_l3,
            COALESCE(home.ppg_l5, home.ppg_season, 20) as home_ppg_l5,
            COALESCE(home.epa_l5, home.epa_season, 0) as home_epa_l5,
            COALESCE(home.success_l5, home.success_season, 0.40) as home_success_l5,
            
            -- Away team features
            COALESCE(away.ppg_season, 20) as away_ppg_season,
            COALESCE(away.ypg_season, 320) as away_ypg_season,
            COALESCE(away.tpg_season, 2.5) as away_tpg_season,
            COALESCE(away.epa_season, 0) as away_epa_season,
            COALESCE(away.success_season, 0.40) as away_success_season,
            COALESCE(away.ypp_season, 5.5) as away_ypp_season,
            COALESCE(away.third_down_season, 38) as away_third_down_season,
            COALESCE(away.pass_epa_season, 0) as away_pass_epa_season,
            COALESCE(away.rush_epa_season, 0) as away_rush_epa_season,
            COALESCE(away.cpoe_season, 0) as away_cpoe_season,
            COALESCE(away.ppg_l3, away.ppg_season, 20) as away_ppg_l3,
            COALESCE(away.epa_l3, away.epa_season, 0) as away_epa_l3,
            COALESCE(away.success_l3, away.success_season, 0.40) as away_success_l3,
            COALESCE(away.ppg_l5, away.ppg_season, 20) as away_ppg_l5,
            COALESCE(away.epa_l5, away.epa_season, 0) as away_epa_l5,
            COALESCE(away.success_l5, away.success_season, 0.40) as away_success_l5,
            
            -- Vegas lines
            COALESCE(home.spread_line, 0) as spread_line,
            COALESCE(home.total_line, 44) as total_line
            
        FROM team_rolling_stats home
        JOIN team_rolling_stats away 
            ON home.game_id = away.game_id 
            AND home.team = home.home_team 
            AND away.team = home.away_team
        WHERE home.ppg_season IS NOT NULL  -- Filter out first games with no history
        ORDER BY home.season, home.week, home.game_id;
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"✅ Loaded {len(df):,} games from database")
    print(f"   Season range: {df['season'].min()} - {df['season'].max()}")
    print(f"   Point differential range: {df['point_differential'].min():.1f} to {df['point_differential'].max():.1f}")
    
    return df

def prepare_features(df):
    """Create feature matrix and target variable"""
    print_subheader("PREPARING FEATURES")
    
    # Feature columns (41 features - same as win/loss model)
    feature_cols = [
        # Home team season stats (10)
        'home_ppg_season', 'home_ypg_season', 'home_tpg_season', 'home_epa_season',
        'home_success_season', 'home_ypp_season', 'home_third_down_season',
        'home_pass_epa_season', 'home_rush_epa_season', 'home_cpoe_season',
        
        # Home team recent form (6)
        'home_ppg_l3', 'home_epa_l3', 'home_success_l3',
        'home_ppg_l5', 'home_epa_l5', 'home_success_l5',
        
        # Away team season stats (10)
        'away_ppg_season', 'away_ypg_season', 'away_tpg_season', 'away_epa_season',
        'away_success_season', 'away_ypp_season', 'away_third_down_season',
        'away_pass_epa_season', 'away_rush_epa_season', 'away_cpoe_season',
        
        # Away team recent form (6)
        'away_ppg_l3', 'away_epa_l3', 'away_success_l3',
        'away_ppg_l5', 'away_epa_l5', 'away_success_l5',
        
        # Vegas lines (2)
        'spread_line', 'total_line'
    ]
    
    # Add matchup differentials (4)
    df['epa_differential'] = df['home_epa_season'] - df['away_epa_season']
    df['ppg_differential'] = df['home_ppg_season'] - df['away_ppg_season']
    df['success_differential'] = df['home_success_season'] - df['away_success_season']
    df['ypp_differential'] = df['home_ypp_season'] - df['away_ypp_season']
    
    feature_cols += ['epa_differential', 'ppg_differential', 'success_differential', 'ypp_differential']
    
    # Add season and week for context (3)
    feature_cols += ['season', 'week']
    
    X = df[feature_cols].copy()
    y = df['point_differential'].copy()
    
    # Replace any remaining NaN/inf
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    
    print(f"✅ Features prepared: {len(feature_cols)} features")
    print(f"   Feature list: {', '.join(feature_cols[:5])}... (+{len(feature_cols)-5} more)")
    
    return X, y, feature_cols

def train_model(X_train, y_train, X_val, y_val, sample_weights):
    """Train neural network with sample weights"""
    print_subheader("TRAINING NEURAL NETWORK")
    
    print("Architecture:")
    print("  Input:    43 features")
    print("  Hidden 1: 128 neurons (ReLU)")
    print("  Hidden 2: 64 neurons (ReLU)")
    print("  Hidden 3: 32 neurons (ReLU)")
    print("  Output:   1 neuron (Linear) - Point Differential")
    print("\nTraining...")
    
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),
        activation='relu',
        solver='adam',
        alpha=0.001,  # L2 regularization
        batch_size=32,
        learning_rate='adaptive',
        learning_rate_init=0.001,
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
        verbose=True,
        random_state=42
    )
    
    model.fit(X_train, y_train, sample_weight=sample_weights)
    
    print("\n✅ Training complete!")
    print(f"   Iterations: {model.n_iter_}")
    print(f"   Final loss: {model.loss_:.4f}")
    
    return model

def evaluate_model(model, scaler, X, y, dataset_name, df_subset=None):
    """Evaluate model performance"""
    print_subheader(f"{dataset_name.upper()} PERFORMANCE")
    
    X_scaled = scaler.transform(X)
    predictions = model.predict(X_scaled)
    
    # Metrics
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    r2 = r2_score(y, predictions)
    
    # Correct winner prediction
    correct_winner = np.sum((predictions > 0) == (y > 0))
    total = len(y)
    winner_accuracy = (correct_winner / total) * 100
    
    print(f"Games: {total:,}")
    print(f"Mean Absolute Error (MAE): {mae:.2f} points")
    print(f"Root Mean Squared Error (RMSE): {rmse:.2f} points")
    print(f"R² Score: {r2:.4f}")
    print(f"Correct Winner: {correct_winner}/{total} ({winner_accuracy:.1f}%)")
    
    # Show sample predictions if we have the dataframe
    if df_subset is not None and len(df_subset) > 0:
        print(f"\n📊 Sample Predictions from {dataset_name}:")
        print("-" * 80)
        
        # Get random sample
        sample_indices = np.random.choice(len(df_subset), min(5, len(df_subset)), replace=False)
        
        for idx in sample_indices:
            game_idx = df_subset.index[idx]
            game = df_subset.loc[game_idx]
            pred = predictions[idx]
            actual = y.iloc[idx]
            error = abs(pred - actual)
            
            winner_pred = game['home_team'] if pred > 0 else game['away_team']
            winner_actual = game['home_team'] if actual > 0 else game['away_team']
            correct = "✅" if winner_pred == winner_actual else "❌"
            
            print(f"Week {int(game['week'])}: {game['away_team']} @ {game['home_team']}")
            print(f"  Predicted: {pred:+.1f} | Actual: {actual:+.1f} | Error: {error:.1f} points {correct}")
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'winner_accuracy': winner_accuracy
    }

def main():
    print_header("NFL POINT SPREAD PREDICTION MODEL TRAINING")
    print("Sprint 11: Score & Spread Predictions")
    print("Training Strategy: Weighted All Data (Option C)")
    print("Author: April V. Sykes | Course: IS330")
    
    # Load data
    df = fetch_training_data()
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    
    # Time-based split
    print_subheader("SPLITTING DATA (TIME-BASED)")
    
    train_mask = df['season'] <= 2023
    val_mask = df['season'] == 2024
    test_mask = df['season'] == 2025
    
    X_train = X[train_mask]
    y_train = y[train_mask]
    df_train = df[train_mask]
    
    X_val = X[val_mask]
    y_val = y[val_mask]
    df_val = df[val_mask]
    
    X_test = X[test_mask]
    y_test = y[test_mask]
    df_test = df[test_mask]
    
    print(f"Training Set (1999-2023): {len(X_train):,} games")
    print(f"Validation Set (2024):    {len(X_val):,} games")
    print(f"Test Set (2025):          {len(X_test):,} games")
    
    # Calculate sample weights
    print_subheader("CALCULATING SAMPLE WEIGHTS (RECENCY EMPHASIS)")
    
    weights = calculate_sample_weights(df_train['season'].values)
    
    print(f"Weight distribution:")
    print(f"  1999-2010 (older):  {np.sum(df_train['season'] < 2011):,} games × 0.5 weight")
    print(f"  2011-2018 (middle): {np.sum((df_train['season'] >= 2011) & (df_train['season'] < 2019)):,} games × 1.0 weight")
    print(f"  2019-2023 (modern): {np.sum(df_train['season'] >= 2019):,} games × 2.0 weight")
    print(f"  Effective training size: {np.sum(weights):,.0f} weighted samples")
    
    # Scale features
    print_subheader("SCALING FEATURES")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    print("✅ Features normalized (mean=0, std=1)")
    
    # Train model
    model = train_model(X_train_scaled, y_train, X_val, y_val, weights)
    
    # Evaluate on all sets
    print("\n" + "=" * 80)
    print("  MODEL EVALUATION")
    print("=" * 80)
    
    train_metrics = evaluate_model(model, scaler, X_train, y_train, "Training Set", df_train)
    val_metrics = evaluate_model(model, scaler, X_val, y_val, "Validation Set (2024)", df_val)
    test_metrics = evaluate_model(model, scaler, X_test, y_test, "Test Set (2025)", df_test)
    
    # Summary
    print_header("FINAL SUMMARY")
    
    print("✅ MODEL VALIDATION COMPLETE")
    print(f"\nValidation MAE: {val_metrics['mae']:.2f} points")
    print(f"Test MAE: {test_metrics['mae']:.2f} points")
    print(f"Winner Accuracy: {test_metrics['winner_accuracy']:.1f}%")
    
    print("\n📊 Comparison to Vegas Spreads:")
    print(f"   Vegas typical MAE: ~10.5 points")
    print(f"   Our model MAE: {val_metrics['mae']:.2f} points")
    
    if val_metrics['mae'] < 10.5:
        print(f"   ✅ We beat Vegas by {10.5 - val_metrics['mae']:.2f} points!")
    else:
        print(f"   ⚠️  Vegas is {val_metrics['mae'] - 10.5:.2f} points better")
    
    # Check for data leakage
    print("\n🔍 Data Leakage Check:")
    if val_metrics['mae'] < 6:
        print(f"   ⚠️  WARNING: MAE too low ({val_metrics['mae']:.2f}) - possible leakage!")
    elif val_metrics['mae'] > 15:
        print(f"   ⚠️  WARNING: MAE too high ({val_metrics['mae']:.2f}) - model not learning")
    else:
        print(f"   ✅ MAE looks reasonable ({val_metrics['mae']:.2f}) - no obvious leakage")
    
    # Save model
    print_subheader("SAVING MODEL TO TESTBED")
    
    output_dir = 'testbed/models'
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = f'{output_dir}/point_spread_model.pkl'
    scaler_path = f'{output_dir}/point_spread_scaler.pkl'
    features_path = f'{output_dir}/point_spread_features.txt'
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    with open(features_path, 'w') as f:
        for feature in feature_names:
            f.write(f"{feature}\n")
    
    print(f"✅ Model saved: {model_path}")
    print(f"✅ Scaler saved: {scaler_path}")
    print(f"✅ Features saved: {features_path}")
    
    print_header("TRAINING COMPLETE - READY FOR PREDICTIONS!")
    
    print("Next steps:")
    print("1. Review validation metrics above")
    print("2. If MAE looks good (~9-11 points), proceed to UI updates")
    print("3. Update predict_week.py to use this model")
    print("4. Update API to return predicted scores")
    print("5. Update frontend cards to show comparisons")

if __name__ == "__main__":
    main()
