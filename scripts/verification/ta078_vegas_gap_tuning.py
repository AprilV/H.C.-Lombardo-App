#!/usr/bin/env python3
"""TA-078: Diagnose and tune AI-vs-Vegas spread gap.

This script evaluates completed-game spread performance using:
- Baseline AI spread
- Mean-bias correction
- Linear calibration (target ~= a + b * ai_spread)
- Delta-optimized bias scan (maximize AI-vs-Vegas head-to-head delta)

Outputs:
- JSON summary
- Markdown report
- CSV bias scan table
- CSV validation-by-week breakdown
- CSV validation-by-vegas-bin breakdown
- CSV validation game-level deltas
- CSV targeted focus-week diagnostics
- CSV targeted high-spread diagnostics
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Iterable

import psycopg2
from psycopg2.extras import RealDictCursor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db_config import DATABASE_CONFIG

DEFAULT_OUT_DIR = PROJECT_ROOT / "docs" / "sprints" / "ta078_vegas_tuning"


@dataclass
class SpreadRow:
    game_id: str
    season: int
    week: int
    actual_margin: float
    ai_spread: float
    vegas_spread: float

    @property
    def target_spread(self) -> float:
        # Keep contract aligned with weekly_ml_pipeline.py and API semantics.
        return -self.actual_margin


@dataclass
class MethodResult:
    method: str
    games: int
    mae: float
    rmse: float
    wins_vs_vegas: int
    vegas_wins: int
    ties_vs_vegas: int
    win_pct: float
    vegas_win_pct: float
    delta_pct: float


def week_label(season: int, week: int) -> str:
    return f"{season}-W{week:02d}"


def parse_seasons(raw: str) -> list[int]:
    seasons: list[int] = []
    for part in raw.split(","):
        s = part.strip()
        if not s:
            continue
        seasons.append(int(s))
    if not seasons:
        raise ValueError("No seasons were provided")
    return sorted(set(seasons))


def pct(n: int, d: int) -> float:
    return round((n / d) * 100.0, 2) if d > 0 else 0.0


def load_rows(schema: str, seasons: Iterable[int]) -> list[SpreadRow]:
    season_list = list(seasons)
    if not season_list:
        return []

    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        f"""
        SELECT
            mp.game_id,
            mp.season,
            mp.week,
            (g.home_score - g.away_score) AS actual_margin,
            mp.ai_spread,
            mp.vegas_spread
        FROM {schema}.ml_predictions mp
        JOIN {schema}.games g ON g.game_id = mp.game_id
        WHERE mp.season = ANY(%s)
          AND COALESCE(g.is_postseason, FALSE) = FALSE
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          AND mp.ai_spread IS NOT NULL
          AND mp.vegas_spread IS NOT NULL
        ORDER BY mp.season, mp.week, mp.game_id
        """,
        (season_list,),
    )
    raw_rows = cur.fetchall() or []
    cur.close()
    conn.close()

    rows: list[SpreadRow] = []
    for row in raw_rows:
        rows.append(
            SpreadRow(
                game_id=str(row["game_id"]),
                season=int(row["season"]),
                week=int(row["week"]),
                actual_margin=float(row["actual_margin"]),
                ai_spread=float(row["ai_spread"]),
                vegas_spread=float(row["vegas_spread"]),
            )
        )
    return rows


def evaluate(rows: list[SpreadRow], method: str, tuned_spread_fn: Callable[[SpreadRow], float]) -> MethodResult:
    abs_errors: list[float] = []
    sq_errors: list[float] = []
    wins_vs_vegas = 0
    vegas_wins = 0
    ties = 0

    for row in rows:
        target = row.target_spread
        tuned = tuned_spread_fn(row)
        tuned_err = abs(tuned - target)
        vegas_err = abs(row.vegas_spread - target)

        abs_errors.append(tuned_err)
        sq_errors.append((tuned - target) ** 2)

        if tuned_err < vegas_err:
            wins_vs_vegas += 1
        elif vegas_err < tuned_err:
            vegas_wins += 1
        else:
            ties += 1

    games = len(rows)
    mae = round(sum(abs_errors) / games, 4) if games else 0.0
    rmse = round(math.sqrt(sum(sq_errors) / games), 4) if games else 0.0
    win_pct = pct(wins_vs_vegas, games)
    vegas_win_pct = pct(vegas_wins, games)

    return MethodResult(
        method=method,
        games=games,
        mae=mae,
        rmse=rmse,
        wins_vs_vegas=wins_vs_vegas,
        vegas_wins=vegas_wins,
        ties_vs_vegas=ties,
        win_pct=win_pct,
        vegas_win_pct=vegas_win_pct,
        delta_pct=round(win_pct - vegas_win_pct, 2),
    )


def fit_bias(rows: list[SpreadRow]) -> float:
    if not rows:
        return 0.0
    residuals = [row.target_spread - row.ai_spread for row in rows]
    return sum(residuals) / len(residuals)


def fit_linear(rows: list[SpreadRow]) -> tuple[float, float]:
    # y ~= a + b*x where y=target_spread, x=ai_spread
    if not rows:
        return 0.0, 1.0

    xs = [r.ai_spread for r in rows]
    ys = [r.target_spread for r in rows]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)

    var_x = sum((x - x_mean) ** 2 for x in xs)
    if var_x == 0:
        return y_mean - x_mean, 1.0

    cov_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=True))
    b = cov_xy / var_x
    a = y_mean - b * x_mean
    return a, b


def bias_scan(rows: list[SpreadRow], bias_min: float, bias_max: float, step: float) -> tuple[float, list[dict]]:
    if step <= 0:
        raise ValueError("step must be > 0")

    scan_rows: list[dict] = []
    best_bias = 0.0
    best_delta = float("-inf")
    best_mae = float("inf")

    points = int(round((bias_max - bias_min) / step)) + 1
    for i in range(points):
        bias = round(bias_min + i * step, 4)
        result = evaluate(rows, "bias_scan", lambda r, b=bias: r.ai_spread + b)
        scan_row = {
            "bias": bias,
            "mae": result.mae,
            "rmse": result.rmse,
            "win_pct": result.win_pct,
            "vegas_win_pct": result.vegas_win_pct,
            "delta_pct": result.delta_pct,
            "wins_vs_vegas": result.wins_vs_vegas,
            "vegas_wins": result.vegas_wins,
            "ties": result.ties_vs_vegas,
        }
        scan_rows.append(scan_row)

        if (result.delta_pct > best_delta) or (result.delta_pct == best_delta and result.mae < best_mae):
            best_bias = bias
            best_delta = result.delta_pct
            best_mae = result.mae

    return best_bias, scan_rows


def to_dict(result: MethodResult) -> dict:
    return {
        "method": result.method,
        "games": result.games,
        "mae": result.mae,
        "rmse": result.rmse,
        "wins_vs_vegas": result.wins_vs_vegas,
        "vegas_wins": result.vegas_wins,
        "ties_vs_vegas": result.ties_vs_vegas,
        "win_pct": result.win_pct,
        "vegas_win_pct": result.vegas_win_pct,
        "delta_pct": result.delta_pct,
    }


def write_bias_scan_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["bias", "mae", "rmse", "win_pct", "vegas_win_pct", "delta_pct", "wins_vs_vegas", "vegas_wins", "ties"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_table_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def evaluate_grouped(
    rows: list[SpreadRow],
    method: str,
    tuned_spread_fn: Callable[[SpreadRow], float],
    group_fn: Callable[[SpreadRow], tuple[str, tuple]],
) -> list[dict]:
    grouped: dict[str, dict] = {}

    for row in rows:
        label, sort_key = group_fn(row)
        bucket = grouped.setdefault(
            label,
            {
                "method": method,
                "group": label,
                "_sort_key": sort_key,
                "games": 0,
                "sum_abs_error": 0.0,
                "sum_sq_error": 0.0,
                "wins_vs_vegas": 0,
                "vegas_wins": 0,
                "ties_vs_vegas": 0,
            },
        )

        target = row.target_spread
        tuned = tuned_spread_fn(row)
        tuned_err = abs(tuned - target)
        vegas_err = abs(row.vegas_spread - target)

        bucket["games"] += 1
        bucket["sum_abs_error"] += tuned_err
        bucket["sum_sq_error"] += (tuned - target) ** 2

        if tuned_err < vegas_err:
            bucket["wins_vs_vegas"] += 1
        elif vegas_err < tuned_err:
            bucket["vegas_wins"] += 1
        else:
            bucket["ties_vs_vegas"] += 1

    rows_out: list[dict] = []
    for bucket in grouped.values():
        games = int(bucket["games"])
        wins = int(bucket["wins_vs_vegas"])
        vegas_wins = int(bucket["vegas_wins"])

        row = {
            "method": bucket["method"],
            "group": bucket["group"],
            "games": games,
            "mae": round(float(bucket["sum_abs_error"]) / games, 4) if games else 0.0,
            "rmse": round(math.sqrt(float(bucket["sum_sq_error"]) / games), 4) if games else 0.0,
            "wins_vs_vegas": wins,
            "vegas_wins": vegas_wins,
            "ties_vs_vegas": int(bucket["ties_vs_vegas"]),
            "win_pct": pct(wins, games),
            "vegas_win_pct": pct(vegas_wins, games),
            "delta_pct": round(pct(wins, games) - pct(vegas_wins, games), 2),
            "_sort_key": bucket["_sort_key"],
        }
        rows_out.append(row)

    rows_out.sort(key=lambda r: (r.get("_sort_key") or ()))
    for row in rows_out:
        row.pop("_sort_key", None)

    return rows_out


def group_by_week(row: SpreadRow) -> tuple[str, tuple]:
    return week_label(row.season, row.week), (row.season, row.week)


def group_by_vegas_bin(row: SpreadRow) -> tuple[str, tuple]:
    abs_line = abs(row.vegas_spread)
    if abs_line < 3:
        return "abs_vegas_lt3", (0,)
    if abs_line < 7:
        return "abs_vegas_3_to_7", (1,)
    if abs_line < 10:
        return "abs_vegas_7_to_10", (2,)
    return "abs_vegas_ge10", (3,)


def _vs_vegas_outcome(tuned_err: float, vegas_err: float) -> str:
    if tuned_err < vegas_err:
        return "ai_better"
    if vegas_err < tuned_err:
        return "vegas_better"
    return "tie"


def _normalize_focus_week_label(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""

    if "-W" not in value:
        return value

    season_part, week_part = value.split("-W", 1)
    try:
        return week_label(int(season_part), int(week_part))
    except ValueError:
        return value


def _summarize_game_delta_slice(rows: list[dict]) -> dict:
    games = len(rows)
    improved = sum(1 for row in rows if float(row.get("err_improvement") or 0.0) > 0.0001)
    regressed = sum(1 for row in rows if float(row.get("err_improvement") or 0.0) < -0.0001)
    flat = games - improved - regressed
    avg_improvement = (
        round(sum(float(row.get("err_improvement") or 0.0) for row in rows) / games, 4)
        if games
        else 0.0
    )

    ai_better = sum(1 for row in rows if row.get("recommended_vs_vegas") == "ai_better")
    vegas_better = sum(1 for row in rows if row.get("recommended_vs_vegas") == "vegas_better")
    ties = games - ai_better - vegas_better

    return {
        "games": games,
        "improved_games": improved,
        "regressed_games": regressed,
        "flat_games": flat,
        "avg_err_improvement": avg_improvement,
        "recommended_vs_vegas": {
            "ai_better": ai_better,
            "vegas_better": vegas_better,
            "ties": ties,
        },
    }


def _compact_delta_rows(rows: list[dict], limit: int = 5) -> list[dict]:
    compact: list[dict] = []
    for row in rows[:limit]:
        compact.append(
            {
                "game_id": row.get("game_id"),
                "season": row.get("season"),
                "week": row.get("week"),
                "vegas_spread": row.get("vegas_spread"),
                "err_improvement": row.get("err_improvement"),
                "recommended_vs_vegas": row.get("recommended_vs_vegas"),
            }
        )
    return compact


def build_targeted_diagnostics(
    game_delta_rows: list[dict],
    breakdown_by_week: list[dict],
    breakdown_by_vegas_bin: list[dict],
    recommended_method: str,
    focus_week_label: str,
    high_spread_threshold: float,
) -> tuple[dict, list[dict], list[dict]]:
    week_rows = [
        row for row in breakdown_by_week if row.get("method") == recommended_method
    ]
    worst_week_row = (
        min(week_rows, key=lambda r: (r.get("delta_pct", 0.0), -r.get("mae", 0.0)))
        if week_rows
        else None
    )
    worst_week_label = str((worst_week_row or {}).get("group") or "")

    enriched_rows: list[dict] = []
    available_weeks: set[str] = set()
    for row in game_delta_rows:
        season = int(row.get("season") or 0)
        week = int(row.get("week") or 0)
        vegas_spread = float(row.get("vegas_spread") or 0.0)

        enriched = dict(row)
        enriched["week_label"] = week_label(season, week)
        enriched["abs_vegas_spread"] = round(abs(vegas_spread), 4)
        enriched_rows.append(enriched)
        available_weeks.add(enriched["week_label"])

    requested_focus_week = _normalize_focus_week_label(focus_week_label)
    focus_week_used = ""
    focus_reason = "none"
    if requested_focus_week and requested_focus_week in available_weeks:
        focus_week_used = requested_focus_week
        focus_reason = "requested"
    elif requested_focus_week and worst_week_label:
        focus_week_used = worst_week_label
        focus_reason = "requested_unavailable_fallback_worst"
    elif not requested_focus_week and worst_week_label:
        focus_week_used = worst_week_label
        focus_reason = "auto_worst_validation_week"

    focus_rows = [
        row for row in enriched_rows if focus_week_used and row.get("week_label") == focus_week_used
    ]
    focus_rows.sort(key=lambda r: float(r.get("err_improvement") or 0.0))

    high_spread_rows = [
        row for row in enriched_rows if float(row.get("abs_vegas_spread") or 0.0) >= high_spread_threshold
    ]
    high_spread_rows.sort(
        key=lambda r: (-float(r.get("abs_vegas_spread") or 0.0), float(r.get("err_improvement") or 0.0))
    )

    high_spread_bin_row = next(
        (
            row for row in breakdown_by_vegas_bin
            if row.get("method") == recommended_method and row.get("group") == "abs_vegas_ge10"
        ),
        None,
    )

    focus_regressions = sorted(focus_rows, key=lambda r: float(r.get("err_improvement") or 0.0))
    focus_improvements = sorted(
        focus_rows,
        key=lambda r: float(r.get("err_improvement") or 0.0),
        reverse=True,
    )
    high_regressions = sorted(high_spread_rows, key=lambda r: float(r.get("err_improvement") or 0.0))
    high_improvements = sorted(
        high_spread_rows,
        key=lambda r: float(r.get("err_improvement") or 0.0),
        reverse=True,
    )

    diagnostics = {
        "focus_week_requested": requested_focus_week or None,
        "focus_week_used": focus_week_used or None,
        "focus_week_selection_reason": focus_reason,
        "worst_validation_week": worst_week_row,
        "focus_week_summary": _summarize_game_delta_slice(focus_rows),
        "high_spread_threshold": high_spread_threshold,
        "high_spread_summary": _summarize_game_delta_slice(high_spread_rows),
        "high_spread_bin_snapshot": high_spread_bin_row,
        "top_focus_week_regressions": _compact_delta_rows(focus_regressions),
        "top_focus_week_improvements": _compact_delta_rows(focus_improvements),
        "top_high_spread_regressions": _compact_delta_rows(high_regressions),
        "top_high_spread_improvements": _compact_delta_rows(high_improvements),
    }

    return diagnostics, focus_rows, high_spread_rows


def build_validation_game_delta_rows(
    rows: list[SpreadRow],
    recommended_method: str,
    baseline_fn: Callable[[SpreadRow], float],
    recommended_fn: Callable[[SpreadRow], float],
) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        target = row.target_spread
        baseline_spread = baseline_fn(row)
        recommended_spread = recommended_fn(row)
        vegas_spread = row.vegas_spread

        baseline_err = abs(baseline_spread - target)
        recommended_err = abs(recommended_spread - target)
        vegas_err = abs(vegas_spread - target)

        out.append(
            {
                "season": row.season,
                "week": row.week,
                "game_id": row.game_id,
                "target_spread": round(target, 4),
                "vegas_spread": round(vegas_spread, 4),
                "baseline_spread": round(baseline_spread, 4),
                "recommended_method": recommended_method,
                "recommended_spread": round(recommended_spread, 4),
                "vegas_err": round(vegas_err, 4),
                "baseline_err": round(baseline_err, 4),
                "recommended_err": round(recommended_err, 4),
                "err_improvement": round(baseline_err - recommended_err, 4),
                "baseline_vs_vegas": _vs_vegas_outcome(baseline_err, vegas_err),
                "recommended_vs_vegas": _vs_vegas_outcome(recommended_err, vegas_err),
            }
        )

    out.sort(key=lambda r: (int(r.get("season") or 0), int(r.get("week") or 0), str(r.get("game_id") or "")))
    return out


def write_markdown(path: Path, summary: dict) -> None:
    train = summary["train"]
    val = summary["validation"]
    rec = summary["recommended"]

    lines = [
        "# TA-078 Vegas Gap Tuning Report",
        "",
        f"Generated (UTC): {summary['generated_at_utc']}",
        f"Schema: {summary['schema']}",
        f"Train seasons: {', '.join(map(str, summary['train_seasons']))}",
        f"Validation seasons: {', '.join(map(str, summary['validation_seasons']))}",
        "",
        "## Baseline vs Tuned (Validation)",
        f"- Baseline delta_pct: {val['baseline']['delta_pct']} (AI win% {val['baseline']['win_pct']}, Vegas win% {val['baseline']['vegas_win_pct']})",
        f"- Bias correction delta_pct: {val['bias']['delta_pct']} (bias={summary['parameters']['bias']})",
        f"- Linear correction delta_pct: {val['linear']['delta_pct']} (a={summary['parameters']['linear_a']}, b={summary['parameters']['linear_b']})",
        f"- Delta-optimized bias delta_pct: {val['bias_scan']['delta_pct']} (bias={summary['parameters']['bias_scan_best']})",
        "",
        "## Recommendation",
        f"- Recommended method: {rec['method']}",
        f"- Recommended runtime env: AI_SPREAD_CAL_BIAS={rec['runtime']['AI_SPREAD_CAL_BIAS']}, AI_SPREAD_CAL_SCALE={rec['runtime']['AI_SPREAD_CAL_SCALE']}",
        "",
        "## Train Snapshot",
        f"- Baseline delta_pct: {train['baseline']['delta_pct']}",
        f"- Best bias-scan delta_pct: {train['bias_scan']['delta_pct']}",
    ]

    breakdowns = summary.get("validation_breakdowns") or {}
    recommended_method = rec.get("method")

    week_rows = [
        row for row in (breakdowns.get("by_week") or []) if row.get("method") == recommended_method
    ]
    if week_rows:
        best_week = max(week_rows, key=lambda r: (r.get("delta_pct", 0.0), -r.get("mae", 0.0)))
        worst_week = min(week_rows, key=lambda r: (r.get("delta_pct", 0.0), -r.get("mae", 0.0)))
        lines.extend(
            [
                "",
                "## Validation Weekly Breakdown",
                f"- Best week ({recommended_method}): {best_week['group']} delta {best_week['delta_pct']} on {best_week['games']} games",
                f"- Worst week ({recommended_method}): {worst_week['group']} delta {worst_week['delta_pct']} on {worst_week['games']} games",
            ]
        )

    bin_rows = [
        row for row in (breakdowns.get("by_vegas_bin") or []) if row.get("method") == recommended_method
    ]
    if bin_rows:
        lines.extend(["", "## Validation Vegas-Spread Bin Breakdown"])
        for row in bin_rows:
            lines.append(
                f"- {row['group']}: delta {row['delta_pct']} (games {row['games']}, MAE {row['mae']})"
            )

    game_delta = summary.get("validation_game_deltas") or {}
    if game_delta:
        lines.extend(
            [
                "",
                "## Validation Game-Level Delta",
                f"- Improved vs baseline: {game_delta.get('improved_games')} games",
                f"- Regressed vs baseline: {game_delta.get('regressed_games')} games",
                f"- Flat vs baseline: {game_delta.get('flat_games')} games",
            ]
        )

        best_game = game_delta.get("largest_improvement") or {}
        worst_game = game_delta.get("largest_regression") or {}
        if best_game:
            lines.append(
                f"- Largest improvement: {best_game.get('game_id')} ({best_game.get('season')}-W{int(best_game.get('week', 0)):02d}) err_improvement {best_game.get('err_improvement')}"
            )
        if worst_game:
            lines.append(
                f"- Largest regression: {worst_game.get('game_id')} ({worst_game.get('season')}-W{int(worst_game.get('week', 0)):02d}) err_improvement {worst_game.get('err_improvement')}"
            )

    targeted = summary.get("targeted_diagnostics") or {}
    if targeted:
        focus = targeted.get("focus_week_summary") or {}
        high = targeted.get("high_spread_summary") or {}
        lines.extend(
            [
                "",
                "## Targeted Diagnostics",
                f"- Focus week requested: {targeted.get('focus_week_requested') or 'auto'}",
                f"- Focus week used: {targeted.get('focus_week_used') or 'none'} ({targeted.get('focus_week_selection_reason')})",
                f"- Focus week improved/regressed/flat: {focus.get('improved_games')} / {focus.get('regressed_games')} / {focus.get('flat_games')}",
                f"- Focus week avg err improvement: {focus.get('avg_err_improvement')}",
                f"- High-spread threshold (abs): {targeted.get('high_spread_threshold')}",
                f"- High-spread improved/regressed/flat: {high.get('improved_games')} / {high.get('regressed_games')} / {high.get('flat_games')}",
                f"- High-spread avg err improvement: {high.get('avg_err_improvement')}",
            ]
        )

        high_bin = targeted.get("high_spread_bin_snapshot") or {}
        if high_bin:
            lines.append(
                f"- High-spread bin snapshot ({high_bin.get('group')}): delta {high_bin.get('delta_pct')} on {high_bin.get('games')} games"
            )

        artifacts = targeted.get("artifacts") or {}
        if artifacts.get("focus_week_csv"):
            lines.append(f"- Focus week artifact: {artifacts.get('focus_week_csv')}")
        if artifacts.get("high_spread_csv"):
            lines.append(f"- High-spread artifact: {artifacts.get('high_spread_csv')}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="TA-078 AI-vs-Vegas spread tuning analysis")
    parser.add_argument("--schema", default="hcl")
    parser.add_argument("--seasons", default="2021,2022,2023,2024,2025")
    parser.add_argument("--validation-seasons", default="")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--bias-min", type=float, default=-8.0)
    parser.add_argument("--bias-max", type=float, default=8.0)
    parser.add_argument("--bias-step", type=float, default=0.1)
    parser.add_argument(
        "--focus-week",
        default="2025-W10",
        help="Validation week label for targeted diagnostics (example: 2025-W10). Empty selects worst validation week.",
    )
    parser.add_argument(
        "--high-spread-threshold",
        type=float,
        default=10.0,
        help="Absolute Vegas spread threshold for high-spread diagnostics.",
    )
    args = parser.parse_args()

    if args.high_spread_threshold <= 0:
        raise ValueError("--high-spread-threshold must be > 0")

    seasons = parse_seasons(args.seasons)
    if args.validation_seasons.strip():
        validation_seasons = parse_seasons(args.validation_seasons)
    else:
        validation_seasons = [max(seasons)]

    train_seasons = [s for s in seasons if s not in set(validation_seasons)]
    if not train_seasons:
        raise ValueError("Training seasons cannot be empty. Provide at least one non-validation season.")

    all_rows = load_rows(args.schema, seasons)
    train_rows = [r for r in all_rows if r.season in set(train_seasons)]
    val_rows = [r for r in all_rows if r.season in set(validation_seasons)]

    if not train_rows or not val_rows:
        raise ValueError("Insufficient rows for train or validation split")

    # Fit parameters from train split.
    bias = round(fit_bias(train_rows), 4)
    linear_a, linear_b = fit_linear(train_rows)
    linear_a = round(linear_a, 4)
    linear_b = round(linear_b, 4)

    best_bias_scan, scan_rows = bias_scan(train_rows, args.bias_min, args.bias_max, args.bias_step)

    method_specs: dict[str, Callable[[SpreadRow], float]] = {
        "baseline": lambda r: r.ai_spread,
        "bias": lambda r, b=bias: r.ai_spread + b,
        "linear": lambda r, a=linear_a, b=linear_b: a + b * r.ai_spread,
        "bias_scan": lambda r, b=best_bias_scan: r.ai_spread + b,
    }

    # Evaluate methods.
    methods_train = {
        name: to_dict(evaluate(train_rows, name, fn)) for name, fn in method_specs.items()
    }

    methods_val = {
        name: to_dict(evaluate(val_rows, name, fn)) for name, fn in method_specs.items()
    }

    # Pick best validation method by delta_pct, then MAE.
    candidates = [methods_val["bias"], methods_val["linear"], methods_val["bias_scan"]]
    candidates.sort(key=lambda m: (m["delta_pct"], -m["mae"]), reverse=True)
    best = candidates[0]

    runtime_map = {
        "bias": {"AI_SPREAD_CAL_BIAS": bias, "AI_SPREAD_CAL_SCALE": 1.0},
        "linear": {"AI_SPREAD_CAL_BIAS": linear_a, "AI_SPREAD_CAL_SCALE": linear_b},
        "bias_scan": {"AI_SPREAD_CAL_BIAS": best_bias_scan, "AI_SPREAD_CAL_SCALE": 1.0},
    }

    breakdown_methods: list[str] = ["baseline", best["method"]]
    if best["method"] == "baseline":
        breakdown_methods = ["baseline"]

    breakdown_by_week: list[dict] = []
    breakdown_by_vegas_bin: list[dict] = []
    for method_name in breakdown_methods:
        fn = method_specs[method_name]
        breakdown_by_week.extend(evaluate_grouped(val_rows, method_name, fn, group_by_week))
        breakdown_by_vegas_bin.extend(evaluate_grouped(val_rows, method_name, fn, group_by_vegas_bin))

    recommended_method = best["method"]
    baseline_fn = method_specs["baseline"]
    recommended_fn = method_specs[recommended_method]
    game_delta_rows = build_validation_game_delta_rows(
        val_rows,
        recommended_method=recommended_method,
        baseline_fn=baseline_fn,
        recommended_fn=recommended_fn,
    )

    targeted_diagnostics, focus_week_rows, high_spread_rows = build_targeted_diagnostics(
        game_delta_rows=game_delta_rows,
        breakdown_by_week=breakdown_by_week,
        breakdown_by_vegas_bin=breakdown_by_vegas_bin,
        recommended_method=recommended_method,
        focus_week_label=args.focus_week,
        high_spread_threshold=args.high_spread_threshold,
    )

    improved_games = sum(1 for r in game_delta_rows if float(r["err_improvement"]) > 0.0001)
    regressed_games = sum(1 for r in game_delta_rows if float(r["err_improvement"]) < -0.0001)
    flat_games = len(game_delta_rows) - improved_games - regressed_games
    best_game = max(game_delta_rows, key=lambda r: float(r.get("err_improvement") or 0.0)) if game_delta_rows else None
    worst_game = min(game_delta_rows, key=lambda r: float(r.get("err_improvement") or 0.0)) if game_delta_rows else None

    generated_at = datetime.now(UTC)
    slug = generated_at.strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "generated_at_utc": generated_at.isoformat(),
        "schema": args.schema,
        "seasons": seasons,
        "train_seasons": train_seasons,
        "validation_seasons": validation_seasons,
        "row_counts": {
            "all": len(all_rows),
            "train": len(train_rows),
            "validation": len(val_rows),
        },
        "parameters": {
            "bias": bias,
            "linear_a": linear_a,
            "linear_b": linear_b,
            "bias_scan_best": best_bias_scan,
            "bias_scan_range": {"min": args.bias_min, "max": args.bias_max, "step": args.bias_step},
        },
        "train": methods_train,
        "validation": methods_val,
        "validation_breakdowns": {
            "methods_included": breakdown_methods,
            "by_week": breakdown_by_week,
            "by_vegas_bin": breakdown_by_vegas_bin,
        },
        "validation_game_deltas": {
            "recommended_method": recommended_method,
            "games": len(game_delta_rows),
            "improved_games": improved_games,
            "regressed_games": regressed_games,
            "flat_games": flat_games,
            "largest_improvement": best_game,
            "largest_regression": worst_game,
        },
        "targeted_diagnostics": targeted_diagnostics,
        "recommended": {
            "method": best["method"],
            "runtime": runtime_map[best["method"]],
        },
    }

    summary_path = out_dir / f"ta078_vegas_tuning_{slug}_summary.json"
    report_path = out_dir / f"ta078_vegas_tuning_{slug}_report.md"
    scan_path = out_dir / f"ta078_vegas_tuning_{slug}_bias_scan.csv"
    by_week_path = out_dir / f"ta078_vegas_tuning_{slug}_validation_by_week.csv"
    by_bin_path = out_dir / f"ta078_vegas_tuning_{slug}_validation_by_vegas_bin.csv"
    game_delta_path = out_dir / f"ta078_vegas_tuning_{slug}_validation_game_deltas.csv"
    focus_week_path = out_dir / f"ta078_vegas_tuning_{slug}_targeted_focus_week.csv"
    high_spread_path = out_dir / f"ta078_vegas_tuning_{slug}_targeted_high_spread.csv"

    targeted_diagnostics["artifacts"] = {
        "focus_week_csv": str(focus_week_path),
        "high_spread_csv": str(high_spread_path),
    }

    breakdown_fields = [
        "method",
        "group",
        "games",
        "mae",
        "rmse",
        "wins_vs_vegas",
        "vegas_wins",
        "ties_vs_vegas",
        "win_pct",
        "vegas_win_pct",
        "delta_pct",
    ]

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(report_path, summary)
    write_bias_scan_csv(scan_path, scan_rows)
    write_table_csv(by_week_path, breakdown_by_week, breakdown_fields)
    write_table_csv(by_bin_path, breakdown_by_vegas_bin, breakdown_fields)
    write_table_csv(
        game_delta_path,
        game_delta_rows,
        [
            "season",
            "week",
            "game_id",
            "target_spread",
            "vegas_spread",
            "baseline_spread",
            "recommended_method",
            "recommended_spread",
            "vegas_err",
            "baseline_err",
            "recommended_err",
            "err_improvement",
            "baseline_vs_vegas",
            "recommended_vs_vegas",
        ],
    )
    write_table_csv(
        focus_week_path,
        focus_week_rows,
        [
            "season",
            "week",
            "week_label",
            "game_id",
            "target_spread",
            "vegas_spread",
            "abs_vegas_spread",
            "baseline_spread",
            "recommended_method",
            "recommended_spread",
            "vegas_err",
            "baseline_err",
            "recommended_err",
            "err_improvement",
            "baseline_vs_vegas",
            "recommended_vs_vegas",
        ],
    )
    write_table_csv(
        high_spread_path,
        high_spread_rows,
        [
            "season",
            "week",
            "week_label",
            "game_id",
            "target_spread",
            "vegas_spread",
            "abs_vegas_spread",
            "baseline_spread",
            "recommended_method",
            "recommended_spread",
            "vegas_err",
            "baseline_err",
            "recommended_err",
            "err_improvement",
            "baseline_vs_vegas",
            "recommended_vs_vegas",
        ],
    )

    print("TA-078 tuning analysis complete")
    print(f"summary={summary_path}")
    print(f"report={report_path}")
    print(f"bias_scan={scan_path}")
    print(f"validation_by_week={by_week_path}")
    print(f"validation_by_vegas_bin={by_bin_path}")
    print(f"validation_game_deltas={game_delta_path}")
    print(f"targeted_focus_week={focus_week_path}")
    print(f"targeted_high_spread={high_spread_path}")
    print(f"targeted_focus_week_label={targeted_diagnostics.get('focus_week_used')}")
    print(f"targeted_high_spread_threshold={args.high_spread_threshold}")
    print(f"recommended_method={summary['recommended']['method']}")
    print(
        "recommended_runtime="
        f"AI_SPREAD_CAL_BIAS={summary['recommended']['runtime']['AI_SPREAD_CAL_BIAS']},"
        f"AI_SPREAD_CAL_SCALE={summary['recommended']['runtime']['AI_SPREAD_CAL_SCALE']}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
