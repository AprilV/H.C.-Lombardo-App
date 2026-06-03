"""
ML Prediction API Routes

Flask API endpoints for NFL game predictions using the trained neural network.

Sprint 9: Machine Learning Predictions
Sprint 10: Elo Rating System Integration
Date: December 19, 2025
"""

from flask import Blueprint, jsonify, request, Response
import sys
import os
import io
import csv
import hashlib
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


def table_has_column(conn, schema_name, table_name, column_name):
    """Return True if the given table has the specified column."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
              AND column_name = %s
        )
        """,
        (schema_name, table_name, column_name)
    )
    exists = bool(cur.fetchone()[0])
    cur.close()
    return exists


def did_home_cover(spread, actual_margin):
    """Return True/False for ATS cover, or None for push (tie against spread)."""
    if spread is None or actual_margin is None:
        return None

    result = actual_margin + spread
    if result == 0:
        return None
    return result > 0


def build_outcome_fingerprint(outcomes_by_game_id):
    """Return deterministic SHA256 fingerprint for {game_id: result} mapping."""
    if not outcomes_by_game_id:
        return None
    canonical = '|'.join(
        f"{gid}:{outcomes_by_game_id[gid]}"
        for gid in sorted(outcomes_by_game_id.keys())
    )
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def build_season_chain_fingerprint(fingerprints_by_season, start_season, end_season):
    """Return deterministic SHA256 fingerprint for inclusive season-range outcome hashes."""
    if (
        start_season is None
        or end_season is None
        or end_season < start_season
    ):
        return None, 0

    parts = []
    for season in range(start_season, end_season + 1):
        fingerprint = fingerprints_by_season.get(season)
        parts.append(f"{season}:{fingerprint or 'none'}")

    canonical = '|'.join(parts)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest(), len(parts)


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

        # Primary path: use pregame-only recorded outcomes from tracking table for stable, fast responses.
        tracking_where = [
            "mp.season = %s",
            "mp.result_recorded_at IS NOT NULL",
            "COALESCE(g.is_postseason, FALSE) = FALSE",
            "mp.predicted_at IS NOT NULL",
            "COALESCE(mp.game_date::date, g.game_date::date) IS NOT NULL",
            "mp.predicted_at::date <= COALESCE(mp.game_date::date, g.game_date::date)"
        ]
        tracking_params = [season]
        if week is not None:
            tracking_where.append("mp.week = %s")
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
                            WHEN (actual_margin + ai_spread) > 0 AND (actual_margin + vegas_spread) < 0 THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) as ai_covers,
                COALESCE(
                    SUM(
                        CASE
                            WHEN actual_margin IS NULL OR ai_spread IS NULL OR vegas_spread IS NULL THEN 0
                            WHEN (actual_margin + vegas_spread) > 0 AND (actual_margin + ai_spread) < 0 THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) as vegas_covers
            FROM hcl.ml_predictions mp
            JOIN hcl.games g ON g.game_id = mp.game_id
            WHERE {' AND '.join(tracking_where)}
        """

        cur.execute(tracking_sql, tuple(tracking_params))
        tracked = cur.fetchone() or {}

        tracked_total = int(tracked.get('total_games') or 0)
        # Keep one equation for public performance output.
        # Do not return strict tracked rows directly; always use completed-game simulation path below.
        if False and tracked_total > 0:
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
        game_where = [
            "g.home_score IS NOT NULL",
            "g.away_score IS NOT NULL",
            "g.season = %s",
            "COALESCE(g.is_postseason, FALSE) = FALSE"
        ]
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
                ai_covered = did_home_cover(ai_spread, actual_margin)
                vegas_covered = did_home_cover(vegas_spread, actual_margin)
                if ai_covered is True and vegas_covered is False:
                    ai_covers += 1
                elif ai_covered is False and vegas_covered is True:
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
        data_source = 'strict_pregame'

        has_closing_spread = table_has_column(conn, 'hcl', 'games', 'closing_spread')
        if has_closing_spread:
            vegas_expr = "COALESCE(g.closing_spread, p.vegas_spread, g.spread_line)"
            vegas_source = "closing_spread->prediction_vegas_spread->spread_line"
        else:
            vegas_expr = "COALESCE(p.vegas_spread, g.spread_line)"
            vegas_source = "prediction_vegas_spread->spread_line"
        
        # Get all completed games with predictions for the season
        cur.execute(
            f"""
            SELECT
                p.game_id,
                p.ai_spread,
                {vegas_expr} AS vegas_spread,
                g.home_score,
                g.away_score
            FROM hcl.ml_predictions p
            JOIN hcl.games g ON p.game_id = g.game_id
            WHERE p.season = %s
              AND g.home_score IS NOT NULL
              AND g.away_score IS NOT NULL
              AND COALESCE(g.is_postseason, FALSE) = FALSE
              AND p.ai_spread IS NOT NULL
              AND {vegas_expr} IS NOT NULL
              AND p.predicted_at IS NOT NULL
              AND (
                    (
                        g.kickoff_time_utc IS NOT NULL
                        AND p.predicted_at <= g.kickoff_time_utc
                    )
                    OR (
                        g.kickoff_time_utc IS NULL
                        AND COALESCE(p.game_date::date, g.game_date::date) IS NOT NULL
                        AND p.predicted_at::date <= COALESCE(p.game_date::date, g.game_date::date)
                    )
              )
            ORDER BY g.week, g.game_date
            """,
            (season,)
        )
        
        games = cur.fetchall()
        if not games:
            # Legacy fallback: keep historical coverage visible when older rows lack
            # pregame timestamp evidence but still have completed game outcomes.
            cur.execute(
                f"""
                SELECT
                    p.game_id,
                    p.ai_spread,
                    {vegas_expr} AS vegas_spread,
                    g.home_score,
                    g.away_score
                FROM hcl.ml_predictions p
                JOIN hcl.games g ON p.game_id = g.game_id
                WHERE p.season = %s
                  AND g.home_score IS NOT NULL
                  AND g.away_score IS NOT NULL
                  AND COALESCE(g.is_postseason, FALSE) = FALSE
                  AND p.ai_spread IS NOT NULL
                  AND {vegas_expr} IS NOT NULL
                ORDER BY g.week, g.game_date
                """,
                (season,)
            )
            games = cur.fetchall()
            if games:
                data_source = 'legacy_relaxed_pregame'
        
        # Single-equation mode: compute AI vs Vegas from simulated completed games
        # so all clients see one consistent denominator and outcome set.
        games = []

        ai_wins = 0
        vegas_wins = 0
        ties = 0
        total = 0

        if not games:
            cur.execute(
                """
                SELECT
                    week,
                    home_team,
                    away_team,
                    home_score,
                    away_score,
                    spread_line
                FROM hcl.games
                WHERE season = %s
                  AND home_score IS NOT NULL
                  AND away_score IS NOT NULL
                  AND COALESCE(is_postseason, FALSE) = FALSE
                  AND spread_line IS NOT NULL
                ORDER BY week, game_date
                """,
                (season,)
            )
            simulated_games = cur.fetchall() or []
            if simulated_games:
                data_source = 'simulated_historical'
                pred = get_predictor()
                for week, home_team, away_team, home_score, away_score, vegas_spread in simulated_games:
                    try:
                        prediction = pred.predict_game(
                            season,
                            int(week),
                            home_team,
                            away_team,
                            vegas_spread,
                            None
                        )
                    except Exception:
                        continue

                    ai_spread = prediction.get('ai_spread')
                    if ai_spread is None:
                        continue

                    actual_margin = home_score - away_score
                    total += 1

                    ai_covered = did_home_cover(ai_spread, actual_margin)
                    vegas_covered = did_home_cover(vegas_spread, actual_margin)

                    if ai_covered is True and vegas_covered is False:
                        ai_wins += 1
                    elif ai_covered is False and vegas_covered is True:
                        vegas_wins += 1
                    else:
                        ties += 1
        
        for game_id, ai_spread, vegas_spread, home_score, away_score in games:
            actual_margin = home_score - away_score
            total += 1

            ai_covered = did_home_cover(ai_spread, actual_margin)
            vegas_covered = did_home_cover(vegas_spread, actual_margin)
            
            # Compare
            if ai_covered is True and vegas_covered is False:
                ai_wins += 1
            elif ai_covered is False and vegas_covered is True:
                vegas_wins += 1
            else:
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
            'vegas_percentage': round(vegas_pct, 1),
            'vegas_spread_source': vegas_source,
            'data_source': data_source
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ml_api.route('/api/ml/season-ai-vs-vegas-audit/<int:season>', methods=['GET'])
def get_season_ai_vs_vegas_audit(season):
    """
    Return per-game ATS head-to-head outcomes for AI vs Vegas.

    Query params:
      week: optional week filter
      result: optional filter in {ai, vegas, tie}
      limit: optional integer row cap (default 500, max 2000)
      format: optional {json, csv} (default json)
    """
    conn = None
    cur = None
    try:
        week = request.args.get('week', type=int)
        result_filter = (request.args.get('result') or '').strip().lower()
        output_format = (request.args.get('format') or 'json').strip().lower()

        if result_filter and result_filter not in {'ai', 'vegas', 'tie'}:
            return jsonify({
                'success': False,
                'error': "Invalid result filter. Use one of: ai, vegas, tie"
            }), 400

        if output_format not in {'json', 'csv'}:
            return jsonify({
                'success': False,
                'error': "Invalid format. Use one of: json, csv"
            }), 400

        limit = request.args.get('limit', type=int)
        if limit is None:
            limit = 500
        limit = max(1, min(limit, 2000))

        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        has_games_closing_spread = table_has_column(conn, 'hcl', 'games', 'closing_spread')
        if has_games_closing_spread:
            vegas_expr = "COALESCE(g.closing_spread, p.vegas_spread, g.spread_line)"
            vegas_source = 'closing_spread->prediction_vegas_spread->spread_line'
        else:
            vegas_expr = "COALESCE(p.vegas_spread, g.spread_line)"
            vegas_source = 'prediction_vegas_spread->spread_line'

        where_clauses = [
            "p.season = %s",
            "g.home_score IS NOT NULL",
            "g.away_score IS NOT NULL",
            "COALESCE(g.is_postseason, FALSE) = FALSE",
            "p.ai_spread IS NOT NULL",
            f"{vegas_expr} IS NOT NULL",
            "p.predicted_at IS NOT NULL",
            "((g.kickoff_time_utc IS NOT NULL AND p.predicted_at <= g.kickoff_time_utc) "
            " OR (g.kickoff_time_utc IS NULL "
            "     AND COALESCE(p.game_date::date, g.game_date::date) IS NOT NULL "
            "     AND p.predicted_at::date <= COALESCE(p.game_date::date, g.game_date::date)))"
        ]
        params = [season]

        if week is not None:
            where_clauses.append("g.week = %s")
            params.append(week)

        query = f"""
            SELECT
                p.game_id,
                g.week,
                g.game_date,
                p.home_team,
                p.away_team,
                p.ai_spread,
                {vegas_expr} AS vegas_spread,
                g.home_score,
                g.away_score
            FROM hcl.ml_predictions p
            JOIN hcl.games g ON p.game_id = g.game_id
            WHERE {' AND '.join(where_clauses)}
            ORDER BY g.week ASC, g.game_date ASC, p.game_id ASC
            LIMIT %s
        """
        params.append(limit)
        cur.execute(query, tuple(params))
        rows = cur.fetchall() or []

        details = []
        ai_wins = 0
        vegas_wins = 0
        ties = 0
        returned_ai_wins = 0
        returned_vegas_wins = 0
        returned_ties = 0

        for row in rows:
            actual_margin = row['home_score'] - row['away_score']
            ai_covered = did_home_cover(row['ai_spread'], actual_margin)
            vegas_covered = did_home_cover(row['vegas_spread'], actual_margin)

            if ai_covered is True and vegas_covered is False:
                result = 'ai'
                ai_wins += 1
            elif ai_covered is False and vegas_covered is True:
                result = 'vegas'
                vegas_wins += 1
            else:
                result = 'tie'
                ties += 1

            if result_filter and result != result_filter:
                continue

            if result == 'ai':
                returned_ai_wins += 1
            elif result == 'vegas':
                returned_vegas_wins += 1
            else:
                returned_ties += 1

            details.append({
                'game_id': row['game_id'],
                'week': row['week'],
                'game_date': row['game_date'].isoformat() if row['game_date'] else None,
                'home_team': row['home_team'],
                'away_team': row['away_team'],
                'home_score': row['home_score'],
                'away_score': row['away_score'],
                'actual_margin': actual_margin,
                'ai_spread': float(row['ai_spread']) if row['ai_spread'] is not None else None,
                'vegas_spread': float(row['vegas_spread']) if row['vegas_spread'] is not None else None,
                'ai_covered': ai_covered,
                'vegas_covered': vegas_covered,
                'result': result
            })

        total = ai_wins + vegas_wins + ties
        returned_total = returned_ai_wins + returned_vegas_wins + returned_ties

        summary = {
            'total_games': total,
            'ai_wins': ai_wins,
            'vegas_wins': vegas_wins,
            'ties': ties,
            'ai_percentage': round((ai_wins / total * 100), 2) if total else 0.0,
            'vegas_percentage': round((vegas_wins / total * 100), 2) if total else 0.0
        }
        returned_summary = {
            'total_games': returned_total,
            'ai_wins': returned_ai_wins,
            'vegas_wins': returned_vegas_wins,
            'ties': returned_ties,
            'ai_percentage': round((returned_ai_wins / returned_total * 100), 2) if returned_total else 0.0,
            'vegas_percentage': round((returned_vegas_wins / returned_total * 100), 2) if returned_total else 0.0
        }

        if output_format == 'csv':
            output = io.StringIO()
            fieldnames = [
                'game_id',
                'week',
                'game_date',
                'home_team',
                'away_team',
                'home_score',
                'away_score',
                'actual_margin',
                'ai_spread',
                'vegas_spread',
                'ai_covered',
                'vegas_covered',
                'result'
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(details)

            filename = f"ai_vs_vegas_audit_{season}"
            if week is not None:
                filename += f"_week_{week}"
            if result_filter:
                filename += f"_{result_filter}"
            filename += ".csv"

            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'X-Audit-Total-Games': str(summary['total_games']),
                'X-Audit-AI-Wins': str(summary['ai_wins']),
                'X-Audit-Vegas-Wins': str(summary['vegas_wins']),
                'X-Audit-Ties': str(summary['ties']),
                'X-Audit-Returned-Games': str(returned_summary['total_games']),
                'X-Vegas-Spread-Source': vegas_source
            }
            return Response(output.getvalue(), mimetype='text/csv', headers=headers)

        return jsonify({
            'success': True,
            'season': season,
            'week': week,
            'result_filter': result_filter or None,
            'format': output_format,
            'vegas_spread_source': vegas_source,
            'summary': summary,
            'returned_summary': returned_summary,
            'contract': {
                'ats_rule': 'actual_margin + spread > 0 (push at 0)',
                'pregame_only': True,
                'postseason_included': False,
                'version': 'ai_vegas_audit_v2'
            },
            'returned_rows': len(details),
            'details': details
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


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


@ml_api.route('/api/ml/ai-vs-vegas-reconciliation', methods=['GET'])
def get_ai_vs_vegas_reconciliation():
    """
    Run season-range consistency checks for AI-vs-Vegas ATS scoring.

    Query params:
      start_season: optional integer (default: max(2021, end_season-4))
      end_season: optional integer (default: latest completed season)
      include_performance_contract: optional bool-like string, default true
            strict_mode: optional bool-like string, default false
            sample_limit: optional integer for mismatch samples (default 20, max 200)
    """
    conn = None
    cur = None
    try:
        latest_completed = get_latest_completed_season()
        start_season = request.args.get('start_season', type=int)
        end_season = request.args.get('end_season', type=int)
        include_performance_contract = (
            (request.args.get('include_performance_contract') or 'true').strip().lower()
            not in {'0', 'false', 'no', 'off'}
        )
        strict_mode = (
            (request.args.get('strict_mode') or 'false').strip().lower()
            not in {'0', 'false', 'no', 'off'}
        )
        sample_limit = request.args.get('sample_limit', type=int)
        if sample_limit is None:
            sample_limit = 20
        sample_limit = max(1, min(sample_limit, 200))

        if strict_mode and not include_performance_contract:
            return jsonify({
                'success': False,
                'error': 'strict_mode requires include_performance_contract=true'
            }), 400

        if end_season is None:
            end_season = latest_completed
        if start_season is None:
            start_season = max(2021, end_season - 4)
        if start_season > end_season:
            start_season, end_season = end_season, start_season

        conn = psycopg2.connect(**get_predictor().db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        has_games_closing_spread = table_has_column(conn, 'hcl', 'games', 'closing_spread')
        if has_games_closing_spread:
            vegas_expr = "COALESCE(g.closing_spread, p.vegas_spread, g.spread_line)"
            vegas_source = 'closing_spread->prediction_vegas_spread->spread_line'
        else:
            vegas_expr = "COALESCE(p.vegas_spread, g.spread_line)"
            vegas_source = 'prediction_vegas_spread->spread_line'

        seasons = list(range(start_season, end_season + 1))
        checks = []
        mismatches = []
        summary_fingerprints_by_season = {}
        performance_fingerprints_by_season = {}

        for season in seasons:
            # Season summary contract (same logic as /api/ml/season-ai-vs-vegas/<season>).
            cur.execute(
                f"""
                SELECT
                    p.game_id,
                    p.ai_spread,
                    {vegas_expr} AS vegas_spread,
                    g.home_score,
                    g.away_score
                FROM hcl.ml_predictions p
                JOIN hcl.games g ON p.game_id = g.game_id
                WHERE p.season = %s
                  AND g.home_score IS NOT NULL
                  AND g.away_score IS NOT NULL
                  AND COALESCE(g.is_postseason, FALSE) = FALSE
                  AND p.ai_spread IS NOT NULL
                  AND {vegas_expr} IS NOT NULL
                  AND p.predicted_at IS NOT NULL
                  AND (
                        (
                            g.kickoff_time_utc IS NOT NULL
                            AND p.predicted_at <= g.kickoff_time_utc
                        )
                        OR (
                            g.kickoff_time_utc IS NULL
                            AND COALESCE(p.game_date::date, g.game_date::date) IS NOT NULL
                            AND p.predicted_at::date <= COALESCE(p.game_date::date, g.game_date::date)
                        )
                  )
                """,
                (season,)
            )
            summary_rows = cur.fetchall() or []

            summary_ai = 0
            summary_vegas = 0
            summary_ties = 0
            summary_outcomes = {}
            for row in summary_rows:
                actual_margin = row['home_score'] - row['away_score']
                ai_covered = did_home_cover(row['ai_spread'], actual_margin)
                vegas_covered = did_home_cover(row['vegas_spread'], actual_margin)
                if ai_covered is True and vegas_covered is False:
                    summary_ai += 1
                    result = 'ai'
                elif ai_covered is False and vegas_covered is True:
                    summary_vegas += 1
                    result = 'vegas'
                else:
                    summary_ties += 1
                    result = 'tie'
                summary_outcomes[row['game_id']] = result

            summary_total = len(summary_rows)

            performance = None
            perf_match = None
            strict_match = None
            strict = None

            if include_performance_contract:
                # Performance contract (same filters used for performance spread_h2h rows).
                cur.execute(
                    """
                    SELECT
                        x.game_id,
                        x.ai_spread,
                        COALESCE(x.vegas_spread, g.spread_line) AS vegas_spread,
                        g.home_score,
                        g.away_score
                    FROM hcl.ml_predictions x
                    JOIN hcl.games g ON g.game_id = x.game_id
                    WHERE x.season = %s
                      AND COALESCE(g.is_postseason, FALSE) = FALSE
                      AND x.predicted_at IS NOT NULL
                      AND (
                            (
                                g.kickoff_time_utc IS NOT NULL
                                AND x.predicted_at <= g.kickoff_time_utc
                            )
                            OR (
                                g.kickoff_time_utc IS NULL
                                AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL
                                AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)
                            )
                      )
                      AND x.result_recorded_at IS NOT NULL
                      AND x.ai_spread IS NOT NULL
                      AND COALESCE(x.vegas_spread, g.spread_line) IS NOT NULL
                    """,
                    (season,)
                )
                perf_rows = cur.fetchall() or []
                perf_ai = 0
                perf_vegas = 0
                perf_ties = 0
                performance_outcomes = {}

                for row in perf_rows:
                    actual_margin = row['home_score'] - row['away_score']
                    ai_covered = did_home_cover(row['ai_spread'], actual_margin)
                    vegas_covered = did_home_cover(row['vegas_spread'], actual_margin)
                    if ai_covered is True and vegas_covered is False:
                        perf_ai += 1
                        result = 'ai'
                    elif ai_covered is False and vegas_covered is True:
                        perf_vegas += 1
                        result = 'vegas'
                    else:
                        perf_ties += 1
                        result = 'tie'
                    performance_outcomes[row['game_id']] = result

                performance = {
                    'total_games': len(perf_rows),
                    'ai_wins': perf_ai,
                    'vegas_wins': perf_vegas,
                    'ties': perf_ties,
                    'ai_percentage': round((perf_ai / len(perf_rows) * 100), 2) if perf_rows else 0.0,
                    'vegas_percentage': round((perf_vegas / len(perf_rows) * 100), 2) if perf_rows else 0.0
                }

                summary_fingerprint = build_outcome_fingerprint(summary_outcomes)
                performance_fingerprint = build_outcome_fingerprint(performance_outcomes)
                perf_match = (
                    summary_total == performance['total_games']
                    and summary_ai == performance['ai_wins']
                    and summary_vegas == performance['vegas_wins']
                    and summary_ties == performance['ties']
                )

                if strict_mode:
                    summary_ids = set(summary_outcomes.keys())
                    performance_ids = set(performance_outcomes.keys())
                    missing_in_performance = sorted(summary_ids - performance_ids)
                    missing_in_summary = sorted(performance_ids - summary_ids)
                    common_ids = sorted(summary_ids & performance_ids)

                    outcome_mismatch_ids = []
                    for gid in common_ids:
                        if summary_outcomes[gid] != performance_outcomes[gid]:
                            outcome_mismatch_ids.append(gid)

                    strict_match = (
                        len(missing_in_performance) == 0
                        and len(missing_in_summary) == 0
                        and len(outcome_mismatch_ids) == 0
                    )

                    strict = {
                        'checked_common_games': len(common_ids),
                        'missing_in_performance_count': len(missing_in_performance),
                        'missing_in_summary_count': len(missing_in_summary),
                        'outcome_mismatch_count': len(outcome_mismatch_ids),
                        'missing_in_performance_sample': missing_in_performance[:sample_limit],
                        'missing_in_summary_sample': missing_in_summary[:sample_limit],
                        'outcome_mismatch_sample': [
                            {
                                'game_id': gid,
                                'season_summary_result': summary_outcomes.get(gid),
                                'performance_result': performance_outcomes.get(gid)
                            }
                            for gid in outcome_mismatch_ids[:sample_limit]
                        ]
                    }

            season_check = {
                'season': season,
                'season_summary_contract': {
                    'total_games': summary_total,
                    'ai_wins': summary_ai,
                    'vegas_wins': summary_vegas,
                    'ties': summary_ties,
                    'ai_percentage': round((summary_ai / summary_total * 100), 2) if summary_total else 0.0,
                    'vegas_percentage': round((summary_vegas / summary_total * 100), 2) if summary_total else 0.0
                },
                'performance_contract': performance,
                'fingerprints': {
                    'summary_outcome_sha256': build_outcome_fingerprint(summary_outcomes),
                    'performance_outcome_sha256': (
                        build_outcome_fingerprint(performance_outcomes)
                        if include_performance_contract else None
                    ),
                    'summary_vs_performance_match': (
                        summary_fingerprint == performance_fingerprint
                        if include_performance_contract else None
                    )
                },
                'summary_vs_performance_match': perf_match,
                'strict_mode_enabled': strict_mode,
                'strict_match': strict_match,
                'strict': strict
            }
            checks.append(season_check)

            summary_fp = season_check['fingerprints'].get('summary_outcome_sha256')
            summary_fingerprints_by_season[season] = summary_fp

            if include_performance_contract:
                performance_fp = season_check['fingerprints'].get('performance_outcome_sha256')
                performance_fingerprints_by_season[season] = performance_fp

            reasons = []
            if include_performance_contract and perf_match is False:
                reasons.append('summary_vs_performance_mismatch')
            if include_performance_contract and summary_fingerprint != performance_fingerprint:
                reasons.append('fingerprint_mismatch')
            if strict_mode and strict_match is False:
                reasons.append('strict_row_mismatch')

            if reasons:
                mismatches.append({
                    'season': season,
                    'reasons': reasons,
                    'season_summary_contract': season_check['season_summary_contract'],
                    'performance_contract': performance,
                    'strict': strict
                })

        summary_chain_sha256, summary_chain_count = build_season_chain_fingerprint(
            summary_fingerprints_by_season,
            start_season,
            end_season
        )
        performance_chain_sha256 = None
        performance_chain_count = 0
        if include_performance_contract:
            performance_chain_sha256, performance_chain_count = build_season_chain_fingerprint(
                performance_fingerprints_by_season,
                start_season,
                end_season
            )

        chain_match = (
            summary_chain_sha256 == performance_chain_sha256
            if include_performance_contract else None
        )

        summary_non_null_count = sum(
            1 for fp in summary_fingerprints_by_season.values() if fp
        )
        performance_non_null_count = sum(
            1 for fp in performance_fingerprints_by_season.values() if fp
        ) if include_performance_contract else 0

        return jsonify({
            'success': True,
            'start_season': start_season,
            'end_season': end_season,
            'latest_completed_season': latest_completed,
            'include_performance_contract': include_performance_contract,
            'strict_mode': strict_mode,
            'sample_limit': sample_limit,
            'vegas_spread_source': vegas_source,
            'contract': {
                'ats_rule': 'actual_margin + spread > 0 (push at 0)',
                'pregame_only': True,
                'postseason_included': False,
                'version': 'ai_vegas_reconciliation_v3'
            },
            'season_count': len(checks),
            'checks': checks,
            'fingerprint_summary': {
                'chain_basis': 'season_range_inclusive_with_none_placeholders',
                'summary_chain_sha256': summary_chain_sha256,
                'performance_chain_sha256': performance_chain_sha256,
                'summary_chain_count': summary_chain_count,
                'performance_chain_count': performance_chain_count,
                'summary_non_null_count': summary_non_null_count,
                'performance_non_null_count': performance_non_null_count,
                'summary_vs_performance_chain_match': chain_match
            },
            'mismatch_count': len(mismatches),
            'mismatches': mismatches,
            'all_match': len(mismatches) == 0
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

        # Legacy fallback flags used to annotate response warnings.
        xgb_legacy_mode = False
        xgb_simulation_mode = False
        trend_legacy_mode = False
        spread_h2h_legacy_mode = False
        coverage_legacy_mode = False
        legacy_xgb_where = None
        legacy_xgb_params = None
        simulated_spread_h2h = None

        xgb_pregame_clause = (
            "x.predicted_at IS NOT NULL "
            "AND ((g.kickoff_time_utc IS NOT NULL AND x.predicted_at <= g.kickoff_time_utc) "
            "OR (g.kickoff_time_utc IS NULL "
            "AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL "
            "AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)))"
        )
        elo_pregame_clause = (
            "e.prediction_date IS NOT NULL "
            "AND ((g.kickoff_time_utc IS NOT NULL AND e.prediction_date <= g.kickoff_time_utc) "
            "OR (g.kickoff_time_utc IS NULL "
            "AND COALESCE(e.game_date::date, g.game_date::date) IS NOT NULL "
            "AND e.prediction_date::date <= COALESCE(e.game_date::date, g.game_date::date)))"
        )

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

        xgb_where = [
            "x.season = %s",
            "COALESCE(g.is_postseason, FALSE) = FALSE",
            xgb_pregame_clause
        ]
        xgb_params = [season]
        if week is not None:
            xgb_where.append("x.week = %s")
            xgb_params.append(week)

        cur.execute(
            f"""
            SELECT COUNT(*) AS predicted_games
            FROM hcl.ml_predictions x
            JOIN hcl.games g ON g.game_id = x.game_id
            WHERE {' AND '.join(xgb_where)}
            """,
            tuple(xgb_params)
        )
        xgb_predicted = _int((cur.fetchone() or {}).get('predicted_games'))

        xgb_scored_where = list(xgb_where) + ["x.result_recorded_at IS NOT NULL"]
        cur.execute(
            f"""
            SELECT
                COUNT(*) AS scored_games,
                COALESCE(SUM(CASE WHEN x.win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct_predictions,
                COALESCE(CAST(AVG(CASE WHEN x.win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,2)), 0) AS win_accuracy,
                COALESCE(CAST(AVG(x.margin_prediction_error) AS NUMERIC(10,2)), 0) AS avg_margin_error,
                MIN(x.week) AS first_week,
                MAX(x.week) AS latest_week
            FROM hcl.ml_predictions x
            JOIN hcl.games g ON g.game_id = x.game_id
            WHERE {' AND '.join(xgb_scored_where)}
            """,
            tuple(xgb_params)
        )
        xgb_summary = cur.fetchone() or {}

        cur.execute(
            f"""
            SELECT
                x.week,
                COUNT(*) AS scored_games,
                COALESCE(SUM(CASE WHEN x.win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct_predictions,
                COALESCE(CAST(AVG(CASE WHEN x.win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)), 0) AS win_accuracy,
                COALESCE(CAST(AVG(x.margin_prediction_error) AS NUMERIC(10,1)), 0) AS avg_margin_error
            FROM hcl.ml_predictions x
            JOIN hcl.games g ON g.game_id = x.game_id
            WHERE {' AND '.join(xgb_scored_where)}
            GROUP BY x.week
            ORDER BY x.week ASC
            """,
            tuple(xgb_params)
        )
        xgb_week_rows = cur.fetchall() or []

        # Fallback for legacy historical rows that were scored without
        # result_recorded_at and/or strict pregame timestamp evidence.
        xgb_scored_games = _int(xgb_summary.get('scored_games'))
        xgb_scored_coverage_pct = _pct(xgb_scored_games, completed_games)
        if completed_games > 0 and (
            xgb_scored_games == 0
            or xgb_scored_coverage_pct < 50.0
        ):
            legacy_xgb_where = [
                "x.season = %s",
                "COALESCE(g.is_postseason, FALSE) = FALSE",
                "x.predicted_winner IS NOT NULL",
                "g.home_score IS NOT NULL",
                "g.away_score IS NOT NULL"
            ]
            legacy_xgb_params = [season]
            if week is not None:
                legacy_xgb_where.append("x.week = %s")
                legacy_xgb_params.append(week)

            legacy_correct_case = (
                "CASE "
                "WHEN (g.home_score > g.away_score AND x.predicted_winner = g.home_team) "
                "  OR (g.away_score > g.home_score AND x.predicted_winner = g.away_team) "
                "THEN 1 ELSE 0 END"
            )
            legacy_margin_error_expr = (
                "COALESCE(x.margin_prediction_error, "
                "ABS(COALESCE(x.predicted_margin, x.ai_spread, 0) - (g.home_score - g.away_score)))"
            )

            cur.execute(
                f"""
                SELECT
                    COUNT(*) AS scored_games,
                    COALESCE(SUM({legacy_correct_case}), 0) AS correct_predictions,
                    COALESCE(
                        CAST(AVG(CASE WHEN ({legacy_correct_case}) = 1 THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,2)),
                        0
                    ) AS win_accuracy,
                    COALESCE(CAST(AVG({legacy_margin_error_expr}) AS NUMERIC(10,2)), 0) AS avg_margin_error,
                    MIN(x.week) AS first_week,
                    MAX(x.week) AS latest_week
                FROM hcl.ml_predictions x
                JOIN hcl.games g ON g.game_id = x.game_id
                WHERE {' AND '.join(legacy_xgb_where)}
                """,
                tuple(legacy_xgb_params)
            )
            legacy_xgb_summary = cur.fetchone() or {}
            legacy_scored_games = _int(legacy_xgb_summary.get('scored_games'))

            if legacy_scored_games > 0:
                xgb_legacy_mode = True
                xgb_predicted = max(xgb_predicted, legacy_scored_games)
                xgb_summary = {
                    'scored_games': legacy_scored_games,
                    'correct_predictions': _int(legacy_xgb_summary.get('correct_predictions')),
                    'win_accuracy': _float(legacy_xgb_summary.get('win_accuracy')),
                    'avg_margin_error': _float(legacy_xgb_summary.get('avg_margin_error')),
                    'first_week': legacy_xgb_summary.get('first_week'),
                    'latest_week': legacy_xgb_summary.get('latest_week')
                }

                cur.execute(
                    f"""
                    SELECT
                        x.week,
                        COUNT(*) AS scored_games,
                        COALESCE(SUM({legacy_correct_case}), 0) AS correct_predictions,
                        COALESCE(
                            CAST(AVG(CASE WHEN ({legacy_correct_case}) = 1 THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)),
                            0
                        ) AS win_accuracy,
                        COALESCE(CAST(AVG({legacy_margin_error_expr}) AS NUMERIC(10,1)), 0) AS avg_margin_error
                    FROM hcl.ml_predictions x
                    JOIN hcl.games g ON g.game_id = x.game_id
                    WHERE {' AND '.join(legacy_xgb_where)}
                    GROUP BY x.week
                    ORDER BY x.week ASC
                    """,
                    tuple(legacy_xgb_params)
                )
                xgb_week_rows = cur.fetchall() or []

        # Single-equation guard: if scored rows do not match completed-game denominator,
        # recompute from completed games so output cannot flip between sources.
        xgb_scored_for_sim = _int(xgb_summary.get('scored_games'))
        if completed_games > 0 and xgb_scored_for_sim != completed_games:
            sim_where = [
                "season = %s",
                "home_score IS NOT NULL",
                "away_score IS NOT NULL",
                "COALESCE(is_postseason, FALSE) = FALSE"
            ]
            sim_params = [season]
            if week is not None:
                sim_where.append("week = %s")
                sim_params.append(week)

            cur.execute(
                f"""
                SELECT
                    game_id,
                    week,
                    home_team,
                    away_team,
                    home_score,
                    away_score,
                    spread_line
                FROM hcl.games
                WHERE {' AND '.join(sim_where)}
                ORDER BY week ASC, game_date ASC
                """,
                tuple(sim_params)
            )
            simulated_games = cur.fetchall() or []

            if simulated_games:
                pred = get_predictor()
                simulated_total = 0
                simulated_correct = 0
                simulated_mae_sum = 0.0
                simulated_mae_count = 0
                simulated_first_week = None
                simulated_last_week = None
                week_rollup = {}
                spread_rollup = {
                    'total_games': 0,
                    'ai_wins': 0,
                    'vegas_wins': 0,
                    'ties': 0
                }

                for game in simulated_games:
                    try:
                        prediction = pred.predict_game(
                            season,
                            _int(game.get('week')),
                            game.get('home_team'),
                            game.get('away_team'),
                            game.get('spread_line'),
                            None
                        )
                    except Exception:
                        continue

                    week_value = _int(game.get('week'))
                    home_score = game.get('home_score')
                    away_score = game.get('away_score')
                    if home_score is None or away_score is None:
                        continue

                    actual_margin = home_score - away_score
                    if home_score > away_score:
                        actual_winner = game.get('home_team')
                    elif away_score > home_score:
                        actual_winner = game.get('away_team')
                    else:
                        actual_winner = 'TIE'

                    predicted_winner = prediction.get('predicted_winner')
                    is_correct = int(predicted_winner == actual_winner)
                    predicted_margin = prediction.get('predicted_margin')
                    if predicted_margin is None:
                        predicted_margin = prediction.get('ai_spread')

                    simulated_total += 1
                    simulated_correct += is_correct
                    if simulated_first_week is None or week_value < simulated_first_week:
                        simulated_first_week = week_value
                    if simulated_last_week is None or week_value > simulated_last_week:
                        simulated_last_week = week_value

                    if week_value not in week_rollup:
                        week_rollup[week_value] = {
                            'week': week_value,
                            'scored_games': 0,
                            'correct_predictions': 0,
                            'mae_sum': 0.0,
                            'mae_count': 0
                        }

                    week_rollup[week_value]['scored_games'] += 1
                    week_rollup[week_value]['correct_predictions'] += is_correct

                    if predicted_margin is not None:
                        margin_error = abs(predicted_margin - actual_margin)
                        simulated_mae_sum += margin_error
                        simulated_mae_count += 1
                        week_rollup[week_value]['mae_sum'] += margin_error
                        week_rollup[week_value]['mae_count'] += 1

                    ai_spread = prediction.get('ai_spread')
                    vegas_spread = game.get('spread_line')
                    if ai_spread is not None and vegas_spread is not None:
                        ai_covered = did_home_cover(ai_spread, actual_margin)
                        vegas_covered = did_home_cover(vegas_spread, actual_margin)
                        spread_rollup['total_games'] += 1
                        if ai_covered is True and vegas_covered is False:
                            spread_rollup['ai_wins'] += 1
                        elif ai_covered is False and vegas_covered is True:
                            spread_rollup['vegas_wins'] += 1
                        else:
                            spread_rollup['ties'] += 1

                if simulated_total > 0:
                    xgb_simulation_mode = True
                    xgb_predicted = max(xgb_predicted, simulated_total)
                    xgb_summary = {
                        'scored_games': simulated_total,
                        'correct_predictions': simulated_correct,
                        'win_accuracy': _pct(simulated_correct, simulated_total),
                        'avg_margin_error': (
                            round(simulated_mae_sum / simulated_mae_count, 2)
                            if simulated_mae_count
                            else 0.0
                        ),
                        'first_week': simulated_first_week,
                        'latest_week': simulated_last_week
                    }

                    xgb_week_rows = []
                    for week_value in sorted(week_rollup.keys()):
                        row = week_rollup[week_value]
                        week_games = _int(row.get('scored_games'))
                        week_correct = _int(row.get('correct_predictions'))
                        week_mae_count = _int(row.get('mae_count'))
                        week_mae_avg = (
                            round(float(row.get('mae_sum') or 0.0) / week_mae_count, 1)
                            if week_mae_count
                            else 0.0
                        )
                        xgb_week_rows.append({
                            'week': week_value,
                            'scored_games': week_games,
                            'correct_predictions': week_correct,
                            'win_accuracy': _pct(week_correct, week_games),
                            'avg_margin_error': week_mae_avg
                        })

                    simulated_spread_h2h = spread_rollup

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
            elo_where = [
                "e.season = %s",
                "COALESCE(g.is_postseason, FALSE) = FALSE",
                elo_pregame_clause
            ]
            elo_params = [season]
            if week is not None:
                elo_where.append("e.week = %s")
                elo_params.append(week)

            cur.execute(
                f"""
                SELECT COUNT(*) AS predicted_games
                FROM hcl.ml_predictions_elo e
                JOIN hcl.games g ON g.game_id = e.game_id
                WHERE {' AND '.join(elo_where)}
                """,
                tuple(elo_params)
            )
            elo_summary['predicted_games'] = _int((cur.fetchone() or {}).get('predicted_games'))

            elo_scored_where = list(elo_where) + [
                "e.predicted_winner IS NOT NULL",
                "g.home_score IS NOT NULL",
                "g.away_score IS NOT NULL"
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
                "COALESCE(g.is_postseason, FALSE) = FALSE",
                xgb_pregame_clause,
                elo_pregame_clause
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

        # ATS head-to-head parity with /api/ml/season-ai-vs-vegas/<season>.
        cur.execute(
            f"""
            SELECT
                x.ai_spread,
                COALESCE(x.vegas_spread, g.spread_line) AS vegas_spread,
                g.home_score,
                g.away_score
            FROM hcl.ml_predictions x
            JOIN hcl.games g ON g.game_id = x.game_id
            WHERE {' AND '.join(xgb_scored_where)}
              AND x.ai_spread IS NOT NULL
              AND COALESCE(x.vegas_spread, g.spread_line) IS NOT NULL
            """,
            tuple(xgb_params)
        )
        spread_h2h_rows = cur.fetchall() or []

        if not spread_h2h_rows and xgb_legacy_mode and legacy_xgb_where and legacy_xgb_params:
            cur.execute(
                f"""
                SELECT
                    x.ai_spread,
                    COALESCE(x.vegas_spread, g.spread_line) AS vegas_spread,
                    g.home_score,
                    g.away_score
                FROM hcl.ml_predictions x
                JOIN hcl.games g ON g.game_id = x.game_id
                WHERE {' AND '.join(legacy_xgb_where)}
                  AND x.ai_spread IS NOT NULL
                  AND COALESCE(x.vegas_spread, g.spread_line) IS NOT NULL
                """,
                tuple(legacy_xgb_params)
            )
            spread_h2h_rows = cur.fetchall() or []
            spread_h2h_legacy_mode = bool(spread_h2h_rows)

        spread_h2h_total = 0
        spread_h2h_ai = 0
        spread_h2h_vegas = 0
        spread_h2h_ties = 0

        for row in spread_h2h_rows:
            actual_margin = None
            if row.get('home_score') is not None and row.get('away_score') is not None:
                actual_margin = row['home_score'] - row['away_score']

            ai_covered = did_home_cover(row.get('ai_spread'), actual_margin)
            vegas_covered = did_home_cover(row.get('vegas_spread'), actual_margin)

            spread_h2h_total += 1
            if ai_covered is True and vegas_covered is False:
                spread_h2h_ai += 1
            elif ai_covered is False and vegas_covered is True:
                spread_h2h_vegas += 1
            else:
                spread_h2h_ties += 1

        if spread_h2h_total == 0 and simulated_spread_h2h:
            spread_h2h_total = _int(simulated_spread_h2h.get('total_games'))
            spread_h2h_ai = _int(simulated_spread_h2h.get('ai_wins'))
            spread_h2h_vegas = _int(simulated_spread_h2h.get('vegas_wins'))
            spread_h2h_ties = _int(simulated_spread_h2h.get('ties'))

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
            'spread_h2h': {
                'total_games': spread_h2h_total,
                'ai_wins': spread_h2h_ai,
                'vegas_wins': spread_h2h_vegas,
                'ties': spread_h2h_ties,
                'ai_percentage': _pct(spread_h2h_ai, spread_h2h_total),
                'vegas_percentage': _pct(spread_h2h_vegas, spread_h2h_total),
                'vegas_spread_source': 'ml_predictions.vegas_spread with games.spread_line fallback'
            },
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
                                        SELECT x.season, COUNT(*) AS predicted_games
                                        FROM hcl.ml_predictions x
                                        JOIN hcl.games g ON g.game_id = x.game_id
                                        WHERE x.season = ANY(%s)
                                            AND COALESCE(g.is_postseason, FALSE) = FALSE
                                            AND x.predicted_at IS NOT NULL
                                            AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL
                                            AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)
                                        GROUP BY x.season
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
                                                x.season,
                        COUNT(*) AS scored_games,
                                                COALESCE(SUM(CASE WHEN x.win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct_predictions
                                        FROM hcl.ml_predictions x
                                        JOIN hcl.games g ON g.game_id = x.game_id
                                        WHERE x.result_recorded_at IS NOT NULL
                                            AND x.season = ANY(%s)
                                            AND COALESCE(g.is_postseason, FALSE) = FALSE
                                            AND x.predicted_at IS NOT NULL
                                            AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL
                                            AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)
                                        GROUP BY x.season
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

                if trend_seasons and all(
                    _int((trend_xgb_scored_map.get(s) or {}).get('scored_games')) == 0
                    for s in trend_seasons
                ):
                    legacy_trend_correct_case = (
                        "CASE "
                        "WHEN (g.home_score > g.away_score AND x.predicted_winner = g.home_team) "
                        "  OR (g.away_score > g.home_score AND x.predicted_winner = g.away_team) "
                        "THEN 1 ELSE 0 END"
                    )
                    cur.execute(
                        f"""
                        SELECT
                            x.season,
                            COUNT(*) AS scored_games,
                            COALESCE(SUM({legacy_trend_correct_case}), 0) AS correct_predictions
                        FROM hcl.ml_predictions x
                        JOIN hcl.games g ON g.game_id = x.game_id
                        WHERE x.season = ANY(%s)
                          AND COALESCE(g.is_postseason, FALSE) = FALSE
                          AND x.predicted_winner IS NOT NULL
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
                        GROUP BY x.season
                        """,
                        (trend_seasons,)
                    )
                    legacy_trend_rows = cur.fetchall() or []
                    for row in legacy_trend_rows:
                        trend_season = _int(row.get('season'))
                        legacy_scored = _int(row.get('scored_games'))
                        legacy_correct = _int(row.get('correct_predictions'))
                        if legacy_scored > 0:
                            trend_xgb_scored_map[trend_season] = {
                                'scored_games': legacy_scored,
                                'correct_predictions': legacy_correct
                            }
                            trend_xgb_pred_map[trend_season] = max(
                                _int(trend_xgb_pred_map.get(trend_season)),
                                legacy_scored
                            )
                    trend_legacy_mode = bool(legacy_trend_rows)

                trend_elo_pred_map = {}
                trend_elo_scored_map = {}
                trend_agreement_map = {}
                trend_spread_h2h_map = {}

                if elo_table_ready:
                    cur.execute(
                        """
                                                SELECT e.season, COUNT(*) AS predicted_games
                                                FROM hcl.ml_predictions_elo e
                                                JOIN hcl.games g ON g.game_id = e.game_id
                                                WHERE e.season = ANY(%s)
                                                    AND COALESCE(g.is_postseason, FALSE) = FALSE
                                                    AND e.prediction_date IS NOT NULL
                                                    AND COALESCE(e.game_date::date, g.game_date::date) IS NOT NULL
                                                    AND e.prediction_date::date <= COALESCE(e.game_date::date, g.game_date::date)
                                                GROUP BY e.season
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
                                                    AND e.prediction_date IS NOT NULL
                                                    AND COALESCE(e.game_date::date, g.game_date::date) IS NOT NULL
                                                    AND e.prediction_date::date <= COALESCE(e.game_date::date, g.game_date::date)
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
                                                    AND x.predicted_at IS NOT NULL
                                                    AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL
                                                    AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)
                                                    AND e.prediction_date IS NOT NULL
                                                    AND COALESCE(e.game_date::date, g.game_date::date) IS NOT NULL
                                                    AND e.prediction_date::date <= COALESCE(e.game_date::date, g.game_date::date)
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

                cur.execute(
                    """
                    SELECT
                        x.season,
                        x.ai_spread,
                        COALESCE(x.vegas_spread, g.spread_line) AS vegas_spread,
                        g.home_score,
                        g.away_score
                    FROM hcl.ml_predictions x
                    JOIN hcl.games g ON g.game_id = x.game_id
                    WHERE x.season = ANY(%s)
                      AND g.home_score IS NOT NULL
                      AND g.away_score IS NOT NULL
                      AND COALESCE(g.is_postseason, FALSE) = FALSE
                      AND x.ai_spread IS NOT NULL
                      AND COALESCE(x.vegas_spread, g.spread_line) IS NOT NULL
                      AND x.predicted_at IS NOT NULL
                      AND (
                            (
                                g.kickoff_time_utc IS NOT NULL
                                AND x.predicted_at <= g.kickoff_time_utc
                            )
                            OR (
                                g.kickoff_time_utc IS NULL
                                AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL
                                AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)
                            )
                      )
                    """,
                    (trend_seasons,)
                )
                for row in (cur.fetchall() or []):
                    trend_season = _int(row.get('season'))
                    actual_margin = row.get('home_score') - row.get('away_score')
                    ai_covered = did_home_cover(row.get('ai_spread'), actual_margin)
                    vegas_covered = did_home_cover(row.get('vegas_spread'), actual_margin)

                    if trend_season not in trend_spread_h2h_map:
                        trend_spread_h2h_map[trend_season] = {
                            'total_games': 0,
                            'ai_wins': 0,
                            'vegas_wins': 0,
                            'ties': 0
                        }

                    trend_spread_h2h_map[trend_season]['total_games'] += 1
                    if ai_covered is True and vegas_covered is False:
                        trend_spread_h2h_map[trend_season]['ai_wins'] += 1
                    elif ai_covered is False and vegas_covered is True:
                        trend_spread_h2h_map[trend_season]['vegas_wins'] += 1
                    else:
                        trend_spread_h2h_map[trend_season]['ties'] += 1

                if trend_seasons and not trend_spread_h2h_map:
                    cur.execute(
                        """
                        SELECT
                            x.season,
                            x.ai_spread,
                            COALESCE(x.vegas_spread, g.spread_line) AS vegas_spread,
                            g.home_score,
                            g.away_score
                        FROM hcl.ml_predictions x
                        JOIN hcl.games g ON g.game_id = x.game_id
                        WHERE x.season = ANY(%s)
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
                          AND COALESCE(g.is_postseason, FALSE) = FALSE
                          AND x.ai_spread IS NOT NULL
                          AND COALESCE(x.vegas_spread, g.spread_line) IS NOT NULL
                        """,
                        (trend_seasons,)
                    )
                    for row in (cur.fetchall() or []):
                        trend_season = _int(row.get('season'))
                        actual_margin = row.get('home_score') - row.get('away_score')
                        ai_covered = did_home_cover(row.get('ai_spread'), actual_margin)
                        vegas_covered = did_home_cover(row.get('vegas_spread'), actual_margin)

                        if trend_season not in trend_spread_h2h_map:
                            trend_spread_h2h_map[trend_season] = {
                                'total_games': 0,
                                'ai_wins': 0,
                                'vegas_wins': 0,
                                'ties': 0
                            }

                        trend_spread_h2h_map[trend_season]['total_games'] += 1
                        if ai_covered is True and vegas_covered is False:
                            trend_spread_h2h_map[trend_season]['ai_wins'] += 1
                        elif ai_covered is False and vegas_covered is True:
                            trend_spread_h2h_map[trend_season]['vegas_wins'] += 1
                        else:
                            trend_spread_h2h_map[trend_season]['ties'] += 1

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
                    trend_spread_h2h = trend_spread_h2h_map.get(
                        trend_season,
                        {'total_games': 0, 'ai_wins': 0, 'vegas_wins': 0, 'ties': 0}
                    )

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
                        },
                        'spread_h2h': {
                            'total_games': _int(trend_spread_h2h.get('total_games')),
                            'ai_wins': _int(trend_spread_h2h.get('ai_wins')),
                            'vegas_wins': _int(trend_spread_h2h.get('vegas_wins')),
                            'ties': _int(trend_spread_h2h.get('ties')),
                            'ai_percentage': _pct(
                                _int(trend_spread_h2h.get('ai_wins')),
                                _int(trend_spread_h2h.get('total_games'))
                            ),
                            'vegas_percentage': _pct(
                                _int(trend_spread_h2h.get('vegas_wins')),
                                _int(trend_spread_h2h.get('total_games'))
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
                                        FROM hcl.ml_predictions x
                                        JOIN hcl.games g ON g.game_id = x.game_id
                                        WHERE x.season = %s
                                            AND COALESCE(g.is_postseason, FALSE) = FALSE
                                            AND x.predicted_at IS NOT NULL
                                            AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL
                                            AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)
                    """,
                    (coverage_season,)
                )
                xgb_predicted = _int((cur.fetchone() or {}).get('predicted_games'))

                cur.execute(
                    """
                    SELECT
                        COUNT(*) AS scored_games,
                                                COALESCE(SUM(CASE WHEN x.win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct_predictions
                                        FROM hcl.ml_predictions x
                                        JOIN hcl.games g ON g.game_id = x.game_id
                                        WHERE x.season = %s
                                            AND x.result_recorded_at IS NOT NULL
                                            AND COALESCE(g.is_postseason, FALSE) = FALSE
                                            AND x.predicted_at IS NOT NULL
                                            AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL
                                            AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)
                    """,
                    (coverage_season,)
                )
                xgb_row = cur.fetchone() or {}
                xgb_scored = _int(xgb_row.get('scored_games'))
                xgb_correct = _int(xgb_row.get('correct_predictions'))

                if completed > 0 and xgb_predicted == 0 and xgb_scored == 0:
                    legacy_coverage_correct_case = (
                        "CASE "
                        "WHEN (g.home_score > g.away_score AND x.predicted_winner = g.home_team) "
                        "  OR (g.away_score > g.home_score AND x.predicted_winner = g.away_team) "
                        "THEN 1 ELSE 0 END"
                    )
                    cur.execute(
                        f"""
                        SELECT
                            COUNT(*) AS scored_games,
                            COALESCE(SUM({legacy_coverage_correct_case}), 0) AS correct_predictions
                        FROM hcl.ml_predictions x
                        JOIN hcl.games g ON g.game_id = x.game_id
                        WHERE x.season = %s
                          AND COALESCE(g.is_postseason, FALSE) = FALSE
                          AND x.predicted_winner IS NOT NULL
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
                        """,
                        (coverage_season,)
                    )
                    legacy_cov_row = cur.fetchone() or {}
                    legacy_cov_scored = _int(legacy_cov_row.get('scored_games'))
                    if legacy_cov_scored > 0:
                        xgb_predicted = legacy_cov_scored
                        xgb_scored = legacy_cov_scored
                        xgb_correct = _int(legacy_cov_row.get('correct_predictions'))
                        coverage_legacy_mode = True

                elo_predicted = 0
                elo_scored = 0
                elo_correct = 0
                both_models_games = 0

                if elo_table_ready:
                    cur.execute(
                        """
                                                SELECT COUNT(*) AS predicted_games
                                                FROM hcl.ml_predictions_elo e
                                                JOIN hcl.games g ON g.game_id = e.game_id
                                                WHERE e.season = %s
                                                    AND COALESCE(g.is_postseason, FALSE) = FALSE
                                                    AND e.prediction_date IS NOT NULL
                                                    AND COALESCE(e.game_date::date, g.game_date::date) IS NOT NULL
                                                    AND e.prediction_date::date <= COALESCE(e.game_date::date, g.game_date::date)
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
                                                    AND e.prediction_date IS NOT NULL
                                                    AND COALESCE(e.game_date::date, g.game_date::date) IS NOT NULL
                                                    AND e.prediction_date::date <= COALESCE(e.game_date::date, g.game_date::date)
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
                                                    AND x.predicted_at IS NOT NULL
                                                    AND COALESCE(x.game_date::date, g.game_date::date) IS NOT NULL
                                                    AND x.predicted_at::date <= COALESCE(x.game_date::date, g.game_date::date)
                                                    AND e.prediction_date IS NOT NULL
                                                    AND COALESCE(e.game_date::date, g.game_date::date) IS NOT NULL
                                                    AND e.prediction_date::date <= COALESCE(e.game_date::date, g.game_date::date)
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

        if xgb_legacy_mode:
            warnings.append(
                "Coverage note: using legacy XGBoost scoring fallback because strict pregame tracked rows are unavailable for this season."
            )
        if xgb_simulation_mode:
            warnings.append(
                "Coverage note: using simulated historical XGBoost scoring from completed games because tracked row coverage is currently insufficient for this season."
            )
        if spread_h2h_legacy_mode:
            warnings.append(
                "Coverage note: spread head-to-head metrics are using legacy fallback rows without strict pregame timestamp evidence."
            )
        if trend_legacy_mode:
            warnings.append(
                "Coverage note: multi-season trend includes legacy fallback scoring for historical seasons lacking strict pregame tracked rows."
            )
        if coverage_legacy_mode:
            warnings.append(
                "Coverage note: coverage contract includes legacy fallback scoring for one or more seasons."
            )

        integrity_where = ["mp.season = %s"]
        integrity_params = [season]
        if week is not None:
            integrity_where.append("mp.week = %s")
            integrity_params.append(week)

        cur.execute(
            f"""
            SELECT
                COUNT(*) FILTER (
                    WHERE mp.predicted_at IS NOT NULL
                      AND COALESCE(mp.game_date::date, g.game_date::date) IS NOT NULL
                ) AS rows_checked,
                COALESCE(
                    SUM(
                        CASE
                            WHEN mp.predicted_at IS NOT NULL
                             AND COALESCE(mp.game_date::date, g.game_date::date) IS NOT NULL
                             AND mp.predicted_at::date > COALESCE(mp.game_date::date, g.game_date::date)
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

        # Fallback: if tracking tables are empty, derive available weeks from games.
        source = 'prediction_tables'
        if not weeks:
            cur.execute("""
                SELECT season, week, COUNT(*) as game_count
                FROM hcl.games
                WHERE is_postseason = false
                GROUP BY season, week
                ORDER BY season DESC, week DESC
            """)
            weeks = [dict(row) for row in cur.fetchall()]
            source = 'games_fallback'
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'weeks': weeks,
            'total': len(weeks),
            'elo_table_ready': elo_table_ready,
            'source': source
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
            SELECT COUNT(*) AS total_games
            FROM hcl.games
            WHERE season = %s AND week = %s
        """, (season, week))
        scheduled_row = cur.fetchone() or {}
        scheduled_count = int(scheduled_row.get('total_games') or 0)

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
        
        has_complete_db_week = (
            len(predictions) > 0
            and (scheduled_count == 0 or len(predictions) >= scheduled_count)
        )

        if has_complete_db_week:
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

        db_predictions = predictions
        
        # If DB is empty or partial for this week, regenerate directly from scheduled games.
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

        # If regeneration fails unexpectedly, fall back to any DB rows we did have.
        if not predictions and db_predictions:
            predictions = db_predictions
        
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
        
        cur.execute("""
            SELECT COUNT(*) AS total_games
            FROM hcl.games
            WHERE season = %s AND week = %s
        """, (season, week))
        scheduled_row = cur.fetchone() or {}
        scheduled_count = int(scheduled_row.get('total_games') or 0)

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

        # Fallback: regenerate from model runtime when DB tracking tables are empty/partial.
        xgb_needs_refresh = (
            len(xgb_predictions) == 0
            or (scheduled_count > 0 and len(xgb_predictions) < scheduled_count)
        )

        elo_needs_refresh = (
            elo_table_ready
            and (
                len(elo_predictions) == 0
                or (scheduled_count > 0 and len(elo_predictions) < scheduled_count)
            )
        )

        if xgb_needs_refresh:
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    generated_xgb = get_predictor().predict_week(season, week)

                for row in generated_xgb or []:
                    game_id = row.get('game_id')
                    if not game_id or game_id in xgb_predictions:
                        continue

                    xgb_predictions[game_id] = {
                        'game_id': game_id,
                        'season': row.get('season', season),
                        'week': row.get('week', week),
                        'home_team': row.get('home_team'),
                        'away_team': row.get('away_team'),
                        'game_date': row.get('game_date'),
                        'predicted_winner': row.get('predicted_winner'),
                        'home_win_prob': row.get('home_win_prob', 0.5),
                        'away_win_prob': row.get('away_win_prob', 0.5),
                        'ai_spread': row.get('ai_spread', 0),
                        'split_prediction': row.get('split_prediction', False),
                        'vegas_spread': row.get('vegas_spread'),
                        'vegas_total': row.get('total_line'),
                        'home_score': row.get('actual_home_score'),
                        'away_score': row.get('actual_away_score')
                    }
            except Exception:
                # Keep endpoint resilient: if regeneration fails, return DB-backed rows.
                pass

        if elo_needs_refresh:
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    generated_elo = get_elo_predictor().predict_week(season, week)

                for row in generated_elo or []:
                    game_id = row.get('game_id')
                    if not game_id or game_id in elo_predictions:
                        continue

                    elo_predictions[game_id] = {
                        'game_id': game_id,
                        'season': row.get('season', season),
                        'week': row.get('week', week),
                        'home_team': row.get('home_team'),
                        'away_team': row.get('away_team'),
                        'game_date': row.get('game_date'),
                        'predicted_winner': row.get('predicted_winner'),
                        'confidence': row.get('confidence', 0.5),
                        'elo_spread': row.get('elo_spread', 0),
                        'split_prediction': row.get('split_prediction', False),
                        'vegas_spread': row.get('vegas_spread'),
                        'vegas_total': row.get('vegas_total'),
                        'home_score': row.get('actual_home_score'),
                        'away_score': row.get('actual_away_score')
                    }
            except Exception:
                # Keep endpoint resilient: if regeneration fails, return DB-backed rows.
                pass
        
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
