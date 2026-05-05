#!/usr/bin/env python3
"""TA-070 s70_3: Perform root-cause analysis on prediction accuracy gaps."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime

import psycopg2

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db_config import DATABASE_CONFIG  # noqa: E402

DEFAULT_OUT_DIR = ROOT_DIR / "docs" / "sprints" / "ta070_audit_data"
S70_1_COMBINED_PATTERN = re.compile(r"ta070_s70_1_(\d{8}_\d{6})_combined\.csv$")


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    norm = value.strip().lower()
    if norm == "true":
        return True
    if norm == "false":
        return False
    return None


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    norm = value.strip().lower()
    if norm in {"", "none", "null", "nan"}:
        return None
    return float(value)


def pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100.0, 2)


def resolve_latest_s70_1_combined(data_dir: pathlib.Path) -> pathlib.Path:
    latest: tuple[str, pathlib.Path] | None = None
    for candidate in data_dir.glob("ta070_s70_1_*_combined.csv"):
        match = S70_1_COMBINED_PATTERN.match(candidate.name)
        if not match:
            continue
        stamp = match.group(1)
        if latest is None or stamp > latest[0]:
            latest = (stamp, candidate)

    if latest is None:
        raise FileNotFoundError(
            f"No s70_1 combined CSV found in {data_dir}. Run ta070_extract_prediction_actuals.py first."
        )

    return latest[1]


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@dataclass
class WeeklyAccuracy:
    season: int
    week: int
    correct: int
    total: int

    @property
    def accuracy_pct(self) -> float:
        return round((self.correct / self.total) * 100.0, 2)


def weekly_winner_accuracy(rows: list[dict[str, str]]) -> list[WeeklyAccuracy]:
    agg: dict[tuple[int, int], list[int]] = defaultdict(lambda: [0, 0])
    for row in rows:
        ok = parse_bool(row.get("winner_pick_correct"))
        if ok is None:
            continue
        key = (int(row["season"]), int(row["week"]))
        agg[key][0] += 1
        agg[key][1] += int(ok)

    result: list[WeeklyAccuracy] = []
    for (season, week), (total, correct) in agg.items():
        if total > 0:
            result.append(WeeklyAccuracy(season=season, week=week, correct=correct, total=total))

    result.sort(key=lambda item: (item.season, item.week))
    return result


def analyze_total_line_lock(rows: list[dict[str, str]]) -> dict:
    paired_rows = 0
    equal_rows = 0
    evaluable_total_rows = 0
    for row in rows:
        predicted_total = parse_float(row.get("predicted_total"))
        vegas_total = parse_float(row.get("vegas_total"))
        total_pick_correct = parse_bool(row.get("total_pick_correct"))

        if predicted_total is not None and vegas_total is not None:
            paired_rows += 1
            if abs(predicted_total - vegas_total) < 1e-9:
                equal_rows += 1

        if total_pick_correct is not None:
            evaluable_total_rows += 1

    return {
        "rows_with_predicted_total_and_vegas_total": paired_rows,
        "rows_predicted_total_equals_vegas_total": equal_rows,
        "predicted_total_equals_vegas_total_pct": pct(equal_rows, paired_rows),
        "total_pick_evaluable_rows": evaluable_total_rows,
    }


def analyze_drift(rows: list[dict[str, str]]) -> dict:
    weekly = weekly_winner_accuracy(rows)
    weekly_pct = [w.accuracy_pct for w in weekly]

    if weekly:
        worst = sorted(weekly, key=lambda w: w.accuracy_pct)[:5]
        best = sorted(weekly, key=lambda w: w.accuracy_pct, reverse=True)[:5]
    else:
        worst = []
        best = []

    early_correct = early_total = late_correct = late_total = 0
    for row in rows:
        ok = parse_bool(row.get("winner_pick_correct"))
        if ok is None:
            continue
        week = int(row["week"])
        if week <= 9:
            early_total += 1
            early_correct += int(ok)
        else:
            late_total += 1
            late_correct += int(ok)

    return {
        "weekly_winner_accuracy_pct_stddev": round(statistics.pstdev(weekly_pct), 3) if len(weekly_pct) > 1 else None,
        "weekly_winner_accuracy_pct_min": round(min(weekly_pct), 2) if weekly_pct else None,
        "weekly_winner_accuracy_pct_max": round(max(weekly_pct), 2) if weekly_pct else None,
        "early_weeks_1_9": {
            "correct": early_correct,
            "total": early_total,
            "accuracy_pct": pct(early_correct, early_total),
        },
        "late_weeks_10_18": {
            "correct": late_correct,
            "total": late_total,
            "accuracy_pct": pct(late_correct, late_total),
        },
        "worst_weeks": [
            {
                "season": item.season,
                "week": item.week,
                "correct": item.correct,
                "total": item.total,
                "accuracy_pct": item.accuracy_pct,
            }
            for item in worst
        ],
        "best_weeks": [
            {
                "season": item.season,
                "week": item.week,
                "correct": item.correct,
                "total": item.total,
                "accuracy_pct": item.accuracy_pct,
            }
            for item in best
        ],
    }


def fetch_db_diagnostics(seasons: list[int]) -> dict:
    with psycopg2.connect(**DATABASE_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS rows_total,
                    COUNT(*) FILTER (WHERE predicted_at IS NULL) AS predicted_at_null,
                    COUNT(*) FILTER (WHERE predicted_at::date > game_date) AS predicted_after_game_date,
                    COUNT(*) FILTER (WHERE predicted_at::date = game_date) AS predicted_on_game_date,
                    COUNT(*) FILTER (WHERE predicted_at::date < game_date) AS predicted_before_game_date,
                    MIN(predicted_at) AS min_predicted_at,
                    MAX(predicted_at) AS max_predicted_at,
                    MIN(game_date) AS min_game_date,
                    MAX(game_date) AS max_game_date,
                    COUNT(*) FILTER (WHERE actual_margin < 0) AS negative_actual_margin_rows
                FROM hcl.ml_predictions
                WHERE season = ANY(%s)
                """,
                (seasons,),
            )
            timing_row = cur.fetchone()

            cur.execute(
                """
                SELECT
                    CASE
                        WHEN win_confidence IS NULL THEN 'null'
                        WHEN win_confidence < 0.55 THEN 'lt55'
                        WHEN win_confidence < 0.65 THEN '55to65'
                        WHEN win_confidence < 0.75 THEN '65to75'
                        ELSE 'gte75'
                    END AS confidence_bin,
                    COUNT(*) AS total_rows,
                    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) AS correct_rows
                FROM hcl.ml_predictions
                WHERE season = ANY(%s)
                GROUP BY 1
                ORDER BY 1
                """,
                (seasons,),
            )
            confidence_rows = cur.fetchall()

            cur.execute(
                """
                SELECT COUNT(*)
                FROM hcl.games
                WHERE season = ANY(%s)
                  AND away_score > home_score
                """,
                (seasons,),
            )
            away_wins = cur.fetchone()[0]

    confidence_bins: list[dict] = []
    for confidence_bin, total_rows, correct_rows in confidence_rows:
        confidence_bins.append(
            {
                "confidence_bin": confidence_bin,
                "total_rows": total_rows,
                "correct_rows": correct_rows,
                "accuracy_pct": pct(correct_rows, total_rows),
            }
        )

    return {
        "timing_and_margin": {
            "rows_total": timing_row[0],
            "predicted_at_null": timing_row[1],
            "predicted_after_game_date": timing_row[2],
            "predicted_on_game_date": timing_row[3],
            "predicted_before_game_date": timing_row[4],
            "predicted_after_game_date_pct": pct(timing_row[2], timing_row[0]),
            "min_predicted_at": timing_row[5].isoformat() if timing_row[5] else None,
            "max_predicted_at": timing_row[6].isoformat() if timing_row[6] else None,
            "min_game_date": timing_row[7].isoformat() if timing_row[7] else None,
            "max_game_date": timing_row[8].isoformat() if timing_row[8] else None,
            "negative_actual_margin_rows": timing_row[9],
            "away_win_games_in_hcl_games": away_wins,
        },
        "confidence_bins": confidence_bins,
    }


def build_findings(analysis: dict) -> list[dict]:
    findings: list[dict] = []

    total_lock = analysis["total_line_lock"]
    if (
        total_lock["rows_with_predicted_total_and_vegas_total"] > 0
        and (total_lock["predicted_total_equals_vegas_total_pct"] or 0) >= 95
        and total_lock["total_pick_evaluable_rows"] == 0
    ):
        findings.append(
            {
                "finding_id": "F1",
                "category": "feature_engineering",
                "severity": "high",
                "title": "Total predictions are line-anchored, not independently predictive",
                "evidence": (
                    f"predicted_total equals vegas_total for {total_lock['rows_predicted_total_equals_vegas_total']}/"
                    f"{total_lock['rows_with_predicted_total_and_vegas_total']} rows "
                    f"({total_lock['predicted_total_equals_vegas_total_pct']}%), with "
                    f"{total_lock['total_pick_evaluable_rows']} evaluable total-pick rows"
                ),
                "code_refs": [
                    "ml/predict_week.py:208",
                    "ml/predict_week.py:210",
                    "ml/predict_week.py:211",
                ],
            }
        )

    timing = analysis["db_diagnostics"]["timing_and_margin"]
    if (timing["predicted_after_game_date_pct"] or 0) >= 50:
        findings.append(
            {
                "finding_id": "F2",
                "category": "data_leakage_risk",
                "severity": "high",
                "title": "Prediction timestamps indicate retrospective generation for evaluated rows",
                "evidence": (
                    f"predicted_at::date > game_date for {timing['predicted_after_game_date']}/"
                    f"{timing['rows_total']} rows ({timing['predicted_after_game_date_pct']}%); "
                    f"predicted_at range {timing['min_predicted_at']} to {timing['max_predicted_at']}"
                ),
                "code_refs": [
                    "scripts/maintenance/backfill_historical_seasons.py:48",
                    "scripts/maintenance/backfill_historical_seasons.py:58",
                    "api_routes_ml.py:158",
                    "api_routes_ml.py:182",
                ],
            }
        )

    if timing["away_win_games_in_hcl_games"] > 0 and timing["negative_actual_margin_rows"] == 0:
        findings.append(
            {
                "finding_id": "F3",
                "category": "label_consistency",
                "severity": "medium",
                "title": "Stored actual margin sign is inconsistent with signed-margin scoring",
                "evidence": (
                    f"negative_actual_margin_rows={timing['negative_actual_margin_rows']} while "
                    f"away_win_games_in_hcl_games={timing['away_win_games_in_hcl_games']}"
                ),
                "code_refs": [
                    "scripts/maintenance/backfill_historical_seasons.py:106",
                    "api_routes_ml.py:761",
                ],
            }
        )

    drift = analysis["drift"]
    findings.append(
        {
            "finding_id": "F4",
            "category": "data_drift_or_instability",
            "severity": "medium",
            "title": "Weekly winner performance is highly volatile without clear directional drift",
            "evidence": (
                f"weekly winner accuracy min={drift['weekly_winner_accuracy_pct_min']}%, "
                f"max={drift['weekly_winner_accuracy_pct_max']}%, stddev={drift['weekly_winner_accuracy_pct_stddev']}; "
                f"early_weeks={drift['early_weeks_1_9']['accuracy_pct']}%, "
                f"late_weeks={drift['late_weeks_10_18']['accuracy_pct']}%"
            ),
            "code_refs": [
                "docs/sprints/ta070_audit_data/ta070_s70_2_20260504_230454_by_week.csv:2",
            ],
        }
    )

    return findings


def format_week_entries(entries: list[dict]) -> str:
    if not entries:
        return "- none"
    lines = []
    for item in entries:
        lines.append(
            f"- {item['season']} W{item['week']}: {item['correct']}/{item['total']} "
            f"({item['accuracy_pct']}%)"
        )
    return "\n".join(lines)


def write_markdown_report(path: pathlib.Path, analysis: dict) -> None:
    drift = analysis["drift"]
    timing = analysis["db_diagnostics"]["timing_and_margin"]
    total_lock = analysis["total_line_lock"]

    lines: list[str] = []
    lines.append("# TA-070 s70_3 Root-Cause Analysis")
    lines.append("")
    lines.append(f"Generated (UTC): {analysis['generated_at_utc']}")
    lines.append(f"Source combined CSV: {analysis['source_combined_csv']}")
    lines.append(f"Seasons analyzed: {analysis['seasons']}")
    lines.append("")
    lines.append("## Diagnostic Summary")
    lines.append(
        f"- Total line lock: {total_lock['rows_predicted_total_equals_vegas_total']}/"
        f"{total_lock['rows_with_predicted_total_and_vegas_total']} rows "
        f"({total_lock['predicted_total_equals_vegas_total_pct']}%)"
    )
    lines.append(
        f"- Evaluable total-pick rows: {total_lock['total_pick_evaluable_rows']}"
    )
    lines.append(
        f"- predicted_at after game_date: {timing['predicted_after_game_date']}/"
        f"{timing['rows_total']} ({timing['predicted_after_game_date_pct']}%)"
    )
    lines.append(
        f"- Winner weekly accuracy range: {drift['weekly_winner_accuracy_pct_min']}% to "
        f"{drift['weekly_winner_accuracy_pct_max']}% (stddev {drift['weekly_winner_accuracy_pct_stddev']})"
    )
    lines.append(
        f"- Winner accuracy early vs late: {drift['early_weeks_1_9']['accuracy_pct']}% "
        f"(weeks 1-9) vs {drift['late_weeks_10_18']['accuracy_pct']}% (weeks 10-18)"
    )
    lines.append("")
    lines.append("## Root-Cause Findings")
    for finding in analysis["findings"]:
        lines.append(
            f"### {finding['finding_id']} — {finding['title']} "
            f"({finding['category']}, severity={finding['severity']})"
        )
        lines.append(f"- Evidence: {finding['evidence']}")
        lines.append(f"- Code references: {', '.join(finding['code_refs'])}")
        lines.append("")

    lines.append("## Confidence Calibration Snapshot")
    for item in analysis["db_diagnostics"]["confidence_bins"]:
        lines.append(
            f"- {item['confidence_bin']}: {item['correct_rows']}/{item['total_rows']} "
            f"({item['accuracy_pct']}%)"
        )
    lines.append("")

    lines.append("## Weekly Extremes")
    lines.append("Worst weeks:")
    lines.append(format_week_entries(drift["worst_weeks"]))
    lines.append("")
    lines.append("Best weeks:")
    lines.append(format_week_entries(drift["best_weeks"]))
    lines.append("")

    lines.append("## Scope Notes")
    lines.append("- This report performs root-cause analysis only (TA-070 s70_3).")
    lines.append("- Corrective action planning is deferred to TA-070 s70_4.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate TA-070 s70_3 root-cause analysis artifacts")
    parser.add_argument(
        "--input-combined",
        default=None,
        help="Path to ta070_s70_1_*_combined.csv. Defaults to latest file in docs/sprints/ta070_audit_data",
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for s70_3 artifacts")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.input_combined:
        input_combined = pathlib.Path(args.input_combined)
    else:
        input_combined = resolve_latest_s70_1_combined(out_dir)

    rows = load_rows(input_combined)
    seasons = sorted({int(r["season"]) for r in rows})

    analysis = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_combined_csv": input_combined.relative_to(ROOT_DIR).as_posix(),
        "seasons": seasons,
        "total_line_lock": analyze_total_line_lock(rows),
        "drift": analyze_drift(rows),
        "db_diagnostics": fetch_db_diagnostics(seasons),
    }
    analysis["findings"] = build_findings(analysis)

    timestamp_slug = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    prefix = f"ta070_s70_3_{timestamp_slug}"
    summary_json_path = out_dir / f"{prefix}_summary.json"
    report_md_path = out_dir / f"{prefix}_root_cause.md"

    write_markdown_report(report_md_path, analysis)
    summary_json_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    print("TA-070 s70_3 root-cause analysis complete")
    print(f"source={input_combined}")
    print(f"seasons={seasons}")
    print(f"summary={summary_json_path}")
    print(f"report={report_md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())