#!/usr/bin/env python3
"""TA-020 stability watch: run Elo API verification repeatedly and aggregate outcomes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VERIFIER = PROJECT_ROOT / "scripts" / "verification" / "ta020_verify_elo_api_routes.py"
DEFAULT_OUT_DIR = PROJECT_ROOT / "docs" / "sprints" / "model_trust_recovery"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# TA-020 Elo Stability Watch Report")
    lines.append("")
    lines.append(f"- Generated UTC: {summary.get('generated_at_utc')}")
    lines.append(f"- Runs requested: {summary.get('runs_requested')}")
    lines.append(f"- Runs completed: {summary.get('runs_completed')}")
    lines.append(f"- Pass count: {summary.get('pass_count')}")
    lines.append(f"- Fail count: {summary.get('fail_count')}")
    lines.append(f"- Max failures allowed: {summary.get('max_failures_allowed')}")
    lines.append(f"- Intermittent failure observed: {summary.get('intermittent_failure_observed')}")
    lines.append(f"- Overall pass: {summary.get('overall_pass')}")
    lines.append("")
    lines.append("## Run Details")
    lines.append("| Run | Exit | all_checks_passed | ratings_status | predict_status | target_week | top_team_route |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")

    for row in summary.get("runs", []):
        lines.append(
            "| {run_index} | {exit_code} | {all_checks_passed} | {ratings_status} | {predict_status} | {target_week} | {top_team_route} |".format(
                **row
            )
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("- This watch executes ta020_verify_elo_api_routes.py in isolated subprocesses.")
    lines.append("- Failures are treated as blocking only when they exceed max_failures_allowed.")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TA-020 Elo verifier repeatedly and aggregate stability")
    parser.add_argument("--runs", type=int, default=5, help="Number of verification runs")
    parser.add_argument("--delay-seconds", type=float, default=1.0, help="Delay between runs")
    parser.add_argument("--max-failures", type=int, default=0, help="Allowed failures before non-zero exit")
    parser.add_argument("--python-exe", default=sys.executable, help="Python executable for subprocess runs")
    parser.add_argument("--verifier-script", default=str(DEFAULT_VERIFIER), help="Path to ta020 verifier script")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for artifacts")
    args = parser.parse_args()

    if args.runs <= 0:
        raise ValueError("--runs must be > 0")
    if args.max_failures < 0:
        raise ValueError("--max-failures must be >= 0")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_stamp = timestamp_slug()
    jsonl_path = out_dir / f"ta020_stability_{run_stamp}_runs.jsonl"
    summary_path = out_dir / f"ta020_stability_{run_stamp}_summary.json"
    report_path = out_dir / f"ta020_stability_{run_stamp}_report.md"

    runs: list[dict[str, Any]] = []

    for index in range(1, args.runs + 1):
        run_ts = timestamp_slug()
        run_summary_path = out_dir / f"ta020_stability_{run_stamp}_run{index:02d}_{run_ts}.json"
        cmd = [
            args.python_exe,
            str(Path(args.verifier_script)),
            "--summary-out",
            str(run_summary_path),
        ]

        started = time.time()
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        elapsed_ms = int((time.time() - started) * 1000)

        summary_payload: dict[str, Any] = {}
        if run_summary_path.exists():
            try:
                summary_payload = read_json(run_summary_path)
            except Exception:
                summary_payload = {}

        row = {
            "run_index": index,
            "timestamp_utc": utc_now(),
            "exit_code": int(result.returncode),
            "elapsed_ms": elapsed_ms,
            "all_checks_passed": bool(summary_payload.get("all_checks_passed", False)),
            "ratings_status": summary_payload.get("ratings_status"),
            "predict_status": summary_payload.get("predict_status"),
            "target_week": (
                f"{summary_payload.get('target_season')}-W{summary_payload.get('target_week')}"
                if summary_payload.get("target_season") is not None and summary_payload.get("target_week") is not None
                else None
            ),
            "top_team_route": summary_payload.get("top_team_route"),
            "summary_file": run_summary_path.relative_to(PROJECT_ROOT).as_posix(),
            "stdout_tail": result.stdout.strip().splitlines()[-8:],
            "stderr_tail": result.stderr.strip().splitlines()[-8:],
        }
        runs.append(row)

        with jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")

        print(
            f"run={index}/{args.runs} exit={row['exit_code']} "
            f"checks={row['all_checks_passed']} ratings_status={row['ratings_status']}"
        )

        if index < args.runs and args.delay_seconds > 0:
            time.sleep(args.delay_seconds)

    pass_count = sum(1 for row in runs if row.get("all_checks_passed"))
    fail_count = len(runs) - pass_count
    intermittent = pass_count > 0 and fail_count > 0
    overall_pass = fail_count <= args.max_failures

    aggregate = {
        "generated_at_utc": utc_now(),
        "runs_requested": args.runs,
        "runs_completed": len(runs),
        "max_failures_allowed": args.max_failures,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "intermittent_failure_observed": intermittent,
        "overall_pass": overall_pass,
        "artifacts": {
            "jsonl": jsonl_path.relative_to(PROJECT_ROOT).as_posix(),
            "summary": summary_path.relative_to(PROJECT_ROOT).as_posix(),
            "report": report_path.relative_to(PROJECT_ROOT).as_posix(),
        },
        "runs": runs,
    }

    summary_path.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    report_path.write_text(build_report(aggregate), encoding="utf-8")

    print(f"summary={summary_path}")
    print(f"report={report_path}")
    print(f"overall_pass={overall_pass}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
