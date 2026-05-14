"""Build TA-061 closure evidence without redoing already-completed TA-018 work."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_prior_baseline_accuracy(path: Path) -> tuple[float | None, str | None]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"'this_model'\s*:\s*'([0-9]+(?:\.[0-9]+)?)%'", text)
    if match:
        return float(match.group(1)), "api_routes_ml.py:model_info.performance.baseline_comparison.this_model"

    match = re.search(r"'accuracy'\s*:\s*'([0-9]+(?:\.[0-9]+)?)%\s+on\s+2025\s+test\s+set'", text)
    if match:
        return float(match.group(1)), "api_routes_ml.py:/api/ml/predict-week accuracy label"

    return None, None


def run_live_smoke(api_base: str, season: int, week: int) -> dict[str, Any]:
    endpoint = f"{api_base.rstrip('/')}/api/ml/predict-week/{season}/{week}"
    result: dict[str, Any] = {
        "mode": "live_http",
        "endpoint": endpoint,
        "status_code": None,
        "total_games": None,
        "prediction_count": None,
        "model": None,
        "accuracy_label": None,
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
        result["model"] = payload.get("model")
        result["accuracy_label"] = payload.get("accuracy")
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
        "model": None,
        "accuracy_label": None,
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
        result["model"] = payload.get("model")
        result["accuracy_label"] = payload.get("accuracy")
    except Exception as exc:  # pragma: no cover - defensive fallback
        result["error"] = f"Exception: {exc}"
    return result


def build_report(summary: dict[str, Any]) -> str:
    checks = summary.get("checks") or {}
    evidence = summary.get("evidence_sources") or {}
    accuracy = summary.get("accuracy_comparison") or {}
    smoke = summary.get("smoke_check") or {}
    artifacts = summary.get("current_artifacts") or {}

    lines = [
        "# TA-061 Closure Audit Report",
        "",
        "## Objective",
        "Close TA-061 by mapping overlap to completed TA-018 winner retrain evidence and running fresh smoke verification without redundant retrain execution.",
        "",
        "## Evidence Sources",
        f"- s18_1_summary: {evidence.get('s18_1_summary')}",
        f"- s18_2_summary: {evidence.get('s18_2_summary')}",
        f"- s18_3_summary: {evidence.get('s18_3_summary')}",
        f"- s18_4_summary: {evidence.get('s18_4_summary')}",
        f"- baseline_source: {accuracy.get('baseline_source')}",
        "",
        "## Accuracy Comparison (s61_2)",
        f"- prior_baseline_accuracy_pct: {accuracy.get('prior_baseline_accuracy_pct')}",
        f"- retrain_test_accuracy_pct: {accuracy.get('retrain_test_accuracy_pct')}",
        f"- delta_pct_points: {accuracy.get('delta_pct_points')}",
        f"- deployment_guard_model_meets_or_exceeds_baseline: {accuracy.get('model_meets_or_exceeds_baseline')}",
        "",
        "## Artifact Integrity (s61_3)",
        f"- model_path: {artifacts.get('model_path')}",
        f"- model_exists: {artifacts.get('model_exists')}",
        f"- model_sha256: {artifacts.get('model_sha256')}",
        f"- feature_path: {artifacts.get('feature_path')}",
        f"- feature_exists: {artifacts.get('feature_exists')}",
        f"- feature_sha256: {artifacts.get('feature_sha256')}",
        f"- feature_count: {artifacts.get('feature_count')}",
        "",
        "## Fresh Smoke Check (s61_4)",
        f"- mode: {smoke.get('mode')}",
        f"- endpoint: {smoke.get('endpoint')}",
        f"- status_code: {smoke.get('status_code')}",
        f"- total_games: {smoke.get('total_games')}",
        f"- prediction_count: {smoke.get('prediction_count')}",
        f"- model: {smoke.get('model')}",
        f"- accuracy_label: {smoke.get('accuracy_label')}",
        f"- smoke_error: {smoke.get('error')}",
        "",
        "## Subtask Pass Matrix",
        f"- s61_1_pass: {checks.get('s61_1_pass')}",
        f"- s61_2_pass: {checks.get('s61_2_pass')}",
        f"- s61_3_pass: {checks.get('s61_3_pass')}",
        f"- s61_4_pass: {checks.get('s61_4_pass')}",
        f"- s61_4_fresh_smoke_pass: {checks.get('s61_4_fresh_smoke_pass')}",
        f"- s61_4_historical_smoke_reference_pass: {checks.get('s61_4_historical_smoke_reference_pass')}",
        f"- all_checks_passed: {summary.get('all_checks_passed')}",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TA-061 closure audit")
    parser.add_argument("--api-base", default="http://127.0.0.1:5000")
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--week", type=int, default=1)
    parser.add_argument("--summary-out", required=False)
    parser.add_argument("--report-out", required=False)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    s18_1_path = PROJECT_ROOT / "docs" / "sprints" / "ta018_winner_retrain" / "ta018_s18_1_20260505_005035_summary.json"
    s18_2_path = PROJECT_ROOT / "docs" / "sprints" / "ta018_winner_retrain" / "ta018_s18_2_20260504_175539_summary.json"
    s18_3_path = PROJECT_ROOT / "docs" / "sprints" / "ta018_winner_retrain" / "ta018_s18_3_20260504_183259_summary.json"
    s18_4_path = PROJECT_ROOT / "docs" / "sprints" / "ta018_winner_retrain" / "ta018_s18_4_20260504_184635_summary.json"

    required_paths = [s18_1_path, s18_2_path, s18_3_path, s18_4_path]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        print("error=missing_required_evidence")
        for item in missing:
            print(f"missing={item}")
        return 2

    s18_1 = read_json(s18_1_path)
    s18_2 = read_json(s18_2_path)
    s18_3 = read_json(s18_3_path)
    s18_4 = read_json(s18_4_path)

    api_routes_path = PROJECT_ROOT / "api_routes_ml.py"
    baseline_pct, baseline_source = parse_prior_baseline_accuracy(api_routes_path)

    retrain_test_accuracy = s18_2.get("metrics", {}).get("test_accuracy_pct")
    if retrain_test_accuracy is not None:
        retrain_test_accuracy = float(retrain_test_accuracy)

    delta = None
    meets_baseline = None
    if baseline_pct is not None and retrain_test_accuracy is not None:
        delta = round(retrain_test_accuracy - baseline_pct, 2)
        meets_baseline = retrain_test_accuracy >= baseline_pct

    model_path = PROJECT_ROOT / "ml" / "models" / "xgb_winner.pkl"
    feature_path = PROJECT_ROOT / "ml" / "models" / "xgb_winner_features.txt"
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
    )
    historical_smoke_ok = bool(
        s18_4.get("checks", {}).get("endpoint_status_200")
        and int(s18_4.get("smoke_test", {}).get("selected_prediction_count") or 0) > 0
    )

    s61_1_pass = bool(
        s18_1.get("readiness", {}).get("ready_for_retrain")
        and int(s18_2.get("execution", {}).get("python_exit_code", 1)) == 0
        and s18_1.get("training_script_inspection", {}).get("uses_load_data_schema_hcl")
    )
    s61_2_pass = bool(
        baseline_pct is not None
        and retrain_test_accuracy is not None
        and delta is not None
    )
    s61_3_pass = bool(
        model_exists
        and feature_exists
        and (feature_count or 0) > 0
        and s18_3.get("checks", {}).get("paths_match_expected")
        and s18_3.get("checks", {}).get("non_empty_files")
    )
    s61_4_pass = bool(smoke_ok or historical_smoke_ok)

    checks = {
        "s61_1_pass": s61_1_pass,
        "s61_2_pass": s61_2_pass,
        "s61_3_pass": s61_3_pass,
        "s61_4_pass": s61_4_pass,
        "s61_4_fresh_smoke_pass": smoke_ok,
        "s61_4_historical_smoke_reference_pass": historical_smoke_ok,
    }
    all_checks_passed = all(
        [
            checks["s61_1_pass"],
            checks["s61_2_pass"],
            checks["s61_3_pass"],
            checks["s61_4_pass"],
        ]
    )

    summary = {
        "task": "TA-061",
        "subtasks": ["s61_1", "s61_2", "s61_3", "s61_4"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "closure_audit_no_redundant_retrain",
        "evidence_sources": {
            "s18_1_summary": str(s18_1_path),
            "s18_2_summary": str(s18_2_path),
            "s18_3_summary": str(s18_3_path),
            "s18_4_summary": str(s18_4_path),
        },
        "accuracy_comparison": {
            "baseline_source": baseline_source,
            "prior_baseline_accuracy_pct": baseline_pct,
            "retrain_test_accuracy_pct": retrain_test_accuracy,
            "delta_pct_points": delta,
            "model_meets_or_exceeds_baseline": meets_baseline,
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
        "historical_smoke_reference": {
            "ta018_s18_4_status_200": s18_4.get("checks", {}).get("endpoint_status_200"),
            "ta018_s18_4_prediction_count": s18_4.get("smoke_test", {}).get("selected_prediction_count"),
        },
        "smoke_check": smoke,
        "checks": checks,
        "all_checks_passed": all_checks_passed,
    }

    print(f"task={summary['task']}")
    print(f"s61_1_pass={checks['s61_1_pass']}")
    print(f"s61_2_pass={checks['s61_2_pass']}")
    print(f"s61_3_pass={checks['s61_3_pass']}")
    print(f"s61_4_pass={checks['s61_4_pass']}")
    print(f"baseline_accuracy={baseline_pct}")
    print(f"retrain_test_accuracy={retrain_test_accuracy}")
    print(f"delta_pct_points={delta}")
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