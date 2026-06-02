#!/usr/bin/env python3
"""Run automated Sprint 16 blocker checks and publish a consolidated status report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass
class RouteProbe:
    path: str
    status_code: int | None
    ok: bool
    error: str | None


@dataclass
class AutomationStatus:
    generated_utc: str
    ta016_blocked: bool | None
    ta037_closure_ready: bool | None
    frontend_base: str
    route_probes: list[RouteProbe]
    api_probe_url: str
    api_probe_status: int | None
    api_probe_ok: bool
    checks: list[CheckResult]
    blocker_count: int
    blockers: list[str]
    all_automatable_checks_passing: bool


def run_python_step(step_script: Path) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [sys.executable, str(step_script)],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"Failed to execute {step_script.name}: {exc}"

    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
        return False, f"{step_script.name} exited {proc.returncode}: {err}"

    return True, f"{step_script.name} completed"


def safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def probe_route(base_url: str, path: str, timeout_seconds: float) -> RouteProbe:
    url = f"{base_url.rstrip('/')}{path}"
    try:
        response = requests.get(url, timeout=timeout_seconds)
        status = response.status_code
        return RouteProbe(path=path, status_code=status, ok=status < 400, error=None)
    except Exception as exc:  # noqa: BLE001
        return RouteProbe(path=path, status_code=None, ok=False, error=str(exc))


def probe_api(url: str, timeout_seconds: float) -> tuple[int | None, bool, str | None]:
    try:
        response = requests.get(url, timeout=timeout_seconds)
        status = response.status_code
        return status, status == 200, None
    except Exception as exc:  # noqa: BLE001
        return None, False, str(exc)


def to_markdown(status: AutomationStatus) -> str:
    lines: list[str] = []
    lines.append("# Sprint 16 Blocker Test Automation Status")
    lines.append("")
    lines.append(f"Generated UTC: {status.generated_utc}")
    lines.append("")
    lines.append("## Summary")
    lines.append(
        f"- all_automatable_checks_passing: {str(status.all_automatable_checks_passing).lower()}"
    )
    lines.append(f"- blocker_count: {status.blocker_count}")
    lines.append(f"- ta016_blocked: {status.ta016_blocked}")
    lines.append(f"- ta037_closure_ready: {status.ta037_closure_ready}")
    lines.append(f"- api_probe_ok: {str(status.api_probe_ok).lower()}")
    lines.append("")
    lines.append("## Blockers")
    if status.blockers:
        for blocker in status.blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Route Probes")
    lines.append(f"Base: {status.frontend_base}")
    for route in status.route_probes:
        lines.append(
            "- "
            + f"path={route.path} ok={str(route.ok).lower()} "
            + f"status={route.status_code} error={route.error}"
        )
    lines.append("")
    lines.append("## API Probe")
    lines.append(f"- url={status.api_probe_url}")
    lines.append(
        "- "
        + f"ok={str(status.api_probe_ok).lower()} status={status.api_probe_status}"
    )
    lines.append("")
    lines.append("## Individual Checks")
    for check in status.checks:
        lines.append(
            "- "
            + f"name={check.name} ok={str(check.ok).lower()} detail={check.detail}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run consolidated Sprint 16 blocker automation checks."
    )
    parser.add_argument(
        "--frontend-base",
        default="https://staging.d2fwv8daemi5y2.amplifyapp.com",
        help="Frontend base URL for route probe checks.",
    )
    parser.add_argument(
        "--api-probe-url",
        default="https://9dkkj5n2rc.execute-api.us-east-2.amazonaws.com/api/hcl/analytics/summary?season=2025",
        help="API URL to probe for backend route health.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="HTTP timeout for route and API probes.",
    )
    parser.add_argument(
        "--output-json",
        default="docs/sprints/ta039_release_tag/s16_blocker_test_status_latest.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--output-md",
        default="docs/sprints/ta039_release_tag/S16_BLOCKER_TEST_AUTOSTATUS_latest.md",
        help="Output markdown path.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    ta016_script = repo_root / "scripts/verification/ta016_probe_status.py"
    ta037_script = repo_root / "scripts/verification/ta037_gate_status.py"

    checks: list[CheckResult] = []

    ok_016_step, detail_016_step = run_python_step(ta016_script)
    checks.append(CheckResult(name="ta016_probe_step", ok=ok_016_step, detail=detail_016_step))

    ok_037_step, detail_037_step = run_python_step(ta037_script)
    checks.append(CheckResult(name="ta037_gate_step", ok=ok_037_step, detail=detail_037_step))

    ta016_json = safe_read_json(
        repo_root
        / "docs/sprints/ta016_production_updater_check/ta016_probe_status_latest.json"
    )
    ta037_json = safe_read_json(
        repo_root / "docs/sprints/ta037_stability_gate/ta037_gate_status_latest.json"
    )

    ta016_blocked = None if ta016_json is None else bool(ta016_json.get("blocked", True))
    ta037_closure_ready = (
        None if ta037_json is None else bool(ta037_json.get("closure_ready", False))
    )

    checks.append(
        CheckResult(
            name="ta016_artifact_present",
            ok=ta016_json is not None,
            detail="ta016_probe_status_latest.json parsed"
            if ta016_json is not None
            else "ta016_probe_status_latest.json missing/invalid",
        )
    )
    checks.append(
        CheckResult(
            name="ta037_artifact_present",
            ok=ta037_json is not None,
            detail="ta037_gate_status_latest.json parsed"
            if ta037_json is not None
            else "ta037_gate_status_latest.json missing/invalid",
        )
    )

    routes = [
        "/",
        "/team-stats",
        "/team-comparison",
        "/matchup-analyzer",
        "/analytics",
        "/game-statistics",
        "/historical-data",
        "/ml-predictions",
        "/model-performance",
        "/admin",
        "/settings",
    ]
    route_probes = [probe_route(args.frontend_base, path, args.timeout_seconds) for path in routes]

    route_failures = [item for item in route_probes if not item.ok]
    checks.append(
        CheckResult(
            name="frontend_deep_link_routes",
            ok=len(route_failures) == 0,
            detail=f"{len(route_failures)} failing routes",
        )
    )

    api_status, api_ok, api_error = probe_api(args.api_probe_url, args.timeout_seconds)
    checks.append(
        CheckResult(
            name="api_probe",
            ok=api_ok,
            detail=(
                f"status={api_status}"
                if api_error is None
                else f"error={api_error}"
            ),
        )
    )

    blockers: list[str] = []
    if ta016_blocked is None:
        blockers.append("TA-016 status artifact missing/invalid")
    elif ta016_blocked:
        blockers.append("TA-016 remains blocked (no reachable production endpoint)")

    if ta037_closure_ready is None:
        blockers.append("TA-037 gate artifact missing/invalid")
    elif not ta037_closure_ready:
        blockers.append("TA-037 remains blocked (stability gate not closure-ready)")

    if route_failures:
        blockers.append(
            f"Frontend deep-link route probe has {len(route_failures)} failing routes"
        )

    if not api_ok:
        blockers.append("API probe endpoint did not return HTTP 200")

    status = AutomationStatus(
        generated_utc=utc_now(),
        ta016_blocked=ta016_blocked,
        ta037_closure_ready=ta037_closure_ready,
        frontend_base=args.frontend_base,
        route_probes=route_probes,
        api_probe_url=args.api_probe_url,
        api_probe_status=api_status,
        api_probe_ok=api_ok,
        checks=checks,
        blocker_count=len(blockers),
        blockers=blockers,
        all_automatable_checks_passing=len(blockers) == 0,
    )

    out_json = repo_root / args.output_json
    out_md = repo_root / args.output_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    out_md.write_text(to_markdown(status), encoding="utf-8")

    print(json.dumps(asdict(status), ensure_ascii=True))
    return 0 if status.all_automatable_checks_passing else 2


if __name__ == "__main__":
    raise SystemExit(main())
