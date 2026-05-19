"""
ML Prediction API Routes

Flask API endpoints for NFL game predictions using the trained neural network.

Sprint 9: Machine Learning Predictions
Sprint 10: Elo Rating System Integration
Date: December 19, 2025
"""

from flask import Blueprint, jsonify, request
import sys
import os
import io
import contextlib
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add ml directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))
from predict_week import WeeklyPredictor
from predict_elo import EloPredictionSystem
from elo_tracker import EloTracker

# Create Blueprint
ml_api = Blueprint('ml_api', __name__)

# Initialize predictors (singletons)
predictor = None
elo_predictor = None
elo_tracker = None

def get_predictor():
    """Lazy load the XGBoost predictor"""
    global predictor
    if predictor is None:
        predictor = WeeklyPredictor()
    return predictor

def get_elo_predictor():
    """Lazy load the Elo predictor"""
    global elo_predictor
    if elo_predictor is None:
        elo_predictor = EloPredictionSystem()
    return elo_predictor

def get_elo_tracker():
    """Lazy load the Elo tracker"""
    global elo_tracker
    if elo_tracker is None:
        elo_tracker = EloTracker()
        elo_tracker.load_current_ratings()
    return elo_tracker


def get_latest_completed_season():
    """Return the latest season with completed games, or current year on failure."""
    fallback_season = datetime.now().year
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(MAX(season), %s)
            FROM hcl.games
            WHERE home_score IS NOT NULL
              AND away_score IS NOT NULL
            """,
            (fallback_season,)
        )
        return cur.fetchone()[0] or fallback_season
    except Exception:
        return fallback_season
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def table_exists(conn, schema_name, table_name):
    """Return True if the given table exists."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name = %s
        )
        """,
        (schema_name, table_name)
    )
    exists = bool(cur.fetchone()[0])
    cur.close()
    return exists


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
        season: Filter by season (default: latest completed season)
        week: Filter by specific week (optional)
    """
    conn = None
    cur = None
    try:
        season = request.args.get('season', type=int)
        week = request.args.get('week', type=int)
        
        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if season is None:
            fallback_season = get_latest_completed_season()
            cur.execute(
                """
                SELECT COALESCE(MAX(season), %s) AS season
                FROM hcl.ml_predictions
                WHERE result_recorded_at IS NOT NULL
                """,
                (fallback_season,)
            )
            season_row = cur.fetchone() or {}
            season = int(season_row.get('season') or fallback_season)

        # Primary path: use recorded prediction outcomes from tracking table for stable, fast responses.
        tracking_where = ["season = %s", "result_recorded_at IS NOT NULL"]
        tracking_params = [season]
        if week is not None:
            tracking_where.append("week = %s")
            tracking_params.append(week)

        tracking_sql = f"""
            SELECT
                COUNT(*) as total_games,
                COALESCE(SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END), 0) as correct_predictions,
                COALESCE(CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,2)), 0) as win_accuracy,
                COALESCE(CAST(AVG(margin_prediction_error) AS NUMERIC(10,2)), 0) as avg_margin_error,
                COALESCE(
                    SUM(
                        CASE
                            WHEN actual_margin IS NULL OR ai_spread IS NULL OR vegas_spread IS NULL THEN 0
                            WHEN ABS(ai_spread - (-actual_margin)) < ABS(vegas_spread - (-actual_margin)) THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) as ai_covers,
                COALESCE(
                    SUM(
                        CASE
                            WHEN actual_margin IS NULL OR ai_spread IS NULL OR vegas_spread IS NULL THEN 0
                            WHEN ABS(vegas_spread - (-actual_margin)) < ABS(ai_spread - (-actual_margin)) THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) as vegas_covers
            FROM hcl.ml_predictions
            WHERE {' AND '.join(tracking_where)}
        """

        cur.execute(tracking_sql, tuple(tracking_params))
        tracked = cur.fetchone() or {}

        tracked_total = int(tracked.get('total_games') or 0)
        if tracked_total > 0:
            tracked_correct = int(tracked.get('correct_predictions') or 0)
            tracked_accuracy = float(tracked.get('win_accuracy') or 0)
            tracked_mae = float(tracked.get('avg_margin_error') or 0)
            tracked_ai_covers = int(tracked.get('ai_covers') or 0)
            tracked_vegas_covers = int(tracked.get('vegas_covers') or 0)

            return jsonify({
                'success': True,
                'season': season,
                'week': week,
                'total_games': tracked_total,
                'classification': {
                    'correct': tracked_correct,
                    'total': tracked_total,
                    'accuracy': round(tracked_accuracy, 2)
                },
                'regression': {
                    'mae': round(tracked_mae, 2),
                    'ai_covers': tracked_ai_covers,
                    'vegas_covers': tracked_vegas_covers,
                    'total': tracked_total
                }
            })

        # Fallback path: compute directly from completed games when tracked rows are unavailable.
        game_where = ["g.home_score IS NOT NULL", "g.away_score IS NOT NULL", "g.season = %s"]
        game_params = [season]
        if week is not None:
            game_where.append("g.week = %s")
            game_params.append(week)

        game_sql = f"""
            SELECT
                g.game_id,
                g.home_team,
                g.away_team,
                g.home_score,
                g.away_score,
                g.week,
                CASE
                    WHEN g.home_score > g.away_score THEN g.home_team
                    WHEN g.away_score > g.home_score THEN g.away_team
                    ELSE 'TIE'
                END as actual_winner,
                g.home_score - g.away_score as actual_margin,
                g.spread_line as vegas_spread
            FROM hcl.games g
            WHERE {' AND '.join(game_where)}
            ORDER BY g.week DESC
        """

        cur.execute(game_sql, tuple(game_params))
        games = cur.fetchall()

        if not games:
            return jsonify({
                'success': True,
                'season': season,
                'week': week,
                'total_games': 0,
                'classification': {'accuracy': 0, 'correct': 0, 'total': 0},
                'regression': {'mae': 0, 'ai_covers': 0, 'vegas_covers': 0, 'total': 0}
            })

        pred = get_predictor()
        classification_correct = 0
        regression_errors = []
        ai_covers = 0
        vegas_covers = 0

        for game in games:
            prediction = pred.predict_game(
                season,
                game['week'],
                game['home_team'],
                game['away_team'],
                game['vegas_spread'],
                None
            )

            if prediction.get('predicted_winner') == game['actual_winner']:
                classification_correct += 1

            predicted_margin = prediction.get('predicted_margin')
            actual_margin = game['actual_margin']
            if predicted_margin is not None and actual_margin is not None:
                regression_errors.append(abs(predicted_margin - actual_margin))

            ai_spread = prediction.get('ai_spread')
            vegas_spread = game['vegas_spread']
            if ai_spread is not None and vegas_spread is not None and actual_margin is not None:
                ai_diff = abs(ai_spread - (-actual_margin))
                vegas_diff = abs(vegas_spread - (-actual_margin))
                if ai_diff < vegas_diff:
                    ai_covers += 1
                elif vegas_diff < ai_diff:
                    vegas_covers += 1

        total_games = len(games)
        mae = sum(regression_errors) / len(regression_errors) if regression_errors else 0

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
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


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
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor()

        # Update all XGBoost predictions that have results but haven't been scored yet
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

        # Keep Elo tracking rows synchronized with game outcomes.
        updated_elo_count = 0
        if table_exists(conn, 'hcl', 'ml_predictions_elo'):
            update_elo_sql = """
                UPDATE hcl.ml_predictions_elo e
                SET
                    actual_winner = CASE
                        WHEN g.home_score > g.away_score THEN g.home_team
                        WHEN g.away_score > g.home_score THEN g.away_team
                        ELSE 'TIE'
                    END,
                    actual_spread = (g.home_score - g.away_score),
                    prediction_correct = CASE
                        WHEN g.home_score > g.away_score THEN e.predicted_winner = g.home_team
                        WHEN g.away_score > g.home_score THEN e.predicted_winner = g.away_team
                        ELSE FALSE
                    END,
                    spread_error = CASE
                        WHEN e.elo_spread IS NULL THEN NULL
                        ELSE ABS(e.elo_spread - (g.home_score - g.away_score))
                    END
                FROM hcl.games g
                WHERE e.game_id = g.game_id
                  AND g.home_score IS NOT NULL
                  AND g.away_score IS NOT NULL
                  AND (
                        e.actual_winner IS NULL
                     OR e.actual_spread IS NULL
                     OR e.prediction_correct IS NULL
                     OR e.spread_error IS NULL
                  )
            """

            cur.execute(update_elo_sql)
            updated_elo_count = cur.rowcount

        conn.commit()

        return jsonify({
            'success': True,
            'updated': updated_count,
            'updated_elo': updated_elo_count,
            'message': f'Updated {updated_count} XGBoost and {updated_elo_count} Elo predictions with actual results'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@ml_api.route('/api/ml/performance-stats', methods=['GET'])
def get_performance_stats():
    """
    Get model performance statistics from tracking table
    Returns win/loss accuracy and spread prediction accuracy
    
    Query params:
        season: Filter by season (default: latest completed season)
        week: Filter by week (optional)
    """
    try:
        season = request.args.get('season', type=int)
        if season is None:
            season = get_latest_completed_season()
        week = request.args.get('week', type=int)

        conn = psycopg2.connect(**get_predictor().db_config)
        elo_table_ready = table_exists(conn, 'hcl', 'ml_predictions_elo')
        cur = conn.cursor(cursor_factory=RealDictCursor)

        def _int(value):
            return int(value or 0)

        def _float(value):
            return float(value or 0.0)

        def _pct(numerator, denominator):
            if not denominator:
                return 0.0
            return round((numerator / denominator) * 100.0, 2)

        game_where = [
            "season = %s",
            "home_score IS NOT NULL",
            "away_score IS NOT NULL",
            "COALESCE(is_postseason, FALSE) = FALSE"
        ]
        game_params = [season]
        if week is not None:
            game_where.append("week = %s")
            game_params.append(week)

        cur.execute(
            f"""
            SELECT
                COUNT(*) AS completed_games,
                MIN(week) AS first_week,
                MAX(week) AS latest_week
            FROM hcl.games
            WHERE {' AND '.join(game_where)}
            """,
            tuple(game_params)
        )
        games_summary = cur.fetchone() or {}
        completed_games = _int(games_summary.get('completed_games'))

        xgb_where = ["season = %s"]
        xgb_params = [season]
        if week is not None:
            xgb_where.append("week = %s")
            xgb_params.append(week)

        cur.execute(
            f"""
            SELECT COUNT(*) AS predicted_games
            FROM hcl.ml_predictions
            WHERE {' AND '.join(xgb_where)}
            """,
            tuple(xgb_params)
        )
        xgb_predicted = _int((cur.fetchone() or {}).get('predicted_games'))

        xgb_scored_where = list(xgb_where) + ["result_recorded_at IS NOT NULL"]
        cur.execute(
            f"""
            SELECT
                COUNT(*) AS scored_games,
                COALESCE(SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct_predictions,
                COALESCE(CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,2)), 0) AS win_accuracy,
                COALESCE(CAST(AVG(margin_prediction_error) AS NUMERIC(10,2)), 0) AS avg_margin_error,
                MIN(week) AS first_week,
                MAX(week) AS latest_week
            FROM hcl.ml_predictions
            WHERE {' AND '.join(xgb_scored_where)}
            """,
            tuple(xgb_params)
        )
        xgb_summary = cur.fetchone() or {}

        cur.execute(
            f"""
            SELECT
                week,
                COUNT(*) AS scored_games,
                COALESCE(SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct_predictions,
                COALESCE(CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)), 0) AS win_accuracy,
                COALESCE(CAST(AVG(margin_prediction_error) AS NUMERIC(10,1)), 0) AS avg_margin_error
            FROM hcl.ml_predictions
            WHERE {' AND '.join(xgb_scored_where)}
            GROUP BY week
            ORDER BY week ASC
            """,
            tuple(xgb_params)
        )
        xgb_week_rows = cur.fetchall() or []

        elo_summary = {
            'predicted_games': 0,
            'scored_games': 0,
            'correct_predictions': 0,
            'win_accuracy': 0,
            'avg_margin_error': 0,
            'first_week': None,
            'latest_week': None
        }
        elo_week_rows = []

        if elo_table_ready:
            elo_where = ["e.season = %s"]
            elo_params = [season]
            if week is not None:
                elo_where.append("e.week = %s")
                elo_params.append(week)

            cur.execute(
                f"""
                SELECT COUNT(*) AS predicted_games
                FROM hcl.ml_predictions_elo e
                WHERE {' AND '.join(elo_where)}
                """,
                tuple(elo_params)
            )
            elo_summary['predicted_games'] = _int((cur.fetchone() or {}).get('predicted_games'))

            elo_scored_where = list(elo_where) + [
                "e.predicted_winner IS NOT NULL",
                "g.home_score IS NOT NULL",
                "g.away_score IS NOT NULL",
                "COALESCE(g.is_postseason, FALSE) = FALSE"
            ]

            cur.execute(
                f"""
                SELECT
                    COUNT(*) AS scored_games,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN (g.home_score > g.away_score AND e.predicted_winner = g.home_team)
                                  OR (g.away_score > g.home_score AND e.predicted_winner = g.away_team)
                                THEN 1 ELSE 0
                            END
                        ),
                        0
                    ) AS correct_predictions,
                    COALESCE(
                        CAST(
                            AVG(
                                CASE
                                    WHEN (g.home_score > g.away_score AND e.predicted_winner = g.home_team)
                                      OR (g.away_score > g.home_score AND e.predicted_winner = g.away_team)
                                    THEN 100.0 ELSE 0.0
                                END
                            ) AS NUMERIC(10,2)
                        ),
                        0
                    ) AS win_accuracy,
                    COALESCE(CAST(AVG(ABS(e.elo_spread - (g.home_score - g.away_score))) AS NUMERIC(10,2)), 0) AS avg_margin_error,
                    MIN(e.week) AS first_week,
                    MAX(e.week) AS latest_week
                FROM hcl.ml_predictions_elo e
                JOIN hcl.games g ON g.game_id = e.game_id
                WHERE {' AND '.join(elo_scored_where)}
                """,
                tuple(elo_params)
            )
            elo_scored_summary = cur.fetchone() or {}

            elo_summary.update({
                'scored_games': _int(elo_scored_summary.get('scored_games')),
                'correct_predictions': _int(elo_scored_summary.get('correct_predictions')),
                'win_accuracy': _float(elo_scored_summary.get('win_accuracy')),
                'avg_margin_error': _float(elo_scored_summary.get('avg_margin_error')),
                'first_week': elo_scored_summary.get('first_week'),
                'latest_week': elo_scored_summary.get('latest_week')
            })

            cur.execute(
                f"""
                SELECT
                    e.week,
                    COUNT(*) AS scored_games,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN (g.home_score > g.away_score AND e.predicted_winner = g.home_team)
                                  OR (g.away_score > g.home_score AND e.predicted_winner = g.away_team)
                                THEN 1 ELSE 0
                            END
                        ),
                        0
                    ) AS correct_predictions,
                    COALESCE(
                        CAST(
                            AVG(
                                CASE
                                    WHEN (g.home_score > g.away_score AND e.predicted_winner = g.home_team)
                                      OR (g.away_score > g.home_score AND e.predicted_winner = g.away_team)
                                    THEN 100.0 ELSE 0.0
                                END
                            ) AS NUMERIC(10,1)
                        ),
                        0
                    ) AS win_accuracy,
                    COALESCE(CAST(AVG(ABS(e.elo_spread - (g.home_score - g.away_score))) AS NUMERIC(10,1)), 0) AS avg_margin_error
                FROM hcl.ml_predictions_elo e
                JOIN hcl.games g ON g.game_id = e.game_id
                WHERE {' AND '.join(elo_scored_where)}
                GROUP BY e.week
                ORDER BY e.week ASC
                """,
                tuple(elo_params)
            )
            elo_week_rows = cur.fetchall() or []

        agreement_summary = {
            'both_models_games': 0,
            'agreements': 0,
            'agreement_rate': 0.0,
            'agreed_correct': 0,
            'agreed_accuracy': 0.0,
            'split_games': 0,
            'xgb_head_to_head_wins': 0,
            'elo_head_to_head_wins': 0,
            'head_to_head_ties': 0
        }

        if elo_table_ready:
            agreement_where = [
                "x.season = %s",
                "x.result_recorded_at IS NOT NULL",
                "x.predicted_winner IS NOT NULL",
                "e.predicted_winner IS NOT NULL",
                "g.home_score IS NOT NULL",
                "g.away_score IS NOT NULL",
                "COALESCE(g.is_postseason, FALSE) = FALSE"
            ]
            agreement_params = [season]
            if week is not None:
                agreement_where.append("x.week = %s")
                agreement_params.append(week)

            cur.execute(
                f"""
                SELECT
                    COUNT(*) AS both_models_games,
                    COALESCE(SUM(CASE WHEN x.predicted_winner = e.predicted_winner THEN 1 ELSE 0 END), 0) AS agreements,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN x.predicted_winner = e.predicted_winner
                                 AND (
                                    (g.home_score > g.away_score AND x.predicted_winner = g.home_team)
                                    OR (g.away_score > g.home_score AND x.predicted_winner = g.away_team)
                                 )
                                THEN 1 ELSE 0
                            END
                        ),
                        0
                    ) AS agreed_correct,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN x.predicted_winner <> e.predicted_winner
                                 AND (
                                    (g.home_score > g.away_score AND x.predicted_winner = g.home_team)
                                    OR (g.away_score > g.home_score AND x.predicted_winner = g.away_team)
                                 )
                                 AND NOT (
                                    (g.home_score > g.away_score AND e.predicted_winner = g.home_team)
                                    OR (g.away_score > g.home_score AND e.predicted_winner = g.away_team)
                                 )
                                THEN 1 ELSE 0
                            END
                        ),
                        0
                    ) AS xgb_head_to_head_wins,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN x.predicted_winner <> e.predicted_winner
                                 AND (
                                    (g.home_score > g.away_score AND e.predicted_winner = g.home_team)
                                    OR (g.away_score > g.home_score AND e.predicted_winner = g.away_team)
                                 )
                                 AND NOT (
                                    (g.home_score > g.away_score AND x.predicted_winner = g.home_team)
                                    OR (g.away_score > g.home_score AND x.predicted_winner = g.away_team)
                                 )
                                THEN 1 ELSE 0
                            END
                        ),
                        0
                    ) AS elo_head_to_head_wins
                FROM hcl.ml_predictions x
                JOIN hcl.ml_predictions_elo e ON e.game_id = x.game_id
                JOIN hcl.games g ON g.game_id = x.game_id
                WHERE {' AND '.join(agreement_where)}
                """,
                tuple(agreement_params)
            )
            agreement_raw = cur.fetchone() or {}

            both_models_games = _int(agreement_raw.get('both_models_games'))
            agreements = _int(agreement_raw.get('agreements'))
            agreed_correct = _int(agreement_raw.get('agreed_correct'))
            split_games = max(0, both_models_games - agreements)
            xgb_head_to_head_wins = _int(agreement_raw.get('xgb_head_to_head_wins'))
            elo_head_to_head_wins = _int(agreement_raw.get('elo_head_to_head_wins'))
            head_to_head_ties = max(0, split_games - (xgb_head_to_head_wins + elo_head_to_head_wins))

            agreement_summary.update({
                'both_models_games': both_models_games,
                'agreements': agreements,
                'agreement_rate': _pct(agreements, both_models_games),
                'agreed_correct': agreed_correct,
                'agreed_accuracy': _pct(agreed_correct, agreements),
                'split_games': split_games,
                'xgb_head_to_head_wins': xgb_head_to_head_wins,
                'elo_head_to_head_wins': elo_head_to_head_wins,
                'head_to_head_ties': head_to_head_ties
            })

        cur.execute(
            f"""
            SELECT
                COALESCE(SUM(CASE WHEN spread_line IS NOT NULL AND spread_line <> 0 THEN 1 ELSE 0 END), 0) AS evaluable_games,
                COALESCE(
                    SUM(
                        CASE
                            WHEN spread_line IS NULL OR spread_line = 0 THEN 0
                            WHEN spread_line > 0 AND home_score > away_score THEN 1
                            WHEN spread_line < 0 AND away_score > home_score THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS correct_predictions
            FROM hcl.games
            WHERE {' AND '.join(game_where)}
            """,
            tuple(game_params)
        )
        vegas_raw = cur.fetchone() or {}
        vegas_evaluable = _int(vegas_raw.get('evaluable_games'))
        vegas_correct = _int(vegas_raw.get('correct_predictions'))

        model_breakdown = {
            'xgb': {
                'predicted_games': xgb_predicted,
                'scored_games': _int(xgb_summary.get('scored_games')),
                'correct_predictions': _int(xgb_summary.get('correct_predictions')),
                'win_accuracy': _float(xgb_summary.get('win_accuracy')),
                'avg_margin_error': _float(xgb_summary.get('avg_margin_error')),
                'coverage_pct': _pct(_int(xgb_summary.get('scored_games')), completed_games),
                'predicted_coverage_pct': _pct(xgb_predicted, completed_games),
                'first_week': xgb_summary.get('first_week'),
                'latest_week': xgb_summary.get('latest_week')
            },
            'elo': {
                'predicted_games': _int(elo_summary.get('predicted_games')),
                'scored_games': _int(elo_summary.get('scored_games')),
                'correct_predictions': _int(elo_summary.get('correct_predictions')),
                'win_accuracy': _float(elo_summary.get('win_accuracy')),
                'avg_margin_error': _float(elo_summary.get('avg_margin_error')),
                'coverage_pct': _pct(_int(elo_summary.get('scored_games')), completed_games),
                'predicted_coverage_pct': _pct(_int(elo_summary.get('predicted_games')), completed_games),
                'first_week': elo_summary.get('first_week'),
                'latest_week': elo_summary.get('latest_week')
            },
            'agreement': agreement_summary,
            'vegas': {
                'evaluable_games': vegas_evaluable,
                'correct_predictions': vegas_correct,
                'win_accuracy': _pct(vegas_correct, vegas_evaluable)
            }
        }

        xgb_week_map = {
            _int(row.get('week')): {
                'week': _int(row.get('week')),
                'scored_games': _int(row.get('scored_games')),
                'correct_predictions': _int(row.get('correct_predictions')),
                'win_accuracy': _float(row.get('win_accuracy')),
                'avg_margin_error': _float(row.get('avg_margin_error'))
            }
            for row in xgb_week_rows
        }
        elo_week_map = {
            _int(row.get('week')): {
                'week': _int(row.get('week')),
                'scored_games': _int(row.get('scored_games')),
                'correct_predictions': _int(row.get('correct_predictions')),
                'win_accuracy': _float(row.get('win_accuracy')),
                'avg_margin_error': _float(row.get('avg_margin_error'))
            }
            for row in elo_week_rows
        }

        all_weeks = sorted(set(list(xgb_week_map.keys()) + list(elo_week_map.keys())))
        by_week_models = []
        for week_value in all_weeks:
            by_week_models.append({
                'week': week_value,
                'xgb': xgb_week_map.get(week_value),
                'elo': elo_week_map.get(week_value)
            })

        xgb_scored_games = model_breakdown['xgb']['scored_games']
        elo_scored_games = model_breakdown['elo']['scored_games']
        if xgb_scored_games > 0:
            primary_model = 'xgb'
            primary_summary = model_breakdown['xgb']
            primary_week_map = xgb_week_map
        elif elo_scored_games > 0:
            primary_model = 'elo'
            primary_summary = model_breakdown['elo']
            primary_week_map = elo_week_map
        else:
            primary_model = 'xgb'
            primary_summary = model_breakdown['xgb']
            primary_week_map = {}

        by_week = []
        for week_value in sorted(primary_week_map.keys(), reverse=True):
            row = primary_week_map[week_value]
            by_week.append({
                'week': week_value,
                'games': row['scored_games'],
                'correct': row['correct_predictions'],
                'accuracy': round(row['win_accuracy'], 1),
                'mae': round(row['avg_margin_error'], 1),
                'model': primary_model
            })

        trend_seasons = []
        season_trend = []
        if week is None:
            cur.execute(
                """
                SELECT DISTINCT season
                FROM hcl.games
                WHERE home_score IS NOT NULL
                  AND away_score IS NOT NULL
                                    AND COALESCE(is_postseason, FALSE) = FALSE
                ORDER BY season DESC
                LIMIT 6
                """
            )
            trend_seasons = [_int(row.get('season')) for row in (cur.fetchall() or [])]

            if trend_seasons:
                cur.execute(
                    """
                    SELECT season, COUNT(*) AS completed_games
                    FROM hcl.games
                    WHERE home_score IS NOT NULL
                      AND away_score IS NOT NULL
                                            AND COALESCE(is_postseason, FALSE) = FALSE
                      AND season = ANY(%s)
                    GROUP BY season
                    """,
                    (trend_seasons,)
                )
                trend_games_map = {
                    _int(row.get('season')): _int(row.get('completed_games'))
                    for row in (cur.fetchall() or [])
                }

                cur.execute(
                    """
                    SELECT season, COUNT(*) AS predicted_games
                    FROM hcl.ml_predictions
                    WHERE season = ANY(%s)
                    GROUP BY season
                    """,
                    (trend_seasons,)
                )
                trend_xgb_pred_map = {
                    _int(row.get('season')): _int(row.get('predicted_games'))
                    for row in (cur.fetchall() or [])
                }

                cur.execute(
                    """
                    SELECT
                        season,
                        COUNT(*) AS scored_games,
                        COALESCE(SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct_predictions
                    FROM hcl.ml_predictions
                    WHERE result_recorded_at IS NOT NULL
                      AND season = ANY(%s)
                    GROUP BY season
                    """,
                    (trend_seasons,)
                )
                trend_xgb_scored_map = {
                    _int(row.get('season')): {
                        'scored_games': _int(row.get('scored_games')),
                        'correct_predictions': _int(row.get('correct_predictions'))
                    }
                    for row in (cur.fetchall() or [])
                }

                trend_elo_pred_map = {}
                trend_elo_scored_map = {}
                trend_agreement_map = {}

                if elo_table_ready:
                    cur.execute(
                        """
                        SELECT season, COUNT(*) AS predicted_games
                        FROM hcl.ml_predictions_elo
                        WHERE season = ANY(%s)
                        GROUP BY season
                        """,
                        (trend_seasons,)
                    )
                    trend_elo_pred_map = {
                        _int(row.get('season')): _int(row.get('predicted_games'))
                        for row in (cur.fetchall() or [])
                    }

                    cur.execute(
                        """
                        SELECT
                            e.season,
                            COUNT(*) AS scored_games,
                            COALESCE(
                                SUM(
                                    CASE
                                        WHEN (g.home_score > g.away_score AND e.predicted_winner = g.home_team)
                                          OR (g.away_score > g.home_score AND e.predicted_winner = g.away_team)
                                        THEN 1 ELSE 0
                                    END
                                ),
                                0
                            ) AS correct_predictions
                        FROM hcl.ml_predictions_elo e
                        JOIN hcl.games g ON g.game_id = e.game_id
                        WHERE e.predicted_winner IS NOT NULL
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
                                                    AND COALESCE(g.is_postseason, FALSE) = FALSE
                          AND e.season = ANY(%s)
                        GROUP BY e.season
                        """,
                        (trend_seasons,)
                    )
                    trend_elo_scored_map = {
                        _int(row.get('season')): {
                            'scored_games': _int(row.get('scored_games')),
                            'correct_predictions': _int(row.get('correct_predictions'))
                        }
                        for row in (cur.fetchall() or [])
                    }

                    cur.execute(
                        """
                        SELECT
                            x.season,
                            COUNT(*) AS both_models_games,
                            COALESCE(SUM(CASE WHEN x.predicted_winner = e.predicted_winner THEN 1 ELSE 0 END), 0) AS agreements
                        FROM hcl.ml_predictions x
                        JOIN hcl.ml_predictions_elo e ON e.game_id = x.game_id
                        JOIN hcl.games g ON g.game_id = x.game_id
                        WHERE x.result_recorded_at IS NOT NULL
                          AND x.predicted_winner IS NOT NULL
                          AND e.predicted_winner IS NOT NULL
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
                                                    AND COALESCE(g.is_postseason, FALSE) = FALSE
                          AND x.season = ANY(%s)
                        GROUP BY x.season
                        """,
                        (trend_seasons,)
                    )
                    trend_agreement_map = {
                        _int(row.get('season')): {
                            'both_models_games': _int(row.get('both_models_games')),
                            'agreements': _int(row.get('agreements'))
                        }
                        for row in (cur.fetchall() or [])
                    }

                cur.execute(
                    """
                    SELECT
                        season,
                        COALESCE(SUM(CASE WHEN spread_line IS NOT NULL AND spread_line <> 0 THEN 1 ELSE 0 END), 0) AS evaluable_games,
                        COALESCE(
                            SUM(
                                CASE
                                    WHEN spread_line IS NULL OR spread_line = 0 THEN 0
                                    WHEN spread_line > 0 AND home_score > away_score THEN 1
                                    WHEN spread_line < 0 AND away_score > home_score THEN 1
                                    ELSE 0
                                END
                            ),
                            0
                        ) AS correct_predictions
                    FROM hcl.games
                    WHERE home_score IS NOT NULL
                      AND away_score IS NOT NULL
                                            AND COALESCE(is_postseason, FALSE) = FALSE
                      AND season = ANY(%s)
                    GROUP BY season
                    """,
                    (trend_seasons,)
                )
                trend_vegas_map = {
                    _int(row.get('season')): {
                        'evaluable_games': _int(row.get('evaluable_games')),
                        'correct_predictions': _int(row.get('correct_predictions'))
                    }
                    for row in (cur.fetchall() or [])
                }

                for trend_season in trend_seasons:
                    trend_completed = trend_games_map.get(trend_season, 0)

                    trend_xgb = trend_xgb_scored_map.get(trend_season, {'scored_games': 0, 'correct_predictions': 0})
                    trend_xgb_scored = _int(trend_xgb.get('scored_games'))
                    trend_xgb_correct = _int(trend_xgb.get('correct_predictions'))

                    trend_elo = trend_elo_scored_map.get(trend_season, {'scored_games': 0, 'correct_predictions': 0})
                    trend_elo_scored = _int(trend_elo.get('scored_games'))
                    trend_elo_correct = _int(trend_elo.get('correct_predictions'))

                    trend_agreement = trend_agreement_map.get(trend_season, {'both_models_games': 0, 'agreements': 0})
                    trend_vegas = trend_vegas_map.get(trend_season, {'evaluable_games': 0, 'correct_predictions': 0})

                    season_trend.append({
                        'season': trend_season,
                        'completed_games': trend_completed,
                        'xgb': {
                            'predicted_games': trend_xgb_pred_map.get(trend_season, 0),
                            'scored_games': trend_xgb_scored,
                            'correct_predictions': trend_xgb_correct,
                            'win_accuracy': _pct(trend_xgb_correct, trend_xgb_scored),
                            'coverage_pct': _pct(trend_xgb_scored, trend_completed)
                        },
                        'elo': {
                            'predicted_games': trend_elo_pred_map.get(trend_season, 0),
                            'scored_games': trend_elo_scored,
                            'correct_predictions': trend_elo_correct,
                            'win_accuracy': _pct(trend_elo_correct, trend_elo_scored),
                            'coverage_pct': _pct(trend_elo_scored, trend_completed)
                        },
                        'agreement': {
                            'both_models_games': _int(trend_agreement.get('both_models_games')),
                            'agreements': _int(trend_agreement.get('agreements')),
                            'agreement_rate': _pct(
                                _int(trend_agreement.get('agreements')),
                                _int(trend_agreement.get('both_models_games'))
                            )
                        },
                        'vegas': {
                            'evaluable_games': _int(trend_vegas.get('evaluable_games')),
                            'correct_predictions': _int(trend_vegas.get('correct_predictions')),
                            'win_accuracy': _pct(
                                _int(trend_vegas.get('correct_predictions')),
                                _int(trend_vegas.get('evaluable_games'))
                            )
                        }
                    })

        coverage_contract = {
            'start_season': None,
            'end_season': None,
            'seasons': [],
            'totals': {
                'completed_games': 0,
                'xgb_predicted_games': 0,
                'xgb_scored_games': 0,
                'elo_predicted_games': 0,
                'elo_scored_games': 0,
                'both_models_games': 0,
                'xgb_predicted_coverage_pct': 0.0,
                'xgb_scored_coverage_pct': 0.0,
                'elo_predicted_coverage_pct': 0.0,
                'elo_scored_coverage_pct': 0.0,
                'both_models_coverage_pct': 0.0
            }
        }

        if week is None:
            coverage_start = request.args.get('coverage_start_season', type=int)
            coverage_end = request.args.get('coverage_end_season', type=int)

            latest_completed_season = get_latest_completed_season()
            if coverage_end is None:
                coverage_end = latest_completed_season
            if coverage_start is None:
                coverage_start = max(2021, coverage_end - 4)

            if coverage_start > coverage_end:
                coverage_start, coverage_end = coverage_end, coverage_start

            coverage_contract['start_season'] = coverage_start
            coverage_contract['end_season'] = coverage_end

            for coverage_season in range(coverage_start, coverage_end + 1):
                cur.execute(
                    """
                    SELECT COUNT(*) AS completed_games
                    FROM hcl.games
                    WHERE season = %s
                      AND home_score IS NOT NULL
                      AND away_score IS NOT NULL
                                            AND COALESCE(is_postseason, FALSE) = FALSE
                    """,
                    (coverage_season,)
                )
                completed = _int((cur.fetchone() or {}).get('completed_games'))

                cur.execute(
                    """
                    SELECT COUNT(*) AS predicted_games
                    FROM hcl.ml_predictions
                    WHERE season = %s
                    """,
                    (coverage_season,)
                )
                xgb_predicted = _int((cur.fetchone() or {}).get('predicted_games'))

                cur.execute(
                    """
                    SELECT
                        COUNT(*) AS scored_games,
                        COALESCE(SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct_predictions
                    FROM hcl.ml_predictions
                    WHERE season = %s
                      AND result_recorded_at IS NOT NULL
                    """,
                    (coverage_season,)
                )
                xgb_row = cur.fetchone() or {}
                xgb_scored = _int(xgb_row.get('scored_games'))
                xgb_correct = _int(xgb_row.get('correct_predictions'))

                elo_predicted = 0
                elo_scored = 0
                elo_correct = 0
                both_models_games = 0

                if elo_table_ready:
                    cur.execute(
                        """
                        SELECT COUNT(*) AS predicted_games
                        FROM hcl.ml_predictions_elo
                        WHERE season = %s
                        """,
                        (coverage_season,)
                    )
                    elo_predicted = _int((cur.fetchone() or {}).get('predicted_games'))

                    cur.execute(
                        """
                        SELECT
                            COUNT(*) AS scored_games,
                            COALESCE(
                                SUM(
                                    CASE
                                        WHEN (g.home_score > g.away_score AND e.predicted_winner = g.home_team)
                                          OR (g.away_score > g.home_score AND e.predicted_winner = g.away_team)
                                        THEN 1 ELSE 0
                                    END
                                ),
                                0
                            ) AS correct_predictions
                        FROM hcl.ml_predictions_elo e
                        JOIN hcl.games g ON g.game_id = e.game_id
                        WHERE e.season = %s
                          AND e.predicted_winner IS NOT NULL
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
                                                    AND COALESCE(g.is_postseason, FALSE) = FALSE
                        """,
                        (coverage_season,)
                    )
                    elo_row = cur.fetchone() or {}
                    elo_scored = _int(elo_row.get('scored_games'))
                    elo_correct = _int(elo_row.get('correct_predictions'))

                    cur.execute(
                        """
                        SELECT COUNT(*) AS both_models_games
                        FROM hcl.ml_predictions x
                        JOIN hcl.ml_predictions_elo e ON e.game_id = x.game_id
                        JOIN hcl.games g ON g.game_id = x.game_id
                        WHERE x.season = %s
                          AND x.result_recorded_at IS NOT NULL
                          AND e.predicted_winner IS NOT NULL
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
                                                    AND COALESCE(g.is_postseason, FALSE) = FALSE
                        """,
                        (coverage_season,)
                    )
                    both_models_games = _int((cur.fetchone() or {}).get('both_models_games'))

                coverage_contract['seasons'].append({
                    'season': coverage_season,
                    'completed_games': completed,
                    'xgb': {
                        'predicted_games': xgb_predicted,
                        'scored_games': xgb_scored,
                        'correct_predictions': xgb_correct,
                        'win_accuracy': _pct(xgb_correct, xgb_scored),
                        'predicted_coverage_pct': _pct(xgb_predicted, completed),
                        'scored_coverage_pct': _pct(xgb_scored, completed)
                    },
                    'elo': {
                        'predicted_games': elo_predicted,
                        'scored_games': elo_scored,
                        'correct_predictions': elo_correct,
                        'win_accuracy': _pct(elo_correct, elo_scored),
                        'predicted_coverage_pct': _pct(elo_predicted, completed),
                        'scored_coverage_pct': _pct(elo_scored, completed)
                    },
                    'agreement': {
                        'both_models_games': both_models_games,
                        'both_models_coverage_pct': _pct(both_models_games, completed)
                    }
                })

            if coverage_contract['seasons']:
                totals = coverage_contract['totals']
                totals['completed_games'] = sum(_int(s.get('completed_games')) for s in coverage_contract['seasons'])
                totals['xgb_predicted_games'] = sum(_int((s.get('xgb') or {}).get('predicted_games')) for s in coverage_contract['seasons'])
                totals['xgb_scored_games'] = sum(_int((s.get('xgb') or {}).get('scored_games')) for s in coverage_contract['seasons'])
                totals['elo_predicted_games'] = sum(_int((s.get('elo') or {}).get('predicted_games')) for s in coverage_contract['seasons'])
                totals['elo_scored_games'] = sum(_int((s.get('elo') or {}).get('scored_games')) for s in coverage_contract['seasons'])
                totals['both_models_games'] = sum(_int((s.get('agreement') or {}).get('both_models_games')) for s in coverage_contract['seasons'])
                totals['xgb_predicted_coverage_pct'] = _pct(totals['xgb_predicted_games'], totals['completed_games'])
                totals['xgb_scored_coverage_pct'] = _pct(totals['xgb_scored_games'], totals['completed_games'])
                totals['elo_predicted_coverage_pct'] = _pct(totals['elo_predicted_games'], totals['completed_games'])
                totals['elo_scored_coverage_pct'] = _pct(totals['elo_scored_games'], totals['completed_games'])
                totals['both_models_coverage_pct'] = _pct(totals['both_models_games'], totals['completed_games'])

        integrity = {
            'leakage': {
                'rows_checked': 0,
                'predicted_after_game_date_count': 0,
                'predicted_after_game_date_pct': 0.0,
                'threshold_pct': 5.0
            },
            'margin_sign': {
                'rows_checked': 0,
                'inconsistent_count': 0,
                'inconsistent_pct': 0.0,
                'threshold_pct': 0.0
            },
            'totals_line_lock': {
                'rows_checked': 0,
                'line_locked_count': 0,
                'line_locked_pct': 0.0,
                'threshold_pct': 95.0
            }
        }

        warnings = []

        integrity_where = ["mp.season = %s"]
        integrity_params = [season]
        if week is not None:
            integrity_where.append("mp.week = %s")
            integrity_params.append(week)

        cur.execute(
            f"""
            SELECT
                COUNT(*) AS rows_checked,
                COALESCE(
                    SUM(
                        CASE
                            WHEN mp.predicted_at IS NOT NULL
                             AND g.game_date IS NOT NULL
                             AND mp.predicted_at > g.game_date
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS predicted_after_game_date_count
            FROM hcl.ml_predictions mp
            JOIN hcl.games g ON g.game_id = mp.game_id
            WHERE {' AND '.join(integrity_where)}
                            AND COALESCE(g.is_postseason, FALSE) = FALSE
            """,
            tuple(integrity_params)
        )
        leakage_row = cur.fetchone() or {}
        leakage_checked = _int(leakage_row.get('rows_checked'))
        leakage_count = _int(leakage_row.get('predicted_after_game_date_count'))
        leakage_pct = _pct(leakage_count, leakage_checked)
        integrity['leakage'].update({
            'rows_checked': leakage_checked,
            'predicted_after_game_date_count': leakage_count,
            'predicted_after_game_date_pct': leakage_pct
        })

        cur.execute(
            f"""
            SELECT
                COUNT(*) AS rows_checked,
                COALESCE(
                    SUM(
                        CASE
                            WHEN mp.actual_winner = mp.away_team AND mp.actual_margin > 0 THEN 1
                            WHEN mp.actual_winner = mp.home_team AND mp.actual_margin < 0 THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS inconsistent_count
            FROM hcl.ml_predictions mp
            WHERE {' AND '.join(integrity_where)}
              AND mp.result_recorded_at IS NOT NULL
              AND mp.actual_winner IN (mp.home_team, mp.away_team)
              AND mp.actual_margin IS NOT NULL
            """,
            tuple(integrity_params)
        )
        margin_row = cur.fetchone() or {}
        margin_checked = _int(margin_row.get('rows_checked'))
        margin_count = _int(margin_row.get('inconsistent_count'))
        margin_pct = _pct(margin_count, margin_checked)
        integrity['margin_sign'].update({
            'rows_checked': margin_checked,
            'inconsistent_count': margin_count,
            'inconsistent_pct': margin_pct
        })

        cur.execute(
            f"""
            SELECT
                COUNT(*) AS rows_checked,
                COALESCE(
                    SUM(
                        CASE
                            WHEN mp.predicted_home_score IS NULL
                              OR mp.predicted_away_score IS NULL
                              OR mp.vegas_total IS NULL THEN 0
                            WHEN ROUND((mp.predicted_home_score + mp.predicted_away_score)::NUMERIC, 1)
                               = ROUND(mp.vegas_total::NUMERIC, 1)
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS line_locked_count
            FROM hcl.ml_predictions mp
            WHERE {' AND '.join(integrity_where)}
            """,
            tuple(integrity_params)
        )
        line_lock_row = cur.fetchone() or {}
        line_lock_checked = _int(line_lock_row.get('rows_checked'))
        line_lock_count = _int(line_lock_row.get('line_locked_count'))
        line_lock_pct = _pct(line_lock_count, line_lock_checked)
        integrity['totals_line_lock'].update({
            'rows_checked': line_lock_checked,
            'line_locked_count': line_lock_count,
            'line_locked_pct': line_lock_pct
        })

        if leakage_pct > integrity['leakage']['threshold_pct']:
            warnings.append(
                f"Integrity warning: {leakage_pct}% of tracked XGBoost rows have predicted_at after game_date"
            )
        if margin_pct > integrity['margin_sign']['threshold_pct']:
            warnings.append(
                f"Integrity warning: {margin_pct}% of scored XGBoost rows have inconsistent actual_margin sign"
            )
        if line_lock_pct >= integrity['totals_line_lock']['threshold_pct']:
            warnings.append(
                f"Integrity warning: {line_lock_pct}% of rows have predicted total locked to vegas_total"
            )

        overall = {
            'total_games': primary_summary.get('scored_games', 0),
            'correct_predictions': primary_summary.get('correct_predictions', 0),
            'win_accuracy': round(_float(primary_summary.get('win_accuracy')), 2),
            'avg_margin_error': round(_float(primary_summary.get('avg_margin_error')), 2),
            'avg_home_score_error': None,
            'avg_away_score_error': None,
            'first_week': primary_summary.get('first_week'),
            'latest_week': primary_summary.get('latest_week'),
            'model': primary_model
        }

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'season': season,
            'week': week,
            'completed_games': completed_games,
            'overall': overall,
            'by_week': by_week,
            'by_week_models': by_week_models,
            'model_breakdown': model_breakdown,
            'season_trend': season_trend,
            'coverage_contract': coverage_contract,
            'elo_table_ready': elo_table_ready,
            'integrity': integrity,
            'warnings': warnings
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ml_api.route('/api/ml/available-weeks', methods=['GET'])
def get_available_weeks():
    """
    Get list of all weeks with predictions available
    
    Returns weeks from both XGBoost and Elo predictions
    """
    try:
        conn = psycopg2.connect(**get_predictor().db_config)
        elo_table_ready = table_exists(conn, 'hcl', 'ml_predictions_elo')
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all weeks with predictions from either table
        if elo_table_ready:
            cur.execute("""
                SELECT DISTINCT season, week, COUNT(*) as game_count
                FROM (
                    SELECT season, week, game_id FROM hcl.ml_predictions
                    UNION
                    SELECT season, week, game_id FROM hcl.ml_predictions_elo
                ) combined
                GROUP BY season, week
                ORDER BY season DESC, week DESC
            """)
        else:
            cur.execute("""
                SELECT season, week, COUNT(*) as game_count
                FROM hcl.ml_predictions
                GROUP BY season, week
                ORDER BY season DESC, week DESC
            """)
        
        weeks = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'weeks': weeks,
            'total': len(weeks),
            'elo_table_ready': elo_table_ready
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ELO RATING SYSTEM ENDPOINTS
# ============================================================================

@ml_api.route('/api/elo/ratings/current', methods=['GET'])
def get_current_elo_ratings():
    """
    Get current Elo ratings for all NFL teams
    
    Example: GET /api/elo/ratings/current
    
    Returns:
    {
        "success": true,
        "last_updated": "2025-12-19T01:01:51",
        "ratings": {
            "PHI": 1767.7,
            "BAL": 1705.2,
            ...
        },
        "rankings": [
            {"rank": 1, "team": "PHI", "rating": 1767.7, "diff": 267.7},
            ...
        ]
    }
    """
    try:
        tracker = get_elo_tracker()
        ratings = tracker.elo.get_all_ratings()
        
        # Create rankings
        rankings = []
        for rank, (team, rating) in enumerate(
            sorted(ratings.items(), key=lambda x: x[1], reverse=True), 1
        ):
            rankings.append({
                'rank': rank,
                'team': team,
                'rating': round(rating, 1),
                'diff': round(rating - tracker.elo.base_elo, 1)
            })
        
        # Load metadata from file
        ratings_file = 'ml/models/elo_ratings_current.json'
        last_updated = None
        if os.path.exists(ratings_file):
            with open(ratings_file, 'r') as f:
                data = json.load(f)
                last_updated = data.get('last_updated')
        
        return jsonify({
            'success': True,
            'last_updated': last_updated,
            'ratings': {k: round(v, 1) for k, v in ratings.items()},
            'rankings': rankings
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ml_api.route('/api/elo/predict-week/<int:season>/<int:week>', methods=['GET'])
def predict_week_elo(season, week):
    """
    Get Elo-based predictions for a specific week
    
    Example: GET /api/elo/predict-week/2025/16
    
    Returns:
    {
        "success": true,
        "season": 2025,
        "week": 16,
        "total_games": 16,
        "predictions": [
            {
                "game_id": "...",
                "home_team": "KC",
                "away_team": "TEN",
                "home_elo": 1699.3,
                "away_elo": 1306.1,
                "predicted_winner": "KC",
                "confidence": 0.869,
                "elo_spread": -13.1,
                "vegas_spread": 3.0,
                "split_prediction": true
            },
            ...
        ],
        "summary": {
            "avg_confidence": 0.697,
            "split_predictions": 10
        }
    }
    """
    try:
        def build_all_game_predictions(elo_pred):
            """Generate Elo predictions for all scheduled games, including completed matchups."""
            games_df = elo_pred.get_scheduled_games(season, week)
            if len(games_df) == 0:
                return []

            predictions = []
            for _, game in games_df.iterrows():
                spread_line = game['spread_line']
                if spread_line is not None and spread_line != spread_line:  # NaN check
                    spread_line = None

                pred = elo_pred.predict_game(
                    game['home_team'],
                    game['away_team'],
                    spread_line=spread_line,
                    is_neutral=False
                )
                pred['game_id'] = game['game_id']
                pred['season'] = season
                pred['week'] = week
                pred['game_date'] = game['game_date']
                predictions.append(pred)

            return predictions

        # Check if predictions already exist in database
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'nfl_analytics'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )

        elo_table_ready = table_exists(conn, 'hcl', 'ml_predictions_elo')

        if not elo_table_ready:
            conn.close()

            # Fallback for environments where Elo storage has not been migrated yet.
            with contextlib.redirect_stdout(io.StringIO()):
                elo_pred = get_elo_predictor()
            predictions = build_all_game_predictions(elo_pred)

            if not predictions:
                return jsonify({
                    'success': False,
                    'message': f'No games found for {season} Week {week}'
                })

            avg_conf = sum(p['confidence'] for p in predictions) / len(predictions)
            split_count = sum(1 for p in predictions if p['split_prediction'])

            return jsonify({
                'success': True,
                'season': season,
                'week': week,
                'total_games': len(predictions),
                'predictions': predictions,
                'summary': {
                    'avg_confidence': round(avg_conf, 3),
                    'split_predictions': split_count
                },
                'model': 'FiveThirtyEight-style Elo',
                'accuracy': '60-65% (proven)',
                'elo_table_ready': False
            })
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                game_id,
                season,
                week,
                home_team,
                away_team,
                home_elo,
                away_elo,
                elo_diff,
                home_win_prob,
                away_win_prob,
                predicted_winner,
                confidence,
                elo_spread,
                vegas_spread,
                spread_diff,
                split_prediction
            FROM hcl.ml_predictions_elo
            WHERE season = %s AND week = %s
            ORDER BY game_id
        """, (season, week))
        
        predictions = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        if predictions:
            # Calculate summary stats
            avg_conf = sum(p['confidence'] for p in predictions) / len(predictions)
            split_count = sum(1 for p in predictions if p['split_prediction'])
            
            return jsonify({
                'success': True,
                'season': season,
                'week': week,
                'total_games': len(predictions),
                'predictions': predictions,
                'summary': {
                    'avg_confidence': round(avg_conf, 3),
                    'split_predictions': split_count
                },
                'model': 'FiveThirtyEight-style Elo',
                'accuracy': '60-65% (proven)',
                'elo_table_ready': True
            })
        
        # If no predictions found, generate them directly from scheduled games.
        with contextlib.redirect_stdout(io.StringIO()):
            elo_pred = get_elo_predictor()
        predictions = build_all_game_predictions(elo_pred)
        if predictions:
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    elo_pred._save_predictions_to_db(predictions)
            except Exception:
                # Prediction delivery should not fail if persistence fails.
                pass
        
        if not predictions:
            return jsonify({
                'success': False,
                'message': f'No games found for {season} Week {week}'
            })
        
        # Calculate summary
        avg_conf = sum(p['confidence'] for p in predictions) / len(predictions)
        split_count = sum(1 for p in predictions if p['split_prediction'])
        
        return jsonify({
            'success': True,
            'season': season,
            'week': week,
            'total_games': len(predictions),
            'predictions': predictions,
            'summary': {
                'avg_confidence': round(avg_conf, 3),
                'split_predictions': split_count
            },
            'model': 'FiveThirtyEight-style Elo',
            'accuracy': '60-65% (proven)',
            'elo_table_ready': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ml_api.route('/api/predictions/combined/<int:season>/<int:week>', methods=['GET'])
def get_combined_predictions(season, week):
    """
    Get both XGBoost and Elo predictions side-by-side
    
    Example: GET /api/predictions/combined/2025/16
    
    Returns both prediction types with comparison
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'nfl_analytics'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )

        elo_table_ready = table_exists(conn, 'hcl', 'ml_predictions_elo')
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get XGBoost predictions WITH Vegas spread from games table
        cur.execute("""
            SELECT 
                p.*,
                g.spread_line as vegas_spread,
                g.total_line as vegas_total,
                g.home_score,
                g.away_score
            FROM hcl.ml_predictions p
            LEFT JOIN hcl.games g ON p.game_id = g.game_id
            WHERE p.season = %s AND p.week = %s
            ORDER BY p.game_date, p.game_id
        """, (season, week))
        xgb_predictions = {row['game_id']: dict(row) for row in cur.fetchall()}
        
        # Get Elo predictions WITH Vegas spread from games table (if available)
        elo_predictions = {}
        if elo_table_ready:
            cur.execute("""
                SELECT 
                    e.*,
                    g.spread_line as vegas_spread,
                    g.total_line as vegas_total,
                    g.home_score,
                    g.away_score
                FROM hcl.ml_predictions_elo e
                LEFT JOIN hcl.games g ON e.game_id = g.game_id
                WHERE e.season = %s AND e.week = %s
                ORDER BY e.game_id
            """, (season, week))
            elo_predictions = {row['game_id']: dict(row) for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        # Combine predictions
        combined = []
        all_game_ids = set(xgb_predictions.keys()) | set(elo_predictions.keys())
        
        for game_id in sorted(all_game_ids):
            xgb = xgb_predictions.get(game_id)
            elo = elo_predictions.get(game_id)

            base_row = xgb if xgb else elo
            home_team = base_row['home_team']
            away_team = base_row['away_team']

            home_score = base_row.get('home_score')
            away_score = base_row.get('away_score')
            is_final = home_score is not None and away_score is not None

            actual_winner = None
            actual_margin = None
            if is_final:
                actual_margin = int(home_score) - int(away_score)
                if home_score > away_score:
                    actual_winner = home_team
                elif away_score > home_score:
                    actual_winner = away_team
                else:
                    actual_winner = 'TIE'

            xgb_correct = None
            if xgb and is_final:
                if actual_winner == 'TIE':
                    xgb_correct = False
                else:
                    xgb_correct = (xgb.get('predicted_winner') == actual_winner)

            elo_correct = None
            if elo and is_final:
                if actual_winner == 'TIE':
                    elo_correct = False
                else:
                    elo_correct = (elo.get('predicted_winner') == actual_winner)
            
            if xgb and elo:
                # Both predictions available
                agreement = xgb['predicted_winner'] == elo['predicted_winner']
                
                combined.append({
                    'game_id': game_id,
                    'home_team': xgb['home_team'],
                    'away_team': xgb['away_team'],
                    'game_date': xgb.get('game_date'),
                    'game_status': 'final' if is_final else 'scheduled',
                    'actual': {
                        'home_score': int(home_score) if home_score is not None else None,
                        'away_score': int(away_score) if away_score is not None else None,
                        'winner': actual_winner,
                        'margin': actual_margin
                    },
                    'model_results': {
                        'xgb_correct': xgb_correct,
                        'elo_correct': elo_correct
                    },
                    'xgb': {
                        'predicted_winner': xgb['predicted_winner'],
                        'confidence': float(xgb['home_win_prob']) if xgb['predicted_winner'] == xgb['home_team'] else float(xgb['away_win_prob']),
                        'spread': float(xgb.get('ai_spread', 0)),
                        'split_prediction': xgb.get('split_prediction', False)
                    },
                    'elo': {
                        'predicted_winner': elo['predicted_winner'],
                        'confidence': float(elo['confidence']),
                        'spread': float(elo['elo_spread']),
                        'split_prediction': elo.get('split_prediction', False)
                    },
                    'agreement': agreement,
                    'vegas_spread': float(xgb['vegas_spread']) if xgb.get('vegas_spread') is not None else None
                })
            elif xgb:
                # Only XGBoost available
                combined.append({
                    'game_id': game_id,
                    'home_team': xgb['home_team'],
                    'away_team': xgb['away_team'],
                    'game_date': xgb.get('game_date'),
                    'game_status': 'final' if is_final else 'scheduled',
                    'actual': {
                        'home_score': int(home_score) if home_score is not None else None,
                        'away_score': int(away_score) if away_score is not None else None,
                        'winner': actual_winner,
                        'margin': actual_margin
                    },
                    'model_results': {
                        'xgb_correct': xgb_correct,
                        'elo_correct': None
                    },
                    'xgb': {
                        'predicted_winner': xgb['predicted_winner'],
                        'confidence': float(xgb['home_win_prob']) if xgb['predicted_winner'] == xgb['home_team'] else float(xgb['away_win_prob']),
                        'spread': float(xgb.get('ai_spread', 0))
                    },
                    'elo': None,
                    'agreement': None,
                    'vegas_spread': float(xgb['vegas_spread']) if xgb.get('vegas_spread') is not None else None
                })
            elif elo:
                # Only Elo available
                combined.append({
                    'game_id': game_id,
                    'home_team': elo['home_team'],
                    'away_team': elo['away_team'],
                    'game_date': elo.get('game_date'),
                    'game_status': 'final' if is_final else 'scheduled',
                    'actual': {
                        'home_score': int(home_score) if home_score is not None else None,
                        'away_score': int(away_score) if away_score is not None else None,
                        'winner': actual_winner,
                        'margin': actual_margin
                    },
                    'model_results': {
                        'xgb_correct': None,
                        'elo_correct': elo_correct
                    },
                    'xgb': None,
                    'elo': {
                        'predicted_winner': elo['predicted_winner'],
                        'confidence': float(elo['confidence']),
                        'spread': float(elo['elo_spread'])
                    },
                    'agreement': None,
                    'vegas_spread': float(elo['vegas_spread']) if elo.get('vegas_spread') is not None else None
                })
        
        # Calculate summary stats
        agreements = [p['agreement'] for p in combined if p['agreement'] is not None]
        agreement_rate = (sum(agreements) / len(agreements)) if agreements else 0
        
        return jsonify({
            'success': True,
            'season': season,
            'week': week,
            'total_games': len(combined),
            'predictions': combined,
            'summary': {
                'agreement_rate': round(agreement_rate, 3),
                'both_models': len([p for p in combined if p['xgb'] and p['elo']]),
                'xgb_only': len([p for p in combined if p['xgb'] and not p['elo']]),
                'elo_only': len([p for p in combined if p['elo'] and not p['xgb']])
            },
            'elo_table_ready': elo_table_ready
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
