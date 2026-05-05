#!/usr/bin/env python3
"""TA-070 s70_2: Compute season/week accuracy, MAE, and coverage metrics."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT_DIR / "docs" / "sprints" / "ta070_audit_data"
S70_1_COMBINED_PATTERN = re.compile(r"ta070_s70_1_(\d{8}_\d{6})_combined\.csv$")

METRIC_FIELDS = [
    "scope",
    "season",
    "week",
    "games_total",
    "winner_evaluable_games",
    "winner_correct_games",
    "winner_accuracy_pct",
    "winner_coverage_pct",
    "spread_evaluable_games",
    "spread_correct_games",
    "spread_accuracy_pct",
    "spread_coverage_pct",
    "margin_mae_points",
    "margin_mae_coverage_pct",
    "total_evaluable_games",
    "total_correct_games",
    "total_accuracy_pct",
    "total_coverage_pct",
    "total_mae_points",
    "total_mae_coverage_pct",
    "vegas_spread_line_count",
    "vegas_spread_line_coverage_pct",
    "vegas_total_line_count",
    "vegas_total_line_coverage_pct",
    "predicted_score_count",
    "predicted_score_coverage_pct",
]


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"", "none", "null", "nan"}:
        return None
    return float(value)


def safe_pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100.0, 2)


def safe_mae(total_error: float, count: int) -> float | None:
    if count <= 0:
        return None
    return round(total_error / count, 3)


def write_csv(path: pathlib.Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


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


@dataclass
class MetricAccumulator:
    games_total: int = 0
    winner_evaluable_games: int = 0
    winner_correct_games: int = 0
    spread_evaluable_games: int = 0
    spread_correct_games: int = 0
    total_evaluable_games: int = 0
    total_correct_games: int = 0
    margin_mae_count: int = 0
    margin_mae_sum: float = 0.0
    total_mae_count: int = 0
    total_mae_sum: float = 0.0
    vegas_spread_line_count: int = 0
    vegas_total_line_count: int = 0
    predicted_score_count: int = 0

    def add_row(self, row: dict[str, str]) -> None:
        self.games_total += 1

        winner_correct = parse_bool(row.get("winner_pick_correct"))
        if winner_correct is not None:
            self.winner_evaluable_games += 1
            if winner_correct:
                self.winner_correct_games += 1

        spread_correct = parse_bool(row.get("spread_pick_correct"))
        if spread_correct is not None:
            self.spread_evaluable_games += 1
            if spread_correct:
                self.spread_correct_games += 1

        total_correct = parse_bool(row.get("total_pick_correct"))
        if total_correct is not None:
            self.total_evaluable_games += 1
            if total_correct:
                self.total_correct_games += 1

        margin_abs_error = parse_float(row.get("margin_abs_error"))
        if margin_abs_error is not None:
            self.margin_mae_count += 1
            self.margin_mae_sum += margin_abs_error

        total_abs_error = parse_float(row.get("total_abs_error"))
        if total_abs_error is not None:
            self.total_mae_count += 1
            self.total_mae_sum += total_abs_error

        if parse_float(row.get("vegas_spread")) is not None:
            self.vegas_spread_line_count += 1
        if parse_float(row.get("vegas_total")) is not None:
            self.vegas_total_line_count += 1

        predicted_home_score = parse_float(row.get("predicted_home_score"))
        predicted_away_score = parse_float(row.get("predicted_away_score"))
        if predicted_home_score is not None and predicted_away_score is not None:
            self.predicted_score_count += 1

    def to_dict(self, scope: str, season: int | None = None, week: int | None = None) -> dict:
        return {
            "scope": scope,
            "season": season,
            "week": week,
            "games_total": self.games_total,
            "winner_evaluable_games": self.winner_evaluable_games,
            "winner_correct_games": self.winner_correct_games,
            "winner_accuracy_pct": safe_pct(self.winner_correct_games, self.winner_evaluable_games),
            "winner_coverage_pct": safe_pct(self.winner_evaluable_games, self.games_total),
            "spread_evaluable_games": self.spread_evaluable_games,
            "spread_correct_games": self.spread_correct_games,
            "spread_accuracy_pct": safe_pct(self.spread_correct_games, self.spread_evaluable_games),
            "spread_coverage_pct": safe_pct(self.spread_evaluable_games, self.games_total),
            "margin_mae_points": safe_mae(self.margin_mae_sum, self.margin_mae_count),
            "margin_mae_coverage_pct": safe_pct(self.margin_mae_count, self.games_total),
            "total_evaluable_games": self.total_evaluable_games,
            "total_correct_games": self.total_correct_games,
            "total_accuracy_pct": safe_pct(self.total_correct_games, self.total_evaluable_games),
            "total_coverage_pct": safe_pct(self.total_evaluable_games, self.games_total),
            "total_mae_points": safe_mae(self.total_mae_sum, self.total_mae_count),
            "total_mae_coverage_pct": safe_pct(self.total_mae_count, self.games_total),
            "vegas_spread_line_count": self.vegas_spread_line_count,
            "vegas_spread_line_coverage_pct": safe_pct(self.vegas_spread_line_count, self.games_total),
            "vegas_total_line_count": self.vegas_total_line_count,
            "vegas_total_line_coverage_pct": safe_pct(self.vegas_total_line_count, self.games_total),
            "predicted_score_count": self.predicted_score_count,
            "predicted_score_coverage_pct": safe_pct(self.predicted_score_count, self.games_total),
        }


def load_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def compute_metrics(rows: list[dict[str, str]]) -> tuple[dict, list[dict], list[dict]]:
    overall = MetricAccumulator()
    by_season: dict[int, MetricAccumulator] = {}
    by_season_week: dict[tuple[int, int], MetricAccumulator] = {}

    for row in rows:
        season = int(row["season"])
        week = int(row["week"])

        overall.add_row(row)

        if season not in by_season:
            by_season[season] = MetricAccumulator()
        by_season[season].add_row(row)

        season_week_key = (season, week)
        if season_week_key not in by_season_week:
            by_season_week[season_week_key] = MetricAccumulator()
        by_season_week[season_week_key].add_row(row)

    season_metrics: list[dict] = []
    for season in sorted(by_season):
        season_metrics.append(by_season[season].to_dict(scope="season", season=season))

    week_metrics: list[dict] = []
    for season, week in sorted(by_season_week):
        week_metrics.append(by_season_week[(season, week)].to_dict(scope="season_week", season=season, week=week))

    return overall.to_dict(scope="overall"), season_metrics, week_metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute TA-070 s70_2 season/week audit metrics from s70_1 output")
    parser.add_argument(
        "--input-combined",
        default=None,
        help="Path to ta070_s70_1_*_combined.csv. Defaults to latest file in docs/sprints/ta070_audit_data",
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_DATA_DIR), help="Output directory for s70_2 artifacts")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.input_combined:
        input_combined = pathlib.Path(args.input_combined)
    else:
        input_combined = resolve_latest_s70_1_combined(out_dir)

    rows = load_rows(input_combined)
    overall_metrics, season_metrics, week_metrics = compute_metrics(rows)

    timestamp_slug = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    prefix = f"ta070_s70_2_{timestamp_slug}"

    season_csv_path = out_dir / f"{prefix}_by_season.csv"
    week_csv_path = out_dir / f"{prefix}_by_week.csv"
    summary_json_path = out_dir / f"{prefix}_summary.json"

    write_csv(season_csv_path, season_metrics, METRIC_FIELDS)
    write_csv(week_csv_path, week_metrics, METRIC_FIELDS)

    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_combined_csv": input_combined.relative_to(ROOT_DIR).as_posix(),
        "row_count": len(rows),
        "overall": overall_metrics,
        "by_season": season_metrics,
        "by_season_week": week_metrics,
        "metric_notes": {
            "accuracy_pct": "correct / evaluable * 100",
            "coverage_pct": "evaluable / games_total * 100",
            "mae_points": "mean absolute error over rows where prediction and actual values are both available",
            "spread_accuracy_scope": "rows where spread_pick_correct is non-null (push and missing-line rows excluded)",
            "total_accuracy_scope": "rows where total_pick_correct is non-null (push and missing-line rows excluded)",
        },
        "files": {
            "by_season_csv": season_csv_path.relative_to(ROOT_DIR).as_posix(),
            "by_week_csv": week_csv_path.relative_to(ROOT_DIR).as_posix(),
        },
    }

    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("TA-070 s70_2 metrics complete")
    print(f"source={input_combined}")
    print(f"rows={len(rows)}")
    print(f"by_season={season_csv_path}")
    print(f"by_week={week_csv_path}")
    print(f"summary={summary_json_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())