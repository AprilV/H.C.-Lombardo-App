#!/usr/bin/env python3
"""TA-018 s18_1: Validate winner-training dataset coverage and schema alignment."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from datetime import UTC, datetime

import psycopg2
from psycopg2.extras import RealDictCursor

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db_config import DATABASE_CONFIG  # noqa: E402

DEFAULT_OUT_DIR = ROOT_DIR / "docs" / "sprints" / "ta018_winner_retrain"
TRAIN_SCRIPT_PATH = ROOT_DIR / "ml" / "train_xgb_winner.py"
SCHEMA_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

REQUIRED_COLUMNS = {
    "games": {
        "game_id",
        "season",
        "week",
        "game_date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "spread_line",
        "total_line",
    },
    "team_game_stats": {
        "game_id",
        "team",
        "points",
        "total_yards",
        "passing_yards",
        "rushing_yards",
        "yards_per_play",
        "turnovers",
        "third_down_pct",
    },
}


def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def safe_pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100.0, 2)


def fetch_table_columns(schema: str) -> dict[str, set[str]]:
    sql = """
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name IN ('games', 'team_game_stats')
    """
    columns: dict[str, set[str]] = {"games": set(), "team_game_stats": set()}
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (schema,))
            for table_name, column_name in cur.fetchall():
                columns[table_name].add(column_name)
    return columns


def fetch_dataset_metrics(schema: str) -> dict:
    sql = f"""
        WITH game_stats AS (
            SELECT
                tgs.game_id,
                tgs.team,
                g.season,
                g.week,
                g.game_date,
                tgs.points,
                tgs.total_yards,
                tgs.passing_yards,
                tgs.rushing_yards,
                tgs.yards_per_play,
                tgs.turnovers,
                tgs.third_down_pct
            FROM {schema}.team_game_stats tgs
            JOIN {schema}.games g ON tgs.game_id = g.game_id
            WHERE g.season >= 2020
        ),
        cumulative_stats AS (
            SELECT
                game_id,
                team,
                season,
                week,
                AVG(points) OVER (
                    PARTITION BY team, season
                    ORDER BY week
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) AS avg_ppg,
                AVG(total_yards) OVER (
                    PARTITION BY team, season
                    ORDER BY week
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) AS avg_yards,
                AVG(passing_yards) OVER (
                    PARTITION BY team, season
                    ORDER BY week
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) AS avg_pass_yards,
                AVG(rushing_yards) OVER (
                    PARTITION BY team, season
                    ORDER BY week
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) AS avg_rush_yards,
                AVG(yards_per_play) OVER (
                    PARTITION BY team, season
                    ORDER BY week
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) AS avg_yards_per_play,
                AVG(turnovers) OVER (
                    PARTITION BY team, season
                    ORDER BY week
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) AS avg_turnovers,
                AVG(third_down_pct) OVER (
                    PARTITION BY team, season
                    ORDER BY week
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ) AS avg_third_down_pct
            FROM game_stats
        ),
        eligible_games AS (
            SELECT
                g.game_id,
                g.season,
                g.week,
                g.home_score,
                g.away_score,
                g.spread_line,
                g.total_line,
                h.team AS home_stats_team,
                a.team AS away_stats_team
            FROM {schema}.games g
            LEFT JOIN cumulative_stats h ON g.game_id = h.game_id AND g.home_team = h.team
            LEFT JOIN cumulative_stats a ON g.game_id = a.game_id AND g.away_team = a.team
            WHERE g.season >= 2020
              AND g.home_score IS NOT NULL
              AND g.away_score IS NOT NULL
              AND g.week >= 2
        )
        SELECT
            season,
            COUNT(*) AS games,
            SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) AS home_wins,
            SUM(CASE WHEN away_score > home_score THEN 1 ELSE 0 END) AS away_wins,
            SUM(CASE WHEN home_score = away_score THEN 1 ELSE 0 END) AS ties,
            SUM(CASE WHEN spread_line IS NULL THEN 1 ELSE 0 END) AS missing_spread_line,
            SUM(CASE WHEN total_line IS NULL THEN 1 ELSE 0 END) AS missing_total_line,
            SUM(CASE WHEN home_stats_team IS NULL THEN 1 ELSE 0 END) AS missing_home_stats_row,
            SUM(CASE WHEN away_stats_team IS NULL THEN 1 ELSE 0 END) AS missing_away_stats_row
        FROM eligible_games
        GROUP BY season
        ORDER BY season
    """

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            by_season = cur.fetchall()

    total_games = sum(r["games"] for r in by_season)
    home_wins = sum(r["home_wins"] for r in by_season)
    away_wins = sum(r["away_wins"] for r in by_season)
    ties = sum(r["ties"] for r in by_season)
    missing_spread_line = sum(r["missing_spread_line"] for r in by_season)
    missing_total_line = sum(r["missing_total_line"] for r in by_season)
    missing_home_stats_row = sum(r["missing_home_stats_row"] for r in by_season)
    missing_away_stats_row = sum(r["missing_away_stats_row"] for r in by_season)

    split = {
        "train_rows_season_lte_2023": sum(r["games"] for r in by_season if r["season"] <= 2023),
        "validation_rows_2024": sum(r["games"] for r in by_season if r["season"] == 2024),
        "test_rows_2025": sum(r["games"] for r in by_season if r["season"] == 2025),
    }

    return {
        "row_count_total": total_games,
        "class_distribution": {
            "home_wins": home_wins,
            "away_wins": away_wins,
            "ties": ties,
            "home_win_rate_pct": safe_pct(home_wins, home_wins + away_wins + ties),
        },
        "line_coverage": {
            "missing_spread_line_rows": missing_spread_line,
            "missing_total_line_rows": missing_total_line,
            "missing_spread_line_pct": safe_pct(missing_spread_line, total_games),
            "missing_total_line_pct": safe_pct(missing_total_line, total_games),
        },
        "team_stats_join_coverage": {
            "missing_home_stats_rows": missing_home_stats_row,
            "missing_away_stats_rows": missing_away_stats_row,
            "missing_home_stats_pct": safe_pct(missing_home_stats_row, total_games),
            "missing_away_stats_pct": safe_pct(missing_away_stats_row, total_games),
        },
        "split_counts": split,
        "by_season": [
            {
                "season": row["season"],
                "games": row["games"],
                "home_wins": row["home_wins"],
                "away_wins": row["away_wins"],
                "ties": row["ties"],
                "missing_spread_line": row["missing_spread_line"],
                "missing_total_line": row["missing_total_line"],
                "missing_home_stats_row": row["missing_home_stats_row"],
                "missing_away_stats_row": row["missing_away_stats_row"],
            }
            for row in by_season
        ],
    }


def inspect_training_script() -> dict:
    text = TRAIN_SCRIPT_PATH.read_text(encoding="utf-8")
    load_data_hcl = bool(re.search(r"load_data\(schema=['\"]hcl['\"]\)", text))
    has_hcl_test = "hcl_test" in text

    return {
        "training_script": TRAIN_SCRIPT_PATH.relative_to(ROOT_DIR).as_posix(),
        "uses_load_data_schema_hcl": load_data_hcl,
        "contains_hcl_test_reference": has_hcl_test,
    }


def build_readiness(missing_columns: dict, script_inspection: dict, metrics: dict) -> dict:
    checks = {
        "required_columns_present": all(len(v) == 0 for v in missing_columns.values()),
        "training_script_uses_hcl": script_inspection["uses_load_data_schema_hcl"],
        "training_script_has_no_hcl_test": not script_inspection["contains_hcl_test_reference"],
        "split_train_nonzero": metrics["split_counts"]["train_rows_season_lte_2023"] > 0,
        "split_validation_2024_nonzero": metrics["split_counts"]["validation_rows_2024"] > 0,
        "split_test_2025_nonzero": metrics["split_counts"]["test_rows_2025"] > 0,
    }

    return {
        "checks": checks,
        "ready_for_retrain": all(checks.values()),
    }


def write_markdown(path: pathlib.Path, summary: dict) -> None:
    lines: list[str] = []
    lines.append("# TA-018 s18_1 Winner Training Dataset Validation")
    lines.append("")
    lines.append(f"Generated (UTC): {summary['generated_at_utc']}")
    lines.append(f"Schema: {summary['schema']}")
    lines.append("")

    readiness = summary["readiness"]
    lines.append("## Readiness")
    lines.append(f"- Ready for retrain: {readiness['ready_for_retrain']}")
    for key, value in readiness["checks"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Dataset Coverage")
    metrics = summary["dataset_metrics"]
    lines.append(f"- Total rows: {metrics['row_count_total']}")
    lines.append(
        f"- Split counts: train<=2023={metrics['split_counts']['train_rows_season_lte_2023']}, "
        f"validation2024={metrics['split_counts']['validation_rows_2024']}, "
        f"test2025={metrics['split_counts']['test_rows_2025']}"
    )
    lines.append(
        f"- Class distribution: home_wins={metrics['class_distribution']['home_wins']}, "
        f"away_wins={metrics['class_distribution']['away_wins']}, ties={metrics['class_distribution']['ties']} "
        f"(home_win_rate={metrics['class_distribution']['home_win_rate_pct']}%)"
    )
    lines.append(
        f"- Missing lines: spread={metrics['line_coverage']['missing_spread_line_rows']} "
        f"({metrics['line_coverage']['missing_spread_line_pct']}%), total={metrics['line_coverage']['missing_total_line_rows']} "
        f"({metrics['line_coverage']['missing_total_line_pct']}%)"
    )
    lines.append(
        f"- Missing team-stats joins: home={metrics['team_stats_join_coverage']['missing_home_stats_rows']} "
        f"({metrics['team_stats_join_coverage']['missing_home_stats_pct']}%), away={metrics['team_stats_join_coverage']['missing_away_stats_rows']} "
        f"({metrics['team_stats_join_coverage']['missing_away_stats_pct']}%)"
    )
    lines.append("")

    lines.append("## Schema Alignment")
    lines.append(
        f"- Script uses load_data(schema='hcl'): {summary['training_script_inspection']['uses_load_data_schema_hcl']}"
    )
    lines.append(
        f"- Script contains hcl_test reference: {summary['training_script_inspection']['contains_hcl_test_reference']}"
    )

    missing_columns = summary["missing_required_columns"]
    for table_name, missing in missing_columns.items():
        if missing:
            lines.append(f"- Missing required columns in {table_name}: {', '.join(missing)}")
        else:
            lines.append(f"- Missing required columns in {table_name}: none")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate TA-018 s18_1 winner training data readiness")
    parser.add_argument("--schema", default="hcl", help="Database schema used for winner training")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for evidence artifacts")
    args = parser.parse_args()

    if not SCHEMA_NAME_PATTERN.match(args.schema):
        raise ValueError(f"Invalid schema name: {args.schema}")

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    columns = fetch_table_columns(args.schema)
    missing_required_columns = {
        table_name: sorted(REQUIRED_COLUMNS[table_name] - columns.get(table_name, set()))
        for table_name in REQUIRED_COLUMNS
    }

    dataset_metrics = fetch_dataset_metrics(args.schema)
    training_script_inspection = inspect_training_script()
    readiness = build_readiness(missing_required_columns, training_script_inspection, dataset_metrics)

    timestamp_slug = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    prefix = f"ta018_s18_1_{timestamp_slug}"
    summary_json_path = out_dir / f"{prefix}_summary.json"
    report_md_path = out_dir / f"{prefix}_report.md"

    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "schema": args.schema,
        "training_script_inspection": training_script_inspection,
        "missing_required_columns": missing_required_columns,
        "dataset_metrics": dataset_metrics,
        "readiness": readiness,
        "files": {
            "summary": summary_json_path.relative_to(ROOT_DIR).as_posix(),
            "report": report_md_path.relative_to(ROOT_DIR).as_posix(),
        },
    }

    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(report_md_path, summary)

    print("TA-018 s18_1 validation complete")
    print(f"schema={args.schema}")
    print(f"ready_for_retrain={summary['readiness']['ready_for_retrain']}")
    print(f"summary={summary_json_path}")
    print(f"report={report_md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())