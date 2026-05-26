"""
Recalculate historical prediction rows for a season range.

Default scope is regular-season games for 2020-2025.
This script regenerates XGBoost rows, regenerates Elo rows, rescoring both
against final game outcomes, and writes a JSON summary artifact.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import warnings
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor


ROOT_DIR = Path(__file__).resolve().parents[2]
TA078_DIR = ROOT_DIR / "docs" / "sprints" / "ta078_vegas_tuning"
OUT_DIR = ROOT_DIR / "docs" / "sprints" / "phase4_weekly_ops"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
ml_dir = ROOT_DIR / "ml"
if str(ml_dir) not in sys.path:
    sys.path.insert(0, str(ml_dir))

from db_config import DATABASE_CONFIG
from ml.predict_elo import EloPredictionSystem
from ml.predict_week import WeeklyPredictor


def _connect():
    return psycopg2.connect(**DATABASE_CONFIG)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
        return datetime.combine(value, time(12, 0, 0))

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("Z", "+00:00")
    for fmt in (None, "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            if fmt is None:
                parsed = datetime.fromisoformat(text)
            else:
                parsed = datetime.strptime(text, fmt)
            return parsed.replace(tzinfo=None)
        except ValueError:
            continue
    return None


def _predicted_at_from_game_date(game_date_value: Any) -> datetime:
    parsed = _parse_datetime(game_date_value)
    if parsed is None:
        return datetime.now(tz=UTC).replace(tzinfo=None)
    return datetime.combine(parsed.date(), time(12, 0, 0))


def _load_latest_ta078() -> dict[str, Any] | None:
    summaries = sorted(TA078_DIR.glob("ta078_vegas_tuning_*_summary.json"))
    if not summaries:
        return None

    latest = summaries[-1]
    data = json.loads(latest.read_text(encoding="utf-8"))
    params = data.get("parameters") or {}
    linear_a = params.get("linear_a")
    linear_b = params.get("linear_b")
    if linear_a is None or linear_b is None:
        return None

    return {
        "summary_path": str(latest.relative_to(ROOT_DIR)).replace("\\", "/"),
        "bias": float(linear_a),
        "scale": float(linear_b),
    }


def _season_weeks(conn, start_season: int, end_season: int) -> list[tuple[int, int]]:
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


def _upsert_xgb_predictions(conn, predictions: list[dict[str, Any]]) -> int:
    if not predictions:
        return 0

    sql = """
        INSERT INTO hcl.ml_predictions (
            game_id, season, week, home_team, away_team, game_date,
            predicted_winner, win_confidence, home_win_prob, away_win_prob,
            predicted_home_score, predicted_away_score, predicted_margin,
            ai_spread, vegas_spread, vegas_total, predicted_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s
        )
        ON CONFLICT (game_id) DO UPDATE SET
            season = EXCLUDED.season,
            week = EXCLUDED.week,
            home_team = EXCLUDED.home_team,
            away_team = EXCLUDED.away_team,
            game_date = EXCLUDED.game_date,
            predicted_winner = EXCLUDED.predicted_winner,
            win_confidence = EXCLUDED.win_confidence,
            home_win_prob = EXCLUDED.home_win_prob,
            away_win_prob = EXCLUDED.away_win_prob,
            predicted_home_score = EXCLUDED.predicted_home_score,
            predicted_away_score = EXCLUDED.predicted_away_score,
            predicted_margin = EXCLUDED.predicted_margin,
            ai_spread = EXCLUDED.ai_spread,
            vegas_spread = EXCLUDED.vegas_spread,
            vegas_total = EXCLUDED.vegas_total,
            predicted_at = EXCLUDED.predicted_at
    """

    cur = conn.cursor()
    affected = 0
    for p in predictions:
        game_dt = _parse_datetime(p.get("game_date"))
        game_date_only = game_dt.date() if game_dt else None
        cur.execute(
            sql,
            (
                p.get("game_id"),
                p.get("season"),
                p.get("week"),
                p.get("home_team"),
                p.get("away_team"),
                game_date_only,
                p.get("predicted_winner"),
                p.get("confidence"),
                p.get("home_win_prob"),
                p.get("away_win_prob"),
                p.get("predicted_home_score"),
                p.get("predicted_away_score"),
                p.get("predicted_margin"),
                p.get("ai_spread"),
                p.get("vegas_spread"),
                p.get("total_line"),
                _predicted_at_from_game_date(p.get("game_date")),
            ),
        )
        affected += cur.rowcount
    cur.close()
    return affected


def _upsert_elo_predictions(conn, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    sql = """
        INSERT INTO hcl.ml_predictions_elo (
            game_id, season, week, game_date,
            home_team, away_team,
            home_elo, away_elo, elo_diff,
            home_win_prob, away_win_prob,
            predicted_winner, confidence,
            elo_spread, vegas_spread, spread_diff,
            split_prediction, prediction_date
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, %s, %s,
            %s, %s
        )
        ON CONFLICT (game_id) DO UPDATE SET
            season = EXCLUDED.season,
            week = EXCLUDED.week,
            game_date = EXCLUDED.game_date,
            home_team = EXCLUDED.home_team,
            away_team = EXCLUDED.away_team,
            home_elo = EXCLUDED.home_elo,
            away_elo = EXCLUDED.away_elo,
            elo_diff = EXCLUDED.elo_diff,
            home_win_prob = EXCLUDED.home_win_prob,
            away_win_prob = EXCLUDED.away_win_prob,
            predicted_winner = EXCLUDED.predicted_winner,
            confidence = EXCLUDED.confidence,
            elo_spread = EXCLUDED.elo_spread,
            vegas_spread = EXCLUDED.vegas_spread,
            spread_diff = EXCLUDED.spread_diff,
            split_prediction = EXCLUDED.split_prediction,
            prediction_date = EXCLUDED.prediction_date
    """

    cur = conn.cursor()
    affected = 0
    for row in rows:
        game_dt = _parse_datetime(row.get("game_date"))
        cur.execute(
            sql,
            (
                row.get("game_id"),
                row.get("season"),
                row.get("week"),
                game_dt,
                row.get("home_team"),
                row.get("away_team"),
                row.get("home_elo"),
                row.get("away_elo"),
                row.get("elo_diff"),
                row.get("home_win_prob"),
                row.get("away_win_prob"),
                row.get("predicted_winner"),
                row.get("confidence"),
                row.get("elo_spread"),
                row.get("vegas_spread"),
                row.get("spread_diff"),
                row.get("split_prediction"),
                _predicted_at_from_game_date(row.get("game_date")),
            ),
        )
        affected += cur.rowcount
    cur.close()
    return affected


def _rescore_predictions(conn, start_season: int, end_season: int) -> tuple[int, int]:
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE hcl.ml_predictions mp
        SET
            actual_winner = CASE
                WHEN g.home_score > g.away_score THEN g.home_team
                WHEN g.away_score > g.home_score THEN g.away_team
                ELSE 'TIE'
            END,
            actual_home_score = g.home_score,
            actual_away_score = g.away_score,
            actual_margin = g.home_score - g.away_score,
            win_prediction_correct = CASE
                WHEN g.home_score > g.away_score THEN mp.predicted_winner = g.home_team
                WHEN g.away_score > g.home_score THEN mp.predicted_winner = g.away_team
                ELSE FALSE
            END,
            score_prediction_error_home = ABS(mp.predicted_home_score - g.home_score),
            score_prediction_error_away = ABS(mp.predicted_away_score - g.away_score),
            margin_prediction_error = ABS(mp.predicted_margin - (g.home_score - g.away_score)),
            result_recorded_at = NOW()
        FROM hcl.games g
        WHERE mp.game_id = g.game_id
          AND mp.season BETWEEN %s AND %s
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          AND COALESCE(g.is_postseason, FALSE) = FALSE
        """,
        (start_season, end_season),
    )
    xgb_updated = cur.rowcount

    cur.execute(
        """
        UPDATE hcl.ml_predictions_elo e
        SET
            actual_winner = CASE
                WHEN g.home_score > g.away_score THEN g.home_team
                WHEN g.away_score > g.home_score THEN g.away_team
                ELSE 'TIE'
            END,
            actual_spread = (g.home_score - g.away_score),
            prediction_correct = CASE
                WHEN g.home_score > g.away_score THEN e.predicted_winner = g.home_team
                WHEN g.away_score > g.home_score THEN e.predicted_winner = g.away_team
                ELSE FALSE
            END,
            spread_error = CASE
                WHEN e.elo_spread IS NULL THEN NULL
                ELSE ABS(e.elo_spread - (g.home_score - g.away_score))
            END
        FROM hcl.games g
        WHERE e.game_id = g.game_id
          AND e.season BETWEEN %s AND %s
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          AND COALESCE(g.is_postseason, FALSE) = FALSE
        """,
        (start_season, end_season),
    )
    elo_updated = cur.rowcount

    cur.close()
    conn.commit()
    return xgb_updated, elo_updated


def _season_summary(conn, season: int) -> dict[str, Any]:
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
        SELECT
            COUNT(*) AS xgb_scored_games,
            COALESCE(SUM(CASE WHEN mp.win_prediction_correct THEN 1 ELSE 0 END), 0) AS xgb_correct,
            COALESCE(CAST(AVG(CASE WHEN mp.win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,2)), 0) AS xgb_win_accuracy,
            COALESCE(CAST(AVG(mp.margin_prediction_error) AS NUMERIC(10,2)), 0) AS xgb_margin_mae
        FROM hcl.ml_predictions mp
        JOIN hcl.games g ON g.game_id = mp.game_id
        WHERE mp.season = %s
          AND mp.result_recorded_at IS NOT NULL
          AND COALESCE(g.is_postseason, FALSE) = FALSE
          AND mp.predicted_at IS NOT NULL
          AND COALESCE(mp.game_date::date, g.game_date::date) IS NOT NULL
          AND mp.predicted_at::date <= COALESCE(mp.game_date::date, g.game_date::date)
        """,
        (season,),
    )
    xgb = cur.fetchone() or {}

    cur.execute(
        """
        SELECT
            COUNT(*) AS total_games,
            COALESCE(SUM(CASE WHEN e.prediction_correct THEN 1 ELSE 0 END), 0) AS elo_correct,
            COALESCE(CAST(AVG(CASE WHEN e.prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,2)), 0) AS elo_win_accuracy,
            COALESCE(CAST(AVG(e.spread_error) AS NUMERIC(10,2)), 0) AS elo_spread_mae
        FROM hcl.ml_predictions_elo e
        JOIN hcl.games g ON g.game_id = e.game_id
        WHERE e.season = %s
          AND e.predicted_winner IS NOT NULL
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          AND COALESCE(g.is_postseason, FALSE) = FALSE
          AND e.prediction_date IS NOT NULL
          AND COALESCE(e.game_date::date, g.game_date::date) IS NOT NULL
          AND e.prediction_date::date <= COALESCE(e.game_date::date, g.game_date::date)
        """,
        (season,),
    )
    elo = cur.fetchone() or {}

    cur.execute(
        """
        SELECT
            COUNT(*) AS compared_games,
            COALESCE(
                SUM(
                    CASE
                        WHEN mp.actual_margin IS NULL OR mp.ai_spread IS NULL OR mp.vegas_spread IS NULL THEN 0
                        WHEN ABS(mp.ai_spread - (-mp.actual_margin)) < ABS(mp.vegas_spread - (-mp.actual_margin)) THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS ai_wins,
            COALESCE(
                SUM(
                    CASE
                        WHEN mp.actual_margin IS NULL OR mp.ai_spread IS NULL OR mp.vegas_spread IS NULL THEN 0
                        WHEN ABS(mp.vegas_spread - (-mp.actual_margin)) < ABS(mp.ai_spread - (-mp.actual_margin)) THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS vegas_wins
        FROM hcl.ml_predictions mp
        JOIN hcl.games g ON g.game_id = mp.game_id
        WHERE mp.season = %s
          AND mp.result_recorded_at IS NOT NULL
          AND COALESCE(g.is_postseason, FALSE) = FALSE
          AND mp.predicted_at IS NOT NULL
          AND COALESCE(mp.game_date::date, g.game_date::date) IS NOT NULL
          AND mp.predicted_at::date <= COALESCE(mp.game_date::date, g.game_date::date)
        """,
        (season,),
    )
    h2h = cur.fetchone() or {}

    cur.close()

    compared_games = int(h2h.get("compared_games") or 0)
    ai_wins = int(h2h.get("ai_wins") or 0)
    vegas_wins = int(h2h.get("vegas_wins") or 0)
    ties = max(0, compared_games - (ai_wins + vegas_wins))

    return {
        "season": season,
        "xgb_scored_games": int(xgb.get("xgb_scored_games") or 0),
        "xgb_correct": int(xgb.get("xgb_correct") or 0),
        "xgb_win_accuracy": float(xgb.get("xgb_win_accuracy") or 0.0),
        "xgb_margin_mae": float(xgb.get("xgb_margin_mae") or 0.0),
        "elo_scored_games": int(elo.get("total_games") or 0),
        "elo_correct": int(elo.get("elo_correct") or 0),
        "elo_win_accuracy": float(elo.get("elo_win_accuracy") or 0.0),
        "elo_spread_mae": float(elo.get("elo_spread_mae") or 0.0),
        "ai_vs_vegas_compared_games": compared_games,
        "ai_vs_vegas_ai_wins": ai_wins,
        "ai_vs_vegas_vegas_wins": vegas_wins,
        "ai_vs_vegas_ties": ties,
    }


def _write_summary(summary: dict[str, Any]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"historical_recalc_{stamp}.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Recalculate historical predictions")
    parser.add_argument("--start-season", type=int, default=2020)
    parser.add_argument("--end-season", type=int, default=2025)
    parser.add_argument("--skip-elo", action="store_true")
    parser.add_argument("--no-ta078", action="store_true")
    args = parser.parse_args()

    warnings.filterwarnings(
        "ignore",
        message="pandas only supports SQLAlchemy connectable",
    )

    ta078 = None
    if not args.no_ta078:
        ta078 = _load_latest_ta078()
        if ta078:
            os.environ["AI_SPREAD_CAL_BIAS"] = str(ta078["bias"])
            os.environ["AI_SPREAD_CAL_SCALE"] = str(ta078["scale"])

    conn = _connect()
    weeks = _season_weeks(conn, args.start_season, args.end_season)

    predictor = WeeklyPredictor()
    elo_predictor = None if args.skip_elo else EloPredictionSystem()

    xgb_affected = 0
    elo_affected = 0

    total_weeks = len(weeks)
    for idx, (season, week) in enumerate(weeks, start=1):
        # Predict-week emits per-game logs; silence during bulk historical replay.
        with contextlib.redirect_stdout(io.StringIO()):
            xgb_predictions = predictor.predict_week(season, week)
        xgb_affected += _upsert_xgb_predictions(conn, xgb_predictions)

        if elo_predictor is not None:
            games_df = elo_predictor.get_scheduled_games(season, week)
            elo_rows: list[dict[str, Any]] = []
            for _, game in games_df.iterrows():
                spread_line = game["spread_line"] if pd.notna(game["spread_line"]) else None
                pred = elo_predictor.predict_game(
                    game["home_team"],
                    game["away_team"],
                    spread_line=spread_line,
                    is_neutral=False,
                )
                pred.update(
                    {
                        "game_id": game["game_id"],
                        "season": season,
                        "week": week,
                        "game_date": game["game_date"],
                    }
                )
                elo_rows.append(pred)
            elo_affected += _upsert_elo_predictions(conn, elo_rows)

        conn.commit()
        print(
            f"[recalc] {idx}/{total_weeks} season={season} week={week} "
            f"xgb_games={len(xgb_predictions)}"
        )

    xgb_scored_updates, elo_scored_updates = _rescore_predictions(
        conn,
        args.start_season,
        args.end_season,
    )

    by_season = [_season_summary(conn, s) for s in range(args.start_season, args.end_season + 1)]
    conn.close()

    summary = {
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "scope": "historical recalculation",
        "start_season": args.start_season,
        "end_season": args.end_season,
        "ta078": ta078,
        "xgb_rows_upserted": xgb_affected,
        "elo_rows_upserted": elo_affected,
        "xgb_rows_scored": xgb_scored_updates,
        "elo_rows_scored": elo_scored_updates,
        "by_season": by_season,
    }

    out_path = _write_summary(summary)

    print("\n=== HISTORICAL RECALC COMPLETE ===")
    print(f"Seasons: {args.start_season}-{args.end_season}")
    print(f"XGB rows upserted: {xgb_affected}")
    print(f"Elo rows upserted: {elo_affected}")
    print(f"XGB rows rescored: {xgb_scored_updates}")
    print(f"Elo rows rescored: {elo_scored_updates}")
    print(f"Summary: {out_path}")

    for row in by_season:
        print(
            f"Season {row['season']}: "
            f"XGB {row['xgb_win_accuracy']:.2f}% ({row['xgb_correct']}/{row['xgb_scored_games']}), "
            f"Elo {row['elo_win_accuracy']:.2f}% ({row['elo_correct']}/{row['elo_scored_games']}), "
            f"AIvsVegas {row['ai_vs_vegas_ai_wins']}-{row['ai_vs_vegas_vegas_wins']}-{row['ai_vs_vegas_ties']}"
        )


if __name__ == "__main__":
    main()
