#!/usr/bin/env python3
"""Generate a traceable session resume checkpoint with runtime evidence.

Creates sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md and captures:
- current git branch / recent commits / working set
- basic local API smoke checks
- standardized next-session startup steps
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a timestamped session resume checkpoint"
    )
    parser.add_argument(
        "--reason",
        default="Chat restart checkpoint to prevent drift and preserve continuity.",
        help="Reason text for the session resume",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path",
    )
    parser.add_argument(
        "--output-dir",
        default="sessions",
        help="Output directory for resume files",
    )
    parser.add_argument(
        "--api-base",
        default="http://127.0.0.1:5000",
        help="Local API base URL for smoke checks",
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Skip API smoke checks",
    )
    return parser.parse_args()


def run_cmd(args: list[str], cwd: pathlib.Path) -> tuple[int, str]:
    proc = subprocess.run(
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.rstrip()


def http_get_json(url: str, timeout: float = 10.0) -> tuple[bool, int | None, dict | list | None, str | None]:
    req = urllib.request.Request(url=url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                return True, resp.status, None, "response_not_json"
            return True, resp.status, data, None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return False, e.code, None, body[:300]
    except Exception as e:  # pragma: no cover
        return False, None, None, str(e)


def format_working_set(status_text: str) -> list[str]:
    lines = [ln.rstrip("\r") for ln in status_text.splitlines() if ln.strip()]
    if not lines:
        return ["- Working tree clean"]

    mapped: list[str] = []
    for ln in lines:
        match = re.match(r"^(..)[ ](.*)$", ln)
        if not match:
            mapped.append(f"- {ln}")
            continue
        code = match.group(1)
        path = match.group(2)
        if code == "??":
            label = "Untracked"
        elif "M" in code:
            label = "Modified"
        elif "A" in code:
            label = "Added"
        elif "D" in code:
            label = "Deleted"
        elif "R" in code:
            label = "Renamed"
        else:
            label = f"State({code})"
        mapped.append(f"- {label}: {path}")
    return mapped


def build_api_snapshot(api_base: str, skip_api: bool) -> list[str]:
    if skip_api:
        return ["- API smoke checks skipped by flag."]

    checks = [
        ("health", f"{api_base}/health"),
        ("teams_count", f"{api_base}/api/teams/count"),
        ("hcl_teams_2025", f"{api_base}/api/hcl/teams?season=2025"),
    ]

    lines: list[str] = []
    for name, url in checks:
        ok, status, payload, err = http_get_json(url)
        if not ok:
            lines.append(f"- {name}: FAIL status={status} error={err}")
            continue

        detail = []
        if isinstance(payload, dict):
            if "count" in payload:
                detail.append(f"count={payload.get('count')}")
            if "source" in payload:
                detail.append(f"source={payload.get('source')}")
            if "season" in payload:
                detail.append(f"season={payload.get('season')}")
            if "status" in payload:
                detail.append(f"status={payload.get('status')}")
            if "success" in payload:
                detail.append(f"success={payload.get('success')}")

        suffix = " " + " ".join(detail) if detail else ""
        lines.append(f"- {name}: PASS status={status}{suffix}")

    return lines


def main() -> int:
    args = parse_args()
    repo_root = pathlib.Path(args.repo_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now()
    stamp = now.strftime("%Y-%m-%d_%H%M")
    filename = f"SESSION_RESUME_{stamp}.md"
    out_path = output_dir / filename

    if out_path.exists():
        print(f"FAIL: Resume file already exists: {out_path}")
        print("Wait one minute and rerun to preserve traceability.")
        return 2

    code, branch = run_cmd(["git", "branch", "--show-current"], repo_root)
    if code != 0 or not branch:
        print("FAIL: Could not read current git branch")
        return 2

    _, commits = run_cmd(["git", "log", "-3", "--oneline", "--decorate"], repo_root)
    _, status = run_cmd(["git", "status", "--short"], repo_root)

    working_set_lines = format_working_set(status)
    api_snapshot_lines = build_api_snapshot(args.api_base, args.skip_api)

    content = [
        f"# Session Resume Note - {now.strftime('%Y-%m-%d %H%M')}",
        "",
        "## Reason",
        args.reason.strip(),
        "",
        "## Current Git State Snapshot",
        f"- Branch: {branch.strip()}",
        "- Latest commits:",
    ]

    commit_lines = [ln.strip() for ln in commits.splitlines() if ln.strip()]
    if commit_lines:
        content.extend([f"  - {ln}" for ln in commit_lines])
    else:
        content.append("  - (no commit data available)")

    content.extend([
        "",
        "## Current Local Working Set (Uncommitted)",
        *working_set_lines,
        "",
        "## Verification Snapshot (Runtime)",
        *api_snapshot_lines,
        "",
        "## Non-Negotiable User Directives (Carry Forward)",
        "1. App is primary project scope.",
        "2. Dashboard is secondary but must stay accurate for stakeholder/professor review.",
        "3. No trust-by-claim: include runtime proof before completion claims.",
        "4. One objective at a time to prevent drift.",
        "",
        "## Next Chat Start Procedure",
        "1. Read this resume file first.",
        "2. Confirm scope lock (app-first unless user explicitly selects dashboard work).",
        "3. Run backend health snapshot before code changes.",
        "4. Complete one concrete fix with proof output before moving on.",
        "",
        "## Fast Resume Commands",
        "- git status --short",
        "- git log -3 --oneline --decorate",
        f"- {sys.executable} scripts/maintenance/session_resume_guard.py --reason \"Manual checkpoint refresh\"",
        "",
    ])

    out_path.write_text("\n".join(content), encoding="utf-8")

    print(f"PASS: Session resume written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
