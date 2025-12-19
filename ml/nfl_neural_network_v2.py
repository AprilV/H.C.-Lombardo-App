"""
NFL Neural Network - Version 2 (Data Leakage Fixed)

This version computes ROLLING FEATURES from previous games only.
No post-game statistics are used as inputs!

Sprint 9: Machine Learning Predictions
Date: November 6, 2025
"""

import psycopg2
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
from dotenv import load_dotenv
from datetime import datetime
from db_config import DATABASE_CONFIG

load_dotenv()

class NFLNeuralNetworkV2:
    """
    Neural network for NFL game prediction using ONLY pre-game information
    
    Key difference from V1: Uses rolling/cumulative stats from PREVIOUS games,
    not stats from the current game being predicted!
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
        # Database connection - use environment variables
        self.db_config = DATABASE_CONFIG
    
    def fetch_training_data(self):
        """Fetch game-level data (not team_game_stats!)"""
        print("\n" + "="*80)
        print("FETCHING GAME DATA FROM DATABASE")
        print("="*80)
        
        conn = psycopg2.connect(**self.db_config)
        
        # Fetch games with betting lines (2020-2025 only)
        query = """
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
          AND g.season >= 2020
        ORDER BY g.season, g.week, g.game_id
        """
        
        games_df = pd.read_sql(query, conn)
        
        # Also fetch all team_game_stats for computing rolling features (2020-2025)
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
        WHERE season >= 2020
        ORDER BY season, week, game_id
        """
        
        stats_df = pd.read_sql(stats_query, conn)
        conn.close()
        
        print(f"✅ Loaded {len(games_df):,} games")
        print(f"✅ Loaded {len(stats_df):,} team-game stats records")
        print(f"   Seasons: {games_df['season'].min()}-{games_df['season'].max()}")
        
        return games_df, stats_df
    
    def compute_rolling_features(self, games_df, stats_df):
        """
        Compute features from PREVIOUS games only!
        
        For each game, calculate:
        - Home team's stats entering the game
        - Away team's stats entering the game
        - Matchup factors
        - Context
        """
        print("\n" + "="*80)
        print("COMPUTING ROLLING FEATURES (Pre-game information only)")
        print("="*80)
        
        features_list = []
        labels_list = []
        
        # Sort stats by season and week
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
            
            # Build feature vector
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
            
            # Label: Did home team win?
            home_won = 1 if game['home_score'] > game['away_score'] else 0
            labels_list.append(home_won)
            
            processed += 1
        
        print(f"✅ Processed {processed:,} games (skipped {skipped:,} games with no previous data)")
        
        # Convert to DataFrames
        X = pd.DataFrame(features_list)
        y = np.array(labels_list)
        
        print(f"✅ Feature matrix shape: {X.shape}")
        print(f"   Total features: {X.shape[1]}")
        print(f"   Sample features: {list(X.columns[:5])}")
        
        return X, y
    
    def split_data(self, X, y):
        """Split by season"""
        print("\n" + "="*80)
        print("SPLITTING DATA BY SEASON")
        print("="*80)
        
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
        
        print(f"✅ Data split:")
        print(f"   Train: {len(X_train):,} games (≤2023)")
        print(f"   Validation: {len(X_val):,} games (2024)")
        print(f"   Test: {len(X_test):,} games (2025)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train(self, X_train, y_train):
        """Train neural network"""
        print("\n" + "="*80)
        print("TRAINING NEURAL NETWORK V2")
        print("="*80)
        
        # Remove season and week from training (use for splitting only)
        feature_cols = [col for col in X_train.columns if col not in ['season', 'week']]
        X_train_features = X_train[feature_cols]
        
        # Handle NaN values - replace with 0 (represents no previous games or missing stats)
        print(f"   Checking for NaN values...")
        nan_counts = X_train_features.isna().sum()
        total_nans = nan_counts.sum()
        if total_nans > 0:
            print(f"   Found {total_nans} NaN values across {(nan_counts > 0).sum()} columns")
            print(f"   Top columns with NaN: {nan_counts[nan_counts > 0].head(5).to_dict()}")
            print(f"   Filling NaN with 0...")
            X_train_features = X_train_features.fillna(0)
        
        # Also handle inf values
        print(f"   Checking for inf values...")
        X_train_features = X_train_features.replace([np.inf, -np.inf], 0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train_features)
        self.feature_names = feature_cols
        
        # Build model
        self.model = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.0001,
            batch_size=32,
            learning_rate='adaptive',
            learning_rate_init=0.001,
            max_iter=200,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=20,
            random_state=42,
            verbose=True
        )
        
        print("🎓 Training...")
        start_time = datetime.now()
        self.model.fit(X_scaled, y_train)
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Training complete in {duration:.1f} seconds")
        print(f"   Final loss: {self.model.loss_:.6f}")
        
        return self.model
    
    def evaluate(self, X_test, y_test, dataset_name="Test"):
        """Evaluate model"""
        print("\n" + "="*80)
        print(f"EVALUATING ON {dataset_name.upper()} SET")
        print("="*80)
        
        feature_cols = [col for col in X_test.columns if col not in ['season', 'week']]
        X_test_features = X_test[feature_cols]
        
        # Handle NaN and inf
        X_test_features = X_test_features.fillna(0).replace([np.inf, -np.inf], 0)
        
        X_scaled = self.scaler.transform(X_test_features)
        
        y_pred = self.model.predict(X_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"📊 {dataset_name} Set Performance:")
        print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Total predictions: {len(y_test)}")
        print(f"   Correct: {(y_pred == y_test).sum()}")
        print(f"   Incorrect: {(y_pred != y_test).sum()}")
        
        print(f"\n   Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"   ┌─────────────┬──────────┬──────────┐")
        print(f"   │             │ Pred: L  │ Pred: W  │")
        print(f"   ├─────────────┼──────────┼──────────┤")
        print(f"   │ Actual: L   │   {cm[0][0]:4d}   │   {cm[0][1]:4d}   │")
        print(f"   │ Actual: W   │   {cm[1][0]:4d}   │   {cm[1][1]:4d}   │")
        print(f"   └─────────────┴──────────┴──────────┘")
        
        print(f"\n{classification_report(y_test, y_pred, target_names=['Away Win', 'Home Win'])}")
        
        return accuracy
    
    def save_model(self, model_dir='ml/models'):
        """Save trained model"""
        os.makedirs(model_dir, exist_ok=True)
        
        joblib.dump(self.model, f'{model_dir}/nfl_neural_network_v2.pkl')
        joblib.dump(self.scaler, f'{model_dir}/scaler_v2.pkl')
        
        with open(f'{model_dir}/feature_names_v2.txt', 'w') as f:
            f.write('\n'.join(self.feature_names))
        
        print(f"\n✅ Model saved: {model_dir}/nfl_neural_network_v2.pkl")
    
    def train_full_pipeline(self):
        """Run complete training pipeline"""
        # 1. Fetch data
        games_df, stats_df = self.fetch_training_data()
        
        # 2. Compute rolling features
        X, y = self.compute_rolling_features(games_df, stats_df)
        
        # 3. Split data
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, y)
        
        # 4. Train
        self.train(X_train, y_train)
        
        # 5. Evaluate
        val_acc = self.evaluate(X_val, y_val, "Validation")
        test_acc = self.evaluate(X_test, y_test, "Test")
        
        # 6. Save
        self.save_model()
        
        return test_acc, val_acc

def main():
    print("="*80)
    print("NFL NEURAL NETWORK V2 - TRAINING PIPELINE (Data Leakage Fixed!)")
    print("Sprint 9: Machine Learning Predictions")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    nn = NFLNeuralNetworkV2()
    test_acc, val_acc = nn.train_full_pipeline()
    
    print("\n" + "="*80)
    print("✅ TRAINING COMPLETE!")
    print("="*80)
    print(f"📊 Final Results:")
    print(f"   Validation Accuracy: {val_acc:.4f} ({val_acc*100:.2f}%)")
    print(f"   Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
    print(f"   Model saved: ml/models/nfl_neural_network_v2.pkl")
    print("="*80)
    
    if test_acc > 0.70:
        print("\n⚠️  WARNING: >70% accuracy might still indicate data leakage!")
        print("   Expected accuracy with proper features: 55-65%")
    elif test_acc >= 0.55:
        print("\n🎉 Model performance looks realistic!")
        print("   This aligns with industry standards (Vegas ~52-55%, Best ML ~57-60%)")
    else:
        print("\n⚠️  Model accuracy below expected range.")
        print("   May need more features or hyperparameter tuning.")

if __name__ == "__main__":
    main()
