#!/usr/bin/env python3
"""Safely backfill Elo predictions without mutating XGBoost prediction rows.

This script only inserts missing records into hcl.ml_predictions_elo using
ON CONFLICT DO NOTHING. It never writes to hcl.ml_predictions.

Usage:
    python scripts/maintenance/backfill_elo_only.py --start-season 2020 --end-season 2024
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import pandas as pd
import psycopg2
from psycopg2.extensions import connection as PgConnection

from db_config import DATABASE_CONFIG
from ml.predict_elo import EloPredictionSystem


def _connect() -> PgConnection:
    return psycopg2.connect(**DATABASE_CONFIG)


def _season_weeks(conn: PgConnection, start_season: int, end_season: int) -> list[tuple[int, int]]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT season, week
        FROM hcl.games
        WHERE season BETWEEN %s AND %s
          AND COALESCE(is_postseason, FALSE) = FALSE
        GROUP BY season, week
        ORDER BY season, week
        """,
        (start_season, end_season),
    )
    rows = [(int(season), int(week)) for season, week in cur.fetchall()]
    cur.close()
    return rows


def _snapshot_ml_predictions(conn: PgConnection, start_season: int, end_season: int) -> dict[str, Any]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            COUNT(*) AS rows_count,
            md5(
                string_agg(
                    game_id::text || '|' ||
                    COALESCE(predicted_winner, '') || '|' ||
                    COALESCE(ai_spread::text, '') || '|' ||
                    COALESCE(vegas_spread::text, ''),
                    ',' ORDER BY game_id
                )
            ) AS fingerprint
        FROM hcl.ml_predictions
        WHERE season BETWEEN %s AND %s
        """,
        (start_season, end_season),
    )
    rows_count, fingerprint = cur.fetchone()
    cur.close()
    return {
        "rows_count": int(rows_count or 0),
        "fingerprint": fingerprint,
    }


def _insert_elo_for_week(
    conn: PgConnection,
    elo: EloPredictionSystem,
    season: int,
    week: int,
) -> dict[str, int]:
    games_df = elo.get_scheduled_games(season, week)
    if len(games_df) == 0:
        return {"generated": 0, "inserted": 0}

    insert_sql = """
        INSERT INTO hcl.ml_predictions_elo (
            game_id, season, week, game_date, home_team, away_team,
            home_elo, away_elo, elo_diff,
            home_win_prob, away_win_prob,
            predicted_winner, confidence,
            elo_spread, vegas_spread, spread_diff,
            split_prediction, prediction_date
        ) VALUES (
            %(game_id)s, %(season)s, %(week)s, %(game_date)s, %(home_team)s, %(away_team)s,
            %(home_elo)s, %(away_elo)s, %(elo_diff)s,
            %(home_win_prob)s, %(away_win_prob)s,
            %(predicted_winner)s, %(confidence)s,
            %(elo_spread)s, %(vegas_spread)s, %(spread_diff)s,
            %(split_prediction)s, NOW()
        )
        ON CONFLICT (game_id) DO NOTHING
    """

    cur = conn.cursor()
    inserted = 0
    generated = 0

    for _, game in games_df.iterrows():
        spread_line = game["spread_line"] if pd.notna(game["spread_line"]) else None
        pred = elo.predict_game(
            game["home_team"],
            game["away_team"],
            spread_line=spread_line,
            is_neutral=False,
        )
        row = {
            "game_id": game["game_id"],
            "season": season,
            "week": week,
            "game_date": game["game_date"],
            "home_team": pred["home_team"],
            "away_team": pred["away_team"],
            "home_elo": pred["home_elo"],
            "away_elo": pred["away_elo"],
            "elo_diff": pred["elo_diff"],
            "home_win_prob": pred["home_win_prob"],
            "away_win_prob": pred["away_win_prob"],
            "predicted_winner": pred["predicted_winner"],
            "confidence": pred["confidence"],
            "elo_spread": pred["elo_spread"],
            "vegas_spread": pred["vegas_spread"],
            "spread_diff": pred["spread_diff"],
            "split_prediction": pred["split_prediction"],
        }
        cur.execute(insert_sql, row)
        inserted += cur.rowcount
        generated += 1

    conn.commit()
    cur.close()
    return {"generated": generated, "inserted": inserted}


def _coverage_by_season(conn: PgConnection, start_season: int, end_season: int) -> list[dict[str, int]]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            g.season,
            COUNT(*) AS regular_games,
            COUNT(mp.game_id) AS xgb_rows,
            COUNT(e.game_id) AS elo_rows
        FROM hcl.games g
        LEFT JOIN hcl.ml_predictions mp ON mp.game_id = g.game_id
        LEFT JOIN hcl.ml_predictions_elo e ON e.game_id = g.game_id
        WHERE g.season BETWEEN %s AND %s
          AND COALESCE(g.is_postseason, FALSE) = FALSE
        GROUP BY g.season
        ORDER BY g.season
        """,
        (start_season, end_season),
    )
    rows = [
        {
            "season": int(season),
            "regular_games": int(regular_games),
            "xgb_rows": int(xgb_rows),
            "elo_rows": int(elo_rows),
        }
        for season, regular_games, xgb_rows, elo_rows in cur.fetchall()
    ]
    cur.close()
    return rows


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely backfill Elo-only predictions for a season range"
    )
    parser.add_argument("--start-season", type=int, default=2020)
    parser.add_argument("--end-season", type=int, default=2024)
    parser.add_argument(
        "--allow-ml-predictions-drift",
        action="store_true",
        help="Do not fail if hcl.ml_predictions fingerprint changes during run",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.start_season > args.end_season:
        raise ValueError("start-season cannot be greater than end-season")

    conn = _connect()
    try:
        pre = _snapshot_ml_predictions(conn, args.start_season, args.end_season)
        weeks = _season_weeks(conn, args.start_season, args.end_season)

        elo = EloPredictionSystem()

        total_generated = 0
        total_inserted = 0
        for season, week in weeks:
            result = _insert_elo_for_week(conn, elo, season, week)
            total_generated += int(result["generated"])
            total_inserted += int(result["inserted"])
            print(
                f"[elo-backfill] season={season} week={week} "
                f"generated={result['generated']} inserted={result['inserted']}"
            )

        post = _snapshot_ml_predictions(conn, args.start_season, args.end_season)
        coverage = _coverage_by_season(conn, args.start_season, args.end_season)

        summary = {
            "range": {
                "start_season": args.start_season,
                "end_season": args.end_season,
            },
            "weeks_processed": len(weeks),
            "elo_generated_total": total_generated,
            "elo_inserted_total": total_inserted,
            "ml_predictions_pre": pre,
            "ml_predictions_post": post,
            "coverage": coverage,
        }

        print("\n=== ELO BACKFILL SUMMARY ===")
        print(json.dumps(summary, indent=2))

        pre_sig = (pre.get("rows_count"), pre.get("fingerprint"))
        post_sig = (post.get("rows_count"), post.get("fingerprint"))
        if pre_sig != post_sig and not args.allow_ml_predictions_drift:
            print(
                "\nABORT: hcl.ml_predictions changed during run; "
                "safety contract violated."
            )
            return 2

        if pre_sig == post_sig:
            print("\nSAFE: hcl.ml_predictions unchanged.")
        else:
            print("\nWARNING: hcl.ml_predictions changed and drift was allowed by flag.")

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
