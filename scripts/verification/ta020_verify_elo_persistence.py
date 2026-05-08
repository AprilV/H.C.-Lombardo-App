"""Validate Elo artifact persistence and workflow consumption for TA-020 s20_2."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_DIR = PROJECT_ROOT / "ml"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from elo_tracker import EloTracker  # noqa: E402
from predict_elo import EloPredictionSystem  # noqa: E402


def build_report(summary: dict) -> str:
    sample = summary.get("sample_prediction") or {}
    checks = summary.get("checks") or {}
    lines = [
        "# TA-020 s20_2 Evidence Report",
        "",
        "## Objective",
        "Persist refreshed Elo outputs and verify they are consumed by tracker and predictor workflows.",
        "",
        "## Artifact",
        f"- Ratings file: {summary.get('ratings_file')}",
        f"- Exists: {summary.get('ratings_file_exists')}",
        f"- Size bytes: {summary.get('ratings_file_size_bytes')}",
        f"- Last updated: {summary.get('ratings_last_updated')}",
        "",
        "## Validation Results",
        f"- ratings_count: {summary.get('ratings_count')}",
        f"- missing_teams_count: {len(summary.get('missing_teams') or [])}",
        f"- tracker_load_success: {summary.get('tracker_load_success')}",
        f"- tracker_ratings_count: {summary.get('tracker_ratings_count')}",
        f"- predictor_ratings_count: {summary.get('predictor_ratings_count')}",
        "",
        "## Sample Predictor Output",
        f"- Matchup: {sample.get('away_team')} at {sample.get('home_team')}",
        f"- Predicted winner: {sample.get('predicted_winner')}",
        f"- Home win probability: {sample.get('home_win_prob')}",
        f"- Away win probability: {sample.get('away_win_prob')}",
        f"- Elo spread: {sample.get('elo_spread')}",
        "",
        "## Checks",
        f"- ratings_file_exists: {checks.get('ratings_file_exists')}",
        f"- ratings_count_32: {checks.get('ratings_count_32')}",
        f"- tracker_load_success: {checks.get('tracker_load_success')}",
        f"- predictor_uses_ratings: {checks.get('predictor_uses_ratings')}",
        f"- sample_prediction_generated: {checks.get('sample_prediction_generated')}",
        f"- all_checks_passed: {summary.get('all_checks_passed')}",
        "",
    ]
    missing = summary.get("missing_teams") or []
    if missing:
        lines.append("## Missing Teams")
        lines.extend([f"- {team}" for team in missing])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="TA-020 Elo persistence verifier")
    parser.add_argument(
        "--ratings-file",
        default=str(PROJECT_ROOT / "ml" / "models" / "elo_ratings_current.json"),
    )
    parser.add_argument("--summary-out", required=False)
    parser.add_argument("--report-out", required=False)
    parser.add_argument("--sample-home", default="KC")
    parser.add_argument("--sample-away", default="BUF")
    args = parser.parse_args()

    ratings_path = Path(args.ratings_file)
    ratings_file_exists = ratings_path.exists()

    raw = {}
    if ratings_file_exists:
        raw = json.loads(ratings_path.read_text(encoding="utf-8"))

    ratings = raw.get("ratings", {}) if isinstance(raw, dict) else {}
    params = raw.get("system_params", {}) if isinstance(raw, dict) else {}

    missing_teams = sorted(set(EloTracker.NFL_TEAMS) - set(ratings.keys()))

    tracker = EloTracker()
    tracker_load_success = tracker.load_current_ratings(filepath=str(ratings_path))
    tracker_ratings_count = len(tracker.elo.get_all_ratings()) if tracker_load_success else 0

    predictor = EloPredictionSystem()
    predictor_ratings_count = len(predictor.tracker.elo.get_all_ratings())
    sample_prediction = predictor.predict_game(args.sample_home, args.sample_away)

    checks = {
        "ratings_file_exists": ratings_file_exists,
        "ratings_count_32": len(ratings) == 32,
        "tracker_load_success": tracker_load_success,
        "predictor_uses_ratings": predictor_ratings_count == 32,
        "sample_prediction_generated": isinstance(sample_prediction, dict)
        and bool(sample_prediction.get("predicted_winner")),
    }

    all_checks_passed = all(checks.values()) and len(missing_teams) == 0

    summary = {
        "task": "TA-020",
        "subtask": "s20_2",
        "ratings_file": str(ratings_path),
        "ratings_file_exists": ratings_file_exists,
        "ratings_file_size_bytes": ratings_path.stat().st_size if ratings_file_exists else 0,
        "ratings_last_updated": raw.get("last_updated") if isinstance(raw, dict) else None,
        "ratings_count": len(ratings),
        "missing_teams": missing_teams,
        "system_params": params,
        "tracker_load_success": tracker_load_success,
        "tracker_ratings_count": tracker_ratings_count,
        "predictor_ratings_count": predictor_ratings_count,
        "sample_prediction": {
            "home_team": sample_prediction.get("home_team"),
            "away_team": sample_prediction.get("away_team"),
            "predicted_winner": sample_prediction.get("predicted_winner"),
            "home_win_prob": sample_prediction.get("home_win_prob"),
            "away_win_prob": sample_prediction.get("away_win_prob"),
            "elo_spread": sample_prediction.get("elo_spread"),
        },
        "checks": checks,
        "all_checks_passed": all_checks_passed,
    }

    print(f"ratings_file_exists={summary['ratings_file_exists']}")
    print(f"ratings_count={summary['ratings_count']}")
    print(f"missing_teams_count={len(summary['missing_teams'])}")
    print(f"tracker_load_success={summary['tracker_load_success']}")
    print(f"predictor_ratings_count={summary['predictor_ratings_count']}")
    print(f"sample_predicted_winner={summary['sample_prediction']['predicted_winner']}")
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
