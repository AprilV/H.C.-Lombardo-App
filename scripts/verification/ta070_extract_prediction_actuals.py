#!/usr/bin/env python3
"""TA-070 s70_1: Extract prediction-vs-actual datasets for winner/spread/total outcomes."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys
from datetime import datetime, UTC

import psycopg2
from psycopg2.extras import RealDictCursor

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db_config import DATABASE_CONFIG  # noqa: E402

DEFAULT_OUT_DIR = ROOT_DIR / "docs" / "sprints" / "ta070_audit_data"
SCHEMA_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load_env_if_available() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT_DIR / ".env")
    except ImportError:
        pass


def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def spread_outcome(delta: float | None) -> str | None:
    if delta is None:
        return None
    if delta > 0:
        return "HOME_COVER"
    if delta < 0:
        return "AWAY_COVER"
    return "PUSH"


def total_outcome(delta: float | None) -> str | None:
    if delta is None:
        return None
    if delta > 0:
        return "OVER"
    if delta < 0:
        return "UNDER"
    return "PUSH"


def safe_abs_delta(a: float | int | None, b: float | int | None) -> float | None:
    if a is None or b is None:
        return None
    return abs(float(a) - float(b))


def write_csv(path: pathlib.Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def extract_rows(schema: str, seasons: list[int]) -> tuple[str, list[dict]]:
    if not SCHEMA_PATTERN.match(schema):
        raise ValueError(f"Invalid schema name: {schema}")

    sql = f"""
        SELECT
            p.game_id,
            p.season,
            p.week,
            COALESCE(g.game_date, p.game_date) AS game_date,
            p.home_team,
            p.away_team,
            p.predicted_winner,
            p.predicted_home_score,
            p.predicted_away_score,
            p.predicted_margin,
            p.ai_spread,
            COALESCE(p.vegas_spread, g.spread_line) AS vegas_spread,
            COALESCE(p.vegas_total, g.total_line) AS vegas_total,
            g.home_score,
            g.away_score,
            CASE
                WHEN g.home_score > g.away_score THEN g.home_team
                WHEN g.away_score > g.home_score THEN g.away_team
                ELSE 'TIE'
            END AS actual_winner,
            (g.home_score - g.away_score) AS actual_margin,
            (g.home_score + g.away_score) AS actual_total
        FROM {schema}.ml_predictions p
        JOIN {schema}.games g
          ON g.game_id = p.game_id
        WHERE p.season = ANY(%s)
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
        ORDER BY p.season, p.week, COALESCE(g.game_date, p.game_date), p.game_id
    """

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT current_database()")
            db_name = cur.fetchone()["current_database"]

            cur.execute(sql, (seasons,))
            records = cur.fetchall()

    rows: list[dict] = []
    for rec in records:
        predicted_total = None
        if rec["predicted_home_score"] is not None and rec["predicted_away_score"] is not None:
            predicted_total = float(rec["predicted_home_score"]) + float(rec["predicted_away_score"])

        vegas_spread = rec["vegas_spread"]
        predicted_margin = rec["predicted_margin"]
        actual_margin = rec["actual_margin"]

        spread_pred_delta = None
        spread_actual_delta = None
        if vegas_spread is not None:
            spread_pred_delta = (float(predicted_margin) + float(vegas_spread)) if predicted_margin is not None else None
            spread_actual_delta = float(actual_margin) + float(vegas_spread)

        predicted_cover_outcome = spread_outcome(spread_pred_delta)
        actual_cover_outcome = spread_outcome(spread_actual_delta)
        spread_pick_correct = None
        if predicted_cover_outcome and actual_cover_outcome and predicted_cover_outcome != "PUSH" and actual_cover_outcome != "PUSH":
            spread_pick_correct = predicted_cover_outcome == actual_cover_outcome

        vegas_total = rec["vegas_total"]
        actual_total = rec["actual_total"]

        total_pred_delta = (predicted_total - float(vegas_total)) if predicted_total is not None and vegas_total is not None else None
        total_actual_delta = (float(actual_total) - float(vegas_total)) if actual_total is not None and vegas_total is not None else None

        predicted_total_outcome = total_outcome(total_pred_delta)
        actual_total_outcome = total_outcome(total_actual_delta)

        total_pick_correct = None
        if predicted_total_outcome and actual_total_outcome and predicted_total_outcome != "PUSH" and actual_total_outcome != "PUSH":
            total_pick_correct = predicted_total_outcome == actual_total_outcome

        row = {
            "season": rec["season"],
            "week": rec["week"],
            "game_id": rec["game_id"],
            "game_date": rec["game_date"],
            "away_team": rec["away_team"],
            "home_team": rec["home_team"],
            "predicted_winner": rec["predicted_winner"],
            "actual_winner": rec["actual_winner"],
            "winner_pick_correct": rec["predicted_winner"] == rec["actual_winner"],
            "predicted_home_score": rec["predicted_home_score"],
            "predicted_away_score": rec["predicted_away_score"],
            "predicted_total": predicted_total,
            "actual_home_score": rec["home_score"],
            "actual_away_score": rec["away_score"],
            "actual_total": actual_total,
            "predicted_margin": predicted_margin,
            "actual_margin": actual_margin,
            "margin_abs_error": safe_abs_delta(predicted_margin, actual_margin),
            "ai_spread": rec["ai_spread"],
            "vegas_spread": vegas_spread,
            "predicted_cover_outcome": predicted_cover_outcome,
            "actual_cover_outcome": actual_cover_outcome,
            "spread_pick_correct": spread_pick_correct,
            "vegas_total": vegas_total,
            "predicted_total_outcome": predicted_total_outcome,
            "actual_total_outcome": actual_total_outcome,
            "total_pick_correct": total_pick_correct,
            "total_abs_error": safe_abs_delta(predicted_total, actual_total),
        }
        rows.append(row)

    return db_name, rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Export TA-070 prediction-vs-actual datasets")
    parser.add_argument("--schema", default="hcl", help="Database schema containing games + ml_predictions")
    parser.add_argument("--seasons", nargs="+", type=int, default=[2024, 2025], help="Seasons to extract")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for CSV/JSON artifacts")
    args = parser.parse_args()

    load_env_if_available()

    db_name, rows = extract_rows(args.schema, args.seasons)

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp_slug = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    prefix = f"ta070_s70_1_{timestamp_slug}"

    combined_fields = [
        "season",
        "week",
        "game_id",
        "game_date",
        "away_team",
        "home_team",
        "predicted_winner",
        "actual_winner",
        "winner_pick_correct",
        "predicted_home_score",
        "predicted_away_score",
        "predicted_total",
        "actual_home_score",
        "actual_away_score",
        "actual_total",
        "predicted_margin",
        "actual_margin",
        "margin_abs_error",
        "ai_spread",
        "vegas_spread",
        "predicted_cover_outcome",
        "actual_cover_outcome",
        "spread_pick_correct",
        "vegas_total",
        "predicted_total_outcome",
        "actual_total_outcome",
        "total_pick_correct",
        "total_abs_error",
    ]

    winner_fields = [
        "season",
        "week",
        "game_id",
        "game_date",
        "away_team",
        "home_team",
        "predicted_winner",
        "actual_winner",
        "winner_pick_correct",
    ]

    spread_fields = [
        "season",
        "week",
        "game_id",
        "game_date",
        "away_team",
        "home_team",
        "predicted_margin",
        "actual_margin",
        "margin_abs_error",
        "ai_spread",
        "vegas_spread",
        "predicted_cover_outcome",
        "actual_cover_outcome",
        "spread_pick_correct",
    ]

    total_fields = [
        "season",
        "week",
        "game_id",
        "game_date",
        "away_team",
        "home_team",
        "predicted_total",
        "actual_total",
        "total_abs_error",
        "vegas_total",
        "predicted_total_outcome",
        "actual_total_outcome",
        "total_pick_correct",
    ]

    combined_path = out_dir / f"{prefix}_combined.csv"
    winner_path = out_dir / f"{prefix}_winner.csv"
    spread_path = out_dir / f"{prefix}_spread.csv"
    total_path = out_dir / f"{prefix}_total.csv"
    summary_path = out_dir / f"{prefix}_summary.json"

    write_csv(combined_path, rows, combined_fields)
    write_csv(winner_path, rows, winner_fields)
    write_csv(spread_path, rows, spread_fields)
    write_csv(total_path, rows, total_fields)

    by_season: dict[str, int] = {}
    for row in rows:
        key = str(row["season"])
        by_season[key] = by_season.get(key, 0) + 1

    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "database": db_name,
        "schema": args.schema,
        "seasons": args.seasons,
        "row_count": len(rows),
        "by_season": by_season,
        "line_coverage": {
            "rows_with_vegas_spread": sum(1 for r in rows if r["vegas_spread"] is not None),
            "rows_with_vegas_total": sum(1 for r in rows if r["vegas_total"] is not None),
            "rows_with_predicted_scores": sum(
                1
                for r in rows
                if r["predicted_home_score"] is not None and r["predicted_away_score"] is not None
            ),
        },
        "files": {
            "combined": combined_path.relative_to(ROOT_DIR).as_posix(),
            "winner": winner_path.relative_to(ROOT_DIR).as_posix(),
            "spread": spread_path.relative_to(ROOT_DIR).as_posix(),
            "total": total_path.relative_to(ROOT_DIR).as_posix(),
        },
    }

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("TA-070 s70_1 extraction complete")
    print(f"database={db_name}")
    print(f"schema={args.schema}")
    print(f"seasons={args.seasons}")
    print(f"rows={len(rows)}")
    print(f"combined={combined_path}")
    print(f"winner={winner_path}")
    print(f"spread={spread_path}")
    print(f"total={total_path}")
    print(f"summary={summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
