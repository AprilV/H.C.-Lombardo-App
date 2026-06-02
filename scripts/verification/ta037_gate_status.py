#!/usr/bin/env python3
"""Evaluate TA-037 stability gate readiness from checkpoint JSONL."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_utc(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GateStatus:
    generated_utc: str
    input_path: str
    selected_run_id: str | None
    total_rows: int
    run_rows: int
    first_timestamp_utc: str | None
    last_timestamp_utc: str | None
    elapsed_hours: float
    all_ok_rows: int
    failed_rows: int
    max_gap_seconds: float
    monotonic_snapshot_index: bool
    required_window_hours: float
    allowed_gap_seconds: int
    closure_ready: bool
    blocking_reasons: list[str]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            raw = line.strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def pick_run_id(rows: list[dict[str, Any]], requested_run_id: str | None) -> str | None:
    if requested_run_id:
        return requested_run_id
    for row in reversed(rows):
        run_id = row.get("run_id")
        if isinstance(run_id, str) and run_id:
            return run_id
    return None


def select_rows(rows: list[dict[str, Any]], run_id: str | None) -> list[dict[str, Any]]:
    if run_id is None:
        return rows
    return [row for row in rows if row.get("run_id") == run_id]


def evaluate(
    rows: list[dict[str, Any]],
    input_path: Path,
    required_window_hours: float,
    allowed_gap_seconds: int,
    run_id: str | None,
) -> GateStatus:
    first_ts: str | None = None
    last_ts: str | None = None
    elapsed_hours = 0.0
    max_gap = 0.0
    monotonic_snapshot_index = True
    all_ok_rows = 0
    failed_rows = 0
    reasons: list[str] = []

    parsed: list[tuple[datetime, dict[str, Any]]] = []
    for row in rows:
        ts_raw = row.get("timestamp_utc")
        if not isinstance(ts_raw, str):
            continue
        try:
            ts = parse_utc(ts_raw)
        except ValueError:
            continue
        parsed.append((ts, row))

    parsed.sort(key=lambda item: item[0])

    if parsed:
        first_ts = parsed[0][0].isoformat()
        last_ts = parsed[-1][0].isoformat()
        elapsed_hours = (parsed[-1][0] - parsed[0][0]).total_seconds() / 3600.0

    prev_ts: datetime | None = None
    prev_index: int | None = None
    for ts, row in parsed:
        if bool(row.get("all_ok")):
            all_ok_rows += 1
        else:
            failed_rows += 1

        idx = row.get("snapshot_index")
        if isinstance(idx, int):
            if prev_index is not None and idx <= prev_index:
                monotonic_snapshot_index = False
            prev_index = idx

        if prev_ts is not None:
            gap = (ts - prev_ts).total_seconds()
            if gap > max_gap:
                max_gap = gap
        prev_ts = ts

    if not parsed:
        reasons.append("No valid checkpoint rows were found for the selected run.")
    if elapsed_hours < required_window_hours:
        reasons.append(
            f"Elapsed window is {elapsed_hours:.3f}h, below required {required_window_hours:.3f}h."
        )
    if failed_rows > 0:
        reasons.append(f"Found {failed_rows} checkpoint rows where all_ok=false.")
    if max_gap > allowed_gap_seconds:
        reasons.append(
            f"Largest checkpoint gap is {max_gap:.1f}s, above allowed {allowed_gap_seconds}s."
        )
    if not monotonic_snapshot_index:
        reasons.append("snapshot_index is not strictly increasing within selected run.")

    closure_ready = len(reasons) == 0

    return GateStatus(
        generated_utc=utc_now(),
        input_path=str(input_path),
        selected_run_id=run_id,
        total_rows=len(read_jsonl(input_path)),
        run_rows=len(parsed),
        first_timestamp_utc=first_ts,
        last_timestamp_utc=last_ts,
        elapsed_hours=round(elapsed_hours, 6),
        all_ok_rows=all_ok_rows,
        failed_rows=failed_rows,
        max_gap_seconds=round(max_gap, 3),
        monotonic_snapshot_index=monotonic_snapshot_index,
        required_window_hours=required_window_hours,
        allowed_gap_seconds=allowed_gap_seconds,
        closure_ready=closure_ready,
        blocking_reasons=reasons,
    )


def to_markdown(status: GateStatus) -> str:
    lines: list[str] = []
    lines.append("# TA-037 Gate Auto-Status")
    lines.append("")
    lines.append(f"Generated UTC: {status.generated_utc}")
    lines.append(f"Input: {status.input_path}")
    lines.append(f"Selected run_id: {status.selected_run_id}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- closure_ready: {str(status.closure_ready).lower()}")
    lines.append(f"- run_rows: {status.run_rows}")
    lines.append(f"- elapsed_hours: {status.elapsed_hours}")
    lines.append(f"- all_ok_rows: {status.all_ok_rows}")
    lines.append(f"- failed_rows: {status.failed_rows}")
    lines.append(f"- max_gap_seconds: {status.max_gap_seconds}")
    lines.append(
        f"- monotonic_snapshot_index: {str(status.monotonic_snapshot_index).lower()}"
    )
    lines.append("")
    lines.append("## Window")
    lines.append(f"- first_timestamp_utc: {status.first_timestamp_utc}")
    lines.append(f"- last_timestamp_utc: {status.last_timestamp_utc}")
    lines.append(f"- required_window_hours: {status.required_window_hours}")
    lines.append(f"- allowed_gap_seconds: {status.allowed_gap_seconds}")
    lines.append("")
    lines.append("## Blocking Reasons")
    if status.blocking_reasons:
        for reason in status.blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate TA-037 gate readiness.")
    parser.add_argument(
        "--input",
        default="docs/sprints/ta037_stability_gate/ta037_stability_checkpoints.jsonl",
        help="Checkpoint JSONL input path.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Specific run_id to evaluate. Defaults to latest run_id found.",
    )
    parser.add_argument(
        "--window-hours",
        type=float,
        default=48.0,
        help="Required stable window duration in hours.",
    )
    parser.add_argument(
        "--allowed-gap-seconds",
        type=int,
        default=900,
        help="Maximum allowed timestamp gap between consecutive checkpoints.",
    )
    parser.add_argument(
        "--output-json",
        default="docs/sprints/ta037_stability_gate/ta037_gate_status_latest.json",
        help="Output JSON summary path.",
    )
    parser.add_argument(
        "--output-md",
        default="docs/sprints/ta037_stability_gate/TA037_GATE_AUTOSTATUS_latest.md",
        help="Output markdown summary path.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    all_rows = read_jsonl(input_path)
    selected_run_id = pick_run_id(all_rows, args.run_id)
    run_rows = select_rows(all_rows, selected_run_id)

    status = evaluate(
        rows=run_rows,
        input_path=input_path,
        required_window_hours=args.window_hours,
        allowed_gap_seconds=args.allowed_gap_seconds,
        run_id=selected_run_id,
    )

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    output_md.write_text(to_markdown(status), encoding="utf-8")

    print(json.dumps(asdict(status), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
