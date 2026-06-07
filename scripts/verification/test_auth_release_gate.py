"""Auth release gate checks for site manifest and public API auth regressions."""

import argparse
import sys
from typing import Dict, Optional, Tuple

import requests


def normalize_base_url(url: str) -> str:
    return url.rstrip("/")


def check_endpoint(
    url: str,
    *,
    name: str,
    params: Optional[Dict[str, str]] = None,
    expect_json: bool = True,
    timeout: int = 20,
) -> Tuple[bool, str]:
    try:
        response = requests.get(url, params=params, timeout=timeout)
    except Exception as exc:
        return False, f"request failed: {exc}"

    if response.status_code == 401:
        return False, "received 401 Unauthorized"

    if response.status_code != 200:
        return False, f"unexpected status={response.status_code}"

    if expect_json:
        try:
            response.json()
        except Exception as exc:
            return False, f"invalid JSON payload: {exc}"

    return True, "ok"


def run_manifest_gate(site_url: Optional[str], timeout: int) -> bool:
    print("\n[auth-1] manifest endpoint")
    if not site_url:
        print("  SKIP: no --public-site-url provided")
        return True

    manifest_url = f"{normalize_base_url(site_url)}/manifest.json"
    ok, details = check_endpoint(
        manifest_url,
        name="manifest",
        expect_json=True,
        timeout=timeout,
    )

    if ok:
        print(f"  PASS: {manifest_url}")
        return True

    print(f"  FAIL: {manifest_url} -> {details}")
    return False


def run_public_api_gate(api_url: str, season: int, timeout: int) -> bool:
    print("\n[auth-2] public API endpoints")
    base = normalize_base_url(api_url)
    checks = [
        ("health", f"{base}/health", None),
        ("hcl_teams", f"{base}/api/hcl/teams", {"season": str(season)}),
        ("predict_upcoming", f"{base}/api/ml/predict-upcoming", None),
        ("live_scores", f"{base}/api/live-scores", None),
    ]

    all_passed = True
    for name, url, params in checks:
        ok, details = check_endpoint(
            url,
            name=name,
            params=params,
            expect_json=True,
            timeout=timeout,
        )
        if ok:
            print(f"  PASS: {name}")
        else:
            all_passed = False
            print(f"  FAIL: {name} -> {details}")

    return all_passed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run auth release gate checks.")
    parser.add_argument("--base-url", default="http://localhost:5000", help="Base API URL to validate")
    parser.add_argument("--public-site-url", default="", help="Optional public site URL (checks /manifest.json)")
    parser.add_argument("--season", type=int, default=2025, help="Season used for /api/hcl/teams")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    args = parser.parse_args()

    print("=" * 80)
    print("AUTH RELEASE GATE")
    print("=" * 80)
    print(f"API URL: {args.base_url}")
    if args.public_site_url:
        print(f"Site URL: {args.public_site_url}")

    checks = [
        run_manifest_gate(args.public_site_url.strip() or None, args.timeout),
        run_public_api_gate(args.base_url, args.season, args.timeout),
    ]

    passed = sum(1 for ok in checks if ok)
    total = len(checks)

    print("\n" + "=" * 80)
    print(f"RESULT: {passed}/{total} checks passed")

    if passed == total:
        print("PASS: Auth release gate is healthy.")
        return 0

    print("FAIL: Auth release gate detected regressions.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
