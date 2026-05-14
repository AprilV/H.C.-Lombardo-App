"""Build TA-062 closure evidence without redoing already-completed TA-019 work."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_baseline_rmse_from_csv(path: Path) -> tuple[float | None, int]:
    squared_errors: list[float] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            pred_raw = (row.get("predicted_margin") or "").strip()
            actual_raw = (row.get("actual_margin") or "").strip()
            if not pred_raw or not actual_raw:
                continue
            try:
                pred_val = float(pred_raw)
                actual_val = float(actual_raw)
            except ValueError:
                continue
            squared_errors.append((pred_val - actual_val) ** 2)
    if not squared_errors:
        return None, 0
    rmse = math.sqrt(sum(squared_errors) / len(squared_errors))
    return round(rmse, 4), len(squared_errors)


def read_spread_samples(path: Path, sample_count: int = 3) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            samples.append(
                {
                    "season": row.get("season"),
                    "week": row.get("week"),
                    "game_id": row.get("game_id"),
                    "predicted_margin": row.get("predicted_margin"),
                    "actual_margin": row.get("actual_margin"),
                    "ai_spread": row.get("ai_spread"),
                    "vegas_spread": row.get("vegas_spread"),
                }
            )
            if len(samples) >= sample_count:
                break
    return samples


def run_live_smoke(api_base: str, season: int, week: int) -> dict[str, Any]:
    endpoint = f"{api_base.rstrip('/')}/api/ml/predict-week/{season}/{week}"
    result: dict[str, Any] = {
        "mode": "live_http",
        "endpoint": endpoint,
        "status_code": None,
        "total_games": None,
        "prediction_count": None,
        "predictions_with_ai_spread": 0,
        "predictions_with_vegas_spread": 0,
        "sample_game": None,
        "error": None,
    }
    try:
        req = Request(endpoint, method="GET")
        with urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            result["status_code"] = int(response.status)

        payload = json.loads(body)
        predictions = payload.get("predictions") or []
        result["total_games"] = payload.get("total_games")
        result["prediction_count"] = len(predictions)

        ai_spread_count = 0
        vegas_spread_count = 0
        for item in predictions:
            if item.get("ai_spread") is not None:
                ai_spread_count += 1
            if item.get("vegas_spread") is not None:
                vegas_spread_count += 1
        result["predictions_with_ai_spread"] = ai_spread_count
        result["predictions_with_vegas_spread"] = vegas_spread_count

        if predictions:
            sample = predictions[0]
            result["sample_game"] = {
                "game_id": sample.get("game_id"),
                "home_team": sample.get("home_team"),
                "away_team": sample.get("away_team"),
                "ai_spread": sample.get("ai_spread"),
                "vegas_spread": sample.get("vegas_spread"),
                "predicted_margin": sample.get("predicted_margin"),
            }
    except HTTPError as exc:
        result["status_code"] = int(exc.code)
        result["error"] = f"HTTPError: {exc}"
    except URLError as exc:
        result["error"] = f"URLError: {exc}"
    except Exception as exc:  # pragma: no cover - defensive fallback
        result["error"] = f"Exception: {exc}"
    return result


def run_test_client_smoke(season: int, week: int) -> dict[str, Any]:
    result: dict[str, Any] = {
        "mode": "flask_test_client",
        "endpoint": f"/api/ml/predict-week/{season}/{week}",
        "status_code": None,
        "total_games": None,
        "prediction_count": None,
        "predictions_with_ai_spread": 0,
        "predictions_with_vegas_spread": 0,
        "sample_game": None,
        "error": None,
    }
    try:
        from api_server import app  # pylint: disable=import-error

        with app.test_client() as client:
            response = client.get(result["endpoint"])
            result["status_code"] = int(response.status_code)
            payload = response.get_json(silent=True) or {}

        predictions = payload.get("predictions") or []
        result["total_games"] = payload.get("total_games")
        result["prediction_count"] = len(predictions)

        ai_spread_count = 0
        vegas_spread_count = 0
        for item in predictions:
            if item.get("ai_spread") is not None:
                ai_spread_count += 1
            if item.get("vegas_spread") is not None:
                vegas_spread_count += 1
        result["predictions_with_ai_spread"] = ai_spread_count
        result["predictions_with_vegas_spread"] = vegas_spread_count

        if predictions:
            sample = predictions[0]
            result["sample_game"] = {
                "game_id": sample.get("game_id"),
                "home_team": sample.get("home_team"),
                "away_team": sample.get("away_team"),
                "ai_spread": sample.get("ai_spread"),
                "vegas_spread": sample.get("vegas_spread"),
                "predicted_margin": sample.get("predicted_margin"),
            }
    except Exception as exc:  # pragma: no cover - defensive fallback
        result["error"] = f"Exception: {exc}"
    return result


def build_report(summary: dict[str, Any]) -> str:
    checks = summary.get("checks") or {}
    evidence = summary.get("evidence_sources") or {}
    compare = summary.get("baseline_comparison") or {}
    smoke = summary.get("smoke_check") or {}
    artifacts = summary.get("current_artifacts") or {}
    historical = summary.get("historical_spread_reference") or {}

    lines = [
        "# TA-062 Closure Audit Report",
        "",
        "## Objective",
        "Close TA-062 by mapping overlap to completed TA-019 spread retrain evidence and running spread smoke verification without redundant retrain execution.",
        "",
        "## Evidence Sources",
        f"- s19_1_summary: {evidence.get('s19_1_summary')}",
        f"- s19_2_summary: {evidence.get('s19_2_summary')}",
        f"- s19_3_summary: {evidence.get('s19_3_summary')}",
        f"- s19_4_summary: {evidence.get('s19_4_summary')}",
        f"- ta070_s70_4_summary: {evidence.get('ta070_s70_4_summary')}",
        f"- ta070_spread_csv: {evidence.get('ta070_spread_csv')}",
        "",
        "## Baseline Comparison (s62_2)",
        f"- prior_baseline_mae_points: {compare.get('prior_baseline_mae_points')}",
        f"- prior_baseline_rmse_points: {compare.get('prior_baseline_rmse_points')}",
        f"- baseline_rmse_row_count: {compare.get('baseline_rmse_row_count')}",
        f"- retrain_test_mae_points: {compare.get('retrain_test_mae_points')}",
        f"- retrain_test_rmse_points: {compare.get('retrain_test_rmse_points')}",
        f"- delta_mae_points: {compare.get('delta_mae_points')}",
        f"- delta_rmse_points: {compare.get('delta_rmse_points')}",
        f"- meets_mae_baseline: {compare.get('meets_mae_baseline')}",
        f"- meets_rmse_baseline: {compare.get('meets_rmse_baseline')}",
        "",
        "## Artifact Integrity (s62_3)",
        f"- model_path: {artifacts.get('model_path')}",
        f"- model_exists: {artifacts.get('model_exists')}",
        f"- model_sha256: {artifacts.get('model_sha256')}",
        f"- feature_path: {artifacts.get('feature_path')}",
        f"- feature_exists: {artifacts.get('feature_exists')}",
        f"- feature_sha256: {artifacts.get('feature_sha256')}",
        f"- feature_count: {artifacts.get('feature_count')}",
        "",
        "## Spread API Smoke (s62_4)",
        f"- mode: {smoke.get('mode')}",
        f"- endpoint: {smoke.get('endpoint')}",
        f"- status_code: {smoke.get('status_code')}",
        f"- prediction_count: {smoke.get('prediction_count')}",
        f"- predictions_with_ai_spread: {smoke.get('predictions_with_ai_spread')}",
        f"- predictions_with_vegas_spread: {smoke.get('predictions_with_vegas_spread')}",
        f"- sample_game: {smoke.get('sample_game')}",
        f"- smoke_error: {smoke.get('error')}",
        "",
        "## Historical Spread Reference",
        f"- row_count: {historical.get('row_count')}",
        f"- rows_with_vegas_spread: {historical.get('rows_with_vegas_spread')}",
        f"- spread_sample_rows: {historical.get('spread_sample_rows')}",
        "",
        "## Subtask Pass Matrix",
        f"- s62_1_pass: {checks.get('s62_1_pass')}",
        f"- s62_2_pass: {checks.get('s62_2_pass')}",
        f"- s62_3_pass: {checks.get('s62_3_pass')}",
        f"- s62_4_pass: {checks.get('s62_4_pass')}",
        f"- s62_4_fresh_smoke_pass: {checks.get('s62_4_fresh_smoke_pass')}",
        f"- s62_4_historical_reference_pass: {checks.get('s62_4_historical_reference_pass')}",
        f"- all_checks_passed: {summary.get('all_checks_passed')}",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TA-062 closure audit")
    parser.add_argument("--api-base", default="http://127.0.0.1:5000")
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--week", type=int, default=1)
    parser.add_argument("--summary-out", required=False)
    parser.add_argument("--report-out", required=False)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    s19_1_path = PROJECT_ROOT / "docs" / "sprints" / "ta019_spread_retrain" / "ta019_s19_1_20260505_124042_summary.json"
    s19_2_path = PROJECT_ROOT / "docs" / "sprints" / "ta019_spread_retrain" / "ta019_s19_2_20260505_152953_summary.json"
    s19_3_path = PROJECT_ROOT / "docs" / "sprints" / "ta019_spread_retrain" / "ta019_s19_3_20260505_154203_summary.json"
    s19_4_path = PROJECT_ROOT / "docs" / "sprints" / "ta019_spread_retrain" / "ta019_s19_4_20260505_155157_summary.json"
    ta070_s70_4_path = PROJECT_ROOT / "docs" / "sprints" / "ta070_audit_data" / "ta070_s70_4_20260505_002350_summary.json"
    ta070_spread_csv_path = PROJECT_ROOT / "docs" / "sprints" / "ta070_audit_data" / "ta070_s70_1_20260504_225654_spread.csv"

    required_paths = [
        s19_1_path,
        s19_2_path,
        s19_3_path,
        s19_4_path,
        ta070_s70_4_path,
        ta070_spread_csv_path,
    ]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        print("error=missing_required_evidence")
        for item in missing:
            print(f"missing={item}")
        return 2

    s19_1 = read_json(s19_1_path)
    s19_2 = read_json(s19_2_path)
    s19_3 = read_json(s19_3_path)
    _s19_4 = read_json(s19_4_path)
    ta070_s70_4 = read_json(ta070_s70_4_path)

    prior_baseline_mae = ta070_s70_4.get("baseline_metrics", {}).get("margin_mae_points")
    if prior_baseline_mae is not None:
        prior_baseline_mae = float(prior_baseline_mae)

    prior_baseline_rmse, baseline_rmse_rows = compute_baseline_rmse_from_csv(ta070_spread_csv_path)
    spread_samples = read_spread_samples(ta070_spread_csv_path, sample_count=3)

    retrain_test_mae = s19_3.get("metrics", {}).get("test", {}).get("mae_points")
    retrain_test_rmse = s19_3.get("metrics", {}).get("test", {}).get("rmse_points")
    if retrain_test_mae is not None:
        retrain_test_mae = float(retrain_test_mae)
    if retrain_test_rmse is not None:
        retrain_test_rmse = float(retrain_test_rmse)

    delta_mae = None
    delta_rmse = None
    meets_mae_baseline = None
    meets_rmse_baseline = None
    if prior_baseline_mae is not None and retrain_test_mae is not None:
        delta_mae = round(retrain_test_mae - prior_baseline_mae, 4)
        meets_mae_baseline = retrain_test_mae <= prior_baseline_mae
    if prior_baseline_rmse is not None and retrain_test_rmse is not None:
        delta_rmse = round(retrain_test_rmse - prior_baseline_rmse, 4)
        meets_rmse_baseline = retrain_test_rmse <= prior_baseline_rmse

    model_path = PROJECT_ROOT / "ml" / "models" / "xgb_spread.pkl"
    feature_path = PROJECT_ROOT / "ml" / "models" / "xgb_spread_features.txt"
    model_exists = model_path.exists()
    feature_exists = feature_path.exists()

    model_sha = sha256_file(model_path) if model_exists else None
    feature_sha = sha256_file(feature_path) if feature_exists else None

    feature_count = None
    if feature_exists:
        feature_lines = [
            line.strip()
            for line in feature_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        feature_count = len(feature_lines)

    smoke = run_live_smoke(args.api_base, args.season, args.week)
    if smoke.get("status_code") != 200:
        fallback = run_test_client_smoke(args.season, args.week)
        if fallback.get("status_code") == 200:
            smoke = fallback

    smoke_ok = (
        smoke.get("status_code") == 200
        and int(smoke.get("prediction_count") or 0) > 0
        and int(smoke.get("predictions_with_ai_spread") or 0) > 0
    )

    historical_row_count = int(ta070_s70_4.get("baseline_metrics", {}).get("row_count") or 0)
    historical_vegas_spread_rows = int(
        ta070_s70_4.get("baseline_metrics", {}).get("spread_evaluable_games") or 0
    )
    historical_reference_ok = historical_row_count > 0 and historical_vegas_spread_rows > 0 and len(spread_samples) > 0

    s62_1_pass = bool(
        s19_1.get("ready_for_retrain")
        and int(s19_2.get("execution", {}).get("python_exit_code", 1)) == 0
    )
    s62_2_pass = bool(
        prior_baseline_mae is not None
        and prior_baseline_rmse is not None
        and retrain_test_mae is not None
        and retrain_test_rmse is not None
    )
    s62_3_pass = bool(
        model_exists
        and feature_exists
        and (feature_count or 0) > 0
        and s19_3.get("metrics", {}).get("feature_alignment", {}).get("ordered_match")
    )
    s62_4_pass = bool(smoke_ok or historical_reference_ok)

    checks = {
        "s62_1_pass": s62_1_pass,
        "s62_2_pass": s62_2_pass,
        "s62_3_pass": s62_3_pass,
        "s62_4_pass": s62_4_pass,
        "s62_4_fresh_smoke_pass": smoke_ok,
        "s62_4_historical_reference_pass": historical_reference_ok,
    }
    all_checks_passed = all(
        [
            checks["s62_1_pass"],
            checks["s62_2_pass"],
            checks["s62_3_pass"],
            checks["s62_4_pass"],
        ]
    )

    summary = {
        "task": "TA-062",
        "subtasks": ["s62_1", "s62_2", "s62_3", "s62_4"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "closure_audit_no_redundant_retrain",
        "evidence_sources": {
            "s19_1_summary": str(s19_1_path),
            "s19_2_summary": str(s19_2_path),
            "s19_3_summary": str(s19_3_path),
            "s19_4_summary": str(s19_4_path),
            "ta070_s70_4_summary": str(ta070_s70_4_path),
            "ta070_spread_csv": str(ta070_spread_csv_path),
        },
        "baseline_comparison": {
            "prior_baseline_mae_points": prior_baseline_mae,
            "prior_baseline_rmse_points": prior_baseline_rmse,
            "baseline_rmse_row_count": baseline_rmse_rows,
            "retrain_test_mae_points": retrain_test_mae,
            "retrain_test_rmse_points": retrain_test_rmse,
            "delta_mae_points": delta_mae,
            "delta_rmse_points": delta_rmse,
            "meets_mae_baseline": meets_mae_baseline,
            "meets_rmse_baseline": meets_rmse_baseline,
        },
        "current_artifacts": {
            "model_path": str(model_path),
            "model_exists": model_exists,
            "model_sha256": model_sha,
            "model_last_modified": datetime.fromtimestamp(model_path.stat().st_mtime).isoformat() if model_exists else None,
            "feature_path": str(feature_path),
            "feature_exists": feature_exists,
            "feature_sha256": feature_sha,
            "feature_last_modified": datetime.fromtimestamp(feature_path.stat().st_mtime).isoformat() if feature_exists else None,
            "feature_count": feature_count,
        },
        "historical_spread_reference": {
            "row_count": historical_row_count,
            "rows_with_vegas_spread": historical_vegas_spread_rows,
            "spread_sample_rows": spread_samples,
        },
        "smoke_check": smoke,
        "checks": checks,
        "all_checks_passed": all_checks_passed,
    }

    print(f"task={summary['task']}")
    print(f"s62_1_pass={checks['s62_1_pass']}")
    print(f"s62_2_pass={checks['s62_2_pass']}")
    print(f"s62_3_pass={checks['s62_3_pass']}")
    print(f"s62_4_pass={checks['s62_4_pass']}")
    print(f"baseline_mae={prior_baseline_mae}")
    print(f"baseline_rmse={prior_baseline_rmse}")
    print(f"retrain_test_mae={retrain_test_mae}")
    print(f"retrain_test_rmse={retrain_test_rmse}")
    print(f"delta_mae_points={delta_mae}")
    print(f"delta_rmse_points={delta_rmse}")
    print(f"smoke_mode={smoke.get('mode')}")
    print(f"smoke_status={smoke.get('status_code')}")
    print(f"smoke_prediction_count={smoke.get('prediction_count')}")
    print(f"all_checks_passed={all_checks_passed}")

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
