"""
ML Prediction API Routes

Flask API endpoints for NFL game predictions using the trained neural network.

Sprint 9: Machine Learning Predictions
Date: November 6, 2025
"""

from flask import Blueprint, jsonify, request
import sys
import os

# Add ml directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))
from predict_week import WeeklyPredictor

# Create Blueprint
ml_api = Blueprint('ml_api', __name__)

# Initialize predictor (singleton)
predictor = None

def get_predictor():
    """Lazy load the predictor"""
    global predictor
    if predictor is None:
        predictor = WeeklyPredictor()
    return predictor


@ml_api.route('/api/ml/predict-week/<int:season>/<int:week>', methods=['GET'])
def predict_week(season, week):
    """
    Predict all games for a given week
    
    Example: GET /api/ml/predict-week/2025/10
    
    Returns:
    {
        "season": 2025,
        "week": 10,
        "total_games": 14,
        "predictions": [
            {
                "game_id": "...",
                "home_team": "DEN",
                "away_team": "LV",
                "predicted_winner": "DEN",
                "home_win_prob": 0.74,
                "away_win_prob": 0.26,
                "confidence": 0.74,
                ...
            },
            ...
        ]
    }
    """
    try:
        pred = get_predictor()
        predictions = pred.predict_week(season, week)
        
        return jsonify({
            'season': season,
            'week': week,
            'total_games': len(predictions),
            'predictions': predictions,
            'model': 'NFL Neural Network V2',
            'accuracy': '65.55% on 2025 test set'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate predictions'
        }), 500


@ml_api.route('/api/ml/predict-upcoming', methods=['GET'])
def predict_upcoming():
    """
    Predict the next upcoming week
    
    Example: GET /api/ml/predict-upcoming
    
    Returns: Same format as predict-week
    """
    try:
        pred = get_predictor()
        predictions = pred.predict_upcoming()
        
        if not predictions:
            return jsonify({
                'message': 'No upcoming games found',
                'predictions': []
            })
        
        # Extract season/week from first prediction
        season = predictions[0].get('season', None)
        week = predictions[0].get('week', None)
        
        return jsonify({
            'season': season,
            'week': week,
            'total_games': len(predictions),
            'predictions': predictions,
            'model': 'NFL Neural Network V2',
            'accuracy': '65.55% on 2025 test set'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate predictions'
        }), 500


@ml_api.route('/api/ml/predict-game', methods=['POST'])
def predict_game():
    """
    Predict a single game matchup
    
    Example POST body:
    {
        "season": 2025,
        "week": 10,
        "home_team": "KC",
        "away_team": "BUF",
        "spread_line": -3.5,
        "total_line": 47.5
    }
    
    Returns:
    {
        "home_team": "KC",
        "away_team": "BUF",
        "predicted_winner": "KC",
        "home_win_prob": 0.68,
        "away_win_prob": 0.32,
        "confidence": 0.68,
        "key_factors": { ... }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['season', 'week', 'home_team', 'away_team']
        for field in required:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        pred = get_predictor()
        
        result = pred.predict_game(
            season=data['season'],
            week=data['week'],
            home_team=data['home_team'],
            away_team=data['away_team'],
            spread_line=data.get('spread_line'),
            total_line=data.get('total_line')
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate prediction'
        }), 500


@ml_api.route('/api/ml/model-info', methods=['GET'])
def model_info():
    """
    Get information about the ML model
    
    Example: GET /api/ml/model-info
    
    Returns model architecture, training data, and performance metrics
    """
    return jsonify({
        'model_name': 'NFL Neural Network V2',
        'version': '2.0',
        'architecture': {
            'type': 'Multi-Layer Perceptron (Neural Network)',
            'layers': [
                {'name': 'Input', 'neurons': 41, 'description': 'Rolling features from previous games'},
                {'name': 'Hidden 1', 'neurons': 128, 'activation': 'ReLU'},
                {'name': 'Hidden 2', 'neurons': 64, 'activation': 'ReLU'},
                {'name': 'Hidden 3', 'neurons': 32, 'activation': 'ReLU'},
                {'name': 'Output', 'neurons': 1, 'activation': 'Sigmoid', 'description': 'Home team win probability'}
            ],
            'total_parameters': 20097
        },
        'training_data': {
            'date_range': '1999-2023',
            'total_games': 7126,
            'training_games': 5477,
            'validation_games': 269,
            'test_games': 119,
            'features': 41
        },
        'performance': {
            'training_accuracy': 'Converged',
            'validation_accuracy': 0.6803,
            'test_accuracy': 0.6555,
            'baseline_comparison': {
                'vegas_spreads': '~52-55%',
                'best_public_models': '~57-60%',
                'this_model': '65.55%'
            }
        },
        'features': {
            'categories': [
                'Season statistics (PPG, EPA, success rate, yards)',
                'Recent form (last 3 and 5 games)',
                'Advanced metrics (CPOE, pass EPA, rush EPA)',
                'Matchup differentials',
                'Vegas betting lines (spread, total)',
                'Context (season, week)'
            ],
            'key_insight': 'Uses ONLY pre-game information (rolling stats from previous games, never stats from the game being predicted)'
        },
        'methodology': {
            'data_leakage_fix': 'V1 had 100% accuracy (data leakage). V2 uses only previous game stats.',
            'time_based_split': 'Train on 1999-2023, validate on 2024, test on 2025',
            'sample_weighting': 'Recent years weighted more heavily',
            'early_stopping': 'Prevents overfitting'
        },
        'updated': '2025-11-06',
        'status': 'Production Ready'
    })


@ml_api.route('/api/ml/explain', methods=['GET'])
def explain_methodology():
    """
    Explain how predictions are made (for frontend display)
    
    Example: GET /api/ml/explain
    """
    return jsonify({
        'title': 'How Our ML Predictions Work',
        'sections': [
            {
                'heading': '1. Training Data',
                'content': 'The model learned from 26 years of NFL games (1999-2023), analyzing 5,477 games with full EPA and advanced statistics.',
                'icon': 'database'
            },
            {
                'heading': '2. Rolling Features',
                'content': 'For each matchup, we compute team statistics from ALL PREVIOUS games in the season (never using stats from the game being predicted). This includes season averages, recent form (last 3 & 5 games), and opponent trends.',
                'icon': 'trending'
            },
            {
                'heading': '3. Neural Network Architecture',
                'content': '3-layer deep learning model with 20,097 learnable parameters. The network identifies complex patterns in team performance, matchup advantages, and situational factors.',
                'icon': 'brain'
            },
            {
                'heading': '4. Key Factors Analyzed',
                'content': [
                    'Expected Points Added (EPA) - Most predictive stat',
                    'Success rate and yards per play',
                    'Pass vs Rush efficiency (CPOE, pass EPA, rush EPA)',
                    'Recent momentum (last 3-5 games)',
                    'Matchup advantages (EPA differential)',
                    'Vegas lines (spread and total) - market wisdom'
                ],
                'icon': 'analytics'
            },
            {
                'heading': '5. Performance',
                'content': '65.55% accuracy on 2025 games (held-out test set). This beats Vegas spreads (~52-55%) and matches the best public NFL prediction models (~57-60%). The model shows realistic, not perfect, predictions.',
                'icon': 'checkmark'
            },
            {
                'heading': '6. Confidence Scores',
                'content': 'Each prediction includes a confidence percentage (50-100%). Higher confidence means the model sees a clearer advantage. Close matchups (~50-55%) are genuine toss-ups.',
                'icon': 'percent'
            }
        ],
        'disclaimer': 'These are statistical predictions based on historical patterns, not guarantees. NFL games have inherent uncertainty due to injuries, weather, turnovers, and coaching decisions not captured in data.',
        'academic_context': 'Built for IS330 coursework to demonstrate understanding of machine learning, feature engineering, and model evaluation. This project showcases proper ML methodology including data leakage prevention and time-based validation.'
    })
