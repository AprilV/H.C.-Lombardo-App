#!/usr/bin/env python3
"""TA-037 stability monitor: captures periodic health checkpoints to JSONL."""

from __future__ import annotations

import argparse
import atexit
import json
import os
import time
import uuid
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


LOCK_HANDLE = None


def acquire_lock(lock_path: Path) -> None:
    global LOCK_HANDLE

    lock_path.parent.mkdir(parents=True, exist_ok=True)

    fh = lock_path.open("a+", encoding="utf-8")
    try:
        if os.name == "nt":
            import msvcrt

            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        fh.close()
        raise RuntimeError(
            f"TA-037 monitor already running (lock busy: {lock_path})."
        ) from exc

    fh.seek(0)
    fh.truncate(0)
    fh.write(
        json.dumps(
            {
                "pid": os.getpid(),
                "started_utc": utc_now(),
            },
            ensure_ascii=True,
        )
    )
    fh.flush()
    LOCK_HANDLE = fh

    def _cleanup() -> None:
        try:
            if LOCK_HANDLE is not None:
                if os.name == "nt":
                    import msvcrt

                    LOCK_HANDLE.seek(0)
                    msvcrt.locking(LOCK_HANDLE.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(LOCK_HANDLE.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            if LOCK_HANDLE is not None:
                LOCK_HANDLE.close()
        except Exception:
            pass
        try:
            if lock_path.exists():
                lock_path.unlink()
        except OSError:
            pass

    atexit.register(_cleanup)


def get_last_snapshot_index(output_path: Path) -> int:
    if not output_path.exists():
        return 0

    try:
        lines = output_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return 0

    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
            return int(payload.get("snapshot_index", 0))
        except Exception:
            continue
    return 0


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
    parser.add_argument(
        "--lock-file",
        default="docs/sprints/ta037_stability_gate/ta037_stability_watch.lock",
        help="Lock file path to enforce single active monitor instance.",
    )

    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(args.lock_file)

    acquire_lock(lock_path)

    start = time.time()
    deadline = start + (args.duration_hours * 3600.0)
    run_id = f"{utc_now()}_{uuid.uuid4()}"

    snapshot_index = get_last_snapshot_index(output_path)
    while True:
        snapshot_index += 1
        record = collect_snapshot(args.targets, args.timeout_seconds)
        record["snapshot_index"] = snapshot_index
        record["run_id"] = run_id

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
