#!/usr/bin/env python3
"""Probe TA-016 production health endpoints and emit status artifacts."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProbeResult:
    url: str
    ok: bool
    status_code: int | None
    elapsed_ms: int
    error: str | None


@dataclass
class ProbeStatus:
    generated_utc: str
    endpoints: list[ProbeResult]
    any_reachable: bool
    all_reachable: bool
    blocked: bool
    blocking_reason: str | None


def probe(url: str, timeout_seconds: float) -> ProbeResult:
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout_seconds)
        elapsed_ms = int((time.time() - start) * 1000)
        return ProbeResult(
            url=url,
            ok=response.status_code == 200,
            status_code=response.status_code,
            elapsed_ms=elapsed_ms,
            error=None,
        )
    except Exception as exc:  # noqa: BLE001 - evidence capture requires full exception text
        elapsed_ms = int((time.time() - start) * 1000)
        return ProbeResult(
            url=url,
            ok=False,
            status_code=None,
            elapsed_ms=elapsed_ms,
            error=str(exc),
        )


def to_markdown(status: ProbeStatus) -> str:
    lines: list[str] = []
    lines.append("# TA-016 Production Probe Auto-Status")
    lines.append("")
    lines.append(f"Generated UTC: {status.generated_utc}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- any_reachable: {str(status.any_reachable).lower()}")
    lines.append(f"- all_reachable: {str(status.all_reachable).lower()}")
    lines.append(f"- blocked: {str(status.blocked).lower()}")
    lines.append(
        f"- blocking_reason: {status.blocking_reason if status.blocking_reason else 'None'}"
    )
    lines.append("")
    lines.append("## Endpoint Results")
    for item in status.endpoints:
        lines.append(
            "- "
            + f"url={item.url} ok={str(item.ok).lower()} status_code={item.status_code} "
            + f"elapsed_ms={item.elapsed_ms} error={item.error}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TA-016 production health probes.")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="Per-endpoint request timeout.",
    )
    parser.add_argument(
        "--endpoints",
        nargs="+",
        default=[
            "http://34.198.25.249:5000/health",
            "https://api.aprilsykes.dev/health",
        ],
        help="Endpoints to probe.",
    )
    parser.add_argument(
        "--output-json",
        default="docs/sprints/ta016_production_updater_check/ta016_probe_status_latest.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--output-md",
        default="docs/sprints/ta016_production_updater_check/TA016_PROBE_AUTOSTATUS_latest.md",
        help="Output Markdown path.",
    )
    args = parser.parse_args()

    endpoint_results = [probe(url, args.timeout_seconds) for url in args.endpoints]
    any_reachable = any(item.ok for item in endpoint_results)
    all_reachable = all(item.ok for item in endpoint_results)
    blocked = not any_reachable

    reason = None
    if blocked:
        reason = "No configured production endpoint returned HTTP 200 from current environment."

    status = ProbeStatus(
        generated_utc=utc_now(),
        endpoints=endpoint_results,
        any_reachable=any_reachable,
        all_reachable=all_reachable,
        blocked=blocked,
        blocking_reason=reason,
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
