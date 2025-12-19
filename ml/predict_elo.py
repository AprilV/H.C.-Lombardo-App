"""
NFL Elo-Based Game Predictions

Uses Elo ratings to predict upcoming NFL games.
Can be used standalone or as part of an ensemble with XGBoost.

Usage:
    python ml/predict_elo.py --season 2025 --week 16
    python ml/predict_elo.py --upcoming

Sprint 10: Elo System Implementation
Date: December 19, 2025
"""

import psycopg2
import pandas as pd
import numpy as np
import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from elo_ratings import EloRatingSystem
from elo_tracker import EloTracker

load_dotenv()

class EloPredictionSystem:
    """Generate game predictions using Elo ratings"""
    
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'nfl_analytics'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        # Initialize Elo tracker
        self.tracker = EloTracker()
        
        # Load current ratings
        ratings_file = 'ml/models/elo_ratings_current.json'
        if not self.tracker.load_current_ratings(ratings_file):
            print("⚠️  Warning: No saved Elo ratings found!")
            print("   Run: python ml/elo_tracker.py --rebuild")
            self.tracker.initialize_all_teams()
    
    def get_scheduled_games(self, season: int, week: int):
        """Get games scheduled for a specific week"""
        conn = psycopg2.connect(**self.db_config)
        
        query = """
        SELECT 
            game_id,
            season,
            week,
            game_date,
            home_team,
            away_team,
            home_score,
            away_score,
            spread_line,
            total_line
        FROM hcl.games
        WHERE season = %s 
          AND week = %s
        ORDER BY game_date, game_id
        """
        
        df = pd.read_sql(query, conn, params=(season, week))
        conn.close()
        
        # Normalize team names
        df['home_team'] = df['home_team'].apply(self.tracker.normalize_team)
        df['away_team'] = df['away_team'].apply(self.tracker.normalize_team)
        
        return df
    
    def predict_game(self, home_team: str, away_team: str, 
                    spread_line: float = None, is_neutral: bool = False):
        """
        Predict a single game using Elo ratings
        
        Args:
            home_team: Home team abbreviation
            away_team: Away team abbreviation
            spread_line: Vegas spread line (for comparison)
            is_neutral: Whether game is at neutral site
        
        Returns:
            Dictionary with prediction details
        """
        # Normalize team names
        home_team = self.tracker.normalize_team(home_team)
        away_team = self.tracker.normalize_team(away_team)
        
        # Get current Elo ratings
        home_elo = self.tracker.elo.get_rating(home_team)
        away_elo = self.tracker.elo.get_rating(away_team)
        
        # Predict win probabilities
        home_win_prob, away_win_prob = self.tracker.elo.predict_game(
            home_team, away_team, is_neutral=is_neutral
        )
        
        # Predict point spread
        elo_spread = self.tracker.elo.predict_spread(
            home_team, away_team, is_neutral=is_neutral
        )
        
        # Determine predicted winner and confidence
        if home_win_prob > 0.5:
            predicted_winner = home_team
            confidence = home_win_prob
        else:
            predicted_winner = away_team
            confidence = away_win_prob
        
        # Compare to Vegas line (if available)
        split_prediction = False
        vegas_implied_prob = None
        
        if spread_line is not None:
            # Vegas spread to implied probability (approximate)
            # Spread of -3 ≈ 60% favorite
            vegas_implied_prob = 0.5 + (spread_line / 22.0)  # Empirical conversion
            vegas_implied_prob = max(0.1, min(0.9, vegas_implied_prob))
            
            # Check if Elo disagrees with Vegas
            vegas_favorite = home_team if spread_line > 0 else away_team
            if predicted_winner != vegas_favorite and abs(elo_spread - spread_line) >= 3.0:
                split_prediction = True
        
        prediction = {
            'home_team': home_team,
            'away_team': away_team,
            'home_elo': round(home_elo, 1),
            'away_elo': round(away_elo, 1),
            'elo_diff': round(home_elo - away_elo, 1),
            'home_win_prob': round(home_win_prob, 3),
            'away_win_prob': round(away_win_prob, 3),
            'predicted_winner': predicted_winner,
            'confidence': round(confidence, 3),
            'elo_spread': round(elo_spread, 1),
            'vegas_spread': round(spread_line, 1) if spread_line is not None else None,
            'spread_diff': round(abs(elo_spread - spread_line), 1) if spread_line is not None else None,
            'split_prediction': split_prediction,
            'vegas_implied_prob': round(vegas_implied_prob, 3) if vegas_implied_prob is not None else None
        }
        
        return prediction
    
    def predict_week(self, season: int, week: int, save_to_db: bool = True):
        """
        Predict all games for a specific week
        
        Args:
            season: Season year
            week: Week number
            save_to_db: Whether to save predictions to database
        
        Returns:
            List of prediction dictionaries
        """
        print(f"\n{'='*70}")
        print(f"NFL ELO PREDICTIONS - {season} Week {week}")
        print(f"{'='*70}\n")
        
        # Get scheduled games
        games_df = self.get_scheduled_games(season, week)
        
        if len(games_df) == 0:
            print(f"❌ No games found for {season} Week {week}")
            return []
        
        print(f"📊 Predicting {len(games_df)} games...\n")
        
        predictions = []
        
        for _, game in games_df.iterrows():
            # Check if game already played
            if pd.notna(game['home_score']) and pd.notna(game['away_score']):
                print(f"⏭️  {game['away_team']} @ {game['home_team']} - Already played")
                continue
            
            # Neutral site detection (assume regular season games have home field)
            is_neutral = False
            
            # Make prediction
            pred = self.predict_game(
                game['home_team'],
                game['away_team'],
                spread_line=game['spread_line'] if pd.notna(game['spread_line']) else None,
                is_neutral=is_neutral
            )
            
            pred['game_id'] = game['game_id']
            pred['season'] = season
            pred['week'] = week
            pred['game_date'] = game['game_date']
            
            predictions.append(pred)
            
            # Display prediction
            self._display_prediction(pred)
        
        # Save to database if requested
        if save_to_db and len(predictions) > 0:
            self._save_predictions_to_db(predictions)
        
        # Summary
        print(f"\n{'='*70}")
        print(f"SUMMARY: {len(predictions)} predictions generated")
        
        if len(predictions) > 0:
            avg_confidence = np.mean([p['confidence'] for p in predictions])
            split_count = sum([p['split_prediction'] for p in predictions])
            print(f"Average confidence: {avg_confidence:.1%}")
            print(f"Split predictions: {split_count} ({split_count/len(predictions):.1%})")
        
        print(f"{'='*70}\n")
        
        return predictions
    
    def _display_prediction(self, pred: dict):
        """Display a single prediction in formatted output"""
        matchup = f"{pred['away_team']} @ {pred['home_team']}"
        winner = pred['predicted_winner']
        confidence = pred['confidence']
        elo_spread = pred['elo_spread']
        
        print(f"🏈 {matchup:<15}")
        print(f"   Elo Ratings: {pred['away_team']} {pred['away_elo']} vs {pred['home_team']} {pred['home_elo']}")
        print(f"   ✅ Prediction: {winner} wins ({confidence:.1%} confidence)")
        print(f"   📊 Elo Spread: {pred['home_team']} {elo_spread:+.1f}")
        
        if pred['vegas_spread'] is not None:
            print(f"   🎲 Vegas Line: {pred['home_team']} {pred['vegas_spread']:+.1f}")
            print(f"   📉 Difference: {pred['spread_diff']:.1f} points")
            
            if pred['split_prediction']:
                print(f"   ⚠️  SPLIT PREDICTION - Elo disagrees with Vegas!")
        
        print()
    
    def _save_predictions_to_db(self, predictions: list):
        """Save predictions to database"""
        print(f"\n💾 Saving {len(predictions)} predictions to database...")
        
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Use upsert to handle existing predictions
        insert_query = """
        INSERT INTO hcl.ml_predictions_elo (
            game_id, season, week, 
            home_team, away_team,
            home_elo, away_elo, elo_diff,
            home_win_prob, away_win_prob,
            predicted_winner, confidence,
            elo_spread, vegas_spread, spread_diff,
            split_prediction,
            prediction_date
        ) VALUES (
            %(game_id)s, %(season)s, %(week)s,
            %(home_team)s, %(away_team)s,
            %(home_elo)s, %(away_elo)s, %(elo_diff)s,
            %(home_win_prob)s, %(away_win_prob)s,
            %(predicted_winner)s, %(confidence)s,
            %(elo_spread)s, %(vegas_spread)s, %(spread_diff)s,
            %(split_prediction)s,
            NOW()
        )
        ON CONFLICT (game_id) 
        DO UPDATE SET
            home_elo = EXCLUDED.home_elo,
            away_elo = EXCLUDED.away_elo,
            elo_diff = EXCLUDED.elo_diff,
            home_win_prob = EXCLUDED.home_win_prob,
            away_win_prob = EXCLUDED.away_win_prob,
            predicted_winner = EXCLUDED.predicted_winner,
            confidence = EXCLUDED.confidence,
            elo_spread = EXCLUDED.elo_spread,
            vegas_spread = EXCLUDED.vegas_spread,
            spread_diff = EXCLUDED.spread_diff,
            split_prediction = EXCLUDED.split_prediction,
            prediction_date = NOW()
        """
        
        try:
            for pred in predictions:
                cursor.execute(insert_query, pred)
            
            conn.commit()
            print(f"✅ Saved {len(predictions)} predictions")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error saving predictions: {e}")
        
        finally:
            cursor.close()
            conn.close()
    
    def predict_upcoming(self):
        """Predict next week's games"""
        # Find the current/next week with unplayed games
        conn = psycopg2.connect(**self.db_config)
        
        query = """
        SELECT season, week, COUNT(*) as game_count
        FROM hcl.games
        WHERE home_score IS NULL 
          AND game_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY season, week
        ORDER BY season DESC, week ASC
        LIMIT 1
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if len(df) == 0:
            print("❌ No upcoming games found")
            return []
        
        season = int(df.iloc[0]['season'])
        week = int(df.iloc[0]['week'])
        
        return self.predict_week(season, week)


def main():
    parser = argparse.ArgumentParser(description='NFL Elo-Based Predictions')
    parser.add_argument('--season', type=int, help='Season year')
    parser.add_argument('--week', type=int, help='Week number')
    parser.add_argument('--upcoming', action='store_true', 
                       help='Predict next upcoming week')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save predictions to database')
    
    args = parser.parse_args()
    
    predictor = EloPredictionSystem()
    
    if args.upcoming:
        predictor.predict_upcoming()
    elif args.season and args.week:
        predictor.predict_week(args.season, args.week, save_to_db=not args.no_save)
    else:
        print("Usage:")
        print("  python ml/predict_elo.py --season 2025 --week 16")
        print("  python ml/predict_elo.py --upcoming")
        print("  python ml/predict_elo.py --season 2025 --week 16 --no-save")


if __name__ == '__main__':
    main()
