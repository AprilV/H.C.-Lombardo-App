"""Regression checks for /api/ml/ai-vs-vegas-reconciliation contract fields."""

import argparse
import sys

import requests


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def fetch_reconciliation(base_url, start_season, end_season, strict_mode=True):
    params = {
        'start_season': start_season,
        'end_season': end_season,
        'strict_mode': 'true' if strict_mode else 'false'
    }
    response = requests.get(
        f"{base_url}/api/ml/ai-vs-vegas-reconciliation",
        params=params,
        timeout=60
    )
    require(response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:300]}")
    payload = response.json()
    require(payload.get('success') is True, "Expected success=true")
    return payload


def validate_common_contract(payload):
    contract = payload.get('contract') or {}
    require(contract.get('version') == 'ai_vegas_reconciliation_v3', "Unexpected contract version")

    summary = payload.get('fingerprint_summary') or {}
    require(summary.get('chain_basis') == 'season_range_inclusive_with_none_placeholders', "Unexpected chain_basis")
    require(isinstance(summary.get('summary_chain_count'), int), "summary_chain_count must be int")
    require(isinstance(summary.get('performance_chain_count'), int), "performance_chain_count must be int")
    require(isinstance(summary.get('summary_non_null_count'), int), "summary_non_null_count must be int")
    require(isinstance(summary.get('performance_non_null_count'), int), "performance_non_null_count must be int")

    require(isinstance(summary.get('summary_chain_sha256'), str), "summary_chain_sha256 must be str")
    require(isinstance(summary.get('performance_chain_sha256'), str), "performance_chain_sha256 must be str")
    require(len(summary.get('summary_chain_sha256')) == 64, "summary_chain_sha256 must be 64 chars")
    require(len(summary.get('performance_chain_sha256')) == 64, "performance_chain_sha256 must be 64 chars")
    require(
        isinstance(summary.get('summary_vs_performance_chain_match'), bool),
        "summary_vs_performance_chain_match must be bool"
    )

    return summary


def main():
    parser = argparse.ArgumentParser(description="Verify reconciliation v3 contract and chain behavior.")
    parser.add_argument('--base-url', default='http://127.0.0.1:5000', help='API base URL')
    parser.add_argument('--start-season', type=int, default=2021, help='Season range start')
    parser.add_argument('--end-season', type=int, default=2025, help='Season range end')
    parser.add_argument(
        '--extended-end-season',
        type=int,
        default=2026,
        help='Extended range end used to verify range-sensitive chain hashing'
    )
    args = parser.parse_args()

    print("=" * 80)
    print("RECONCILIATION V3 CONTRACT REGRESSION CHECK")
    print("=" * 80)

    try:
        base_payload = fetch_reconciliation(args.base_url, args.start_season, args.end_season, strict_mode=True)
        ext_payload = fetch_reconciliation(args.base_url, args.start_season, args.extended_end_season, strict_mode=True)

        base_summary = validate_common_contract(base_payload)
        ext_summary = validate_common_contract(ext_payload)

        expected_base_count = args.end_season - args.start_season + 1
        expected_ext_count = args.extended_end_season - args.start_season + 1

        require(base_summary['summary_chain_count'] == expected_base_count, "Base summary_chain_count mismatch")
        require(base_summary['performance_chain_count'] == expected_base_count, "Base performance_chain_count mismatch")
        require(ext_summary['summary_chain_count'] == expected_ext_count, "Extended summary_chain_count mismatch")
        require(ext_summary['performance_chain_count'] == expected_ext_count, "Extended performance_chain_count mismatch")

        require(base_payload.get('all_match') is True, "Expected base all_match=true")
        require(ext_payload.get('all_match') is True, "Expected extended all_match=true")
        require(base_payload.get('mismatch_count') == 0, "Expected base mismatch_count=0")
        require(ext_payload.get('mismatch_count') == 0, "Expected extended mismatch_count=0")

        require(base_summary['summary_vs_performance_chain_match'] is True, "Base chain_match expected true")
        require(ext_summary['summary_vs_performance_chain_match'] is True, "Extended chain_match expected true")

        require(
            base_summary['summary_chain_sha256'] != ext_summary['summary_chain_sha256'],
            "Expected range-sensitive summary chain hash to change when end season changes"
        )
        require(
            base_summary['performance_chain_sha256'] != ext_summary['performance_chain_sha256'],
            "Expected range-sensitive performance chain hash to change when end season changes"
        )

        print(
            f"PASS base {args.start_season}-{args.end_season}: "
            f"summary_count={base_summary['summary_chain_count']} "
            f"non_null={base_summary['summary_non_null_count']} "
            f"hash_prefix={base_summary['summary_chain_sha256'][:16]}"
        )
        print(
            f"PASS extended {args.start_season}-{args.extended_end_season}: "
            f"summary_count={ext_summary['summary_chain_count']} "
            f"non_null={ext_summary['summary_non_null_count']} "
            f"hash_prefix={ext_summary['summary_chain_sha256'][:16]}"
        )
        print("PASS chain hash is range-sensitive and contracts are stable.")
        return 0

    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
