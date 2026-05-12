#!/usr/bin/env python3
"""TA-023 leakage audit for feature pipeline and split boundaries."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import UTC, datetime
from typing import Any

import psycopg2


ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db_config import DATABASE_CONFIG  # noqa: E402


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def check_source_guards() -> dict[str, Any]:
    winner_path = ROOT_DIR / "ml" / "train_xgb_winner.py"
    spread_path = ROOT_DIR / "ml" / "train_xgb_spread.py"
    predict_path = ROOT_DIR / "ml" / "predict_week.py"

    winner_src = read_text(winner_path)
    spread_src = read_text(spread_path)
    predict_src = read_text(predict_path)

    checks = {
        "winner_prior_window_clause": "ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING" in winner_src,
        "spread_prior_window_clause": "ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING" in spread_src,
        "winner_week1_excluded": "g.week >= 2" in winner_src,
        "spread_week1_excluded": "g.week >= 2" in spread_src,
        "predictor_uses_prior_weeks_only": "g.week < %s" in predict_src,
        "predictor_excludes_postseason": "g.is_postseason = FALSE" in predict_src,
    }

    return {
        "files": {
            "winner": winner_path.relative_to(ROOT_DIR).as_posix(),
            "spread": spread_path.relative_to(ROOT_DIR).as_posix(),
            "predictor": predict_path.relative_to(ROOT_DIR).as_posix(),
        },
        "checks": checks,
        "all_checks_passed": all(checks.values()),
    }


def validate_split_boundaries() -> dict[str, Any]:
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS rows_total,
                    MIN(season) AS season_min,
                    MAX(season) AS season_max,
                    MIN(week) AS week_min,
                    COUNT(*) FILTER (WHERE season <= 2023) AS train_rows,
                    COUNT(*) FILTER (WHERE season = 2024) AS val_rows,
                    COUNT(*) FILTER (WHERE season = 2025) AS test_rows,
                    COUNT(*) FILTER (WHERE season NOT IN (2020, 2021, 2022, 2023, 2024, 2025)) AS out_of_scope_season_rows
                FROM hcl.games
                WHERE season >= 2020
                  AND home_score IS NOT NULL
                  AND away_score IS NOT NULL
                  AND week >= 2
                """
            )
            winner_total, winner_min_season, winner_max_season, winner_min_week, winner_train, winner_val, winner_test, winner_oos = cur.fetchone()

            cur.execute(
                """
                SELECT
                    COUNT(*) AS rows_total,
                    MIN(season) AS season_min,
                    MAX(season) AS season_max,
                    MIN(week) AS week_min,
                    COUNT(*) FILTER (WHERE season <= 2023) AS train_rows,
                    COUNT(*) FILTER (WHERE season = 2024) AS val_rows,
                    COUNT(*) FILTER (WHERE season = 2025) AS test_rows,
                    COUNT(*) FILTER (WHERE season NOT IN (2020, 2021, 2022, 2023, 2024, 2025)) AS out_of_scope_season_rows
                FROM hcl.games
                WHERE season >= 2020
                  AND is_postseason = FALSE
                  AND home_score IS NOT NULL
                  AND away_score IS NOT NULL
                  AND week >= 2
                """
            )
            spread_total, spread_min_season, spread_max_season, spread_min_week, spread_train, spread_val, spread_test, spread_oos = cur.fetchone()

    finally:
        conn.close()

    def split_report(
        pipeline: str,
        rows_total: int,
        season_min: int | None,
        season_max: int | None,
        week_min: int | None,
        train_rows: int,
        val_rows: int,
        test_rows: int,
        out_of_scope_season_rows: int,
    ) -> dict[str, Any]:
        checks = {
            "rows_nonempty": rows_total > 0,
            "train_nonempty": train_rows > 0,
            "val_nonempty": val_rows > 0,
            "test_nonempty": test_rows > 0,
            "season_min_gte_2020": (season_min or 0) >= 2020,
            "season_max_lte_2025": (season_max or 0) <= 2025,
            "week_min_gte_2": (week_min or 0) >= 2,
            "no_out_of_scope_season_rows": out_of_scope_season_rows == 0,
        }

        return {
            "pipeline": pipeline,
            "rows": int(rows_total),
            "season_min": int(season_min) if season_min is not None else None,
            "season_max": int(season_max) if season_max is not None else None,
            "week_min": int(week_min) if week_min is not None else None,
            "train_rows": int(train_rows),
            "val_rows": int(val_rows),
            "test_rows": int(test_rows),
            "out_of_scope_season_rows": int(out_of_scope_season_rows),
            "checks": checks,
            "all_checks_passed": all(checks.values()),
        }

    winner_report = split_report(
        pipeline="winner",
        rows_total=int(winner_total or 0),
        season_min=int(winner_min_season) if winner_min_season is not None else None,
        season_max=int(winner_max_season) if winner_max_season is not None else None,
        week_min=int(winner_min_week) if winner_min_week is not None else None,
        train_rows=int(winner_train or 0),
        val_rows=int(winner_val or 0),
        test_rows=int(winner_test or 0),
        out_of_scope_season_rows=int(winner_oos or 0),
    )
    spread_report = split_report(
        pipeline="spread",
        rows_total=int(spread_total or 0),
        season_min=int(spread_min_season) if spread_min_season is not None else None,
        season_max=int(spread_max_season) if spread_max_season is not None else None,
        week_min=int(spread_min_week) if spread_min_week is not None else None,
        train_rows=int(spread_train or 0),
        val_rows=int(spread_val or 0),
        test_rows=int(spread_test or 0),
        out_of_scope_season_rows=int(spread_oos or 0),
    )

    return {
        "winner": winner_report,
        "spread": spread_report,
        "all_checks_passed": winner_report["all_checks_passed"] and spread_report["all_checks_passed"],
    }


def run_same_game_leakage_sql(limit_rows: int = 10) -> dict[str, Any]:
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        with conn.cursor() as cur:
            # Validate that training home/away PPG features equal strictly prior-week averages.
            cur.execute(
                """
                WITH game_stats AS (
                    SELECT
                        tgs.game_id,
                        tgs.team,
                        g.season,
                        g.week,
                        tgs.points
                    FROM hcl.team_game_stats tgs
                    JOIN hcl.games g ON g.game_id = tgs.game_id
                    WHERE g.season >= 2020
                      AND g.home_score IS NOT NULL
                      AND g.away_score IS NOT NULL
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
                        ) AS avg_ppg
                    FROM game_stats
                ),
                winner_rows AS (
                    SELECT
                        g.game_id,
                        g.season,
                        g.week,
                        g.home_team,
                        g.away_team,
                        COALESCE(h.avg_ppg, 20)::double precision AS home_ppg,
                        COALESCE(a.avg_ppg, 20)::double precision AS away_ppg
                    FROM hcl.games g
                    LEFT JOIN cumulative_stats h ON g.game_id = h.game_id AND g.home_team = h.team
                    LEFT JOIN cumulative_stats a ON g.game_id = a.game_id AND g.away_team = a.team
                    WHERE g.season >= 2020
                      AND g.home_score IS NOT NULL
                      AND g.away_score IS NOT NULL
                      AND g.week >= 2
                )
                SELECT
                    COUNT(*) AS total_rows,
                    COUNT(*) FILTER (
                        WHERE (
                            (eh.expected_home IS NULL AND ABS(w.home_ppg - 20.0) < 1e-6) OR
                            (eh.expected_home IS NOT NULL AND ABS(w.home_ppg - eh.expected_home) < 1e-6)
                        ) AND (
                            (ea.expected_away IS NULL AND ABS(w.away_ppg - 20.0) < 1e-6) OR
                            (ea.expected_away IS NOT NULL AND ABS(w.away_ppg - ea.expected_away) < 1e-6)
                        )
                    ) AS strict_prior_match_rows
                FROM winner_rows w
                LEFT JOIN LATERAL (
                    SELECT AVG(tgs.points)::double precision AS expected_home
                    FROM hcl.team_game_stats tgs
                    JOIN hcl.games g2 ON g2.game_id = tgs.game_id
                    WHERE g2.season = w.season
                      AND tgs.team = w.home_team
                      AND g2.week < w.week
                      AND g2.home_score IS NOT NULL
                      AND g2.away_score IS NOT NULL
                ) eh ON TRUE
                LEFT JOIN LATERAL (
                    SELECT AVG(tgs.points)::double precision AS expected_away
                    FROM hcl.team_game_stats tgs
                    JOIN hcl.games g2 ON g2.game_id = tgs.game_id
                    WHERE g2.season = w.season
                      AND tgs.team = w.away_team
                      AND g2.week < w.week
                      AND g2.home_score IS NOT NULL
                      AND g2.away_score IS NOT NULL
                ) ea ON TRUE
                """
            )
            total_rows, strict_match_rows = cur.fetchone()

            cur.execute("SELECT to_regclass('hcl.ml_predictions')")
            prediction_timing_table = cur.fetchone()[0]

            timing_total = timing_null = timing_after = timing_on_or_before = None
            if prediction_timing_table is not None:
                cur.execute(
                    """
                    SELECT
                        COUNT(*) AS rows_total,
                        COUNT(*) FILTER (WHERE predicted_at IS NULL) AS predicted_at_null,
                        COUNT(*) FILTER (WHERE predicted_at::date > game_date) AS predicted_after_game_date,
                        COUNT(*) FILTER (WHERE predicted_at::date <= game_date) AS predicted_on_or_before_game_date
                    FROM hcl.ml_predictions
                    WHERE season IN (2024, 2025)
                    """
                )
                timing_total, timing_null, timing_after, timing_on_or_before = cur.fetchone()

            mismatch_rows: list[dict[str, Any]] = []
            if total_rows and strict_match_rows < total_rows:
                cur.execute(
                    """
                    WITH game_stats AS (
                        SELECT
                            tgs.game_id,
                            tgs.team,
                            g.season,
                            g.week,
                            tgs.points
                        FROM hcl.team_game_stats tgs
                        JOIN hcl.games g ON g.game_id = tgs.game_id
                        WHERE g.season >= 2020
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
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
                            ) AS avg_ppg
                        FROM game_stats
                    ),
                    winner_rows AS (
                        SELECT
                            g.game_id,
                            g.season,
                            g.week,
                            g.home_team,
                            g.away_team,
                            COALESCE(h.avg_ppg, 20)::double precision AS home_ppg,
                            COALESCE(a.avg_ppg, 20)::double precision AS away_ppg
                        FROM hcl.games g
                        LEFT JOIN cumulative_stats h ON g.game_id = h.game_id AND g.home_team = h.team
                        LEFT JOIN cumulative_stats a ON g.game_id = a.game_id AND g.away_team = a.team
                        WHERE g.season >= 2020
                          AND g.home_score IS NOT NULL
                          AND g.away_score IS NOT NULL
                          AND g.week >= 2
                    )
                    SELECT
                        w.game_id,
                        w.season,
                        w.week,
                        w.home_team,
                        w.away_team,
                        ROUND(w.home_ppg::numeric, 3) AS home_ppg,
                        ROUND(COALESCE(eh.expected_home, 20)::numeric, 3) AS expected_home_ppg,
                        ROUND(w.away_ppg::numeric, 3) AS away_ppg,
                        ROUND(COALESCE(ea.expected_away, 20)::numeric, 3) AS expected_away_ppg
                    FROM winner_rows w
                    LEFT JOIN LATERAL (
                        SELECT AVG(tgs.points)::double precision AS expected_home
                        FROM hcl.team_game_stats tgs
                        JOIN hcl.games g2 ON g2.game_id = tgs.game_id
                        WHERE g2.season = w.season
                          AND tgs.team = w.home_team
                          AND g2.week < w.week
                          AND g2.home_score IS NOT NULL
                          AND g2.away_score IS NOT NULL
                    ) eh ON TRUE
                    LEFT JOIN LATERAL (
                        SELECT AVG(tgs.points)::double precision AS expected_away
                        FROM hcl.team_game_stats tgs
                        JOIN hcl.games g2 ON g2.game_id = tgs.game_id
                        WHERE g2.season = w.season
                          AND tgs.team = w.away_team
                          AND g2.week < w.week
                          AND g2.home_score IS NOT NULL
                          AND g2.away_score IS NOT NULL
                    ) ea ON TRUE
                    WHERE NOT (
                        ((eh.expected_home IS NULL AND ABS(w.home_ppg - 20.0) < 1e-6) OR
                         (eh.expected_home IS NOT NULL AND ABS(w.home_ppg - eh.expected_home) < 1e-6))
                        AND
                        ((ea.expected_away IS NULL AND ABS(w.away_ppg - 20.0) < 1e-6) OR
                         (ea.expected_away IS NOT NULL AND ABS(w.away_ppg - ea.expected_away) < 1e-6))
                    )
                    ORDER BY w.season, w.week, w.game_id
                    LIMIT %s
                    """,
                    (limit_rows,),
                )
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    mismatch_rows.append(dict(zip(cols, row)))

        strict_match_pct = round((strict_match_rows / total_rows) * 100.0, 2) if total_rows else None
        predicted_after_pct = round((timing_after / timing_total) * 100.0, 2) if timing_total else None

        indicators = {
            "same_game_feature_leakage_indicator": strict_match_rows != total_rows,
            "prediction_timestamp_after_game_indicator": (timing_after or 0) > 0 if timing_total is not None else None,
        }

        checks = {
            "winner_home_away_ppg_matches_strict_prior_avg": strict_match_rows == total_rows,
            "predictions_timestamped_on_or_before_game_date": (timing_after or 0) == 0 if timing_total is not None else None,
        }

        return {
            "winner_training_rows": int(total_rows or 0),
            "strict_prior_match_rows": int(strict_match_rows or 0),
            "strict_prior_match_pct": strict_match_pct,
            "prediction_timing_table_present": timing_total is not None,
            "prediction_timing_rows_total_2024_2025": int(timing_total) if timing_total is not None else None,
            "prediction_timing_predicted_at_null": int(timing_null) if timing_null is not None else None,
            "prediction_timing_predicted_after_game_date": int(timing_after) if timing_after is not None else None,
            "prediction_timing_predicted_on_or_before_game_date": int(timing_on_or_before) if timing_on_or_before is not None else None,
            "prediction_timing_predicted_after_game_date_pct": predicted_after_pct,
            "indicators": indicators,
            "checks": checks,
            "same_game_mismatch_examples": mismatch_rows,
        }
    finally:
        conn.close()


def write_report(path: pathlib.Path, summary: dict[str, Any]) -> None:
    source_checks = summary["source_guard_audit"]["checks"]
    split_checks = summary["split_boundary_audit"]
    leakage = summary["leakage_indicator_audit"]

    lines: list[str] = []
    lines.append("# TA-023 Leakage Audit Summary")
    lines.append("")
    lines.append(f"Generated (UTC): {summary['generated_at_utc']}")
    lines.append("")
    lines.append("## s23_1 — Feature Builder Prior-Data Audit")
    lines.append(f"- all_checks_passed: {summary['source_guard_audit']['all_checks_passed']}")
    for key, value in source_checks.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## s23_2 — Same-Game Leakage Indicators")
    lines.append(f"- strict_prior_match_rows: {leakage['strict_prior_match_rows']}/{leakage['winner_training_rows']} ({leakage['strict_prior_match_pct']}%)")
    lines.append(f"- same_game_feature_leakage_indicator: {leakage['indicators']['same_game_feature_leakage_indicator']}")
    lines.append(f"- prediction_timestamp_after_game_indicator: {leakage['indicators']['prediction_timestamp_after_game_indicator']}")
    lines.append(f"- predicted_after_game_date_2024_2025: {leakage['prediction_timing_predicted_after_game_date']}/{leakage['prediction_timing_rows_total_2024_2025']} ({leakage['prediction_timing_predicted_after_game_date_pct']}%)")
    lines.append("")

    lines.append("## s23_3 — Chronological Split Boundary Validation")
    lines.append(f"- all_checks_passed: {split_checks['all_checks_passed']}")
    for pipeline in ("winner", "spread"):
        p = split_checks[pipeline]
        lines.append(f"- {pipeline}: rows={p['rows']} train={p['train_rows']} val={p['val_rows']} test={p['test_rows']} checks_passed={p['all_checks_passed']}")
    lines.append("")

    lines.append("## s23_4 — Pass/Fail Decision")
    lines.append(f"- s23_1_pass: {summary['subtask_status']['s23_1_pass']}")
    lines.append(f"- s23_2_pass: {summary['subtask_status']['s23_2_pass']}")
    lines.append(f"- s23_3_pass: {summary['subtask_status']['s23_3_pass']}")
    lines.append(f"- s23_4_pass: {summary['subtask_status']['s23_4_pass']}")
    lines.append(f"- overall_feature_pipeline_pass: {summary['overall_feature_pipeline_pass']}")
    lines.append("")

    lines.append("## Notes")
    lines.append("- same_game_feature_leakage_indicator reflects direct feature leakage in training feature construction.")
    lines.append("- prediction_timestamp_after_game_indicator is tracked as an operational/evaluation leakage risk on historical prediction records, not a training feature-window failure.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TA-023 leakage audit")
    parser.add_argument(
        "--out-dir",
        default=str(ROOT_DIR / "docs" / "sprints" / "ta023_leakage_audit"),
        help="Output directory for TA-023 artifacts",
    )
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(UTC)
    timestamp_slug = generated_at.strftime("%Y%m%d_%H%M%S")
    prefix = f"ta023_audit_{timestamp_slug}"

    source_guard_audit = check_source_guards()
    split_boundary_audit = validate_split_boundaries()
    leakage_indicator_audit = run_same_game_leakage_sql(limit_rows=10)

    subtask_status = {
        "s23_1_pass": bool(source_guard_audit["all_checks_passed"]),
        "s23_2_pass": bool(leakage_indicator_audit["checks"]["winner_home_away_ppg_matches_strict_prior_avg"]),
        "s23_3_pass": bool(split_boundary_audit["all_checks_passed"]),
    }
    subtask_status["s23_4_pass"] = all(subtask_status.values())

    summary = {
        "task": "TA-023",
        "generated_at_utc": generated_at.isoformat(),
        "source_guard_audit": source_guard_audit,
        "split_boundary_audit": split_boundary_audit,
        "leakage_indicator_audit": leakage_indicator_audit,
        "subtask_status": subtask_status,
        "overall_feature_pipeline_pass": all(subtask_status.values()),
    }

    summary_path = out_dir / f"{prefix}_summary.json"
    report_path = out_dir / f"{prefix}_report.md"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(report_path, summary)

    print("TA-023 leakage audit complete")
    print(f"summary={summary_path}")
    print(f"report={report_path}")
    print(f"s23_1_pass={subtask_status['s23_1_pass']}")
    print(f"s23_2_pass={subtask_status['s23_2_pass']}")
    print(f"s23_3_pass={subtask_status['s23_3_pass']}")
    print(f"s23_4_pass={subtask_status['s23_4_pass']}")
    print(f"overall_feature_pipeline_pass={summary['overall_feature_pipeline_pass']}")

    return 0 if summary["overall_feature_pipeline_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
