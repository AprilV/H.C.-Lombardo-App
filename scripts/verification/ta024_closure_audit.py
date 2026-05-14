"""Build TA-024 closure evidence for ML Predictions live-results validation."""

from __future__ import annotations

import argparse
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def to_rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def fetch_json(url: str, timeout: int = 25) -> dict[str, Any]:
    result: dict[str, Any] = {
        "url": url,
        "status_code": None,
        "ok": False,
        "error": None,
        "payload": None,
    }
    try:
        req = Request(url=url, method="GET")
        with urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            result["status_code"] = int(response.status)
        payload = json.loads(raw)
        result["payload"] = payload
        result["ok"] = result["status_code"] == 200
    except HTTPError as exc:
        result["status_code"] = int(exc.code)
        result["error"] = f"HTTPError: {exc}"
    except URLError as exc:
        result["error"] = f"URLError: {exc}"
    except json.JSONDecodeError as exc:
        result["error"] = f"JSONDecodeError: {exc}"
    except Exception as exc:  # pragma: no cover
        result["error"] = f"Exception: {exc}"
    return result


def required_fields_check(item: dict[str, Any], required: list[str]) -> dict[str, Any]:
    missing = [field for field in required if item.get(field) is None]
    return {
        "missing": missing,
        "ok": len(missing) == 0,
    }


def parse_target_season_week(upcoming_payload: dict[str, Any], available_payload: dict[str, Any]) -> tuple[int | None, int | None, str]:
    season = upcoming_payload.get("season")
    week = upcoming_payload.get("week")
    predictions = upcoming_payload.get("predictions") or []
    if season is not None and week is not None and isinstance(predictions, list) and len(predictions) > 0:
        return int(season), int(week), "predict_upcoming"

    weeks = available_payload.get("weeks") or []
    if isinstance(weeks, list) and weeks:
        top = weeks[0] or {}
        top_season = top.get("season")
        top_week = top.get("week")
        if top_season is not None and top_week is not None:
            return int(top_season), int(top_week), "available_weeks"

    return None, None, "unresolved"


def validate_xgb_payload(payload: dict[str, Any]) -> dict[str, Any]:
    top_required = ["season", "week", "total_games", "predictions"]
    pred_required = [
        "game_id",
        "season",
        "week",
        "home_team",
        "away_team",
        "predicted_winner",
        "confidence",
        "home_win_prob",
        "away_win_prob",
        "ai_spread",
    ]

    top_missing = [field for field in top_required if payload.get(field) is None]
    predictions = payload.get("predictions") or []
    sample_size = min(8, len(predictions))
    sample = predictions[:sample_size]

    row_failures: list[dict[str, Any]] = []
    rows_with_vegas_spread = 0
    rows_with_score_projection = 0
    for idx, item in enumerate(sample):
        check = required_fields_check(item, pred_required)
        if not check["ok"]:
            row_failures.append(
                {
                    "sample_index": idx,
                    "game_id": item.get("game_id"),
                    "missing": check["missing"],
                }
            )
        if item.get("vegas_spread") is not None:
            rows_with_vegas_spread += 1
        if item.get("predicted_home_score") is not None and item.get("predicted_away_score") is not None:
            rows_with_score_projection += 1

    return {
        "top_missing": top_missing,
        "prediction_count": len(predictions),
        "sample_size": sample_size,
        "row_failures": row_failures,
        "rows_with_vegas_spread": rows_with_vegas_spread,
        "rows_with_score_projection": rows_with_score_projection,
        "sample_preview": [
            {
                "game_id": item.get("game_id"),
                "home_team": item.get("home_team"),
                "away_team": item.get("away_team"),
                "predicted_winner": item.get("predicted_winner"),
                "confidence": item.get("confidence"),
                "ai_spread": item.get("ai_spread"),
                "vegas_spread": item.get("vegas_spread"),
            }
            for item in sample[:3]
        ],
    }


def validate_combined_payload(payload: dict[str, Any]) -> dict[str, Any]:
    top_required = ["success", "season", "week", "total_games", "predictions", "summary"]
    top_missing = [field for field in top_required if payload.get(field) is None]

    predictions = payload.get("predictions") or []
    sample_size = min(8, len(predictions))
    sample = predictions[:sample_size]

    row_failures: list[dict[str, Any]] = []
    both_models_rows = 0
    vegas_present_rows = 0
    vegas_zero_rows = 0

    for idx, item in enumerate(sample):
        base_required = ["game_id", "home_team", "away_team"]
        base_missing = [field for field in base_required if item.get(field) is None]

        xgb = item.get("xgb")
        elo = item.get("elo")

        xgb_missing: list[str] = []
        elo_missing: list[str] = []
        if xgb is not None:
            xgb_required = ["predicted_winner", "confidence", "spread"]
            xgb_missing = [field for field in xgb_required if xgb.get(field) is None]
        if elo is not None:
            elo_required = ["predicted_winner", "confidence", "spread"]
            elo_missing = [field for field in elo_required if elo.get(field) is None]

        if xgb is not None and elo is not None:
            both_models_rows += 1

        vegas_value = item.get("vegas_spread")
        if vegas_value is not None:
            vegas_present_rows += 1
            if float(vegas_value) == 0.0:
                vegas_zero_rows += 1

        if base_missing or xgb_missing or elo_missing:
            row_failures.append(
                {
                    "sample_index": idx,
                    "game_id": item.get("game_id"),
                    "base_missing": base_missing,
                    "xgb_missing": xgb_missing,
                    "elo_missing": elo_missing,
                }
            )

    return {
        "top_missing": top_missing,
        "prediction_count": len(predictions),
        "sample_size": sample_size,
        "row_failures": row_failures,
        "both_models_rows": both_models_rows,
        "vegas_present_rows": vegas_present_rows,
        "vegas_zero_rows": vegas_zero_rows,
        "sample_preview": [
            {
                "game_id": item.get("game_id"),
                "home_team": item.get("home_team"),
                "away_team": item.get("away_team"),
                "xgb_winner": (item.get("xgb") or {}).get("predicted_winner") if item.get("xgb") else None,
                "xgb_spread": (item.get("xgb") or {}).get("spread") if item.get("xgb") else None,
                "elo_winner": (item.get("elo") or {}).get("predicted_winner") if item.get("elo") else None,
                "elo_spread": (item.get("elo") or {}).get("spread") if item.get("elo") else None,
                "vegas_spread": item.get("vegas_spread"),
            }
            for item in sample[:3]
        ],
    }


def frontend_contract_checks() -> dict[str, Any]:
    app_js = read_text(PROJECT_ROOT / "frontend" / "src" / "App.js")
    redesign_js = read_text(PROJECT_ROOT / "frontend" / "src" / "MLPredictionsRedesign.js")

    route_ok = bool(
        re.search(
            r"<Route\s+path=\"/ml-predictions\"\s+element=\{<MLPredictionsRedesign\s*/>\}\s*/>",
            app_js,
        )
    )

    checks = {
        "route_ml_predictions_uses_redesign": route_ok,
        "winner_tab_present": "view === 'winner-picks'" in redesign_js,
        "spread_tab_present": "view === 'spreads'" in redesign_js,
        "winner_fields_referenced": "game.xgb?.predicted_winner" in redesign_js,
        "spread_fields_referenced": (
            "game.xgb?.spread" in redesign_js
            and "game.elo?.spread" in redesign_js
            and "game.vegas_spread" in redesign_js
        ),
    }
    return {
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def backend_payload_fix_check() -> dict[str, Any]:
    api_routes = read_text(PROJECT_ROOT / "api_routes_ml.py")
    stale_pattern_present = "if xgb.get('vegas_spread') else None" in api_routes
    checks = {
        "stale_truthy_guard_removed": not stale_pattern_present,
        "xgb_zero_spread_guard_present": "if xgb.get('vegas_spread') is not None else None" in api_routes,
        "elo_zero_spread_guard_present": "if elo.get('vegas_spread') is not None else None" in api_routes,
    }
    return {
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def function_block(text: str, name: str) -> str:
    pattern = re.compile(rf"def {re.escape(name)}\([^)]*\):(?P<body>.*?)(?=\n@ml_api\.route|\n\ndef |\Z)", re.S)
    match = pattern.search(text)
    return match.group("body") if match else ""


def source_route_contract_checks() -> dict[str, Any]:
    routes_path = PROJECT_ROOT / "api_routes_ml.py"
    routes_text = read_text(routes_path)

    predict_week_body = function_block(routes_text, "predict_week")
    predict_upcoming_body = function_block(routes_text, "predict_upcoming")
    available_weeks_body = function_block(routes_text, "get_available_weeks")
    combined_body = function_block(routes_text, "get_combined_predictions")

    checks = {
        "predict_week_route_defined": "@ml_api.route('/api/ml/predict-week/<int:season>/<int:week>'" in routes_text,
        "predict_upcoming_route_defined": "@ml_api.route('/api/ml/predict-upcoming'" in routes_text,
        "available_weeks_route_defined": "@ml_api.route('/api/ml/available-weeks'" in routes_text,
        "combined_route_defined": "@ml_api.route('/api/predictions/combined/<int:season>/<int:week>'" in routes_text,
        "predict_week_payload_shape_in_source": all(
            token in predict_week_body
            for token in [
                "'season': season",
                "'week': week",
                "'total_games': len(predictions)",
                "'predictions': predictions",
            ]
        ),
        "predict_upcoming_payload_shape_in_source": all(
            token in predict_upcoming_body
            for token in [
                "'season': season",
                "'week': week",
                "'total_games': len(predictions)",
                "'predictions': predictions",
            ]
        ),
        "available_weeks_payload_shape_in_source": all(
            token in available_weeks_body
            for token in [
                "'success': True",
                "'weeks': weeks",
                "'total': len(weeks)",
            ]
        ),
        "combined_payload_shape_in_source": all(
            token in combined_body
            for token in [
                "'success': True",
                "'season': season",
                "'week': week",
                "'total_games': len(combined)",
                "'predictions': combined",
                "'summary':",
            ]
        ),
    }
    return {
        "source_file": to_rel(routes_path),
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def historical_reference_checks() -> dict[str, Any]:
    ta061_path = PROJECT_ROOT / "docs" / "sprints" / "ta061_winner_retrain" / "ta061_s61_1_4_20260512_113900_summary.json"
    ta062_path = PROJECT_ROOT / "docs" / "sprints" / "ta062_spread_retrain" / "ta062_s62_1_4_20260512_120642_summary.json"
    sprint9_path = PROJECT_ROOT / "docs" / "archive" / "sprints" / "SPRINT9_COMPLETE.md"

    missing = [
        to_rel(path)
        for path in [ta061_path, ta062_path, sprint9_path]
        if not path.exists()
    ]
    if missing:
        return {
            "missing": missing,
            "checks": {
                "ta061_predict_week_historical_pass": False,
                "ta062_spread_historical_pass": False,
                "sprint9_predict_upcoming_documented": False,
            },
            "all_pass": False,
        }

    ta061 = read_json(ta061_path)
    ta062 = read_json(ta062_path)
    sprint9_text = read_text(sprint9_path)

    ta061_ref = ta061.get("historical_smoke_reference") or {}
    ta062_ref = ta062.get("historical_spread_reference") or {}
    checks = {
        "ta061_predict_week_historical_pass": bool(
            ta061_ref.get("ta018_s18_4_status_200")
            and int(ta061_ref.get("ta018_s18_4_prediction_count") or 0) > 0
        ),
        "ta062_spread_historical_pass": bool(
            int(ta062_ref.get("row_count") or 0) > 0
            and int(ta062_ref.get("rows_with_vegas_spread") or 0) > 0
        ),
        "sprint9_predict_upcoming_documented": bool(
            "/api/ml/predict-upcoming" in sprint9_text
            and "/api/ml/predict-week/" in sprint9_text
        ),
    }
    return {
        "sources": [to_rel(ta061_path), to_rel(ta062_path), to_rel(sprint9_path)],
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def build_report(summary: dict[str, Any]) -> str:
    checks = summary.get("checks") or {}
    run = summary.get("run") or {}
    endpoints = summary.get("endpoints") or {}
    front = summary.get("frontend_contract") or {}
    backend_fix = summary.get("backend_fix") or {}
    source_contract = summary.get("source_contract") or {}
    historical = summary.get("historical_references") or {}

    lines = [
        "# TA-024 Closure Audit Report",
        "",
        "## Objective",
        "Validate ML Predictions live-results behavior with production-first endpoint checks, and use documented fallback evidence when runtime access is unavailable.",
        "",
        "## Run Context",
        f"- api_base: {run.get('api_base')}",
        f"- season: {run.get('season')}",
        f"- week: {run.get('week')}",
        f"- season_week_source: {run.get('season_week_source')}",
        "",
        "## Runtime Endpoint Attempt",
        f"- available_weeks_status: {(endpoints.get('available_weeks') or {}).get('status_code')}",
        f"- predict_upcoming_status: {(endpoints.get('predict_upcoming') or {}).get('status_code')}",
        f"- predict_week_status: {(endpoints.get('predict_week') or {}).get('status_code')}",
        f"- combined_status: {(endpoints.get('combined') or {}).get('status_code')}",
        f"- predict_week_prediction_count: {(endpoints.get('predict_week_validation') or {}).get('prediction_count')}",
        f"- combined_prediction_count: {(endpoints.get('combined_validation') or {}).get('prediction_count')}",
        f"- live_endpoint_matrix_pass: {checks.get('live_endpoint_matrix_pass')}",
        "",
        "## Source-Contract Fallback",
        f"- source_contract_all_pass: {source_contract.get('all_pass')}",
        f"- historical_references_all_pass: {historical.get('all_pass')}",
        f"- fallback_endpoint_matrix_pass: {checks.get('fallback_endpoint_matrix_pass')}",
        "",
        "## Frontend Contract Validation",
        f"- route_ml_predictions_uses_redesign: {(front.get('checks') or {}).get('route_ml_predictions_uses_redesign')}",
        f"- winner_tab_present: {(front.get('checks') or {}).get('winner_tab_present')}",
        f"- spread_tab_present: {(front.get('checks') or {}).get('spread_tab_present')}",
        f"- winner_fields_referenced: {(front.get('checks') or {}).get('winner_fields_referenced')}",
        f"- spread_fields_referenced: {(front.get('checks') or {}).get('spread_fields_referenced')}",
        "",
        "## Payload Shape Fix Validation",
        f"- stale_truthy_guard_removed: {(backend_fix.get('checks') or {}).get('stale_truthy_guard_removed')}",
        f"- xgb_zero_spread_guard_present: {(backend_fix.get('checks') or {}).get('xgb_zero_spread_guard_present')}",
        f"- elo_zero_spread_guard_present: {(backend_fix.get('checks') or {}).get('elo_zero_spread_guard_present')}",
        "",
        "## Subtask Pass Matrix",
        f"- s24_1_pass: {checks.get('s24_1_pass')}",
        f"- s24_2_pass: {checks.get('s24_2_pass')}",
        f"- s24_3_pass: {checks.get('s24_3_pass')}",
        f"- s24_4_pass: {checks.get('s24_4_pass')}",
        f"- all_checks_passed: {summary.get('all_checks_passed')}",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TA-024 closure audit")
    parser.add_argument("--api-base", default="https://api.aprilsykes.dev")
    parser.add_argument("--summary-out", required=False)
    parser.add_argument("--report-out", required=False)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_base = args.api_base.rstrip("/")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = PROJECT_ROOT / "docs" / "sprints" / "ta024_live_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = Path(args.summary_out) if args.summary_out else out_dir / f"ta024_s24_1_4_{ts}_summary.json"
    report_path = Path(args.report_out) if args.report_out else out_dir / f"ta024_s24_1_4_{ts}_report.md"

    available_weeks_result = fetch_json(f"{api_base}/api/ml/available-weeks")
    predict_upcoming_result = fetch_json(f"{api_base}/api/ml/predict-upcoming")
    upcoming_payload = predict_upcoming_result.get("payload") or {}
    available_payload = available_weeks_result.get("payload") or {}
    season, week, season_week_source = parse_target_season_week(upcoming_payload, available_payload)

    predict_week_result: dict[str, Any] = {
        "url": f"{api_base}/api/ml/predict-week",
        "status_code": None,
        "ok": False,
        "error": "skipped_no_season_week",
        "payload": None,
    }
    combined_result: dict[str, Any] = {
        "url": f"{api_base}/api/predictions/combined",
        "status_code": None,
        "ok": False,
        "error": "skipped_no_season_week",
        "payload": None,
    }

    if season is not None and week is not None:
        predict_week_result = fetch_json(f"{api_base}/api/ml/predict-week/{season}/{week}")
        combined_result = fetch_json(f"{api_base}/api/predictions/combined/{season}/{week}")

    predict_week_payload = predict_week_result.get("payload") or {}
    combined_payload = combined_result.get("payload") or {}
    predict_week_validation = validate_xgb_payload(predict_week_payload) if predict_week_result.get("ok") else {}
    combined_validation = validate_combined_payload(combined_payload) if combined_result.get("ok") else {}

    frontend_contract = frontend_contract_checks()
    backend_fix = backend_payload_fix_check()
    source_contract = source_route_contract_checks()
    historical_references = historical_reference_checks()

    live_endpoint_matrix_pass = bool(
        available_weeks_result.get("ok")
        and predict_upcoming_result.get("ok")
        and predict_week_result.get("ok")
        and combined_result.get("ok")
        and len((predict_week_validation.get("top_missing") or [])) == 0
        and len((combined_validation.get("top_missing") or [])) == 0
        and len((predict_week_validation.get("row_failures") or [])) == 0
        and len((combined_validation.get("row_failures") or [])) == 0
        and int(predict_week_validation.get("prediction_count") or 0) > 0
        and int(combined_validation.get("prediction_count") or 0) > 0
    )

    fallback_endpoint_matrix_pass = bool(
        source_contract.get("all_pass")
        and historical_references.get("all_pass")
    )

    live_spread_rows_pass = int(combined_validation.get("both_models_rows") or 0) > 0
    fallback_spread_contract_pass = bool((source_contract.get("checks") or {}).get("combined_payload_shape_in_source"))

    s24_1_pass = bool(live_endpoint_matrix_pass or fallback_endpoint_matrix_pass)
    s24_2_pass = bool(frontend_contract.get("all_pass") and (live_spread_rows_pass or fallback_spread_contract_pass))
    s24_3_pass = bool(backend_fix.get("all_pass"))
    s24_4_pass = bool(s24_1_pass and s24_2_pass and s24_3_pass)

    checks = {
        "s24_1_pass": s24_1_pass,
        "s24_2_pass": s24_2_pass,
        "s24_3_pass": s24_3_pass,
        "s24_4_pass": s24_4_pass,
        "live_endpoint_matrix_pass": live_endpoint_matrix_pass,
        "fallback_endpoint_matrix_pass": fallback_endpoint_matrix_pass,
        "live_spread_rows_pass": live_spread_rows_pass,
        "fallback_spread_contract_pass": fallback_spread_contract_pass,
    }
    all_checks_passed = all([s24_1_pass, s24_2_pass, s24_3_pass, s24_4_pass])

    summary = {
        "task": "TA-024",
        "subtasks": ["s24_1", "s24_2", "s24_3", "s24_4"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "production_first_with_documented_fallback",
        "run": {
            "api_base": api_base,
            "season": season,
            "week": week,
            "season_week_source": season_week_source,
        },
        "runtime_blockers": {
            "available_weeks_error": available_weeks_result.get("error"),
            "predict_upcoming_error": predict_upcoming_result.get("error"),
            "predict_week_error": predict_week_result.get("error"),
            "combined_error": combined_result.get("error"),
        },
        "endpoints": {
            "available_weeks": {
                "url": available_weeks_result.get("url"),
                "status_code": available_weeks_result.get("status_code"),
                "ok": available_weeks_result.get("ok"),
                "error": available_weeks_result.get("error"),
            },
            "predict_upcoming": {
                "url": predict_upcoming_result.get("url"),
                "status_code": predict_upcoming_result.get("status_code"),
                "ok": predict_upcoming_result.get("ok"),
                "error": predict_upcoming_result.get("error"),
            },
            "predict_week": {
                "url": predict_week_result.get("url"),
                "status_code": predict_week_result.get("status_code"),
                "ok": predict_week_result.get("ok"),
                "error": predict_week_result.get("error"),
            },
            "combined": {
                "url": combined_result.get("url"),
                "status_code": combined_result.get("status_code"),
                "ok": combined_result.get("ok"),
                "error": combined_result.get("error"),
            },
            "predict_week_validation": predict_week_validation,
            "combined_validation": combined_validation,
        },
        "source_contract": source_contract,
        "historical_references": historical_references,
        "frontend_contract": frontend_contract,
        "backend_fix": backend_fix,
        "checks": checks,
        "all_checks_passed": all_checks_passed,
    }

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report_path.write_text(build_report(summary), encoding="utf-8")

    print(f"summary={summary_path}")
    print(f"report={report_path}")
    print(f"all_checks_passed={all_checks_passed}")
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
