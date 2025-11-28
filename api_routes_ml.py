"""
ML Prediction API Routes

Flask API endpoints for NFL game predictions using the trained neural network.

Sprint 9: Machine Learning Predictions
Date: November 6, 2025
"""

from flask import Blueprint, jsonify, request
import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor

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
    Predict the next upcoming week and save to tracking table
    
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
        
        # Automatically save predictions to tracking table
        try:
            conn = psycopg2.connect(**pred.db_config)
            cur = conn.cursor()
            
            saved_count = 0
            for p in predictions:
                insert_sql = """
                    INSERT INTO hcl.ml_predictions (
                        game_id, season, week, home_team, away_team, game_date,
                        predicted_winner, win_confidence, home_win_prob, away_win_prob,
                        predicted_home_score, predicted_away_score, predicted_margin, ai_spread,
                        vegas_spread, vegas_total
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (game_id) DO UPDATE SET
                        predicted_winner = EXCLUDED.predicted_winner,
                        win_confidence = EXCLUDED.win_confidence,
                        home_win_prob = EXCLUDED.home_win_prob,
                        away_win_prob = EXCLUDED.away_win_prob,
                        predicted_home_score = EXCLUDED.predicted_home_score,
                        predicted_away_score = EXCLUDED.predicted_away_score,
                        predicted_margin = EXCLUDED.predicted_margin,
                        ai_spread = EXCLUDED.ai_spread,
                        vegas_spread = EXCLUDED.vegas_spread,
                        vegas_total = EXCLUDED.vegas_total,
                        predicted_at = NOW()
                """
                
                cur.execute(insert_sql, (
                    p.get('game_id'),
                    p.get('season'),
                    p.get('week'),
                    p.get('home_team'),
                    p.get('away_team'),
                    p.get('game_date'),
                    p.get('predicted_winner'),
                    p.get('confidence'),
                    p.get('home_win_prob'),
                    p.get('away_win_prob'),
                    p.get('predicted_home_score'),
                    p.get('predicted_away_score'),
                    p.get('predicted_margin'),
                    p.get('ai_spread'),
                    p.get('vegas_spread'),
                    p.get('total_line')
                ))
                saved_count += 1
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Auto-saved {saved_count} predictions to tracking table")
            
        except Exception as save_err:
            print(f"⚠️ Failed to save predictions: {save_err}")
            # Don't fail the whole request if save fails
        
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


@ml_api.route('/api/predictions/current-week', methods=['GET'])
def get_current_week_predictions():
    """
    Get simplified predictions for Homepage widget
    Returns upcoming games with AI vs Vegas comparison
    """
    try:
        pred = get_predictor()
        predictions = pred.predict_upcoming()
        
        if not predictions:
            return jsonify({
                'success': True,
                'predictions': []
            })
        
        # Simplify predictions for homepage display
        simplified = []
        for p in predictions:
            simplified.append({
                'home_team': p.get('home_team'),
                'away_team': p.get('away_team'),
                'game_date': p.get('game_date'),
                'ai_spread': p.get('ai_spread'),
                'vegas_spread': p.get('vegas_spread'),
                'ai_total': round(p.get('predicted_home_score', 0) + p.get('predicted_away_score', 0), 1),
                'vegas_total': p.get('total_line'),
                'predicted_winner': p.get('predicted_winner')
            })
        
        return jsonify({
            'success': True,
            'week': predictions[0].get('week') if predictions else None,
            'predictions': simplified
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'predictions': []
        })


@ml_api.route('/api/ml/model-performance', methods=['GET'])
def get_model_performance():
    """
    Calculate and return model performance statistics
    Tracks both win/loss classifier and point spread regressor accuracy
    
    Query params:
        season: Filter by season (default: 2025)
        week: Filter by specific week (optional)
    """
    try:
        season = request.args.get('season', default=2025, type=int)
        week = request.args.get('week', type=int)
        
        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build WHERE clause
        where_conditions = [f"g.season = {season}"]
        if week:
            where_conditions.append(f"g.week = {week}")
        where_clause = " AND " + " AND ".join(where_conditions)
        
        # Get completed games with predictions
        query = f"""
            WITH predictions AS (
                SELECT 
                    g.game_id,
                    g.home_team,
                    g.away_team,
                    g.home_score,
                    g.away_score,
                    g.week,
                    CASE WHEN g.home_score > g.away_score THEN g.home_team
                         WHEN g.away_score > g.home_score THEN g.away_team
                         ELSE 'TIE' END as actual_winner,
                    g.home_score - g.away_score as actual_margin,
                    g.spread_line as vegas_spread
                FROM hcl.games g
                WHERE g.home_score IS NOT NULL 
                  AND g.away_score IS NOT NULL
                  {where_clause}
            )
            SELECT * FROM predictions
            ORDER BY week DESC
        """
        
        cur.execute(query)
        games = cur.fetchall()
        
        if not games:
            return jsonify({
                'success': True,
                'season': season,
                'week': week,
                'total_games': 0,
                'classification': {'accuracy': 0, 'correct': 0, 'total': 0},
                'regression': {'mae': 0, 'correct_covers': 0, 'total': 0}
            })
        
        # Get predictions for these games
        pred = get_predictor()
        classification_correct = 0
        regression_errors = []
        ai_covers = 0
        vegas_covers = 0
        
        for game in games:
            # Generate prediction for this game
            prediction = pred.predict_game(
                season,
                game['week'],
                game['home_team'],
                game['away_team'],
                game['vegas_spread'],
                None
            )
            
            # Check classification accuracy (did we pick the right winner?)
            if prediction['predicted_winner'] == game['actual_winner']:
                classification_correct += 1
            
            # Check regression accuracy (how close was our spread?)
            predicted_margin = prediction['predicted_margin']
            actual_margin = game['actual_margin']
            regression_errors.append(abs(predicted_margin - actual_margin))
            
            # Check spread betting performance
            ai_spread = prediction['ai_spread']
            vegas_spread = game['vegas_spread']
            
            # Did AI spread beat the actual result better than Vegas?
            if vegas_spread:
                ai_diff = abs(ai_spread - (-actual_margin))  # AI spread is negative of margin
                vegas_diff = abs(vegas_spread - (-actual_margin))
                
                if ai_diff < vegas_diff:
                    ai_covers += 1
                elif vegas_diff < ai_diff:
                    vegas_covers += 1
        
        # Calculate statistics
        total_games = len(games)
        mae = sum(regression_errors) / total_games if regression_errors else 0
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'season': season,
            'week': week,
            'total_games': total_games,
            'classification': {
                'correct': classification_correct,
                'total': total_games,
                'accuracy': round((classification_correct / total_games * 100), 2) if total_games > 0 else 0
            },
            'regression': {
                'mae': round(mae, 2),
                'ai_covers': ai_covers,
                'vegas_covers': vegas_covers,
                'total': total_games
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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


@ml_api.route('/api/ml/save-predictions', methods=['POST'])
def save_predictions():
    """
    Save predictions to tracking table for future performance analysis
    Call this after generating predictions for upcoming games
    """
    try:
        data = request.get_json()
        predictions = data.get('predictions', [])
        
        if not predictions:
            return jsonify({'success': False, 'error': 'No predictions provided'}), 400
        
        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor()
        
        saved_count = 0
        for pred in predictions:
            insert_sql = """
                INSERT INTO hcl.ml_predictions (
                    game_id, season, week, home_team, away_team, game_date,
                    predicted_winner, win_confidence, home_win_prob, away_win_prob,
                    predicted_home_score, predicted_away_score, predicted_margin, ai_spread,
                    vegas_spread, vegas_total
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (game_id) DO UPDATE SET
                    predicted_winner = EXCLUDED.predicted_winner,
                    win_confidence = EXCLUDED.win_confidence,
                    home_win_prob = EXCLUDED.home_win_prob,
                    away_win_prob = EXCLUDED.away_win_prob,
                    predicted_home_score = EXCLUDED.predicted_home_score,
                    predicted_away_score = EXCLUDED.predicted_away_score,
                    predicted_margin = EXCLUDED.predicted_margin,
                    ai_spread = EXCLUDED.ai_spread,
                    vegas_spread = EXCLUDED.vegas_spread,
                    vegas_total = EXCLUDED.vegas_total,
                    predicted_at = NOW()
            """
            
            cur.execute(insert_sql, (
                pred.get('game_id'),
                pred.get('season'),
                pred.get('week'),
                pred.get('home_team'),
                pred.get('away_team'),
                pred.get('game_date'),
                pred.get('predicted_winner'),
                pred.get('confidence'),
                pred.get('home_win_prob'),
                pred.get('away_win_prob'),
                pred.get('predicted_home_score'),
                pred.get('predicted_away_score'),
                pred.get('predicted_margin'),
                pred.get('ai_spread'),
                pred.get('vegas_spread'),
                pred.get('total_line')
            ))
            saved_count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'saved': saved_count,
            'message': f'Saved {saved_count} predictions to tracking table'
        })
        
    except Exception as e:
        return jsonify({'success': True, 'error': str(e)}), 500


@ml_api.route('/api/ml/season-ai-vs-vegas/<int:season>', methods=['GET'])
def get_season_ai_vs_vegas(season):
    """
    Get season-to-date AI vs Vegas spread performance
    Shows how many games AI beat Vegas on spread coverage
    """
    try:
        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor()
        
        # Get all completed games with predictions for the season
        cur.execute("""
            SELECT 
                p.game_id,
                p.ai_spread,
                p.vegas_spread,
                g.home_score,
                g.away_score
            FROM hcl.ml_predictions p
            JOIN hcl.games g ON p.game_id = g.game_id
            WHERE p.season = %s
              AND g.home_score IS NOT NULL
              AND g.away_score IS NOT NULL
              AND p.ai_spread IS NOT NULL
              AND p.vegas_spread IS NOT NULL
            ORDER BY g.week, g.game_date
        """, (season,))
        
        games = cur.fetchall()
        
        ai_wins = 0
        vegas_wins = 0
        ties = 0
        total = 0
        
        for game_id, ai_spread, vegas_spread, home_score, away_score in games:
            actual_margin = home_score - away_score
            total += 1
            
            # Check AI spread coverage
            ai_result = actual_margin + ai_spread
            ai_covered = False
            if ai_result != 0:
                if ai_spread < 0:
                    ai_covered = actual_margin > abs(ai_spread)
                else:
                    ai_covered = actual_margin < -abs(ai_spread)
            
            # Check Vegas spread coverage
            vegas_result = actual_margin + vegas_spread
            vegas_covered = False
            if vegas_result != 0:
                if vegas_spread < 0:
                    vegas_covered = actual_margin > abs(vegas_spread)
                else:
                    vegas_covered = actual_margin < -abs(vegas_spread)
            
            # Compare
            if ai_covered and not vegas_covered:
                ai_wins += 1
            elif not ai_covered and vegas_covered:
                vegas_wins += 1
            elif ai_covered == vegas_covered:
                ties += 1
        
        ai_pct = (ai_wins / total * 100) if total > 0 else 0
        vegas_pct = (vegas_wins / total * 100) if total > 0 else 0
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'season': season,
            'ai_wins': ai_wins,
            'vegas_wins': vegas_wins,
            'ties': ties,
            'total_games': total,
            'ai_percentage': round(ai_pct, 1),
            'vegas_percentage': round(vegas_pct, 1)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ml_api.route('/api/ml/update-results', methods=['POST'])
def update_results():
    """
    Update predictions with actual results after games complete
    Automatically called when new game results are loaded
    """
    try:
        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor()
        
        # Update all predictions that have results but haven't been scored yet
        update_sql = """
            UPDATE hcl.ml_predictions mp
            SET 
                actual_winner = CASE 
                    WHEN g.home_score > g.away_score THEN g.home_team
                    WHEN g.away_score > g.home_score THEN g.away_team
                    ELSE 'TIE'
                END,
                actual_home_score = g.home_score,
                actual_away_score = g.away_score,
                actual_margin = g.home_score - g.away_score,
                win_prediction_correct = CASE 
                    WHEN g.home_score > g.away_score THEN mp.predicted_winner = g.home_team
                    WHEN g.away_score > g.home_score THEN mp.predicted_winner = g.away_team
                    ELSE FALSE
                END,
                score_prediction_error_home = ABS(mp.predicted_home_score - g.home_score),
                score_prediction_error_away = ABS(mp.predicted_away_score - g.away_score),
                margin_prediction_error = ABS(mp.predicted_margin - (g.home_score - g.away_score)),
                result_recorded_at = NOW()
            FROM hcl.games g
            WHERE mp.game_id = g.game_id
              AND g.home_score IS NOT NULL
              AND g.away_score IS NOT NULL
              AND mp.result_recorded_at IS NULL
        """
        
        cur.execute(update_sql)
        updated_count = cur.rowcount
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'updated': updated_count,
            'message': f'Updated {updated_count} predictions with actual results'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ml_api.route('/api/ml/performance-stats', methods=['GET'])
def get_performance_stats():
    """
    Get model performance statistics from tracking table
    Returns win/loss accuracy and spread prediction accuracy
    
    Query params:
        season: Filter by season (default: 2025)
        week: Filter by week (optional)
    """
    try:
        season = request.args.get('season', default=2025, type=int)
        week = request.args.get('week', type=int)
        
        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build WHERE clause
        where_conditions = [f"season = {season}", "result_recorded_at IS NOT NULL"]
        if week:
            where_conditions.append(f"week = {week}")
        where_clause = " AND ".join(where_conditions)
        
        # Get statistics
        stats_sql = f"""
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct_predictions,
                CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,2)) as win_accuracy,
                CAST(AVG(margin_prediction_error) AS NUMERIC(10,2)) as avg_margin_error,
                CAST(AVG(score_prediction_error_home) AS NUMERIC(10,2)) as avg_home_score_error,
                CAST(AVG(score_prediction_error_away) AS NUMERIC(10,2)) as avg_away_score_error,
                MIN(week) as first_week,
                MAX(week) as latest_week
            FROM hcl.ml_predictions
            WHERE {where_clause}
        """
        
        cur.execute(stats_sql)
        stats = cur.fetchone()
        
        # Get week-by-week breakdown
        weekly_sql = f"""
            SELECT 
                week,
                COUNT(*) as games,
                SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct,
                CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)) as accuracy,
                CAST(AVG(margin_prediction_error) AS NUMERIC(10,1)) as mae
            FROM hcl.ml_predictions
            WHERE {where_clause}
            GROUP BY week
            ORDER BY week DESC
        """
        
        cur.execute(weekly_sql)
        weekly_stats = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'season': season,
            'overall': dict(stats) if stats else {},
            'by_week': [dict(w) for w in weekly_stats]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
