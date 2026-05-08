"""Verify TA-020 s20_3: Elo API routes return 200 and consume updated ratings."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg2


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import api_routes_ml as ml_routes  # noqa: E402
from api_server import app  # noqa: E402


def db_config() -> dict[str, Any]:
    return {
        "dbname": os.getenv("DB_NAME", "nfl_analytics"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
    }


def pick_elo_week() -> tuple[int, int, bool]:
    """Pick a week, preferring one with no cached Elo predictions."""
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**db_config())
        cur = conn.cursor()
        cur.execute(
            """
            SELECT g.season, g.week
            FROM hcl.games g
            LEFT JOIN hcl.ml_predictions_elo e ON g.game_id = e.game_id
            GROUP BY g.season, g.week
            HAVING COUNT(e.game_id) = 0
            ORDER BY g.season DESC, g.week DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if row:
            return int(row[0]), int(row[1]), False

        cur.execute(
            """
            SELECT season, week
            FROM hcl.ml_predictions_elo
            GROUP BY season, week
            ORDER BY season DESC, week DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if row:
            return int(row[0]), int(row[1]), True
    except Exception:
        pass
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return 2025, 18, False


def build_report(summary: dict[str, Any]) -> str:
    sample = summary.get("prediction_sample") or {}
    checks = summary.get("checks") or {}

    lines = [
        "# TA-020 s20_3 Evidence Report",
        "",
        "## Objective",
        "Verify Elo API routes return HTTP 200 and consume refreshed Elo ratings data.",
        "",
        "## Endpoints Tested",
        "- GET /api/elo/ratings/current",
        f"- GET /api/elo/predict-week/{summary.get('target_season')}/{summary.get('target_week')}",
        "",
        "## Route Results",
        f"- ratings_current_status: {summary.get('ratings_status')}",
        f"- predict_week_status: {summary.get('predict_status')}",
        f"- predict_source: {summary.get('predict_source')}",
        f"- predict_total_games: {summary.get('predict_total_games')}",
        f"- predict_message: {summary.get('predict_message')}",
        "",
        "## Ratings Consumption Validation",
        f"- file_last_updated: {summary.get('file_last_updated')}",
        f"- route_last_updated: {summary.get('route_last_updated')}",
        f"- file_ratings_count: {summary.get('file_ratings_count')}",
        f"- route_ratings_count: {summary.get('route_ratings_count')}",
        f"- top_team_file: {summary.get('top_team_file')} ({summary.get('top_rating_file')})",
        f"- top_team_route: {summary.get('top_team_route')} ({summary.get('top_rating_route')})",
        f"- predictor_top_rating: {summary.get('predictor_top_rating')}",
        "",
        "## Prediction Sample",
        f"- game_id: {sample.get('game_id')}",
        f"- matchup: {sample.get('away_team')} at {sample.get('home_team')}",
        f"- home_elo: {sample.get('home_elo')}",
        f"- away_elo: {sample.get('away_elo')}",
        f"- home_rating_current: {sample.get('home_rating_current')}",
        f"- away_rating_current: {sample.get('away_rating_current')}",
        f"- predicted_winner: {sample.get('predicted_winner')}",
        "",
        "## Checks",
        f"- ratings_route_status_200: {checks.get('ratings_route_status_200')}",
        f"- predict_route_status_200: {checks.get('predict_route_status_200')}",
        f"- ratings_last_updated_matches_file: {checks.get('ratings_last_updated_matches_file')}",
        f"- ratings_count_32: {checks.get('ratings_count_32')}",
        f"- top_ranking_matches_file: {checks.get('top_ranking_matches_file')}",
        f"- predictor_uses_current_ratings: {checks.get('predictor_uses_current_ratings')}",
        f"- predict_route_generation_path: {checks.get('predict_route_generation_path')}",
        f"- predict_payload_uses_current_ratings: {checks.get('predict_payload_uses_current_ratings')}",
        f"- all_checks_passed: {summary.get('all_checks_passed')}",
        "",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="TA-020 Elo API route verifier")
    parser.add_argument(
        "--ratings-file",
        default=str(PROJECT_ROOT / "ml" / "models" / "elo_ratings_current.json"),
    )
    parser.add_argument("--summary-out", required=False)
    parser.add_argument("--report-out", required=False)
    args = parser.parse_args()

    ratings_path = Path(args.ratings_file)
    file_data = json.loads(ratings_path.read_text(encoding="utf-8"))
    file_ratings = file_data.get("ratings", {})
    file_last_updated = file_data.get("last_updated")

    file_sorted = sorted(file_ratings.items(), key=lambda item: item[1], reverse=True)
    top_team_file, top_rating_file = file_sorted[0]

    # Reset lazy singletons to ensure current file is loaded for this verification.
    ml_routes.elo_tracker = None
    ml_routes.elo_predictor = None

    client = app.test_client()

    ratings_resp = client.get("/api/elo/ratings/current")
    ratings_json = ratings_resp.get_json(silent=True) or {}

    route_ratings = ratings_json.get("ratings") or {}
    rankings = ratings_json.get("rankings") or []
    top_team_route = rankings[0]["team"] if rankings else None
    top_rating_route = rankings[0]["rating"] if rankings else None

    target_season, target_week, had_db_week = pick_elo_week()
    predict_resp = client.get(f"/api/elo/predict-week/{target_season}/{target_week}")
    predict_json = predict_resp.get_json(silent=True) or {}

    predictions = predict_json.get("predictions") or []
    predict_message = predict_json.get("message")
    prediction_sample = {}
    predict_payload_uses_current_ratings = True

    if predictions:
        sample = predictions[0]
        home_team = sample.get("home_team")
        away_team = sample.get("away_team")
        home_current = route_ratings.get(home_team)
        away_current = route_ratings.get(away_team)
        home_elo = sample.get("home_elo")
        away_elo = sample.get("away_elo")

        # Allow small rounding drift because route values are rounded to 1 decimal.
        home_ok = home_current is not None and home_elo is not None and abs(float(home_elo) - float(home_current)) <= 0.2
        away_ok = away_current is not None and away_elo is not None and abs(float(away_elo) - float(away_current)) <= 0.2
        predict_payload_uses_current_ratings = bool(home_ok and away_ok)

        prediction_sample = {
            "game_id": sample.get("game_id"),
            "home_team": home_team,
            "away_team": away_team,
            "home_elo": home_elo,
            "away_elo": away_elo,
            "home_rating_current": home_current,
            "away_rating_current": away_current,
            "predicted_winner": sample.get("predicted_winner"),
        }

    predictor = ml_routes.get_elo_predictor()
    predictor_top_rating = round(float(predictor.tracker.elo.get_rating(top_team_file)), 1)

    checks = {
        "ratings_route_status_200": ratings_resp.status_code == 200,
        "predict_route_status_200": predict_resp.status_code == 200,
        "ratings_last_updated_matches_file": ratings_json.get("last_updated") == file_last_updated,
        "ratings_count_32": len(route_ratings) == 32,
        "top_ranking_matches_file": top_team_route == top_team_file and (top_rating_route is not None) and abs(float(top_rating_route) - round(float(top_rating_file), 1)) <= 0.2,
        "predictor_uses_current_ratings": abs(predictor_top_rating - round(float(top_rating_file), 1)) <= 0.2,
        "predict_route_generation_path": not had_db_week,
        "predict_payload_uses_current_ratings": predict_payload_uses_current_ratings,
    }

    all_checks_passed = all(checks.values())

    summary = {
        "task": "TA-020",
        "subtask": "s20_3",
        "ratings_file": str(ratings_path),
        "file_last_updated": file_last_updated,
        "file_ratings_count": len(file_ratings),
        "route_last_updated": ratings_json.get("last_updated"),
        "route_ratings_count": len(route_ratings),
        "ratings_status": ratings_resp.status_code,
        "predict_status": predict_resp.status_code,
        "target_season": target_season,
        "target_week": target_week,
        "predict_source": "db_ml_predictions_elo" if had_db_week else "runtime_generation_path",
        "predict_total_games": len(predictions),
        "predict_message": predict_message,
        "top_team_file": top_team_file,
        "top_rating_file": round(float(top_rating_file), 1),
        "top_team_route": top_team_route,
        "top_rating_route": top_rating_route,
        "predictor_top_rating": predictor_top_rating,
        "prediction_sample": prediction_sample,
        "checks": checks,
        "all_checks_passed": all_checks_passed,
    }

    print(f"ratings_status={summary['ratings_status']}")
    print(f"predict_status={summary['predict_status']}")
    print(f"target_week={summary['target_season']}-W{summary['target_week']}")
    print(f"predict_total_games={summary['predict_total_games']}")
    print(f"top_team_file={summary['top_team_file']}")
    print(f"top_team_route={summary['top_team_route']}")
    print(f"all_checks_passed={summary['all_checks_passed']}")

    if args.summary_out:
        summary_path = Path(args.summary_out)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"summary_out={summary_path}")

    if args.report_out:
        report_path = Path(args.report_out)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(build_report(summary), encoding="utf-8")
        print(f"report_out={report_path}")

    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
