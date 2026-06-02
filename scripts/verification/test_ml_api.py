import json
import subprocess
import sys
import argparse
from pathlib import Path

import requests

BASE_URL = "http://localhost:5000"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_CONTRACT_SCRIPT = PROJECT_ROOT / "scripts" / "verification" / "test_reconciliation_contract.py"


def test_predict_upcoming(base_url: str) -> bool:
    print("\n[1/2] /api/ml/predict-upcoming")
    try:
        response = requests.get(f"{base_url}/api/ml/predict-upcoming", timeout=20)
        if response.status_code != 200:
            print(f"  FAIL: status {response.status_code}")
            return False

        data = response.json()
        print(f"  Season: {data.get('season')}")
        print(f"  Week: {data.get('week')}")
        print(f"  Total Games: {data.get('total_games')}")

        predictions = data.get('predictions') or []
        if not predictions:
            message = str(data.get('message') or '').lower()
            if 'no upcoming games found' in message:
                print("  PASS: no upcoming games found (expected in off-window)")
                return True
            print("  FAIL: no predictions returned")
            print(json.dumps(data, indent=2)[:600])
            return False

        for i, pred in enumerate(predictions[:3], 1):
            confidence = pred.get('confidence')
            confidence_pct = f"{confidence * 100:.1f}%" if isinstance(confidence, (int, float)) else "n/a"
            print(f"  Game {i}: {pred.get('away_team')} @ {pred.get('home_team')} | Winner={pred.get('predicted_winner')} | Confidence={confidence_pct}")

        print("  PASS")
        return True
    except Exception as exc:
        print(f"  FAIL: {exc}")
        return False


def test_reconciliation_contract(base_url: str) -> bool:
    print("\n[2/2] reconciliation contract regression")
    if not RECONCILIATION_CONTRACT_SCRIPT.exists():
        print(f"  FAIL: missing script {RECONCILIATION_CONTRACT_SCRIPT}")
        return False

    command = [
        sys.executable,
        str(RECONCILIATION_CONTRACT_SCRIPT),
        "--base-url",
        base_url,
    ]

    result = subprocess.run(command, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

    if result.returncode != 0:
        print(f"  FAIL: reconciliation regression exited {result.returncode}")
        return False

    print("  PASS")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ML API verification chain checks.")
    parser.add_argument("--base-url", default=BASE_URL, help="API base URL")
    args = parser.parse_args()

    print("Testing ML API Verification Chain...")
    print("=" * 80)
    print(f"Base URL: {args.base_url}")

    checks = [
        ("predict_upcoming", test_predict_upcoming(args.base_url)),
        ("reconciliation_contract", test_reconciliation_contract(args.base_url)),
    ]
    passed = sum(1 for _, ok in checks if ok)

    print("\n" + "=" * 80)
    print(f"RESULT: {passed}/{len(checks)} checks passed")
    if passed == len(checks):
        print("PASS: ML verification chain is healthy.")
        return 0

    print("FAIL: ML verification chain has regressions.")
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
