#!/usr/bin/env python3
"""TA-077: Run multi-season ML evaluation and AI-vs-Vegas comparison using TA-070 pipeline stages."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import statistics
import subprocess
import sys
from datetime import UTC, datetime

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT_DIR / "docs" / "sprints" / "ta077_multi_season_eval"

S70_1_SCRIPT = ROOT_DIR / "scripts" / "verification" / "ta070_extract_prediction_actuals.py"
S70_2_SCRIPT = ROOT_DIR / "scripts" / "verification" / "ta070_compute_audit_metrics.py"
S70_3_SCRIPT = ROOT_DIR / "scripts" / "verification" / "ta070_root_cause_analysis.py"
S70_4_SCRIPT = ROOT_DIR / "scripts" / "verification" / "ta070_publish_audit_summary.py"

PATTERN_S70_1_SUMMARY = re.compile(r"ta070_s70_1_(\d{8}_\d{6})_summary\.json$")
PATTERN_S70_1_COMBINED = re.compile(r"ta070_s70_1_(\d{8}_\d{6})_combined\.csv$")
PATTERN_S70_2_SUMMARY = re.compile(r"ta070_s70_2_(\d{8}_\d{6})_summary\.json$")
PATTERN_S70_3_SUMMARY = re.compile(r"ta070_s70_3_(\d{8}_\d{6})_summary\.json$")
PATTERN_S70_4_SUMMARY = re.compile(r"ta070_s70_4_(\d{8}_\d{6})_summary\.json$")


def resolve_latest(path: pathlib.Path, pattern: re.Pattern[str], glob_pattern: str) -> pathlib.Path:
    latest: tuple[str, pathlib.Path] | None = None
    for candidate in path.glob(glob_pattern):
        match = pattern.match(candidate.name)
        if not match:
            continue
        stamp = match.group(1)
        if latest is None or stamp > latest[0]:
            latest = (stamp, candidate)

    if latest is None:
        raise FileNotFoundError(f"No artifact matched {glob_pattern} in {path}")

    return latest[1]


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_float(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    if text in {"", "none", "null", "nan"}:
        return None
    return float(text)


def pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100.0, 2)


def run_step(command: list[str], cwd: pathlib.Path) -> dict:
    result = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True)
    payload = {
        "command": " ".join(command),
        "return_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
    if result.returncode != 0:
        raise RuntimeError(json.dumps(payload, indent=2))
    return payload


def compute_ai_vs_vegas_from_combined(path: pathlib.Path) -> dict:
    ai_wins = 0
    vegas_wins = 0
    ties = 0
    total = 0

    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            actual_margin = safe_float(row.get("actual_margin"))
            ai_spread = safe_float(row.get("ai_spread"))
            vegas_spread = safe_float(row.get("vegas_spread"))
            if actual_margin is None or ai_spread is None or vegas_spread is None:
                continue

            total += 1

            ai_result = actual_margin + ai_spread
            ai_covered = False
            if ai_result != 0:
                if ai_spread < 0:
                    ai_covered = actual_margin > abs(ai_spread)
                else:
                    ai_covered = actual_margin < -abs(ai_spread)

            vegas_result = actual_margin + vegas_spread
            vegas_covered = False
            if vegas_result != 0:
                if vegas_spread < 0:
                    vegas_covered = actual_margin > abs(vegas_spread)
                else:
                    vegas_covered = actual_margin < -abs(vegas_spread)

            if ai_covered and not vegas_covered:
                ai_wins += 1
            elif not ai_covered and vegas_covered:
                vegas_wins += 1
            else:
                ties += 1

    return {
        "total_games": total,
        "ai_wins": ai_wins,
        "vegas_wins": vegas_wins,
        "ties": ties,
        "ai_win_pct": pct(ai_wins, total),
        "vegas_win_pct": pct(vegas_wins, total),
        "tie_pct": pct(ties, total),
    }


def gate_status(
    leakage_pct: float | None,
    line_lock_pct: float | None,
    total_coverage_pct: float | None,
    max_leakage_pct: float,
    max_line_lock_pct: float,
    min_total_coverage_pct: float,
) -> dict:
    leakage_pass = leakage_pct is not None and leakage_pct <= max_leakage_pct
    line_lock_pass = line_lock_pct is not None and line_lock_pct <= max_line_lock_pct
    total_coverage_pass = total_coverage_pct is not None and total_coverage_pct >= min_total_coverage_pct

    return {
        "leakage_pass": leakage_pass,
        "line_lock_pass": line_lock_pass,
        "total_coverage_pass": total_coverage_pass,
        "overall_pass": leakage_pass and line_lock_pass and total_coverage_pass,
    }


def run_for_season(
    season: int,
    schema: str,
    season_dir: pathlib.Path,
    max_leakage_pct: float,
    max_line_lock_pct: float,
    min_total_coverage_pct: float,
) -> dict:
    season_dir.mkdir(parents=True, exist_ok=True)

    commands = [
        [sys.executable, str(S70_1_SCRIPT), "--schema", schema, "--seasons", str(season), "--out-dir", str(season_dir)],
        [sys.executable, str(S70_2_SCRIPT), "--out-dir", str(season_dir)],
        [sys.executable, str(S70_3_SCRIPT), "--out-dir", str(season_dir)],
        [sys.executable, str(S70_4_SCRIPT), "--out-dir", str(season_dir)],
    ]

    logs: list[dict] = []
    for command in commands:
        logs.append(run_step(command, ROOT_DIR))

    s70_1_summary_path = resolve_latest(season_dir, PATTERN_S70_1_SUMMARY, "ta070_s70_1_*_summary.json")
    s70_1_combined_path = resolve_latest(season_dir, PATTERN_S70_1_COMBINED, "ta070_s70_1_*_combined.csv")
    s70_2_summary_path = resolve_latest(season_dir, PATTERN_S70_2_SUMMARY, "ta070_s70_2_*_summary.json")
    s70_3_summary_path = resolve_latest(season_dir, PATTERN_S70_3_SUMMARY, "ta070_s70_3_*_summary.json")
    s70_4_summary_path = resolve_latest(season_dir, PATTERN_S70_4_SUMMARY, "ta070_s70_4_*_summary.json")

    s70_1 = load_json(s70_1_summary_path)
    s70_2 = load_json(s70_2_summary_path)
    s70_3 = load_json(s70_3_summary_path)
    s70_4 = load_json(s70_4_summary_path)

    overall = s70_2.get("overall", {})
    total_line_lock = s70_3.get("total_line_lock", {})
    timing = s70_3.get("db_diagnostics", {}).get("timing_and_margin", {})
    findings = s70_3.get("findings", [])

    ai_vs_vegas = compute_ai_vs_vegas_from_combined(s70_1_combined_path)

    season_row = {
        "season": season,
        "row_count": s70_2.get("row_count"),
        "winner_accuracy_pct": overall.get("winner_accuracy_pct"),
        "spread_accuracy_pct": overall.get("spread_accuracy_pct"),
        "total_accuracy_pct": overall.get("total_accuracy_pct"),
        "margin_mae_points": overall.get("margin_mae_points"),
        "total_mae_points": overall.get("total_mae_points"),
        "winner_coverage_pct": overall.get("winner_coverage_pct"),
        "spread_coverage_pct": overall.get("spread_coverage_pct"),
        "total_coverage_pct": overall.get("total_coverage_pct"),
        "predicted_total_equals_vegas_total_pct": total_line_lock.get("predicted_total_equals_vegas_total_pct"),
        "total_pick_evaluable_rows": total_line_lock.get("total_pick_evaluable_rows"),
        "predicted_after_game_date_pct": timing.get("predicted_after_game_date_pct"),
        "finding_ids": ",".join(f.get("finding_id", "") for f in findings if f.get("finding_id")),
        "ai_vs_vegas_total_games": ai_vs_vegas.get("total_games"),
        "ai_vs_vegas_ai_wins": ai_vs_vegas.get("ai_wins"),
        "ai_vs_vegas_vegas_wins": ai_vs_vegas.get("vegas_wins"),
        "ai_vs_vegas_ties": ai_vs_vegas.get("ties"),
        "ai_vs_vegas_ai_win_pct": ai_vs_vegas.get("ai_win_pct"),
        "ai_vs_vegas_vegas_win_pct": ai_vs_vegas.get("vegas_win_pct"),
        "ai_vs_vegas_tie_pct": ai_vs_vegas.get("tie_pct"),
    }

    gates = gate_status(
        leakage_pct=safe_float(season_row.get("predicted_after_game_date_pct")),
        line_lock_pct=safe_float(season_row.get("predicted_total_equals_vegas_total_pct")),
        total_coverage_pct=safe_float(season_row.get("total_coverage_pct")),
        max_leakage_pct=max_leakage_pct,
        max_line_lock_pct=max_line_lock_pct,
        min_total_coverage_pct=min_total_coverage_pct,
    )
    season_row.update(gates)

    return {
        "season": season,
        "season_dir": season_dir,
        "logs": logs,
        "row": season_row,
        "artifacts": {
            "s70_1_summary": s70_1_summary_path,
            "s70_1_combined": s70_1_combined_path,
            "s70_2_summary": s70_2_summary_path,
            "s70_3_summary": s70_3_summary_path,
            "s70_4_summary": s70_4_summary_path,
        },
        "s70_1": s70_1,
        "s70_2": s70_2,
        "s70_3": s70_3,
        "s70_4": s70_4,
    }


def write_csv(path: pathlib.Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def mean_or_none(values: list[float | None], precision: int = 3) -> float | None:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return round(statistics.mean(nums), precision)


def build_aggregate(rows: list[dict]) -> dict:
    winner_correct_total = sum(int(r.get("winner_correct_games") or 0) for r in rows)
    winner_eval_total = sum(int(r.get("winner_evaluable_games") or 0) for r in rows)
    spread_correct_total = sum(int(r.get("spread_correct_games") or 0) for r in rows)
    spread_eval_total = sum(int(r.get("spread_evaluable_games") or 0) for r in rows)
    total_correct_total = sum(int(r.get("total_correct_games") or 0) for r in rows)
    total_eval_total = sum(int(r.get("total_evaluable_games") or 0) for r in rows)

    ai_wins_total = sum(int(r.get("ai_vs_vegas_ai_wins") or 0) for r in rows)
    vegas_wins_total = sum(int(r.get("ai_vs_vegas_vegas_wins") or 0) for r in rows)
    ai_vs_vegas_total = sum(int(r.get("ai_vs_vegas_total_games") or 0) for r in rows)

    overall_pass_count = sum(1 for r in rows if r.get("overall_pass"))

    return {
        "season_count": len(rows),
        "weighted_winner_accuracy_pct": pct(winner_correct_total, winner_eval_total),
        "weighted_spread_accuracy_pct": pct(spread_correct_total, spread_eval_total),
        "weighted_total_accuracy_pct": pct(total_correct_total, total_eval_total),
        "average_margin_mae_points": mean_or_none([safe_float(r.get("margin_mae_points")) for r in rows]),
        "average_total_mae_points": mean_or_none([safe_float(r.get("total_mae_points")) for r in rows]),
        "average_total_coverage_pct": mean_or_none([safe_float(r.get("total_coverage_pct")) for r in rows], precision=2),
        "average_line_lock_pct": mean_or_none(
            [safe_float(r.get("predicted_total_equals_vegas_total_pct")) for r in rows],
            precision=2,
        ),
        "average_predicted_after_game_date_pct": mean_or_none(
            [safe_float(r.get("predicted_after_game_date_pct")) for r in rows],
            precision=2,
        ),
        "ai_vs_vegas_total_games": ai_vs_vegas_total,
        "ai_vs_vegas_ai_wins": ai_wins_total,
        "ai_vs_vegas_vegas_wins": vegas_wins_total,
        "ai_vs_vegas_ai_win_pct": pct(ai_wins_total, ai_vs_vegas_total),
        "ai_vs_vegas_vegas_win_pct": pct(vegas_wins_total, ai_vs_vegas_total),
        "seasons_passing_all_gates": overall_pass_count,
        "seasons_failing_any_gate": len(rows) - overall_pass_count,
    }


def write_report(path: pathlib.Path, run_summary: dict) -> None:
    aggregate = run_summary["aggregate"]
    rows = run_summary["by_season"]

    lines: list[str] = []
    lines.append("# TA-077 Multi-Season Evaluation Report")
    lines.append("")
    lines.append(f"Generated (UTC): {run_summary['generated_at_utc']}")
    lines.append(f"Schema: {run_summary['schema']}")
    lines.append(f"Seasons: {', '.join(str(s) for s in run_summary['seasons'])}")
    lines.append("")
    lines.append("## Aggregate Summary")
    lines.append(f"- Weighted winner accuracy: {aggregate.get('weighted_winner_accuracy_pct')}%")
    lines.append(f"- Weighted spread accuracy: {aggregate.get('weighted_spread_accuracy_pct')}%")
    lines.append(f"- Weighted total accuracy: {aggregate.get('weighted_total_accuracy_pct')}%")
    lines.append(f"- Average margin MAE: {aggregate.get('average_margin_mae_points')} points")
    lines.append(f"- Average total MAE: {aggregate.get('average_total_mae_points')} points")
    lines.append(f"- AI vs Vegas (spread head-to-head): AI {aggregate.get('ai_vs_vegas_ai_wins')} wins, Vegas {aggregate.get('ai_vs_vegas_vegas_wins')} wins, total {aggregate.get('ai_vs_vegas_total_games')} games")
    lines.append(f"- Gate pass count: {aggregate.get('seasons_passing_all_gates')} / {aggregate.get('season_count')}")
    lines.append("")
    lines.append("## Season Table")
    lines.append("| Season | Winner% | Spread% | Total% | Margin MAE | Total MAE | AI vs Vegas (AI/VEG/TIE) | Leak% | Line-Lock% | Total Coverage% | Gates Pass |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        lines.append(
            "| {season} | {winner_accuracy_pct} | {spread_accuracy_pct} | {total_accuracy_pct} | {margin_mae_points} | {total_mae_points} | {ai_vs_vegas_ai_wins}/{ai_vs_vegas_vegas_wins}/{ai_vs_vegas_ties} | {predicted_after_game_date_pct} | {predicted_total_equals_vegas_total_pct} | {total_coverage_pct} | {overall_pass} |".format(
                **row
            )
        )

    lines.append("")
    lines.append("## Gate Thresholds")
    lines.append(f"- Max leakage pct: {run_summary['gate_thresholds']['max_leakage_pct']}")
    lines.append(f"- Max line-lock pct: {run_summary['gate_thresholds']['max_line_lock_pct']}")
    lines.append(f"- Min totals coverage pct: {run_summary['gate_thresholds']['min_total_coverage_pct']}")
    lines.append("")
    lines.append("## Notes")
    lines.append("- AI vs Vegas values mirror the existing /api/ml/season-ai-vs-vegas comparison logic.")
    lines.append("- Totals quality is highly sensitive to predicted_total independence from vegas_total.")
    lines.append("- Gate failures indicate measurement integrity risks that should block completion claims.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TA-077 multi-season evaluation pipeline")
    parser.add_argument("--schema", default="hcl", help="Database schema containing games + ml_predictions")
    parser.add_argument("--seasons", nargs="+", type=int, default=[2021, 2022, 2023, 2024, 2025], help="Seasons to evaluate")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Root output directory for TA-077 artifacts")
    parser.add_argument("--max-leakage-pct", type=float, default=5.0, help="Pass threshold for predicted_after_game_date_pct")
    parser.add_argument("--max-line-lock-pct", type=float, default=95.0, help="Pass threshold for predicted_total_equals_vegas_total_pct")
    parser.add_argument("--min-total-coverage-pct", type=float, default=5.0, help="Pass threshold for total_coverage_pct")
    parser.add_argument("--fail-on-threshold", action="store_true", help="Exit with code 1 if any season fails gate thresholds")
    args = parser.parse_args()

    run_stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    run_dir = pathlib.Path(args.out_dir) / f"ta077_run_{run_stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    season_results: list[dict] = []
    by_season_rows: list[dict] = []
    execution_log: list[dict] = []

    for season in args.seasons:
        season_dir = run_dir / f"season_{season}"
        result = run_for_season(
            season=season,
            schema=args.schema,
            season_dir=season_dir,
            max_leakage_pct=args.max_leakage_pct,
            max_line_lock_pct=args.max_line_lock_pct,
            min_total_coverage_pct=args.min_total_coverage_pct,
        )
        season_results.append(result)

        row = dict(result["row"])
        row["winner_correct_games"] = result["s70_2"].get("overall", {}).get("winner_correct_games")
        row["winner_evaluable_games"] = result["s70_2"].get("overall", {}).get("winner_evaluable_games")
        row["spread_correct_games"] = result["s70_2"].get("overall", {}).get("spread_correct_games")
        row["spread_evaluable_games"] = result["s70_2"].get("overall", {}).get("spread_evaluable_games")
        row["total_correct_games"] = result["s70_2"].get("overall", {}).get("total_correct_games")
        row["total_evaluable_games"] = result["s70_2"].get("overall", {}).get("total_evaluable_games")
        by_season_rows.append(row)

        execution_log.extend(result["logs"])

    aggregate = build_aggregate(by_season_rows)

    run_summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "schema": args.schema,
        "seasons": args.seasons,
        "run_dir": run_dir.relative_to(ROOT_DIR).as_posix(),
        "gate_thresholds": {
            "max_leakage_pct": args.max_leakage_pct,
            "max_line_lock_pct": args.max_line_lock_pct,
            "min_total_coverage_pct": args.min_total_coverage_pct,
        },
        "aggregate": aggregate,
        "by_season": by_season_rows,
        "artifacts": {
            str(item["season"]): {
                key: value.relative_to(ROOT_DIR).as_posix() for key, value in item["artifacts"].items()
            }
            for item in season_results
        },
        "execution_log": execution_log,
    }

    season_csv_path = run_dir / f"ta077_multi_season_{run_stamp}_by_season.csv"
    summary_json_path = run_dir / f"ta077_multi_season_{run_stamp}_summary.json"
    report_md_path = run_dir / f"ta077_multi_season_{run_stamp}_report.md"

    csv_fields = [
        "season",
        "row_count",
        "winner_accuracy_pct",
        "spread_accuracy_pct",
        "total_accuracy_pct",
        "margin_mae_points",
        "total_mae_points",
        "winner_coverage_pct",
        "spread_coverage_pct",
        "total_coverage_pct",
        "predicted_total_equals_vegas_total_pct",
        "total_pick_evaluable_rows",
        "predicted_after_game_date_pct",
        "ai_vs_vegas_total_games",
        "ai_vs_vegas_ai_wins",
        "ai_vs_vegas_vegas_wins",
        "ai_vs_vegas_ties",
        "ai_vs_vegas_ai_win_pct",
        "ai_vs_vegas_vegas_win_pct",
        "ai_vs_vegas_tie_pct",
        "finding_ids",
        "leakage_pass",
        "line_lock_pass",
        "total_coverage_pass",
        "overall_pass",
    ]

    write_csv(season_csv_path, by_season_rows, csv_fields)
    summary_json_path.write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
    write_report(report_md_path, run_summary)

    print("TA-077 multi-season evaluation complete")
    print(f"run_dir={run_dir}")
    print(f"season_table={season_csv_path}")
    print(f"summary={summary_json_path}")
    print(f"report={report_md_path}")

    if args.fail_on_threshold and aggregate.get("seasons_failing_any_gate", 0) > 0:
        print("Gate failure detected. Exiting with non-zero status due to --fail-on-threshold.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
