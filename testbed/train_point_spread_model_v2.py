"""
NFL Point Spread Prediction Model - FIXED VERSION

Train neural network to predict point differentials (home_score - away_score)
Uses same data loading approach as nfl_neural_network_v2.py (Python loops, not SQL)

Sprint 11: Score & Spread Predictions
Author: April V. Sykes | Course: IS330
Date: November 20, 2025
"""

import psycopg2
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'dbname': 'nfl_analytics',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD'),
    'host': 'localhost'
}

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_subheader(text):
    print("\n" + "-"*80)
    print(f"  {text}")
    print("-"*80)

def calculate_sample_weights(years):
    """
    Calculate sample weights based on recency
    Recent games (2019+) get 2x weight
    Middle era (2011-2018) gets 1x weight
    Older games (1999-2010) get 0.5x weight
    """
    weights = np.ones(len(years))
    weights[years < 2011] = 0.5
    weights[(years >= 2011) & (years < 2019)] = 1.0
    weights[years >= 2019] = 2.0
    return weights

def fetch_training_data():
    """Fetch game-level data and team stats (same as original model)"""
    print_header("LOADING TRAINING DATA FROM DATABASE")
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Fetch games
    games_query = """
        SELECT 
            g.game_id,
            g.season,
            g.week,
            g.home_team,
            g.away_team,
            g.home_score,
            g.away_score,
            g.spread_line,
            g.total_line,
            g.home_moneyline,
            g.away_moneyline
        FROM hcl.games g
        WHERE g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
        ORDER BY g.season, g.week, g.game_id
    """
    
    games_df = pd.read_sql(games_query, conn)
    
    # Fetch team stats
    stats_query = """
        SELECT 
            game_id,
            team,
            season,
            week,
            points,
            total_yards,
            turnovers,
            epa_per_play,
            success_rate,
            pass_epa,
            rush_epa,
            wpa,
            yards_per_play,
            third_down_pct,
            red_zone_pct,
            time_of_possession_pct
        FROM hcl.team_game_stats
        ORDER BY season, week, game_id
    """
    
    stats_df = pd.read_sql(stats_query, conn)
    conn.close()
    
    print(f"✅ Loaded {len(games_df):,} games")
    print(f"✅ Loaded {len(stats_df):,} team-game stats records")
    print(f"   Season range: {games_df['season'].min()} - {games_df['season'].max()}")
    
    return games_df, stats_df

def compute_rolling_features(games_df, stats_df):
    """
    Compute features from PREVIOUS games only (same as original model)
    Target: point_differential = home_score - away_score
    """
    print_header("COMPUTING ROLLING FEATURES (Pre-game information only)")
    
    features_list = []
    labels_list = []
    
    stats_df = stats_df.sort_values(['season', 'week', 'game_id'])
    
    total_games = len(games_df)
    processed = 0
    skipped = 0
    
    for idx, game in games_df.iterrows():
        if idx % 1000 == 0:
            print(f"   Processing game {idx:,}/{total_games:,}...")
        
        season = game['season']
        week = game['week']
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Get home team's stats from PREVIOUS games
        home_prev_stats = stats_df[
            (stats_df['team'] == home_team) &
            (stats_df['season'] == season) &
            (stats_df['week'] < week)
        ]
        
        # Get away team's stats from PREVIOUS games
        away_prev_stats = stats_df[
            (stats_df['team'] == away_team) &
            (stats_df['season'] == season) &
            (stats_df['week'] < week)
        ]
        
        # Skip games where teams have no previous games this season
        if len(home_prev_stats) == 0 or len(away_prev_stats) == 0:
            skipped += 1
            continue
        
        # Calculate season-to-date averages for home team
        home_ppg = home_prev_stats['points'].mean()
        home_ypg = home_prev_stats['total_yards'].mean()
        home_tpg = home_prev_stats['turnovers'].mean()
        home_epa = home_prev_stats['epa_per_play'].mean()
        home_success = home_prev_stats['success_rate'].mean()
        home_pass_epa = home_prev_stats['pass_epa'].mean()
        home_rush_epa = home_prev_stats['rush_epa'].mean()
        home_wpa = home_prev_stats['wpa'].mean()
        home_ypp = home_prev_stats['yards_per_play'].mean()
        home_3rd_pct = home_prev_stats['third_down_pct'].mean()
        home_rz_pct = home_prev_stats['red_zone_pct'].mean()
        home_top_pct = home_prev_stats['time_of_possession_pct'].mean()
        
        # Recent form (last 5 games)
        home_recent = home_prev_stats.tail(5)
        home_epa_l5 = home_recent['epa_per_play'].mean() if len(home_recent) > 0 else home_epa
        home_ppg_l5 = home_recent['points'].mean() if len(home_recent) > 0 else home_ppg
        
        # Recent form (last 3 games)
        home_recent3 = home_prev_stats.tail(3)
        home_epa_l3 = home_recent3['epa_per_play'].mean() if len(home_recent3) > 0 else home_epa
        
        # Calculate season-to-date averages for away team
        away_ppg = away_prev_stats['points'].mean()
        away_ypg = away_prev_stats['total_yards'].mean()
        away_tpg = away_prev_stats['turnovers'].mean()
        away_epa = away_prev_stats['epa_per_play'].mean()
        away_success = away_prev_stats['success_rate'].mean()
        away_pass_epa = away_prev_stats['pass_epa'].mean()
        away_rush_epa = away_prev_stats['rush_epa'].mean()
        away_wpa = away_prev_stats['wpa'].mean()
        away_ypp = away_prev_stats['yards_per_play'].mean()
        away_3rd_pct = away_prev_stats['third_down_pct'].mean()
        away_rz_pct = away_prev_stats['red_zone_pct'].mean()
        away_top_pct = away_prev_stats['time_of_possession_pct'].mean()
        
        # Recent form
        away_recent = away_prev_stats.tail(5)
        away_epa_l5 = away_recent['epa_per_play'].mean() if len(away_recent) > 0 else away_epa
        away_ppg_l5 = away_recent['points'].mean() if len(away_recent) > 0 else away_ppg
        
        away_recent3 = away_prev_stats.tail(3)
        away_epa_l3 = away_recent3['epa_per_play'].mean() if len(away_recent3) > 0 else away_epa
        
        # Matchup differentials
        epa_diff = home_epa - away_epa
        ppg_diff = home_ppg - away_ppg
        success_diff = home_success - away_success
        
        # Build feature vector (same as original model)
        features = {
            # Home team stats
            'home_ppg_season': home_ppg,
            'home_ypg_season': home_ypg,
            'home_tpg_season': home_tpg,
            'home_epa_season': home_epa,
            'home_success_season': home_success,
            'home_pass_epa_season': home_pass_epa,
            'home_rush_epa_season': home_rush_epa,
            'home_wpa_season': home_wpa,
            'home_ypp_season': home_ypp,
            'home_3rd_pct_season': home_3rd_pct,
            'home_rz_pct_season': home_rz_pct,
            'home_top_pct_season': home_top_pct,
            'home_epa_l5': home_epa_l5,
            'home_ppg_l5': home_ppg_l5,
            'home_epa_l3': home_epa_l3,
            'home_games_played': len(home_prev_stats),
            
            # Away team stats
            'away_ppg_season': away_ppg,
            'away_ypg_season': away_ypg,
            'away_tpg_season': away_tpg,
            'away_epa_season': away_epa,
            'away_success_season': away_success,
            'away_pass_epa_season': away_pass_epa,
            'away_rush_epa_season': away_rush_epa,
            'away_wpa_season': away_wpa,
            'away_ypp_season': away_ypp,
            'away_3rd_pct_season': away_3rd_pct,
            'away_rz_pct_season': away_rz_pct,
            'away_top_pct_season': away_top_pct,
            'away_epa_l5': away_epa_l5,
            'away_ppg_l5': away_ppg_l5,
            'away_epa_l3': away_epa_l3,
            'away_games_played': len(away_prev_stats),
            
            # Matchup differentials
            'epa_differential': epa_diff,
            'ppg_differential': ppg_diff,
            'success_differential': success_diff,
            
            # Betting lines (available pre-game)
            'spread_line': game['spread_line'] if pd.notna(game['spread_line']) else 0.0,
            'total_line': game['total_line'] if pd.notna(game['total_line']) else 47.0,
            'home_moneyline': game['home_moneyline'] if pd.notna(game['home_moneyline']) else -110,
            'away_moneyline': game['away_moneyline'] if pd.notna(game['away_moneyline']) else -110,
            
            # Context
            'season': season,
            'week': week,
        }
        
        features_list.append(features)
        
        # Label: Point differential (home_score - away_score)
        point_diff = game['home_score'] - game['away_score']
        labels_list.append(point_diff)
        
        processed += 1
    
    print(f"✅ Processed {processed:,} games (skipped {skipped:,} games with no previous data)")
    
    # Convert to DataFrames
    X = pd.DataFrame(features_list)
    y = np.array(labels_list)
    
    # Handle NaN values (fill with median)
    nan_count = X.isnull().sum().sum()
    if nan_count > 0:
        print(f"⚠️  Found {nan_count} NaN values, filling with median...")
        X = X.fillna(X.median())
    
    # Replace any remaining inf values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    
    print(f"✅ Feature matrix shape: {X.shape}")
    print(f"   Total features: {X.shape[1]}")
    print(f"   Point differential range: {y.min():.1f} to {y.max():.1f}")
    
    return X, y

def split_data(X, y):
    """Split by season (same as original model)"""
    print_subheader("SPLITTING DATA (TIME-BASED)")
    
    seasons = X['season'].values
    
    train_mask = seasons <= 2023
    val_mask = seasons == 2024
    test_mask = seasons == 2025
    
    X_train = X[train_mask]
    y_train = y[train_mask]
    
    X_val = X[val_mask]
    y_val = y[val_mask]
    
    X_test = X[test_mask]
    y_test = y[test_mask]
    
    print(f"Training Set (1999-2023): {len(X_train):,} games")
    print(f"Validation Set (2024):    {len(X_val):,} games")
    print(f"Test Set (2025):          {len(X_test):,} games")
    
    return X_train, X_val, X_test, y_train, y_val, y_test

def prepare_features(X_train, X_val, X_test):
    """Prepare features for training"""
    print_subheader("CALCULATING SAMPLE WEIGHTS (RECENCY EMPHASIS)")
    
    # Remove non-feature columns
    feature_cols = [col for col in X_train.columns if col not in ['season', 'week']]
    
    X_train_features = X_train[feature_cols]
    X_val_features = X_val[feature_cols]
    X_test_features = X_test[feature_cols]
    
    # Calculate sample weights
    train_years = X_train['season'].values
    weights = calculate_sample_weights(train_years)
    
    print("Weight distribution:")
    print(f"  1999-2010 (older):  {np.sum(train_years < 2011):,} games × 0.5 weight")
    print(f"  2011-2018 (middle): {np.sum((train_years >= 2011) & (train_years < 2019)):,} games × 1.0 weight")
    print(f"  2019-2023 (modern): {np.sum(train_years >= 2019):,} games × 2.0 weight")
    print(f"  Effective training size: {int(np.sum(weights)):,} weighted samples")
    
    return X_train_features, X_val_features, X_test_features, weights, feature_cols

def train_model(X_train, y_train, weights):
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
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
        verbose=True,
        random_state=42
    )
    
    model.fit(X_train, y_train, sample_weight=weights)
    
    print(f"\n✅ Training complete!")
    print(f"   Iterations: {model.n_iter_}")
    print(f"   Final loss: {model.loss_:.4f}")
    
    return model

def evaluate_model(model, X, y, set_name):
    """Evaluate model performance"""
    print_subheader(f"{set_name.upper()} SET PERFORMANCE")
    
    predictions = model.predict(X)
    
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    r2 = r2_score(y, predictions)
    
    # Winner prediction accuracy (positive = home wins)
    correct_winner = np.sum((predictions > 0) == (y > 0))
    total = len(y)
    winner_acc = correct_winner / total
    
    print(f"Games: {total:,}")
    print(f"Mean Absolute Error (MAE): {mae:.2f} points")
    print(f"Root Mean Squared Error (RMSE): {rmse:.2f} points")
    print(f"R² Score: {r2:.4f}")
    print(f"Correct Winner: {correct_winner}/{total} ({winner_acc*100:.1f}%)")
    
    # Show sample predictions
    print(f"\n📊 Sample Predictions from {set_name} Set:")
    print("-"*80)
    sample_indices = np.random.choice(len(y), min(5, len(y)), replace=False)
    for idx in sample_indices:
        pred = predictions[idx]
        actual = y[idx]
        error = abs(pred - actual)
        check = "✅" if error <= 10 else "❌"
        print(f"  Predicted: {pred:+.1f} | Actual: {actual:+.1f} | Error: {error:.1f} points {check}")
    
    return mae, rmse, r2, winner_acc

def main():
    print_header("NFL POINT SPREAD PREDICTION MODEL TRAINING (FIXED)")
    print("\nSprint 11: Score & Spread Predictions")
    print("Training Strategy: Weighted All Data (Option C)")
    print("Using proven Python loop approach from nfl_neural_network_v2.py")
    print("Author: April V. Sykes | Course: IS330\n")
    
    # Load data
    games_df, stats_df = fetch_training_data()
    
    # Compute rolling features
    X, y = compute_rolling_features(games_df, stats_df)
    
    # Split by season
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)
    
    # Prepare features and weights
    X_train_features, X_val_features, X_test_features, weights, feature_cols = prepare_features(
        X_train, X_val, X_test
    )
    
    # Scale features
    print_subheader("SCALING FEATURES")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_features)
    X_val_scaled = scaler.transform(X_val_features)
    X_test_scaled = scaler.transform(X_test_features)
    print("✅ Features scaled")
    
    # Train model
    model = train_model(X_train_scaled, y_train, weights)
    
    # Evaluate
    print_header("MODEL EVALUATION")
    
    train_mae, _, _, _ = evaluate_model(model, X_train_scaled, y_train, "Training")
    val_mae, val_rmse, val_r2, val_acc = evaluate_model(model, X_val_scaled, y_val, "Validation (2024)")
    test_mae, test_rmse, test_r2, test_acc = evaluate_model(model, X_test_scaled, y_test, "Test (2025)")
    
    # Final summary
    print_header("FINAL SUMMARY")
    print("\n✅ MODEL VALIDATION COMPLETE\n")
    print(f"Validation MAE: {val_mae:.2f} points")
    print(f"Test MAE: {test_mae:.2f} points")
    print(f"Winner Accuracy: {test_acc*100:.1f}%")
    print(f"\n📊 Comparison to Vegas Spreads:")
    print(f"   Vegas typical MAE: ~10.5 points")
    print(f"   Our model MAE: {val_mae:.2f} points")
    if val_mae <= 11:
        print(f"   ✅ Within competitive range!")
    else:
        print(f"   ⚠️  Vegas is {val_mae - 10.5:.2f} points better")
    
    print(f"\n🔍 Data Leakage Check:")
    if val_mae < 6:
        print(f"   ⚠️  MAE too low ({val_mae:.2f}) - possible data leakage!")
    elif val_mae > 15:
        print(f"   ⚠️  MAE too high ({val_mae:.2f}) - model not learning well")
    else:
        print(f"   ✅ MAE looks reasonable ({val_mae:.2f}) - no obvious leakage")
    
    # Save model
    print_subheader("SAVING MODEL TO TESTBED")
    
    os.makedirs('testbed/models', exist_ok=True)
    
    joblib.dump(model, 'testbed/models/point_spread_model.pkl')
    joblib.dump(scaler, 'testbed/models/point_spread_scaler.pkl')
    
    with open('testbed/models/point_spread_features.txt', 'w') as f:
        for col in feature_cols:
            f.write(f"{col}\n")
    
    print("✅ Model saved: testbed/models/point_spread_model.pkl")
    print("✅ Scaler saved: testbed/models/point_spread_scaler.pkl")
    print("✅ Features saved: testbed/models/point_spread_features.txt")
    
    print_header("TRAINING COMPLETE - READY FOR PREDICTIONS!")
    
    print("\nNext steps:")
    print("1. ✅ Point spread model trained and validated")
    print("2. Update predict_week.py to load BOTH models (win/loss + spread)")
    print("3. Update API to return: win_prob, predicted_scores, point_diff, ai_spread")
    print("4. Update frontend to show AI predictions vs Vegas lines")
    print("5. Test in browser and validate predictions")

if __name__ == '__main__':
    main()
