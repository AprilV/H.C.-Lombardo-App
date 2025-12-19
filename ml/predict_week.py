"""
NFL Weekly Game Predictions

This script uses the trained XGBoost models to predict upcoming games.
It computes rolling features from previous games and generates predictions.

Usage:
    python ml/predict_week.py --season 2025 --week 10
    python ml/predict_week.py --upcoming  # Next week's games

Sprint 10: XGBoost Model Integration
Date: December 18, 2025
"""

import psycopg2
import pandas as pd
import numpy as np
import joblib
import os
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class WeeklyPredictor:
    """Predict NFL games for a given week using trained model"""
    
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'nfl_analytics'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        # Load XGBoost WIN/LOSS model (classification)
        model_dir = 'ml/models'
        self.win_model = joblib.load(f'{model_dir}/xgb_winner.pkl')
        
        with open(f'{model_dir}/xgb_winner_features.txt', 'r') as f:
            self.win_feature_names = [line.strip() for line in f.readlines()]
        
        # Load XGBoost POINT SPREAD model (regression)
        self.spread_model = joblib.load(f'{model_dir}/xgb_spread.pkl')
        
        with open(f'{model_dir}/xgb_spread_features.txt', 'r') as f:
            self.spread_feature_names = [line.strip() for line in f.readlines()]
        
        print(f"[OK] Loaded XGBoost win/loss model with {len(self.win_feature_names)} features")
        print(f"[OK] Loaded XGBoost point spread model with {len(self.spread_feature_names)} features")
    
    def fetch_schedule(self, season, week):
        """Fetch games scheduled for the given week"""
        conn = psycopg2.connect(**self.db_config)
        
        query = """
            SELECT
                game_id,
                season,
                week,
                home_team,
                away_team,
                game_date,
                kickoff_time_utc,
                home_score,
                away_score,
                spread_line,
                total_line,
                home_moneyline,
                away_moneyline,
                is_postseason
            FROM hcl.games
            WHERE season = %s 
            AND week = %s
            AND is_postseason = false
            ORDER BY game_date, kickoff_time_utc;
        """
        
        df = pd.read_sql(query, conn, params=(season, week))
        conn.close()
        
        return df
    
    def fetch_team_cumulative_stats(self, season, week, team):
        """Fetch cumulative stats for a team BEFORE the target week (matches training query)"""
        conn = psycopg2.connect(**self.db_config)
        
        query = """
            WITH game_stats AS (
                SELECT 
                    tgs.game_id, tgs.team, g.season, g.week,
                    tgs.points, tgs.total_yards, tgs.passing_yards, tgs.rushing_yards,
                    tgs.yards_per_play, tgs.turnovers, tgs.third_down_pct, tgs.red_zone_pct,
                    tgs.epa_per_play, tgs.success_rate, tgs.pass_epa, tgs.rush_epa,
                    tgs.cpoe, tgs.pass_success_rate, tgs.rush_success_rate,
                    tgs.completion_pct, tgs.qb_rating, tgs.interceptions, tgs.sacks_taken,
                    tgs.yards_per_carry, tgs.explosive_play_pct, tgs.time_of_possession_pct
                FROM hcl.team_game_stats tgs
                JOIN hcl.games g ON tgs.game_id = g.game_id
                WHERE g.season = %s
                  AND g.week < %s
                  AND tgs.team = %s
                  AND g.is_postseason = FALSE
            )
            SELECT 
                AVG(points) as avg_ppg,
                AVG(total_yards) as avg_yards,
                AVG(passing_yards) as avg_pass_yards,
                AVG(rushing_yards) as avg_rush_yards,
                AVG(yards_per_play) as avg_ypp,
                AVG(turnovers) as avg_turnovers,
                AVG(third_down_pct) as avg_3rd_pct,
                AVG(red_zone_pct) as avg_rz_pct,
                AVG(epa_per_play) as avg_epa,
                AVG(success_rate) as avg_success,
                AVG(pass_epa) as avg_pass_epa,
                AVG(rush_epa) as avg_rush_epa,
                AVG(cpoe) as avg_cpoe,
                AVG(pass_success_rate) as avg_pass_success,
                AVG(rush_success_rate) as avg_rush_success,
                AVG(completion_pct) as avg_comp_pct,
                AVG(qb_rating) as avg_qb_rating,
                AVG(interceptions) as avg_ints,
                AVG(sacks_taken) as avg_sacks,
                AVG(yards_per_carry) as avg_ypc,
                AVG(explosive_play_pct) as avg_explosive,
                AVG(time_of_possession_pct) as avg_top
            FROM game_stats
        """
        
        df = pd.read_sql(query, conn, params=(season, week, team))
        conn.close()
        
        if len(df) == 0 or df.iloc[0]['avg_ppg'] is None:
            return None
        
        return df.iloc[0].to_dict()
    
    def compute_rolling_features(self, season, week, home_team, away_team):
        """
        Compute features matching the 46-feature XGBoost model
        """
        # Fetch cumulative stats for both teams
        home_stats = self.fetch_team_cumulative_stats(season, week, home_team)
        away_stats = self.fetch_team_cumulative_stats(season, week, away_team)
        
        # Default values (league averages) if no prior games
        defaults = {
            'avg_ppg': 20, 'avg_yards': 320, 'avg_pass_yards': 220, 'avg_rush_yards': 100,
            'avg_ypp': 5.0, 'avg_turnovers': 1.0, 'avg_3rd_pct': 40.0, 'avg_rz_pct': 55.0,
            'avg_epa': 0.0, 'avg_success': 45.0, 'avg_pass_epa': 0.0, 'avg_rush_epa': 0.0,
            'avg_cpoe': 0.0, 'avg_pass_success': 45.0, 'avg_rush_success': 45.0,
            'avg_comp_pct': 63.0, 'avg_qb_rating': 90.0, 'avg_ints': 0.8, 'avg_sacks': 2.0,
            'avg_ypc': 4.3, 'avg_explosive': 10.0, 'avg_top': 50.0
        }
        
        if home_stats is None:
            home_stats = defaults
        if away_stats is None:
            away_stats = defaults
        
        # Build feature dictionary matching model feature names
        features = {}
        for key in defaults.keys():
            stat_name = key.replace('avg_', '')
            features[f'home_{stat_name}'] = home_stats.get(key, defaults[key])
            features[f'away_{stat_name}'] = away_stats.get(key, defaults[key])
        
        return features
        features['ppg_differential'] = features['home_ppg_season'] - features['away_ppg_season']
        features['success_differential'] = features['home_success_season'] - features['away_success_season']
        features['ypp_differential'] = features['home_ypp_season'] - features['away_ypp_season']
        
        # Handle NaN and inf values
        for key in features:
            if pd.isna(features[key]) or np.isinf(features[key]):
                features[key] = 0.0
        
        return features
    
    def predict_game(self, season, week, home_team, away_team, spread_line=None, total_line=None):
        """
        Predict outcome of a single game using BOTH models
        Returns: dict with win probability, predicted scores, and point differential
        """
        # Compute features
        features = self.compute_rolling_features(season, week, home_team, away_team)
        
        # Add betting lines if available
        if 'spread_line' in self.win_feature_names:
            features['spread_line'] = spread_line if spread_line is not None else 0.0
        if 'total_line' in self.win_feature_names:
            features['total_line'] = total_line if total_line is not None else 44.0
        
        # PREDICT WIN/LOSS (XGBoost Classification)
        X_win = np.array([[features.get(name, 0.0) for name in self.win_feature_names]])
        
        win_prediction = self.win_model.predict(X_win)[0]  # 1 = home win, 0 = away win
        win_confidence = self.win_model.predict_proba(X_win)[0]
        
        # PREDICT POINT SPREAD (XGBoost Regression)
        X_spread = np.array([[features.get(name, 0.0) for name in self.spread_feature_names]])
        
        predicted_margin = self.spread_model.predict(X_spread)[0]  # Positive = home favored
        
        # Calculate predicted scores using point spread + total line
        avg_total = total_line if total_line is not None else 47.0
        predicted_home_score = round((avg_total + predicted_margin) / 2, 1)
        predicted_away_score = round((avg_total - predicted_margin) / 2, 1)
        
        # AI-generated spread (negative means home favored)
        ai_spread = -predicted_margin
        
        # Winner from POINT SPREAD model (more specific than win/loss model)
        spread_predicted_winner = home_team if predicted_margin > 0 else away_team
        
        # Compare to Vegas spread
        spread_difference = None
        if spread_line is not None:
            spread_difference = round(ai_spread - spread_line, 1)
        
        # Build comprehensive result
        result = {
            'home_team': home_team,
            'away_team': away_team,
            
            # Win/Loss prediction from classification model
            'win_model_prediction': home_team if win_prediction == 1 else away_team,
            'home_win_prob': float(win_confidence[1]),
            'away_win_prob': float(win_confidence[0]),
            'confidence': float(max(win_confidence)),
            
            # Use spread model's winner as primary (more granular)
            'predicted_winner': spread_predicted_winner,
            
            # Score predictions
            'predicted_home_score': predicted_home_score,
            'predicted_away_score': predicted_away_score,
            'predicted_margin': round(predicted_margin, 1),
            
            # Spread analysis
            'ai_spread': round(ai_spread, 1),
            'vegas_spread': spread_line,
            'spread_difference': spread_difference,
            'total_line': total_line,
            
            # Key factors
            'key_factors': {
                'home_epa': features.get('home_epa_season', 0),
                'away_epa': features.get('away_epa_season', 0),
                'epa_advantage': features.get('epa_differential', 0),
                'home_recent_epa': features.get('home_epa_l3', 0),
                'away_recent_epa': features.get('away_epa_l3', 0),
            }
        }
        
        return result
    
    def predict_week(self, season, week):
        """Predict all games for a given week"""
        print(f"\n{'='*80}")
        print(f"PREDICTING WEEK {week} of {season} SEASON")
        print(f"{'='*80}\n")
        
        # Fetch schedule
        schedule = self.fetch_schedule(season, week)
        
        if len(schedule) == 0:
            print(f"[ERROR] No games found for Week {week}")
            return []
        
        print(f"Found {len(schedule)} games\n")
        
        predictions = []
        
        for idx, game in schedule.iterrows():
            print(f"Predicting: {game['away_team']} @ {game['home_team']}")
            
            # NFLverse uses inverted sign convention: positive = home favored
            # We need to flip to standard convention: negative = favored
            raw_spread = game.get('spread_line')
            vegas_spread = -raw_spread if raw_spread is not None else None
            
            result = self.predict_game(
                season=season,
                week=week,
                home_team=game['home_team'],
                away_team=game['away_team'],
                spread_line=vegas_spread,
                total_line=game.get('total_line')
            )
            
            # Add game metadata
            result['game_id'] = game['game_id']
            result['season'] = season
            result['week'] = week
            result['game_date'] = str(game['game_date']) if pd.notna(game['game_date']) else None
            result['kickoff_time'] = str(game['kickoff_time_utc']) if pd.notna(game['kickoff_time_utc']) else None
            
            # Determine game status
            if pd.notna(game['home_score']) and pd.notna(game['away_score']):
                # Game has been played (completed)
                result['status'] = 'final'
                result['actual_home_score'] = int(game['home_score'])
                result['actual_away_score'] = int(game['away_score'])
                result['actual_winner'] = game['home_team'] if game['home_score'] > game['away_score'] else game['away_team']
                result['correct'] = result['predicted_winner'] == result['actual_winner']
            else:
                # Game not started yet - check if it's in progress or scheduled
                # For now, mark as scheduled (live API will provide in_progress status)
                result['status'] = 'scheduled'
            
            predictions.append(result)
            
            # Print summary
            winner = result['predicted_winner']
            conf = result['confidence'] * 100
            print(f"   > Prediction: {winner} wins ({conf:.1f}% confidence)")
            
            if 'correct' in result:
                status = "[CORRECT]" if result['correct'] else "[WRONG]"
                print(f"   {status} (Actual: {result['actual_winner']} won)")
            
            print()
        
        # Summary
        if any('correct' in p for p in predictions):
            correct = sum(1 for p in predictions if p.get('correct', False))
            total = sum(1 for p in predictions if 'correct' in p)
            accuracy = (correct / total * 100) if total > 0 else 0
            print(f"{'='*80}")
            print(f"ACCURACY: {correct}/{total} correct ({accuracy:.1f}%)")
            print(f"{'='*80}\n")
        
        return predictions
    
    def predict_upcoming(self):
        """Predict the next upcoming week (games that haven't been played yet)"""
        conn = psycopg2.connect(**self.db_config)
        
        # Find upcoming games based on game_date >= today
        query = """
            SELECT season, week
            FROM hcl.games
            WHERE is_postseason = false
            AND game_date >= CURRENT_DATE
            ORDER BY season ASC, week ASC
            LIMIT 1;
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if len(df) == 0:
            print("[ERROR] No upcoming games found")
            return []
        
        season = int(df.iloc[0]['season'])
        week = int(df.iloc[0]['week'])
        
        print(f"📅 Predicting upcoming games: Season {season}, Week {week}")
        
        # Get all predictions for the week
        all_predictions = self.predict_week(season, week)
        
        # Return ALL games (scheduled, in-progress, and completed)
        # The frontend will handle filtering/display based on game status
        print(f"[OK] Generated {len(all_predictions)} predictions (all games for the week)")
        
        return all_predictions


def main():
    parser = argparse.ArgumentParser(description='Predict NFL games for a given week')
    parser.add_argument('--season', type=int, help='Season year (e.g., 2025)')
    parser.add_argument('--week', type=int, help='Week number (1-18)')
    parser.add_argument('--upcoming', action='store_true', help='Predict next upcoming week')
    
    args = parser.parse_args()
    
    predictor = WeeklyPredictor()
    
    if args.upcoming:
        predictions = predictor.predict_upcoming()
    elif args.season and args.week:
        predictions = predictor.predict_week(args.season, args.week)
    else:
        print("Usage:")
        print("  python ml/predict_week.py --season 2025 --week 10")
        print("  python ml/predict_week.py --upcoming")
        return
    
    # Save predictions to file
    if predictions:
        output_file = f"ml/predictions_week_{predictions[0].get('week', 'upcoming')}.json"
        import json
        with open(output_file, 'w') as f:
            json.dump(predictions, f, indent=2, default=str)
        print(f"[SAVED] Predictions saved to {output_file}")


if __name__ == "__main__":
    main()
