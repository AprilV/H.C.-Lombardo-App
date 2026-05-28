#!/usr/bin/env python3
"""TA-037 stability monitor: captures periodic health checkpoints to JSONL."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_endpoint(url: str, timeout: float) -> Dict[str, object]:
    started = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "ok": response.status_code == 200,
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
        }
    except Exception as exc:  # noqa: BLE001 - capture network/runtime failures in evidence
        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "ok": False,
            "status_code": None,
            "elapsed_ms": elapsed_ms,
            "error": str(exc),
        }


def collect_snapshot(targets: List[str], timeout: float) -> Dict[str, object]:
    checks = {url: check_endpoint(url, timeout) for url in targets}
    all_ok = all(item.get("ok") for item in checks.values())
    return {
        "timestamp_utc": utc_now(),
        "all_ok": all_ok,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect TA-037 stability checkpoints.")
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=300,
        help="Seconds between snapshots (default: 300).",
    )
    parser.add_argument(
        "--duration-hours",
        type=float,
        default=0.0,
        help="How long to run. 0 means capture a single snapshot and exit.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=5.0,
        help="Per-endpoint request timeout in seconds.",
    )
    parser.add_argument(
        "--output",
        default="docs/sprints/ta037_stability_gate/ta037_stability_checkpoints.jsonl",
        help="JSONL output path.",
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        default=[
            "http://127.0.0.1:5000/health",
            "http://127.0.0.1:5000/api/teams",
            "http://127.0.0.1:3000",
        ],
        help="Target URLs to probe each cycle.",
    )

    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    start = time.time()
    deadline = start + (args.duration_hours * 3600.0)

    snapshot_index = 0
    while True:
        snapshot_index += 1
        record = collect_snapshot(args.targets, args.timeout_seconds)
        record["snapshot_index"] = snapshot_index

        with output_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")

        print(
            f"[{record['timestamp_utc']}] snapshot={snapshot_index} all_ok={record['all_ok']}"
        )

        if args.duration_hours <= 0:
            break
        if time.time() >= deadline:
            break
        time.sleep(max(1, args.interval_seconds))

    print(f"Wrote checkpoints to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
