"""Run core backend verification checks in a single command."""

import argparse
import subprocess
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_CHAIN_SCRIPT = PROJECT_ROOT / "scripts" / "verification" / "test_ml_api.py"
AUTH_GATE_SCRIPT = PROJECT_ROOT / "scripts" / "verification" / "test_auth_release_gate.py"


def run_health_check(base_url: str) -> bool:
    print("\n[1/3] health endpoint")
    try:
        response = requests.get(f"{base_url}/health", timeout=15)
        if response.status_code != 200:
            print(f"  FAIL: status={response.status_code}")
            return False

        payload = response.json()
        status = payload.get("status")
        database = payload.get("database")
        print(f"  status={status} database={database}")

        if status != "healthy" or database != "connected":
            print("  FAIL: health contract mismatch")
            return False

        print("  PASS")
        return True
    except Exception as exc:
        print(f"  FAIL: {exc}")
        return False


def run_hcl_teams_check(base_url: str, season: int) -> bool:
    print("\n[2/3] HCL teams endpoint")
    try:
        response = requests.get(f"{base_url}/api/hcl/teams", params={"season": season}, timeout=20)
        if response.status_code != 200:
            print(f"  FAIL: status={response.status_code}")
            return False

        payload = response.json()
        if not payload.get("success"):
            print("  FAIL: success=false")
            return False

        teams = payload.get("teams") or []
        print(f"  season={season} teams={len(teams)}")
        if len(teams) != 32:
            print("  FAIL: expected 32 teams")
            return False

        print("  PASS")
        return True
    except Exception as exc:
        print(f"  FAIL: {exc}")
        return False


def run_ml_chain(base_url: str) -> bool:
    print("\n[3/4] ML verification chain")
    if not ML_CHAIN_SCRIPT.exists():
        print(f"  FAIL: missing script {ML_CHAIN_SCRIPT}")
        return False

    command = [sys.executable, str(ML_CHAIN_SCRIPT), "--base-url", base_url]
    result = subprocess.run(command, cwd=str(PROJECT_ROOT), capture_output=True, text=True)

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

    if result.returncode != 0:
        print(f"  FAIL: ML chain exited {result.returncode}")
        return False

    print("  PASS")
    return True


def run_auth_release_gate(base_url: str, season: int, public_site_url: str | None = None) -> bool:
    print("\n[4/4] auth release gate")
    if not AUTH_GATE_SCRIPT.exists():
        print(f"  FAIL: missing script {AUTH_GATE_SCRIPT}")
        return False

    command = [
        sys.executable,
        str(AUTH_GATE_SCRIPT),
        "--base-url",
        base_url,
        "--season",
        str(season),
    ]

    if public_site_url:
        command.extend(["--public-site-url", public_site_url])

    result = subprocess.run(command, cwd=str(PROJECT_ROOT), capture_output=True, text=True)

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

    if result.returncode != 0:
        print(f"  FAIL: auth release gate exited {result.returncode}")
        return False

    print("  PASS")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run core backend verification chain checks.")
    parser.add_argument("--base-url", default="http://localhost:5000", help="API base URL")
    parser.add_argument("--season", type=int, default=2025, help="Season for HCL teams endpoint check")
    parser.add_argument(
        "--public-site-url",
        default="",
        help="Optional public website URL (adds /manifest.json auth check)",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("CORE BACKEND VERIFICATION CHAIN")
    print("=" * 80)
    print(f"Base URL: {args.base_url}")
    print(f"Season: {args.season}")

    checks = [
        ("health", run_health_check(args.base_url)),
        ("hcl_teams", run_hcl_teams_check(args.base_url, args.season)),
        ("ml_chain", run_ml_chain(args.base_url)),
        (
            "auth_release_gate",
            run_auth_release_gate(
                args.base_url,
                args.season,
                args.public_site_url.strip() or None,
            ),
        ),
    ]

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    print("\n" + "=" * 80)
    print(f"RESULT: {passed}/{total} checks passed")

    if passed == total:
        print("PASS: Core backend verification chain is healthy.")
        return 0

    print("FAIL: Core backend verification chain has regressions.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
