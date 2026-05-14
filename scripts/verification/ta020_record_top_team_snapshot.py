"""Record TA-020 s20_4: top-team Elo snapshot for audit traceability."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def build_report(summary: dict[str, Any]) -> str:
    checks = summary.get("checks") or {}
    top5 = summary.get("top5") or []
    route_top = summary.get("route_top") or {}

    lines = [
        "# TA-020 s20_4 Evidence Report",
        "",
        "## Objective",
        "Record top-team Elo rating snapshot for audit traceability.",
        "",
        "## Snapshot Source",
        f"- ratings_file: {summary.get('ratings_file')}",
        f"- file_sha256: {summary.get('ratings_file_sha256')}",
        f"- file_last_updated: {summary.get('file_last_updated')}",
        f"- snapshot_captured_at_utc: {summary.get('snapshot_captured_at_utc')}",
        f"- ratings_count: {summary.get('ratings_count')}",
        "",
        "## Top-Team Snapshot",
        f"- top_team: {summary.get('top_team')}",
        f"- top_rating: {summary.get('top_rating')}",
        f"- second_team: {summary.get('second_team')}",
        f"- second_rating: {summary.get('second_rating')}",
        f"- top_gap: {summary.get('top_gap')}",
        f"- bottom_team: {summary.get('bottom_team')}",
        f"- bottom_rating: {summary.get('bottom_rating')}",
        "",
        "## Top 5 Teams",
    ]

    for row in top5:
        lines.append(f"- #{row.get('rank')}: {row.get('team')} ({row.get('rating')})")

    lines.extend(
        [
            "",
            "## Route Cross-Check (/api/elo/ratings/current)",
            f"- route_status: {summary.get('route_status')}",
            f"- route_last_updated: {summary.get('route_last_updated')}",
            f"- route_top_team: {route_top.get('team')}",
            f"- route_top_rating: {route_top.get('rating')}",
            "",
            "## Checks",
            f"- ratings_count_32: {checks.get('ratings_count_32')}",
            f"- top_team_exists: {checks.get('top_team_exists')}",
            f"- route_status_200: {checks.get('route_status_200')}",
            f"- route_top_matches_file: {checks.get('route_top_matches_file')}",
            f"- route_last_updated_matches_file: {checks.get('route_last_updated_matches_file')}",
            f"- all_checks_passed: {summary.get('all_checks_passed')}",
            "",
        ]
    )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TA-020 top-team Elo snapshot recorder")
    parser.add_argument(
        "--ratings-file",
        default=str(PROJECT_ROOT / "ml" / "models" / "elo_ratings_current.json"),
    )
    parser.add_argument("--api-base", default="http://127.0.0.1:5000")
    parser.add_argument("--summary-out", required=False)
    parser.add_argument("--report-out", required=False)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    ratings_path = Path(args.ratings_file)
    if not ratings_path.exists():
        print(f"error=ratings_file_missing path={ratings_path}")
        return 2

    file_data = json.loads(ratings_path.read_text(encoding="utf-8"))
    ratings: dict[str, float] = file_data.get("ratings") or {}

    if not ratings:
        print("error=ratings_map_empty")
        return 2

    sorted_ratings = sorted(
        ((team, float(value)) for team, value in ratings.items()),
        key=lambda item: item[1],
        reverse=True,
    )

    top_team, top_rating = sorted_ratings[0]
    second_team, second_rating = sorted_ratings[1]
    bottom_team, bottom_rating = sorted_ratings[-1]

    top5 = [
        {"rank": idx + 1, "team": team, "rating": round(value, 1)}
        for idx, (team, value) in enumerate(sorted_ratings[:5])
    ]

    route_status = None
    route_last_updated = None
    route_top = {}
    route_top_team = None
    route_top_rating = None
    route_error = None

    try:
        endpoint = args.api_base.rstrip("/") + "/api/elo/ratings/current"
        req = Request(endpoint, method="GET")
        with urlopen(req, timeout=12) as resp:
            route_status = int(resp.status)
            payload = resp.read().decode("utf-8", errors="replace")
        route_json = json.loads(payload)
        route_last_updated = route_json.get("last_updated")
        rankings = route_json.get("rankings") or []
        if rankings:
            route_top = rankings[0]
            route_top_team = route_top.get("team")
            route_top_rating = route_top.get("rating")
    except HTTPError as exc:
        route_status = int(exc.code)
        route_error = f"HTTPError: {exc}"
    except URLError as exc:
        route_error = f"URLError: {exc}"
    except Exception as exc:
        route_error = f"Exception: {exc}"
        route_status = None

    checks = {
        "ratings_count_32": len(ratings) == 32,
        "top_team_exists": top_team is not None,
        "route_status_200": route_status == 200,
        "route_top_matches_file": (
            route_top_team == top_team
            and route_top_rating is not None
            and abs(float(route_top_rating) - round(float(top_rating), 1)) <= 0.2
        ),
        "route_last_updated_matches_file": route_last_updated == file_data.get("last_updated"),
    }
    all_checks_passed = all(checks.values())

    summary = {
        "task": "TA-020",
        "subtask": "s20_4",
        "ratings_file": str(ratings_path),
        "ratings_file_sha256": sha256_file(ratings_path),
        "file_last_updated": file_data.get("last_updated"),
        "snapshot_captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "ratings_count": len(ratings),
        "top_team": top_team,
        "top_rating": round(float(top_rating), 1),
        "second_team": second_team,
        "second_rating": round(float(second_rating), 1),
        "top_gap": round(float(top_rating - second_rating), 1),
        "bottom_team": bottom_team,
        "bottom_rating": round(float(bottom_rating), 1),
        "top5": top5,
        "route_status": route_status,
        "route_last_updated": route_last_updated,
        "route_top": {
            "team": route_top_team,
            "rating": route_top_rating,
        },
        "route_error": route_error,
        "checks": checks,
        "all_checks_passed": all_checks_passed,
    }

    print(f"ratings_count={summary['ratings_count']}")
    print(f"top_team={summary['top_team']}")
    print(f"top_rating={summary['top_rating']}")
    print(f"top_gap={summary['top_gap']}")
    print(f"route_status={summary['route_status']}")
    print(f"route_top={route_top_team}:{route_top_rating}")
    print(f"route_error={summary['route_error']}")
    print(f"all_checks_passed={summary['all_checks_passed']}")

    if args.summary_out:
        summary_path = Path(args.summary_out)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"summary_out={summary_path}")

    if args.report_out:
        report_path = Path(args.report_out)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(build_report(summary), encoding="utf-8")
        print(f"report_out={report_path}")

    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())