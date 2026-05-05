#!/usr/bin/env python3
"""TA-070 s70_4: Publish audit summary with prioritized corrective actions."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from datetime import UTC, datetime

ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT_DIR / "docs" / "sprints" / "ta070_audit_data"

PATTERN_S70_1_SUMMARY = re.compile(r"ta070_s70_1_(\d{8}_\d{6})_summary\.json$")
PATTERN_S70_2_SUMMARY = re.compile(r"ta070_s70_2_(\d{8}_\d{6})_summary\.json$")
PATTERN_S70_3_SUMMARY = re.compile(r"ta070_s70_3_(\d{8}_\d{6})_summary\.json$")


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


def build_actions(s70_3: dict) -> list[dict]:
    findings_by_id = {f.get("finding_id"): f for f in s70_3.get("findings", [])}

    return [
        {
            "priority": "P0",
            "action_id": "A1",
            "title": "Enforce leakage-safe evaluation windows and prediction provenance",
            "objective": "Separate retrospective backfill records from true pregame predictions and block post-game records from accuracy scoring.",
            "addresses_findings": ["F2"],
            "evidence": findings_by_id.get("F2", {}).get("evidence"),
            "implementation_scope": [
                "Add prediction provenance metadata (for example prediction_mode: live/backfill) to ml_predictions",
                "Restrict scored evaluation cohorts to rows where predicted_at <= game_date and prediction_mode=live",
                "Retain backfill rows for diagnostics only, not benchmark accuracy claims",
            ],
            "acceptance_criteria": [
                "Published evaluation query excludes post-game predictions by construction",
                "Model Performance/API metrics show cohort counts for live vs backfill records",
                "Leakage check in TA-070 rerun reports predicted_after_game_date_pct=0 for benchmark cohort",
            ],
            "estimated_effort": "M",
        },
        {
            "priority": "P0",
            "action_id": "A2",
            "title": "Decouple total-score predictions from vegas_total line anchoring",
            "objective": "Produce independently predictive totals so over/under outcomes become measurable and useful.",
            "addresses_findings": ["F1"],
            "evidence": findings_by_id.get("F1", {}).get("evidence"),
            "implementation_scope": [
                "Implement an explicit total-points model or equation independent of vegas_total",
                "Store predicted_total directly and derive predicted_home_score/predicted_away_score from that independent total",
                "Recompute TA-070 metrics and verify non-zero evaluable total-pick coverage",
            ],
            "acceptance_criteria": [
                "predicted_total_equals_vegas_total_pct drops well below 95%",
                "total_pick_evaluable_rows > 0 for completed games",
                "s70_2 total accuracy is populated (not null) for evaluated cohort",
            ],
            "estimated_effort": "M",
        },
        {
            "priority": "P1",
            "action_id": "A3",
            "title": "Standardize signed margin labels across backfill and scoring paths",
            "objective": "Align margin targets/errors with home-minus-away convention to eliminate label inconsistency.",
            "addresses_findings": ["F3"],
            "evidence": findings_by_id.get("F3", {}).get("evidence"),
            "implementation_scope": [
                "Replace ABS(home_score-away_score) with signed (home_score-away_score) where actual_margin is persisted",
                "Recalculate margin_prediction_error against signed actual_margin definitions",
                "Backfill corrected margin fields for affected historical records",
            ],
            "acceptance_criteria": [
                "negative_actual_margin_rows > 0 when away wins exist",
                "Margin MAE computed with signed convention is stable and documented",
                "No conflicting margin definitions remain in API and maintenance scripts",
            ],
            "estimated_effort": "S-M",
        },
        {
            "priority": "P1",
            "action_id": "A4",
            "title": "Add automated TA-070 guardrails to prevent recurrence",
            "objective": "Convert current diagnostic checks into repeatable quality gates for future prediction runs.",
            "addresses_findings": ["F1", "F2", "F3"],
            "evidence": "High-severity feature/leakage findings require automated prevention, not one-time manual detection.",
            "implementation_scope": [
                "Keep ta070_extract/compute/root-cause/publish scripts as repeatable pipeline",
                "Add threshold checks for leakage pct, line-lock pct, and margin-sign sanity",
                "Fail verification step when thresholds are violated",
            ],
            "acceptance_criteria": [
                "Single command reruns TA-070 pipeline end-to-end",
                "Pipeline emits pass/fail status with threshold evidence",
                "Sprint evidence includes threshold outcomes for each run",
            ],
            "estimated_effort": "S",
        },
        {
            "priority": "P2",
            "action_id": "A5",
            "title": "Stabilize week-to-week volatility via feature and retrain diagnostics",
            "objective": "Reduce large swings in winner accuracy and identify unstable feature regimes.",
            "addresses_findings": ["F4"],
            "evidence": findings_by_id.get("F4", {}).get("evidence"),
            "implementation_scope": [
                "Segment post-fix performance by week and confidence bands",
                "Inspect feature drift around worst weeks and retraining cut points",
                "Tune model/feature pipeline only after leakage and label fixes are landed",
            ],
            "acceptance_criteria": [
                "Weekly accuracy variance decreases versus current baseline",
                "Worst-week performance floor improves over current 28.57% minimum",
                "Confidence bins remain monotonic after fixes",
            ],
            "estimated_effort": "M-L",
        },
    ]


def write_markdown(path: pathlib.Path, published: dict) -> None:
    metrics = published["baseline_metrics"]
    findings = published["root_cause_findings"]
    actions = published["prioritized_actions"]

    lines: list[str] = []
    lines.append("# TA-070 Final Audit Summary (s70_4)")
    lines.append("")
    lines.append(f"Published (UTC): {published['published_at_utc']}")
    lines.append(f"Source s70_1 summary: {published['source_artifacts']['s70_1_summary']}")
    lines.append(f"Source s70_2 summary: {published['source_artifacts']['s70_2_summary']}")
    lines.append(f"Source s70_3 summary: {published['source_artifacts']['s70_3_summary']}")
    lines.append("")
    lines.append("## Baseline Metrics")
    lines.append(f"- Winner accuracy: {metrics['winner_accuracy_pct']}% ({metrics['winner_correct_games']}/{metrics['winner_evaluable_games']})")
    lines.append(f"- Spread accuracy: {metrics['spread_accuracy_pct']}% ({metrics['spread_correct_games']}/{metrics['spread_evaluable_games']})")
    lines.append(f"- Margin MAE: {metrics['margin_mae_points']} points")
    lines.append(f"- Total MAE: {metrics['total_mae_points']} points")
    lines.append(f"- Total-pick evaluable coverage: {metrics['total_coverage_pct']}%")
    lines.append(f"- Predicted-score coverage: {metrics['predicted_score_coverage_pct']}%")
    lines.append("")
    lines.append("## Root-Cause Summary")
    for finding in findings:
        lines.append(
            f"- {finding['finding_id']} ({finding['severity']}/{finding['category']}): "
            f"{finding['title']}"
        )
    lines.append("")
    lines.append("## Prioritized Corrective Actions")
    lines.append("| Priority | Action | Objective |")
    lines.append("| --- | --- | --- |")
    for action in actions:
        lines.append(
            f"| {action['priority']} | {action['action_id']} — {action['title']} | {action['objective']} |"
        )
    lines.append("")
    lines.append("## Action Details")
    for action in actions:
        lines.append(f"### {action['action_id']} — {action['title']} ({action['priority']})")
        lines.append(f"- Objective: {action['objective']}")
        lines.append(f"- Addresses findings: {', '.join(action['addresses_findings'])}")
        if action.get("evidence"):
            lines.append(f"- Evidence: {action['evidence']}")
        lines.append(f"- Estimated effort: {action['estimated_effort']}")
        lines.append("- Implementation scope:")
        for item in action["implementation_scope"]:
            lines.append(f"  - {item}")
        lines.append("- Acceptance criteria:")
        for item in action["acceptance_criteria"]:
            lines.append(f"  - {item}")
        lines.append("")

    lines.append("## Publication Scope")
    lines.append("- This s70_4 artifact publishes the audit summary and prioritized corrective plan.")
    lines.append("- Implementation of these actions is out of scope for TA-070 s70_4 and should be tracked as follow-on work.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish TA-070 s70_4 final audit summary")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Directory containing TA-070 artifacts")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    s70_1_summary_path = resolve_latest(out_dir, PATTERN_S70_1_SUMMARY, "ta070_s70_1_*_summary.json")
    s70_2_summary_path = resolve_latest(out_dir, PATTERN_S70_2_SUMMARY, "ta070_s70_2_*_summary.json")
    s70_3_summary_path = resolve_latest(out_dir, PATTERN_S70_3_SUMMARY, "ta070_s70_3_*_summary.json")

    s70_1 = load_json(s70_1_summary_path)
    s70_2 = load_json(s70_2_summary_path)
    s70_3 = load_json(s70_3_summary_path)

    prioritized_actions = build_actions(s70_3)

    published = {
        "published_at_utc": datetime.now(UTC).isoformat(),
        "source_artifacts": {
            "s70_1_summary": s70_1_summary_path.relative_to(ROOT_DIR).as_posix(),
            "s70_2_summary": s70_2_summary_path.relative_to(ROOT_DIR).as_posix(),
            "s70_3_summary": s70_3_summary_path.relative_to(ROOT_DIR).as_posix(),
        },
        "baseline_metrics": {
            "row_count": s70_2.get("row_count"),
            "winner_accuracy_pct": s70_2.get("overall", {}).get("winner_accuracy_pct"),
            "winner_correct_games": s70_2.get("overall", {}).get("winner_correct_games"),
            "winner_evaluable_games": s70_2.get("overall", {}).get("winner_evaluable_games"),
            "spread_accuracy_pct": s70_2.get("overall", {}).get("spread_accuracy_pct"),
            "spread_correct_games": s70_2.get("overall", {}).get("spread_correct_games"),
            "spread_evaluable_games": s70_2.get("overall", {}).get("spread_evaluable_games"),
            "margin_mae_points": s70_2.get("overall", {}).get("margin_mae_points"),
            "total_mae_points": s70_2.get("overall", {}).get("total_mae_points"),
            "total_coverage_pct": s70_2.get("overall", {}).get("total_coverage_pct"),
            "predicted_score_coverage_pct": s70_2.get("overall", {}).get("predicted_score_coverage_pct"),
        },
        "root_cause_findings": s70_3.get("findings", []),
        "prioritized_actions": prioritized_actions,
        "publication_notes": [
            "Actions are ordered by risk reduction and audit integrity impact.",
            "P0 actions are required before claiming production-grade benchmark accuracy.",
        ],
    }

    timestamp_slug = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    prefix = f"ta070_s70_4_{timestamp_slug}"

    summary_json_path = out_dir / f"{prefix}_summary.json"
    report_md_path = out_dir / f"{prefix}_audit_summary.md"

    summary_json_path.write_text(json.dumps(published, indent=2), encoding="utf-8")
    write_markdown(report_md_path, published)

    print("TA-070 s70_4 publish complete")
    print(f"summary={summary_json_path}")
    print(f"report={report_md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())