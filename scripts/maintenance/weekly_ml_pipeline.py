#!/usr/bin/env python3
"""Phase 4 weekly ML operations pipeline.

Forward-only workflow:
1. Pick target season/week (or use explicit --season/--week).
2. Generate and persist missing XGBoost/Elo predictions for target week.
3. Score completed games for pending rows only.
4. Compute season snapshot + gates.
5. Write JSON/Markdown evidence artifacts.

By default, existing prediction rows are preserved (immutability-friendly):
- Inserts use ON CONFLICT DO NOTHING.
- If a target week already has rows, generation is skipped.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

from db_config import DATABASE_CONFIG
from ml.predict_elo import EloPredictionSystem
from ml.predict_week import WeeklyPredictor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_DIR = PROJECT_ROOT / "ml"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

DEFAULT_OUT_DIR = PROJECT_ROOT / "docs" / "sprints" / "phase4_weekly_ops"

GATE_PROFILE_DEFAULTS: dict[str, dict[str, Any]] = {
    "operational": {
        "winner_accuracy_floor": 40.0,
        "spread_mae_ceiling": 14.0,
        "coverage_min": 95.0,
        "elo_winner_accuracy_floor": 50.0,
        "elo_spread_mae_ceiling": 14.0,
        "elo_coverage_min": 95.0,
        "ai_vs_vegas_min_games": 32,
        "strict_ai_vs_vegas_sample": False,
        "ai_vs_vegas_delta_floor": -30.0,
    },
    "balanced": {
        "winner_accuracy_floor": 40.25,
        "spread_mae_ceiling": 13.9,
        "coverage_min": 98.0,
        "elo_winner_accuracy_floor": 55.0,
        "elo_spread_mae_ceiling": 11.0,
        "elo_coverage_min": 98.0,
        "ai_vs_vegas_min_games": 64,
        "strict_ai_vs_vegas_sample": False,
        "ai_vs_vegas_delta_floor": -29.0,
    },
    "strict-research": {
        "winner_accuracy_floor": 42.0,
        "spread_mae_ceiling": 13.5,
        "coverage_min": 98.0,
        "elo_winner_accuracy_floor": 54.0,
        "elo_spread_mae_ceiling": 12.5,
        "elo_coverage_min": 98.0,
        "ai_vs_vegas_min_games": 96,
        "strict_ai_vs_vegas_sample": True,
        "ai_vs_vegas_delta_floor": -10.0,
    },
}

PROFILE_RECOMMENDATION_ORDER = ("strict-research", "balanced", "operational")

CHECK_PRIORITY_WEIGHTS: dict[str, float] = {
    "xgb_winner_accuracy_floor": 5.0,
    "xgb_spread_mae_ceiling": 4.5,
    "ai_vs_vegas_delta_floor": 4.0,
    "elo_winner_accuracy_floor": 3.5,
    "elo_spread_mae_ceiling": 3.0,
    "xgb_coverage_min": 2.0,
    "elo_coverage_min": 1.5,
}


@dataclass
class GateThresholds:
    xgb_winner_accuracy_floor_pct: float
    xgb_spread_mae_ceiling: float
    xgb_coverage_min_pct: float
    elo_winner_accuracy_floor_pct: float
    elo_spread_mae_ceiling: float
    elo_coverage_min_pct: float
    ai_vs_vegas_min_games: int
    strict_ai_vs_vegas_sample: bool
    ai_vs_vegas_delta_floor_pct: float


def _connect():
    return psycopg2.connect(**DATABASE_CONFIG)


def _determine_target_week(conn, explicit_season: int | None, explicit_week: int | None) -> tuple[int, int, str]:
    if explicit_season is not None and explicit_week is not None:
        return explicit_season, explicit_week, "explicit"

    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Prefer the nearest upcoming regular-season week.
    cur.execute(
        """
        SELECT season, week
        FROM hcl.games
        WHERE COALESCE(is_postseason, FALSE) = FALSE
          AND home_score IS NULL
          AND away_score IS NULL
        GROUP BY season, week
        ORDER BY season DESC, week ASC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    if row:
        cur.close()
        return int(row["season"]), int(row["week"]), "auto_upcoming"

    # Fallback to latest regular-season week in data.
    cur.execute(
        """
        SELECT season, week
        FROM hcl.games
        WHERE COALESCE(is_postseason, FALSE) = FALSE
        ORDER BY season DESC, week DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        raise RuntimeError("No games found in hcl.games")

    return int(row["season"]), int(row["week"]), "auto_latest"


def _count_week_rows(conn, table_name: str, season: int, week: int) -> int:
    cur = conn.cursor()
    cur.execute(
        f"SELECT COUNT(*) FROM hcl.{table_name} WHERE season = %s AND week = %s",
        (season, week),
    )
    count = int(cur.fetchone()[0])
    cur.close()
    return count


def _insert_xgb_predictions(conn, season: int, week: int) -> dict[str, Any]:
    existing = _count_week_rows(conn, "ml_predictions", season, week)
    if existing > 0:
        return {
            "generated": 0,
            "inserted": 0,
            "skipped_existing_week": True,
            "existing_rows": existing,
        }

    predictor = WeeklyPredictor()
    predictions = predictor.predict_week(season, week)

    cur = conn.cursor()
    inserted = 0

    insert_sql = """
        INSERT INTO hcl.ml_predictions (
            game_id, season, week, home_team, away_team, game_date,
            predicted_winner, win_confidence, home_win_prob, away_win_prob,
            predicted_home_score, predicted_away_score, predicted_margin,
            ai_spread, vegas_spread, vegas_total
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (game_id) DO NOTHING
    """

    for p in predictions:
        cur.execute(
            insert_sql,
            (
                p.get("game_id"),
                p.get("season"),
                p.get("week"),
                p.get("home_team"),
                p.get("away_team"),
                p.get("game_date"),
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
            ),
        )
        inserted += cur.rowcount

    conn.commit()
    cur.close()

    return {
        "generated": len(predictions),
        "inserted": inserted,
        "skipped_existing_week": False,
        "existing_rows": existing,
    }


def _insert_elo_predictions(conn, season: int, week: int) -> dict[str, Any]:
    existing = _count_week_rows(conn, "ml_predictions_elo", season, week)
    if existing > 0:
        return {
            "generated": 0,
            "inserted": 0,
            "skipped_existing_week": True,
            "existing_rows": existing,
        }

    elo = EloPredictionSystem()
    games_df = elo.get_scheduled_games(season, week)

    if len(games_df) == 0:
        return {
            "generated": 0,
            "inserted": 0,
            "skipped_existing_week": False,
            "existing_rows": existing,
            "message": "No games found for target week",
        }

    cur = conn.cursor()
    inserted = 0
    generated = 0

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

    return {
        "generated": generated,
        "inserted": inserted,
        "skipped_existing_week": False,
        "existing_rows": existing,
    }


def _score_pending_rows(conn) -> dict[str, int]:
    cur = conn.cursor()

    # Forward-only scoring for pending XGBoost rows.
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
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          AND mp.result_recorded_at IS NULL
        """
    )
    xgb_updated = cur.rowcount

    # Forward-only scoring for Elo rows with missing outcome fields.
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
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          AND (
                e.actual_winner IS NULL
             OR e.actual_spread IS NULL
             OR e.prediction_correct IS NULL
             OR e.spread_error IS NULL
          )
        """
    )
    elo_updated = cur.rowcount

    conn.commit()
    cur.close()

    return {"xgb_updated": xgb_updated, "elo_updated": elo_updated}


def _season_snapshot(conn, season: int) -> dict[str, Any]:
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
        SELECT COUNT(*) AS completed_games
        FROM hcl.games
        WHERE season = %s
          AND COALESCE(is_postseason, FALSE) = FALSE
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        """,
        (season,),
    )
    completed = int((cur.fetchone() or {}).get("completed_games") or 0)

    cur.execute(
        """
        SELECT
            COUNT(*) AS scored,
            COALESCE(SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END), 0) AS correct,
            COALESCE(CAST(AVG(margin_prediction_error) AS NUMERIC(10,3)), 0) AS mae
        FROM hcl.ml_predictions
        WHERE season = %s
          AND result_recorded_at IS NOT NULL
        """,
        (season,),
    )
    xgb_row = cur.fetchone() or {}

    cur.execute(
        """
        SELECT
            COUNT(*) AS scored,
            COALESCE(SUM(CASE WHEN prediction_correct THEN 1 ELSE 0 END), 0) AS correct,
            COALESCE(CAST(AVG(spread_error) AS NUMERIC(10,3)), 0) AS mae
        FROM hcl.ml_predictions_elo
        WHERE season = %s
          AND prediction_correct IS NOT NULL
        """,
        (season,),
    )
    elo_row = cur.fetchone() or {}

    cur.close()

    xgb_scored = int(xgb_row.get("scored") or 0)
    xgb_correct = int(xgb_row.get("correct") or 0)
    xgb_mae = float(xgb_row.get("mae") or 0.0)

    elo_scored = int(elo_row.get("scored") or 0)
    elo_correct = int(elo_row.get("correct") or 0)
    elo_mae = float(elo_row.get("mae") or 0.0)

    def pct(n: int, d: int) -> float:
        return round((n / d) * 100.0, 2) if d > 0 else 0.0

    return {
        "season": season,
        "completed_games": completed,
        "xgb": {
            "scored_games": xgb_scored,
            "correct_predictions": xgb_correct,
            "winner_accuracy_pct": pct(xgb_correct, xgb_scored),
            "spread_mae": round(xgb_mae, 3),
            "coverage_pct": pct(xgb_scored, completed),
        },
        "elo": {
            "scored_games": elo_scored,
            "correct_predictions": elo_correct,
            "winner_accuracy_pct": pct(elo_correct, elo_scored),
            "spread_mae": round(elo_mae, 3),
            "coverage_pct": pct(elo_scored, completed),
        },
        "ai_vs_vegas": _ai_vs_vegas_snapshot(conn, season),
    }


def _ai_vs_vegas_snapshot(conn, season: int) -> dict[str, Any]:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT
            (g.home_score - g.away_score) AS actual_margin,
            mp.ai_spread,
            mp.vegas_spread
        FROM hcl.ml_predictions mp
        JOIN hcl.games g ON g.game_id = mp.game_id
        WHERE mp.season = %s
          AND COALESCE(g.is_postseason, FALSE) = FALSE
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          AND mp.ai_spread IS NOT NULL
          AND mp.vegas_spread IS NOT NULL
        """,
        (season,),
    )
    rows = cur.fetchall() or []
    cur.close()

    ai_wins = 0
    vegas_wins = 0
    ties = 0

    for row in rows:
        actual_margin = float(row["actual_margin"])
        ai_spread = float(row["ai_spread"])
        vegas_spread = float(row["vegas_spread"])

        # Match API tracking semantics: whichever spread is closer to -actual_margin wins.
        target_spread = -actual_margin
        ai_error = abs(ai_spread - target_spread)
        vegas_error = abs(vegas_spread - target_spread)

        if ai_error < vegas_error:
            ai_wins += 1
        elif vegas_error < ai_error:
            vegas_wins += 1
        else:
            ties += 1

    total_games = len(rows)

    def pct(n: int, d: int) -> float:
        return round((n / d) * 100.0, 2) if d > 0 else 0.0

    ai_win_pct = pct(ai_wins, total_games)
    vegas_win_pct = pct(vegas_wins, total_games)

    return {
        "total_games": total_games,
        "ai_wins": ai_wins,
        "vegas_wins": vegas_wins,
        "ties": ties,
        "ai_win_pct": ai_win_pct,
        "vegas_win_pct": vegas_win_pct,
        "delta_pct": round(ai_win_pct - vegas_win_pct, 2),
    }


def _evaluate_gates(snapshot: dict[str, Any], thresholds: GateThresholds) -> dict[str, Any]:
    completed = int(snapshot.get("completed_games") or 0)
    xgb = snapshot.get("xgb") or {}
    elo = snapshot.get("elo") or {}
    ai_vs_vegas = snapshot.get("ai_vs_vegas") or {}

    if completed == 0:
        return {
            "evaluated": False,
            "overall_pass": True,
            "reason": "No completed regular-season games for target season",
        }

    xgb_accuracy_pass = float(xgb.get("winner_accuracy_pct") or 0.0) >= thresholds.xgb_winner_accuracy_floor_pct
    xgb_mae_pass = float(xgb.get("spread_mae") or 0.0) <= thresholds.xgb_spread_mae_ceiling
    xgb_coverage_pass = float(xgb.get("coverage_pct") or 0.0) >= thresholds.xgb_coverage_min_pct

    elo_accuracy_pass = float(elo.get("winner_accuracy_pct") or 0.0) >= thresholds.elo_winner_accuracy_floor_pct
    elo_mae_pass = float(elo.get("spread_mae") or 0.0) <= thresholds.elo_spread_mae_ceiling
    elo_coverage_pass = float(elo.get("coverage_pct") or 0.0) >= thresholds.elo_coverage_min_pct

    ai_vs_vegas_games = int(ai_vs_vegas.get("total_games") or 0)
    ai_vs_vegas_delta = float(ai_vs_vegas.get("delta_pct") or 0.0)
    ai_vs_vegas_has_sample = ai_vs_vegas_games >= thresholds.ai_vs_vegas_min_games
    if ai_vs_vegas_has_sample:
        ai_vs_vegas_pass = ai_vs_vegas_delta >= thresholds.ai_vs_vegas_delta_floor_pct
        ai_vs_vegas_reason = None
    elif thresholds.strict_ai_vs_vegas_sample:
        ai_vs_vegas_pass = False
        ai_vs_vegas_reason = "insufficient sample; strict mode requires minimum games"
    else:
        ai_vs_vegas_pass = True
        ai_vs_vegas_reason = "insufficient sample; delta gate skipped"

    return {
        "evaluated": True,
        "overall_pass": (
            xgb_accuracy_pass
            and xgb_mae_pass
            and xgb_coverage_pass
            and elo_accuracy_pass
            and elo_mae_pass
            and elo_coverage_pass
            and ai_vs_vegas_pass
        ),
        "checks": {
            "xgb_winner_accuracy_floor": {
                "threshold": thresholds.xgb_winner_accuracy_floor_pct,
                "actual": float(xgb.get("winner_accuracy_pct") or 0.0),
                "pass": xgb_accuracy_pass,
            },
            "xgb_spread_mae_ceiling": {
                "threshold": thresholds.xgb_spread_mae_ceiling,
                "actual": float(xgb.get("spread_mae") or 0.0),
                "pass": xgb_mae_pass,
            },
            "xgb_coverage_min": {
                "threshold": thresholds.xgb_coverage_min_pct,
                "actual": float(xgb.get("coverage_pct") or 0.0),
                "pass": xgb_coverage_pass,
            },
            "elo_winner_accuracy_floor": {
                "threshold": thresholds.elo_winner_accuracy_floor_pct,
                "actual": float(elo.get("winner_accuracy_pct") or 0.0),
                "pass": elo_accuracy_pass,
            },
            "elo_spread_mae_ceiling": {
                "threshold": thresholds.elo_spread_mae_ceiling,
                "actual": float(elo.get("spread_mae") or 0.0),
                "pass": elo_mae_pass,
            },
            "elo_coverage_min": {
                "threshold": thresholds.elo_coverage_min_pct,
                "actual": float(elo.get("coverage_pct") or 0.0),
                "pass": elo_coverage_pass,
            },
            "ai_vs_vegas_delta_floor": {
                "threshold": thresholds.ai_vs_vegas_delta_floor_pct,
                "actual": ai_vs_vegas_delta,
                "total_games": ai_vs_vegas_games,
                "min_games": thresholds.ai_vs_vegas_min_games,
                "strict_sample_required": thresholds.strict_ai_vs_vegas_sample,
                "has_sample": ai_vs_vegas_has_sample,
                "pass": ai_vs_vegas_pass,
                "reason": ai_vs_vegas_reason,
            },
        },
    }


def _thresholds_from_profile(profile_name: str) -> GateThresholds:
    defaults = GATE_PROFILE_DEFAULTS[profile_name]
    return GateThresholds(
        xgb_winner_accuracy_floor_pct=float(defaults["winner_accuracy_floor"]),
        xgb_spread_mae_ceiling=float(defaults["spread_mae_ceiling"]),
        xgb_coverage_min_pct=float(defaults["coverage_min"]),
        elo_winner_accuracy_floor_pct=float(defaults["elo_winner_accuracy_floor"]),
        elo_spread_mae_ceiling=float(defaults["elo_spread_mae_ceiling"]),
        elo_coverage_min_pct=float(defaults["elo_coverage_min"]),
        ai_vs_vegas_min_games=int(defaults["ai_vs_vegas_min_games"]),
        strict_ai_vs_vegas_sample=bool(defaults["strict_ai_vs_vegas_sample"]),
        ai_vs_vegas_delta_floor_pct=float(defaults["ai_vs_vegas_delta_floor"]),
    )


def _thresholds_to_dict(profile_name: str, thresholds: GateThresholds) -> dict[str, Any]:
    return {
        "profile": profile_name,
        "xgb_winner_accuracy_floor_pct": thresholds.xgb_winner_accuracy_floor_pct,
        "xgb_spread_mae_ceiling": thresholds.xgb_spread_mae_ceiling,
        "xgb_coverage_min_pct": thresholds.xgb_coverage_min_pct,
        "elo_winner_accuracy_floor_pct": thresholds.elo_winner_accuracy_floor_pct,
        "elo_spread_mae_ceiling": thresholds.elo_spread_mae_ceiling,
        "elo_coverage_min_pct": thresholds.elo_coverage_min_pct,
        "ai_vs_vegas_min_games": thresholds.ai_vs_vegas_min_games,
        "strict_ai_vs_vegas_sample": thresholds.strict_ai_vs_vegas_sample,
        "ai_vs_vegas_delta_floor_pct": thresholds.ai_vs_vegas_delta_floor_pct,
    }


def _check_gap_to_pass(check_name: str, check_data: dict[str, Any]) -> dict[str, Any]:
    if bool(check_data.get("pass")):
        return {
            "check": check_name,
            "gap_type": "none",
            "gap_to_pass": 0,
        }

    threshold = float(check_data.get("threshold") or 0.0)
    actual = float(check_data.get("actual") or 0.0)

    if check_name == "ai_vs_vegas_delta_floor" and bool(check_data.get("strict_sample_required")) and not bool(
        check_data.get("has_sample")
    ):
        min_games = int(check_data.get("min_games") or 0)
        total_games = int(check_data.get("total_games") or 0)
        return {
            "check": check_name,
            "gap_type": "games_short",
            "gap_to_pass": max(min_games - total_games, 0),
            "min_games": min_games,
            "total_games": total_games,
        }

    if check_name.endswith("_ceiling"):
        gap = max(actual - threshold, 0.0)
    else:
        gap = max(threshold - actual, 0.0)

    return {
        "check": check_name,
        "gap_type": "metric",
        "gap_to_pass": round(gap, 3),
        "actual": actual,
        "threshold": threshold,
    }


def _format_failed_check_gap(gap_row: dict[str, Any]) -> str:
    check_name = str(gap_row.get("check"))
    gap_type = str(gap_row.get("gap_type"))
    gap_to_pass = gap_row.get("gap_to_pass")

    if gap_type == "games_short":
        return f"{check_name}(+{int(gap_to_pass)} games)"
    return f"{check_name}(+{float(gap_to_pass):.3f})"


def _resolve_priority_weights(args: argparse.Namespace) -> tuple[dict[str, float], str]:
    weights = {k: float(v) for k, v in CHECK_PRIORITY_WEIGHTS.items()}
    source_tokens: list[str] = ["default"]

    if args.priority_weights_file:
        weight_path = Path(args.priority_weights_file)
        if not weight_path.exists():
            raise ValueError(f"Priority weights file not found: {weight_path}")
        payload = json.loads(weight_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Priority weights file must be a JSON object of check->weight")

        for check_name, value in payload.items():
            if check_name not in CHECK_PRIORITY_WEIGHTS:
                valid = ", ".join(sorted(CHECK_PRIORITY_WEIGHTS.keys()))
                raise ValueError(f"Unknown priority check '{check_name}'. Valid checks: {valid}")
            weights[str(check_name)] = float(value)

        source_tokens.append(f"file:{weight_path}")

    for override in args.priority_weight or []:
        if "=" not in override:
            raise ValueError(f"Invalid --priority-weight format '{override}'. Use check=value")
        check_name, raw_value = override.split("=", 1)
        check_name = check_name.strip()
        if check_name not in CHECK_PRIORITY_WEIGHTS:
            valid = ", ".join(sorted(CHECK_PRIORITY_WEIGHTS.keys()))
            raise ValueError(f"Unknown priority check '{check_name}'. Valid checks: {valid}")
        weights[check_name] = float(raw_value.strip())
        source_tokens.append(f"arg:{check_name}")

    return weights, ";".join(source_tokens)


def _build_priority_order(
    failed_check_gaps: list[dict[str, Any]],
    priority_weights: dict[str, float],
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []

    for gap in failed_check_gaps:
        check_name = str(gap.get("check") or "")
        weight = float(priority_weights.get(check_name, 1.0))
        gap_value = float(gap.get("gap_to_pass") or 0.0)
        score = round((weight * 100.0) + gap_value, 3)

        ranked.append(
            {
                "check": check_name,
                "priority_weight": weight,
                "priority_score": score,
                "gap_type": gap.get("gap_type"),
                "gap_to_pass": gap.get("gap_to_pass"),
            }
        )

    ranked.sort(key=lambda item: float(item.get("priority_score") or 0.0), reverse=True)
    return ranked


def _format_priority_item(item: dict[str, Any]) -> str:
    check_name = str(item.get("check") or "")
    score = float(item.get("priority_score") or 0.0)
    return f"{check_name}({score:.1f})"


def _build_improvement_estimate(failed_check_gaps: list[dict[str, Any]]) -> dict[str, Any]:
    estimate: dict[str, Any] = {
        "xgb_accuracy_increase_pct_points": 0.0,
        "xgb_mae_reduction": 0.0,
        "xgb_coverage_increase_pct_points": 0.0,
        "elo_accuracy_increase_pct_points": 0.0,
        "elo_mae_reduction": 0.0,
        "elo_coverage_increase_pct_points": 0.0,
        "ai_vs_vegas_delta_improvement_pct_points": 0.0,
        "ai_vs_vegas_additional_games_needed": 0,
    }

    for gap in failed_check_gaps:
        check = str(gap.get("check") or "")
        gap_value = float(gap.get("gap_to_pass") or 0.0)

        if check == "xgb_winner_accuracy_floor":
            estimate["xgb_accuracy_increase_pct_points"] = gap_value
        elif check == "xgb_spread_mae_ceiling":
            estimate["xgb_mae_reduction"] = gap_value
        elif check == "xgb_coverage_min":
            estimate["xgb_coverage_increase_pct_points"] = gap_value
        elif check == "elo_winner_accuracy_floor":
            estimate["elo_accuracy_increase_pct_points"] = gap_value
        elif check == "elo_spread_mae_ceiling":
            estimate["elo_mae_reduction"] = gap_value
        elif check == "elo_coverage_min":
            estimate["elo_coverage_increase_pct_points"] = gap_value
        elif check == "ai_vs_vegas_delta_floor":
            if str(gap.get("gap_type")) == "games_short":
                estimate["ai_vs_vegas_additional_games_needed"] = int(gap.get("gap_to_pass") or 0)
            else:
                estimate["ai_vs_vegas_delta_improvement_pct_points"] = gap_value

    return estimate


def _format_improvement_estimate(estimate: dict[str, Any]) -> str:
    tokens: list[str] = []
    if float(estimate.get("xgb_accuracy_increase_pct_points") or 0.0) > 0:
        tokens.append(
            f"xgb_acc+{float(estimate['xgb_accuracy_increase_pct_points']):.3f}"
        )
    if float(estimate.get("xgb_mae_reduction") or 0.0) > 0:
        tokens.append(
            f"xgb_mae-{float(estimate['xgb_mae_reduction']):.3f}"
        )
    if float(estimate.get("xgb_coverage_increase_pct_points") or 0.0) > 0:
        tokens.append(
            f"xgb_cov+{float(estimate['xgb_coverage_increase_pct_points']):.3f}"
        )
    if float(estimate.get("elo_accuracy_increase_pct_points") or 0.0) > 0:
        tokens.append(
            f"elo_acc+{float(estimate['elo_accuracy_increase_pct_points']):.3f}"
        )
    if float(estimate.get("elo_mae_reduction") or 0.0) > 0:
        tokens.append(
            f"elo_mae-{float(estimate['elo_mae_reduction']):.3f}"
        )
    if float(estimate.get("elo_coverage_increase_pct_points") or 0.0) > 0:
        tokens.append(
            f"elo_cov+{float(estimate['elo_coverage_increase_pct_points']):.3f}"
        )
    if float(estimate.get("ai_vs_vegas_delta_improvement_pct_points") or 0.0) > 0:
        tokens.append(
            f"ai_vs_vegas_delta+{float(estimate['ai_vs_vegas_delta_improvement_pct_points']):.3f}"
        )
    if int(estimate.get("ai_vs_vegas_additional_games_needed") or 0) > 0:
        tokens.append(
            f"ai_vs_vegas_games+{int(estimate['ai_vs_vegas_additional_games_needed'])}"
        )
    return ", ".join(tokens) if tokens else "none"


def _resolve_gate_thresholds(args: argparse.Namespace) -> tuple[GateThresholds, str]:
    profile_name = args.gate_profile
    thresholds = _thresholds_from_profile(profile_name)

    if args.winner_accuracy_floor is not None:
        thresholds.xgb_winner_accuracy_floor_pct = float(args.winner_accuracy_floor)
    if args.spread_mae_ceiling is not None:
        thresholds.xgb_spread_mae_ceiling = float(args.spread_mae_ceiling)
    if args.coverage_min is not None:
        thresholds.xgb_coverage_min_pct = float(args.coverage_min)
    if args.elo_winner_accuracy_floor is not None:
        thresholds.elo_winner_accuracy_floor_pct = float(args.elo_winner_accuracy_floor)
    if args.elo_spread_mae_ceiling is not None:
        thresholds.elo_spread_mae_ceiling = float(args.elo_spread_mae_ceiling)
    if args.elo_coverage_min is not None:
        thresholds.elo_coverage_min_pct = float(args.elo_coverage_min)
    if args.ai_vs_vegas_min_games is not None:
        thresholds.ai_vs_vegas_min_games = int(args.ai_vs_vegas_min_games)
    if args.strict_ai_vs_vegas_sample is not None:
        thresholds.strict_ai_vs_vegas_sample = bool(args.strict_ai_vs_vegas_sample)
    if args.ai_vs_vegas_delta_floor is not None:
        thresholds.ai_vs_vegas_delta_floor_pct = float(args.ai_vs_vegas_delta_floor)

    return thresholds, profile_name


def _write_profile_advisor_markdown(path: Path, report: dict[str, Any]) -> None:
    season = report["target"]["season"]
    week = report["target"]["week"]
    snapshot = report["snapshot"]

    lines = [
        "# Phase 4 Gate Profile Advisor",
        "",
        f"Generated (UTC): {report['generated_at_utc']}",
        f"Target: season {season}, week {week}",
        f"Target source: {report['target'].get('source')}",
        f"Recommendation: {report['recommended_profile']}",
        f"Reason: {report['recommendation_reason']}",
        f"Priority weight source: {report.get('priority_weight_source')}",
        "",
        "## Snapshot",
        f"- Completed games: {snapshot['completed_games']}",
        f"- XGBoost: {snapshot['xgb']['winner_accuracy_pct']}% accuracy, MAE {snapshot['xgb']['spread_mae']}, coverage {snapshot['xgb']['coverage_pct']}%",
        f"- Elo: {snapshot['elo']['winner_accuracy_pct']}% accuracy, MAE {snapshot['elo']['spread_mae']}, coverage {snapshot['elo']['coverage_pct']}%",
        f"- AI vs Vegas delta: {snapshot['ai_vs_vegas']['delta_pct']} across {snapshot['ai_vs_vegas']['total_games']} games",
        "",
        "## Profiles",
    ]

    for profile in sorted(report["profiles"].keys()):
        profile_row = report["profiles"][profile]
        lines.append(f"- {profile}: pass={profile_row.get('overall_pass')}")
        failed_checks = profile_row.get("failed_checks") or []
        failed_check_gaps = profile_row.get("failed_check_gaps") or []
        priority_order = profile_row.get("priority_order") or []
        improvement_estimate = profile_row.get("improvement_estimate") or {}
        if failed_checks:
            lines.append(f"  failed_checks: {', '.join(failed_checks)}")
        if failed_check_gaps:
            lines.append(
                f"  failed_check_gaps: {', '.join([_format_failed_check_gap(g) for g in failed_check_gaps])}"
            )
        if priority_order:
            lines.append(
                f"  priority_order: {', '.join([_format_priority_item(p) for p in priority_order])}"
            )
        if improvement_estimate:
            lines.append(
                f"  improvement_estimate: {_format_improvement_estimate(improvement_estimate)}"
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_markdown(path: Path, report: dict[str, Any]) -> None:
    season = report["target"]["season"]
    week = report["target"]["week"]
    snapshot = report["snapshot"]
    gates = report["gates"]

    lines = [
        "# Phase 4 Weekly ML Pipeline Report",
        "",
        f"Generated (UTC): {report['generated_at_utc']}",
        f"Target: season {season}, week {week}",
        f"Target source: {report['target'].get('source')}",
        "",
        "## Operations",
        f"- XGBoost generated: {report['xgb_generation']['generated']}",
        f"- XGBoost inserted: {report['xgb_generation']['inserted']}",
        f"- Elo generated: {report['elo_generation']['generated']}",
        f"- Elo inserted: {report['elo_generation']['inserted']}",
        f"- XGBoost rows scored this run: {report['scoring']['xgb_updated']}",
        f"- Elo rows scored this run: {report['scoring']['elo_updated']}",
        "",
        "## Season Snapshot",
        f"- Completed games: {snapshot['completed_games']}",
        f"- XGBoost: {snapshot['xgb']['correct_predictions']}/{snapshot['xgb']['scored_games']} ({snapshot['xgb']['winner_accuracy_pct']}%), MAE {snapshot['xgb']['spread_mae']}, coverage {snapshot['xgb']['coverage_pct']}%",
        f"- Elo: {snapshot['elo']['correct_predictions']}/{snapshot['elo']['scored_games']} ({snapshot['elo']['winner_accuracy_pct']}%), MAE {snapshot['elo']['spread_mae']}, coverage {snapshot['elo']['coverage_pct']}%",
        f"- AI vs Vegas: AI {snapshot['ai_vs_vegas']['ai_wins']} wins, Vegas {snapshot['ai_vs_vegas']['vegas_wins']} wins, ties {snapshot['ai_vs_vegas']['ties']}, delta {snapshot['ai_vs_vegas']['delta_pct']} pts",
        "",
        "## Gates",
        f"- Profile: {report['gate_thresholds'].get('profile')}",
        f"- Evaluated: {gates.get('evaluated')}",
        f"- Overall pass: {gates.get('overall_pass')}",
    ]

    checks = (gates.get("checks") or {})
    if checks:
        lines.append(f"- XGBoost winner accuracy floor: actual {checks['xgb_winner_accuracy_floor']['actual']} vs threshold {checks['xgb_winner_accuracy_floor']['threshold']} (pass={checks['xgb_winner_accuracy_floor']['pass']})")
        lines.append(f"- XGBoost spread MAE ceiling: actual {checks['xgb_spread_mae_ceiling']['actual']} vs threshold {checks['xgb_spread_mae_ceiling']['threshold']} (pass={checks['xgb_spread_mae_ceiling']['pass']})")
        lines.append(f"- XGBoost coverage minimum: actual {checks['xgb_coverage_min']['actual']} vs threshold {checks['xgb_coverage_min']['threshold']} (pass={checks['xgb_coverage_min']['pass']})")
        lines.append(f"- Elo winner accuracy floor: actual {checks['elo_winner_accuracy_floor']['actual']} vs threshold {checks['elo_winner_accuracy_floor']['threshold']} (pass={checks['elo_winner_accuracy_floor']['pass']})")
        lines.append(f"- Elo spread MAE ceiling: actual {checks['elo_spread_mae_ceiling']['actual']} vs threshold {checks['elo_spread_mae_ceiling']['threshold']} (pass={checks['elo_spread_mae_ceiling']['pass']})")
        lines.append(f"- Elo coverage minimum: actual {checks['elo_coverage_min']['actual']} vs threshold {checks['elo_coverage_min']['threshold']} (pass={checks['elo_coverage_min']['pass']})")
        lines.append(f"- AI vs Vegas delta floor: actual {checks['ai_vs_vegas_delta_floor']['actual']} across {checks['ai_vs_vegas_delta_floor']['total_games']} games vs threshold {checks['ai_vs_vegas_delta_floor']['threshold']} (pass={checks['ai_vs_vegas_delta_floor']['pass']})")
        if not checks["ai_vs_vegas_delta_floor"].get("has_sample"):
            lines.append(f"- AI vs Vegas gate note: {checks['ai_vs_vegas_delta_floor'].get('reason')}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline(args: argparse.Namespace) -> dict[str, Any]:
    conn = _connect()
    try:
        season, week, target_source = _determine_target_week(conn, args.season, args.week)

        xgb_generation = _insert_xgb_predictions(conn, season, week)
        elo_generation = _insert_elo_predictions(conn, season, week)
        scoring = _score_pending_rows(conn)

        snapshot = _season_snapshot(conn, season)
        thresholds, gate_profile = _resolve_gate_thresholds(args)
        gates = _evaluate_gates(snapshot, thresholds)

        report = {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "target": {
                "season": season,
                "week": week,
                "source": target_source,
            },
            "xgb_generation": xgb_generation,
            "elo_generation": elo_generation,
            "scoring": scoring,
            "snapshot": snapshot,
            "gate_thresholds": _thresholds_to_dict(gate_profile, thresholds),
            "gates": gates,
        }

        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        json_path = out_dir / f"weekly_ml_pipeline_{stamp}.json"
        md_path = out_dir / f"weekly_ml_pipeline_{stamp}.md"

        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        _write_markdown(md_path, report)

        report["artifact_paths"] = {
            "json": str(json_path),
            "markdown": str(md_path),
        }
        return report
    finally:
        conn.close()


def run_profile_advisor(args: argparse.Namespace) -> dict[str, Any]:
    conn = _connect()
    try:
        season, week, target_source = _determine_target_week(conn, args.season, args.week)
        snapshot = _season_snapshot(conn, season)
        priority_weights, priority_weight_source = _resolve_priority_weights(args)

        profile_rows: dict[str, Any] = {}
        for profile in sorted(GATE_PROFILE_DEFAULTS.keys()):
            thresholds = _thresholds_from_profile(profile)
            gates = _evaluate_gates(snapshot, thresholds)
            checks = gates.get("checks") or {}
            failed_checks = sorted(
                [name for name, data in checks.items() if not bool((data or {}).get("pass"))]
            )
            failed_check_gaps = [
                _check_gap_to_pass(name, checks[name] or {})
                for name in failed_checks
            ]
            priority_order = _build_priority_order(failed_check_gaps, priority_weights)
            improvement_estimate = _build_improvement_estimate(failed_check_gaps)
            profile_rows[profile] = {
                "gate_thresholds": _thresholds_to_dict(profile, thresholds),
                "gates": gates,
                "overall_pass": bool(gates.get("overall_pass")),
                "failed_checks": failed_checks,
                "failed_check_gaps": failed_check_gaps,
                "priority_order": priority_order,
                "improvement_estimate": improvement_estimate,
            }

        recommended_profile = "none"
        recommendation_reason = "No profile passed; review thresholds or metrics"
        for profile in PROFILE_RECOMMENDATION_ORDER:
            if profile_rows[profile]["overall_pass"]:
                recommended_profile = profile
                recommendation_reason = (
                    "Highest-strictness passing profile selected"
                    if profile != "operational"
                    else "Only operational profile currently passes"
                )
                break

        report = {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "mode": "profile_advisor",
            "target": {
                "season": season,
                "week": week,
                "source": target_source,
            },
            "snapshot": snapshot,
            "profiles": profile_rows,
            "recommended_profile": recommended_profile,
            "recommendation_reason": recommendation_reason,
            "priority_weights": priority_weights,
            "priority_weight_source": priority_weight_source,
        }

        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        json_path = out_dir / f"weekly_ml_profile_advisor_{stamp}.json"
        md_path = out_dir / f"weekly_ml_profile_advisor_{stamp}.md"

        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        _write_profile_advisor_markdown(md_path, report)

        report["artifact_paths"] = {
            "json": str(json_path),
            "markdown": str(md_path),
        }
        return report
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly Phase 4 ML operations pipeline")
    parser.add_argument("--season", type=int, default=None, help="Target season (optional)")
    parser.add_argument("--week", type=int, default=None, help="Target week (optional)")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Artifact output directory")
    parser.add_argument(
        "--gate-profile",
        choices=sorted(GATE_PROFILE_DEFAULTS.keys()),
        default="operational",
        help="Gate profile for default thresholds",
    )
    parser.add_argument(
        "--recommend-profile",
        action="store_true",
        help="Read-only advisor mode that evaluates all gate profiles without generation/scoring",
    )
    parser.add_argument(
        "--recommend-profile-compact",
        action="store_true",
        help="Advisor mode console output only lists failed checks by profile",
    )
    parser.add_argument(
        "--priority-weights-file",
        default=None,
        help="Optional JSON file with check->weight mappings for advisor priority scoring",
    )
    parser.add_argument(
        "--priority-weight",
        action="append",
        default=None,
        help="Override a single advisor priority weight (format: check=value). Repeatable.",
    )
    parser.add_argument("--winner-accuracy-floor", type=float, default=None)
    parser.add_argument("--spread-mae-ceiling", type=float, default=None)
    parser.add_argument("--coverage-min", type=float, default=None)
    parser.add_argument("--elo-winner-accuracy-floor", type=float, default=None)
    parser.add_argument("--elo-spread-mae-ceiling", type=float, default=None)
    parser.add_argument("--elo-coverage-min", type=float, default=None)
    parser.add_argument("--ai-vs-vegas-min-games", type=int, default=None)
    parser.add_argument(
        "--strict-ai-vs-vegas-sample",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Fail AI-vs-Vegas gate when sample size is below minimum",
    )
    parser.add_argument("--ai-vs-vegas-delta-floor", type=float, default=None)
    parser.add_argument(
        "--fail-on-gate",
        action="store_true",
        help="Exit code 1 when gates are evaluated and fail",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.recommend_profile:
        try:
            report = run_profile_advisor(args)
        except ValueError as exc:
            print(f"Advisor configuration error: {exc}")
            return 2

        print("=" * 72)
        print("PHASE 4 GATE PROFILE ADVISOR")
        print("=" * 72)
        print(f"Target season/week: {report['target']['season']} / {report['target']['week']} ({report['target']['source']})")
        print(f"Recommended profile: {report['recommended_profile']}")
        print(f"Reason: {report['recommendation_reason']}")
        print(f"Priority weight source: {report.get('priority_weight_source')}")

        snapshot = report["snapshot"]
        print(
            "Snapshot XGB/Elo accuracy: "
            f"{snapshot['xgb']['winner_accuracy_pct']}% / {snapshot['elo']['winner_accuracy_pct']}%"
        )
        print(
            "Snapshot AI vs Vegas delta: "
            f"{snapshot['ai_vs_vegas']['delta_pct']} across {snapshot['ai_vs_vegas']['total_games']} games"
        )

        for profile in sorted(report["profiles"].keys()):
            row = report["profiles"][profile]
            failed_checks = row.get("failed_checks") or []
            failed_check_gaps = row.get("failed_check_gaps") or []
            priority_order = row.get("priority_order") or []
            improvement_estimate = row.get("improvement_estimate") or {}
            if args.recommend_profile_compact:
                if failed_check_gaps:
                    compact = ", ".join([_format_failed_check_gap(g) for g in failed_check_gaps])
                    priority_text = ", ".join([_format_priority_item(p) for p in priority_order])
                    estimate_text = _format_improvement_estimate(improvement_estimate)
                    print(
                        f"Profile {profile}: failed_checks={compact} | priority={priority_text} | target={estimate_text}"
                    )
                else:
                    print(f"Profile {profile}: failed_checks=none")
            else:
                print(f"Profile {profile}: pass={row['overall_pass']}")
                if failed_checks:
                    print(f"  failed_checks: {', '.join(failed_checks)}")
                if failed_check_gaps:
                    full = ", ".join([_format_failed_check_gap(g) for g in failed_check_gaps])
                    print(f"  failed_check_gaps: {full}")
                if priority_order:
                    priority_text = ", ".join([_format_priority_item(p) for p in priority_order])
                    print(f"  priority_order: {priority_text}")
                if improvement_estimate:
                    print(f"  improvement_estimate: {_format_improvement_estimate(improvement_estimate)}")

        print(f"Artifact JSON: {report['artifact_paths']['json']}")
        print(f"Artifact MD:   {report['artifact_paths']['markdown']}")

        if args.fail_on_gate and report.get("recommended_profile") == "none":
            return 1
        return 0

    report = run_pipeline(args)

    print("=" * 72)
    print("PHASE 4 WEEKLY ML PIPELINE")
    print("=" * 72)
    print(f"Target season/week: {report['target']['season']} / {report['target']['week']} ({report['target']['source']})")
    print(
        "XGB generated/inserted: "
        f"{report['xgb_generation']['generated']} / {report['xgb_generation']['inserted']}"
    )
    print(
        "Elo generated/inserted: "
        f"{report['elo_generation']['generated']} / {report['elo_generation']['inserted']}"
    )
    print(
        "Scored rows (XGB/Elo): "
        f"{report['scoring']['xgb_updated']} / {report['scoring']['elo_updated']}"
    )

    xgb = report["snapshot"]["xgb"]
    elo = report["snapshot"]["elo"]
    ai_vs_vegas = report["snapshot"]["ai_vs_vegas"]
    print(
        "Season XGB snapshot: "
        f"accuracy {xgb['winner_accuracy_pct']}%, MAE {xgb['spread_mae']}, coverage {xgb['coverage_pct']}%"
    )
    print(
        "Season Elo snapshot: "
        f"accuracy {elo['winner_accuracy_pct']}%, MAE {elo['spread_mae']}, coverage {elo['coverage_pct']}%"
    )
    print(
        "AI vs Vegas snapshot: "
        f"AI {ai_vs_vegas['ai_wins']} vs Vegas {ai_vs_vegas['vegas_wins']} (ties {ai_vs_vegas['ties']}), delta {ai_vs_vegas['delta_pct']}"
    )

    gates = report["gates"]
    print(f"Gate profile: {report['gate_thresholds'].get('profile')}")
    print(f"Gates evaluated: {gates.get('evaluated')} | overall pass: {gates.get('overall_pass')}")
    print(f"Artifact JSON: {report['artifact_paths']['json']}")
    print(f"Artifact MD:   {report['artifact_paths']['markdown']}")

    if args.fail_on_gate and gates.get("evaluated") and not gates.get("overall_pass"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
