#!/usr/bin/env python3
"""TA-019 s19_1: validate spread-training query extraction completeness.

Checks that ml/train_xgb_spread.py load_data(schema=...) returns all expected
regular-season rows for 2020+ week>=2 completed games.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import psycopg2

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db_config import DATABASE_CONFIG
from ml.train_xgb_spread import load_data

DEFAULT_OUT_DIR = ROOT_DIR / "docs" / "sprints" / "ta019_spread_retrain"


@dataclass
class ValidationResult:
    schema: str
    expected_total_rows: int
    extracted_total_rows: int
    expected_unique_game_ids: int
    extracted_unique_game_ids: int
    expected_by_season: Dict[str, int]
    extracted_by_season: Dict[str, int]
    duplicate_rows_in_extraction: int
    missing_expected_game_ids_count: int
    extra_game_ids_count: int
    null_feature_cells: int
    ready_for_retrain: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate spread-training query extraction completeness"
    )
    parser.add_argument("--schema", default="hcl", help="Database schema")
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help="Output directory for summary/report artifacts",
    )
    return parser.parse_args()


def query_expected(conn, schema: str):
    expected_sql = f"""
        SELECT
            season,
            COUNT(*) AS row_count,
            COUNT(DISTINCT game_id) AS distinct_game_ids
        FROM {schema}.games
        WHERE season >= 2020
          AND is_postseason = FALSE
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
          AND week >= 2
        GROUP BY season
        ORDER BY season
    """

    ids_sql = f"""
        SELECT game_id
        FROM {schema}.games
        WHERE season >= 2020
          AND is_postseason = FALSE
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
          AND week >= 2
    """

    by_season: Dict[str, int] = {}
    total_rows = 0
    total_distinct = 0

    with conn.cursor() as cur:
        cur.execute(expected_sql)
        for season, row_count, distinct_count in cur.fetchall():
            by_season[str(season)] = int(row_count)
            total_rows += int(row_count)
            total_distinct += int(distinct_count)

        cur.execute(ids_sql)
        expected_ids = {row[0] for row in cur.fetchall()}

    return total_rows, total_distinct, by_season, expected_ids


def evaluate(schema: str) -> ValidationResult:
    conn = psycopg2.connect(
        host=DATABASE_CONFIG["host"],
        port=DATABASE_CONFIG["port"],
        dbname=DATABASE_CONFIG["dbname"],
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"],
    )

    try:
        (
            expected_total_rows,
            expected_unique_game_ids,
            expected_by_season,
            expected_ids,
        ) = query_expected(conn, schema)
    finally:
        conn.close()

    df = load_data(schema=schema)

    extracted_total_rows = int(len(df))
    extracted_unique_game_ids = int(df["game_id"].nunique())
    extracted_by_season = {
        str(int(k)): int(v)
        for k, v in df.groupby("season")["game_id"].count().sort_index().to_dict().items()
    }
    extracted_ids = set(df["game_id"].tolist())

    duplicate_rows_in_extraction = extracted_total_rows - extracted_unique_game_ids
    missing_expected_ids_count = len(expected_ids - extracted_ids)
    extra_game_ids_count = len(extracted_ids - expected_ids)

    feature_columns: List[str] = [
        "home_ppg",
        "home_yards_pg",
        "home_pass_yards_pg",
        "home_rush_yards_pg",
        "home_yards_per_play",
        "home_turnovers",
        "home_third_down_pct",
        "home_red_zone_pct",
        "away_ppg",
        "away_yards_pg",
        "away_pass_yards_pg",
        "away_rush_yards_pg",
        "away_yards_per_play",
        "away_turnovers",
        "away_third_down_pct",
        "away_red_zone_pct",
        "spread_line",
        "total_line",
        "point_differential",
    ]
    null_feature_cells = int(df[feature_columns].isna().sum().sum())

    ready_for_retrain = all(
        [
            extracted_total_rows == expected_total_rows,
            extracted_unique_game_ids == expected_unique_game_ids,
            extracted_by_season == expected_by_season,
            duplicate_rows_in_extraction == 0,
            missing_expected_ids_count == 0,
            extra_game_ids_count == 0,
            null_feature_cells == 0,
        ]
    )

    return ValidationResult(
        schema=schema,
        expected_total_rows=expected_total_rows,
        extracted_total_rows=extracted_total_rows,
        expected_unique_game_ids=expected_unique_game_ids,
        extracted_unique_game_ids=extracted_unique_game_ids,
        expected_by_season=expected_by_season,
        extracted_by_season=extracted_by_season,
        duplicate_rows_in_extraction=duplicate_rows_in_extraction,
        missing_expected_game_ids_count=missing_expected_ids_count,
        extra_game_ids_count=extra_game_ids_count,
        null_feature_cells=null_feature_cells,
        ready_for_retrain=ready_for_retrain,
    )


def write_artifacts(result: ValidationResult, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"ta019_s19_1_{ts}"

    summary_path = out_dir / f"{stem}_summary.json"
    report_path = out_dir / f"{stem}_report.md"

    payload = {
        "subtask": "s19_1",
        "ticket": "TA-019",
        "objective": "Validate spread training query/data extraction returns complete expected rows",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "schema": result.schema,
        "checks": {
            "expected_total_rows": result.expected_total_rows,
            "extracted_total_rows": result.extracted_total_rows,
            "expected_unique_game_ids": result.expected_unique_game_ids,
            "extracted_unique_game_ids": result.extracted_unique_game_ids,
            "expected_by_season": result.expected_by_season,
            "extracted_by_season": result.extracted_by_season,
            "duplicate_rows_in_extraction": result.duplicate_rows_in_extraction,
            "missing_expected_game_ids_count": result.missing_expected_game_ids_count,
            "extra_game_ids_count": result.extra_game_ids_count,
            "null_feature_cells": result.null_feature_cells,
        },
        "ready_for_retrain": result.ready_for_retrain,
    }

    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report_lines = [
        "# TA-019 s19_1 Spread Data Validation",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Schema: {result.schema}",
        f"- Ready for retrain: {result.ready_for_retrain}",
        "",
        "## Coverage Checks",
        f"- Expected total rows: {result.expected_total_rows}",
        f"- Extracted total rows: {result.extracted_total_rows}",
        f"- Expected unique game IDs: {result.expected_unique_game_ids}",
        f"- Extracted unique game IDs: {result.extracted_unique_game_ids}",
        f"- Duplicate rows in extraction: {result.duplicate_rows_in_extraction}",
        f"- Missing expected game IDs: {result.missing_expected_game_ids_count}",
        f"- Extra extracted game IDs: {result.extra_game_ids_count}",
        f"- Null feature cells (selected model inputs + target): {result.null_feature_cells}",
        "",
        "## Season Coverage",
        f"- Expected by season: {result.expected_by_season}",
        f"- Extracted by season: {result.extracted_by_season}",
        "",
        "## Artifacts",
        f"- Summary JSON: {summary_path.as_posix()}",
        f"- Report MD: {report_path.as_posix()}",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return summary_path, report_path


def main() -> int:
    args = parse_args()
    result = evaluate(schema=args.schema)
    summary_path, report_path = write_artifacts(result, Path(args.out_dir))

    print("TA-019 s19_1 validation complete")
    print(f"schema={result.schema}")
    print(f"ready_for_retrain={result.ready_for_retrain}")
    print(
        "rows expected/extracted="
        f"{result.expected_total_rows}/{result.extracted_total_rows}"
    )
    print(
        "unique game_ids expected/extracted="
        f"{result.expected_unique_game_ids}/{result.extracted_unique_game_ids}"
    )
    print(f"duplicate_rows_in_extraction={result.duplicate_rows_in_extraction}")
    print(f"missing_expected_game_ids_count={result.missing_expected_game_ids_count}")
    print(f"extra_game_ids_count={result.extra_game_ids_count}")
    print(f"null_feature_cells={result.null_feature_cells}")
    print(f"summary={summary_path.as_posix()}")
    print(f"report={report_path.as_posix()}")

    return 0 if result.ready_for_retrain else 1


if __name__ == "__main__":
    raise SystemExit(main())
