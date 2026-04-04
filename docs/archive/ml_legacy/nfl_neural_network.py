"""
NFL Neural Network Predictor - Sprint 9
3-layer deep learning model for game predictions

Architecture:
- Input layer: 90+ features (team stats + EPA metrics)
- Hidden layer 1: 128 neurons (ReLU activation)
- Hidden layer 2: 64 neurons (ReLU activation)  
- Hidden layer 3: 32 neurons (ReLU activation)
- Output layer: 4 outputs (winner, home_score, away_score, confidence)

Academic Focus (Dr. Foster's ML Curriculum):
- Neurons and activation functions
- Neural networks and deep learning
- Backpropagation and gradient descent
- Training/validation/test splits
"""

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error
import joblib

# Neural network imports (using scikit-learn's MLP - works better on Windows)
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

load_dotenv()

class NFLNeuralNetwork:
    """3-layer neural network for NFL game predictions"""
    
    def __init__(self, model_dir='ml/models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.feature_names = []
        
        # Database connection
        self.db_config = {
            'dbname': 'nfl_analytics',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD'),
            'host': 'localhost'
        }
    
    def fetch_training_data(self):
        """Fetch historical data (1999-2025) with EPA stats"""
        print("\n" + "="*80)
        print("FETCHING TRAINING DATA FROM DATABASE")
        print("="*80)
        
        conn = psycopg2.connect(**self.db_config)
        
        # Fetch team-game stats with EPA metrics
        query = """
        SELECT 
            tgs.*,
            g.season AS game_season,
            g.week AS game_week,
            g.home_score,
            g.away_score,
            g.spread_line,
            g.total_line,
            g.home_moneyline,
            g.away_moneyline
        FROM hcl.team_game_stats tgs
        JOIN hcl.games g ON tgs.game_id = g.game_id
        WHERE g.home_score IS NOT NULL  -- Only completed games
          AND g.away_score IS NOT NULL
        ORDER BY g.season, g.week, tgs.game_id
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"✅ Loaded {len(df):,} team-game records")
        print(f"   Seasons: {df['season'].min()}-{df['season'].max()}")
        print(f"   Unique games: {df['game_id'].nunique():,}")
        
        return df
    
    def prepare_features(self, df):
        """
        Prepare feature matrix for neural network
        
        Features include:
        - Basic stats (51 columns from original schema)
        - EPA metrics (13 columns we just added)
        - Betting lines (spread, total, moneyline)
        - Context (season, week, home/away)
        
        EXCLUDE outcome-related columns to prevent data leakage!
        """
        print("\n" + "="*80)
        print("PREPARING FEATURES")
        print("="*80)
        
        # Columns to EXCLUDE (prevent data leakage!)
        exclude_cols = [
            'game_id', 'team', 'opponent', 'created_at', 'updated_at',
            # OUTCOME COLUMNS - These reveal who won!
            'home_score', 'away_score',           # Final scores
            'won', 'team_score', 'opponent_score',  # Derived from scores
            'point_diff',                          # Point differential
            # ALSO exclude game_season and game_week (use season/week from team_game_stats)
            'game_season', 'game_week'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Convert boolean to int
        if 'is_home' in df.columns:
            df['is_home'] = df['is_home'].astype(int)
        
        # Fill NaN with 0 (for stats that might be missing)
        X = df[feature_cols].fillna(0)
        
        self.feature_names = feature_cols
        
        print(f"✅ Feature matrix shape: {X.shape}")
        print(f"   Total features: {X.shape[1]}")
        print(f"   Sample features: {feature_cols[:10]}")
        print(f"   Excluded (data leakage prevention): {len(exclude_cols)} columns")
        
        return X
    
    def create_labels(self, df):
        """
        Create target labels for training
        
        For each game, we predict:
        1. Winner (1 if team won, 0 if lost)
        2. Team score
        3. Opponent score  
        4. Point differential
        """
        print("\n" + "="*80)
        print("CREATING LABELS")
        print("="*80)
        
        # Determine winner (home team perspective)
        df['won'] = (
            (df['is_home'] & (df['home_score'] > df['away_score'])) |
            (~df['is_home'] & (df['away_score'] > df['home_score']))
        ).astype(int)
        
        # Get team's score and opponent's score
        df['team_score'] = df.apply(
            lambda row: row['home_score'] if row['is_home'] else row['away_score'],
            axis=1
        )
        
        df['opponent_score'] = df.apply(
            lambda row: row['away_score'] if row['is_home'] else row['home_score'],
            axis=1
        )
        
        # Point differential (positive = won by X, negative = lost by X)
        df['point_diff'] = df['team_score'] - df['opponent_score']
        
        print(f"✅ Labels created:")
        print(f"   Wins: {df['won'].sum():,} ({df['won'].mean()*100:.1f}%)")
        print(f"   Losses: {(1-df['won']).sum():,} ({(1-df['won']).mean()*100:.1f}%)")
        print(f"   Avg point differential: {df['point_diff'].mean():.2f}")
        
        return df
    
    def build_model(self, input_dim):
        """
        Build 3-layer deep neural network using scikit-learn MLPClassifier
        
        Architecture (Dr. Foster's ML curriculum):
        - Layer 1: 128 neurons + ReLU activation
        - Layer 2: 64 neurons + ReLU activation
        - Layer 3: 32 neurons + ReLU activation
        - Output: 1 neuron (winner probability)
        
        MLPClassifier uses:
        - Backpropagation for training
        - Adam optimizer
        - Automatic handling of activation functions
        """
        print("\n" + "="*80)
        print("BUILDING NEURAL NETWORK")
        print("="*80)
        
        model = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),  # 3 hidden layers
            activation='relu',                   # ReLU activation
            solver='adam',                       # Adam optimizer
            alpha=0.0001,                        # L2 regularization
            batch_size=32,                       # Mini-batch size
            learning_rate='adaptive',            # Adaptive learning rate
            learning_rate_init=0.001,           # Initial learning rate
            max_iter=100,                        # Maximum epochs
            early_stopping=True,                 # Stop if no improvement
            validation_fraction=0.15,            # Use for validation
            n_iter_no_change=10,                 # Patience for early stopping
            random_state=42,                     # Reproducibility
            verbose=True                         # Print progress
        )
        
        print("✅ Model architecture:")
        print(f"   Input layer: {input_dim} features")
        print(f"   Hidden layer 1: 128 neurons (ReLU)")
        print(f"   Hidden layer 2: 64 neurons (ReLU)")
        print(f"   Hidden layer 3: 32 neurons (ReLU)")
        print(f"   Output layer: 1 neuron (binary classification)")
        print(f"   Total parameters: ~{input_dim*128 + 128*64 + 64*32 + 32:,}")
        
        return model
    
    def split_data(self, X, y, df):
        """
        Split data into train/validation/test sets
        
        Strategy:
        - Train: 1999-2023 (70% of data)
        - Validation: 2024 season (15%)
        - Test: 2025 season (15%)
        
        Also apply sample weighting: Recent years = more weight
        """
        print("\n" + "="*80)
        print("SPLITTING DATA")
        print("="*80)
        
        # Reset index to ensure proper alignment
        df_reset = df.reset_index(drop=True)
        
        # Extract season as 1D array  (use 'game_season' which was aliased)
        seasons = df_reset['game_season'].values
        if seasons.ndim > 1:
            print(f"WARNING: seasons is {seasons.ndim}D with shape {seasons.shape}, flattening...")
            seasons = seasons.ravel()
        
        print(f"✅ Seasons extracted: shape={seasons.shape}, range={seasons.min()}-{seasons.max()}")
        
        # Split by season (time-based) using boolean mask
        train_mask = seasons <= 2023
        val_mask = seasons == 2024
        test_mask = seasons == 2025
        
        # Boolean indexing automatically selects rows for 2D arrays
        X_train = X[train_mask]
        y_train = y[train_mask]
        
        X_val = X[val_mask]
        y_val = y[val_mask]
        
        X_test = X[test_mask]
        y_test = y[test_mask]
        
        # Calculate sample weights (recent years more important)
        train_seasons = seasons[train_mask]
        sample_weights = self._calculate_sample_weights(train_seasons)
        
        print(f"✅ Data split:")
        print(f"   Train: {len(X_train):,} records (1999-2023)")
        print(f"   Validation: {len(X_val):,} records (2024)")
        print(f"   Test: {len(X_test):,} records (2025)")
        print(f"   Sample weights shape: {sample_weights.shape} (min: {sample_weights.min():.2f}, max: {sample_weights.max():.2f})")
        
        return X_train, X_val, X_test, y_train, y_val, y_test, sample_weights
    
    def _calculate_sample_weights(self, seasons):
        """
        Calculate sample weights based on season
        Recent years = more weight (more relevant to current game)
        
        Weighting strategy:
        - 2020-2023: 100% weight (1.0)
        - 2010-2019: 60% weight (0.6)
        - 1999-2009: 20% weight (0.2)
        """
        # Ensure seasons is 1D array
        seasons = np.array(seasons).ravel()  # Use ravel instead of flatten
        
        print(f"   DEBUG: seasons shape = {seasons.shape}, unique seasons = {np.unique(seasons)[:5]}...")
        
        weights = np.zeros(len(seasons))
        
        # Use numpy conditions
        recent_mask = seasons >= 2020
        mid_mask = (seasons >= 2010) & (seasons < 2020)
        old_mask = seasons < 2010
        
        weights[recent_mask] = 1.0
        weights[mid_mask] = 0.6
        weights[old_mask] = 0.2
        
        print(f"   DEBUG: weights shape = {weights.shape}")
        
        return weights
    
    def train(self, X_train, y_train, X_val, y_val, sample_weights, epochs=100, batch_size=32):
        """
        Train neural network
        
        Note: MLPClassifier handles validation and early stopping internally
        """
        print("\n" + "="*80)
        print("TRAINING NEURAL NETWORK")
        print("="*80)
        
        print(f"\n🎓 Training neural network...")
        print(f"   Max epochs: {epochs}")
        print(f"   Batch size: {batch_size}")
        print(f"   Using sample weights: Yes")
        print(f"   Early stopping: Yes (patience=10)")
        
        start_time = datetime.now()
        
        # Train on training set only (MLPClassifier creates own validation split)
        self.model.fit(X_train, y_train, sample_weight=sample_weights)
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ Training complete in {training_time:.1f} seconds")
        print(f"   Iterations completed: {self.model.n_iter_}")
        print(f"   Final loss: {self.model.loss_:.6f}")
        
        # Evaluate on validation set
        val_pred = self.model.predict(X_val)
        val_accuracy = accuracy_score(y_val, val_pred)
        print(f"   Validation accuracy: {val_accuracy:.4f} ({val_accuracy*100:.2f}%)")
        
        return None  # MLPClassifier doesn't return history like Keras
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test set (2025 season)"""
        print("\n" + "="*80)
        print("EVALUATING MODEL")
        print("="*80)
        
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📊 Test Set Performance (2025 season):")
        print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Total predictions: {len(y_test):,}")
        print(f"   Correct: {(y_pred == y_test).sum():,}")
        print(f"   Incorrect: {(y_pred != y_test).sum():,}")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        print(f"\n   Confusion Matrix:")
        print(f"   ┌─────────────┬──────────┬──────────┐")
        print(f"   │             │ Pred: L  │ Pred: W  │")
        print(f"   ├─────────────┼──────────┼──────────┤")
        print(f"   │ Actual: L   │   {tn:4d}   │   {fp:4d}   │")
        print(f"   │ Actual: W   │   {fn:4d}   │   {tp:4d}   │")
        print(f"   └─────────────┴──────────┴──────────┘")
        
        # Classification report
        print("\n" + classification_report(y_test, y_pred, target_names=['Loss', 'Win']))
        
        return accuracy, None
    
    def save_model(self):
        """Save trained model and scaler"""
        print("\n" + "="*80)
        print("SAVING MODEL")
        print("="*80)
        
        # Save sklearn model
        model_path = f'{self.model_dir}/nfl_neural_network.pkl'
        joblib.dump(self.model, model_path)
        print(f"✅ Model saved: {model_path}")
        
        # Save scaler
        scaler_path = f'{self.model_dir}/scaler.pkl'
        joblib.dump(self.scaler, scaler_path)
        print(f"✅ Scaler saved: {scaler_path}")
        
        # Save feature names
        features_path = f'{self.model_dir}/feature_names.txt'
        with open(features_path, 'w') as f:
            f.write('\n'.join(self.feature_names))
        print(f"✅ Feature names saved: {features_path}")
    
    def load_model(self):
        """Load trained model and scaler"""
        model_path = f'{self.model_dir}/nfl_neural_network.pkl'
        scaler_path = f'{self.model_dir}/scaler.pkl'
        features_path = f'{self.model_dir}/feature_names.txt'
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        with open(features_path, 'r') as f:
            self.feature_names = [line.strip() for line in f]
        
        print(f"✅ Model loaded from {model_path}")
    
    def predict_game(self, home_team_features, away_team_features):
        """
        Predict outcome of a game
        
        Args:
            home_team_features: dict of home team stats
            away_team_features: dict of away team stats
        
        Returns:
            dict with prediction results
        """
        # TODO: Implement game prediction logic
        # This will be used by the API endpoint
        pass
    
    def train_full_pipeline(self):
        """Run complete training pipeline"""
        print("\n" + "="*80)
        print("NFL NEURAL NETWORK - TRAINING PIPELINE")
        print("Sprint 9: Machine Learning Predictions")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 1. Fetch data
        df = self.fetch_training_data()
        
        # 2. Create labels
        df = self.create_labels(df)
        
        # 3. Prepare features
        X = self.prepare_features(df)
        y = df['won'].values
        
        # 4. Scale features
        print("\n" + "="*80)
        print("SCALING FEATURES")
        print("="*80)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        print(f"✅ Features scaled (mean=0, std=1)")
        
        # 5. Split data
        X_train, X_val, X_test, y_train, y_val, y_test, sample_weights = \
            self.split_data(X_scaled, y, df)
        
        # 6. Build model
        self.model = self.build_model(input_dim=X_train.shape[1])
        
        # 7. Train model
        history = self.train(
            X_train, y_train,
            X_val, y_val,
            sample_weights,
            epochs=100,
            batch_size=32
        )
        
        # 8. Evaluate model
        accuracy, _ = self.evaluate(X_test, y_test)
        
        # 9. Save model
        self.save_model()
        
        print("\n" + "="*80)
        print("✅ TRAINING COMPLETE!")
        print("="*80)
        print(f"📊 Final Results:")
        print(f"   Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Model saved: {self.model_dir}/nfl_neural_network.pkl")
        print(f"   Ready for predictions!")
        print("="*80 + "\n")
        
        return accuracy, None

def main():
    """Train NFL neural network"""
    nn = NFLNeuralNetwork()
    accuracy, _ = nn.train_full_pipeline()
    
    print(f"\n🎉 Model training successful!")
    print(f"   Accuracy: {accuracy*100:.2f}%")
    print(f"   Next: Create API endpoint and frontend")

if __name__ == "__main__":
    main()
