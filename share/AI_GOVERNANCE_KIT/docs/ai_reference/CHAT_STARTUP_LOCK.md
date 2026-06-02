# CHAT_STARTUP_LOCK

## Purpose
This runbook sets a strict startup protocol for AI chats to prevent drift.

The protocol is called Execute Order 66.

Before any implementation work starts, the assistant must capture and report:

1. Current scope priority.
2. Current uncommitted working set.
3. Runtime verification snapshot.
4. Read matrix status (complete or blocked).
5. Explicit exclusions used.

## Trigger Phrases

Use one of these messages in chat:

- EXECUTE ORDER 66
- RUN STARTUP LOCK
- LOOK AT CHAT_STARTUP_LOCK AND EXECUTE

Or explicitly reference this file path:

- docs/ai_reference/CHAT_STARTUP_LOCK.md

## Step-By-Step Build Instructions

Follow all steps in order for a new project.

### Step 1: Create required folders

PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "docs/ai_reference" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts/maintenance" | Out-Null
New-Item -ItemType Directory -Force -Path "sessions" | Out-Null
New-Item -ItemType Directory -Force -Path ".github" | Out-Null
```

### Step 2: Create required governance documents

Create these files in docs/ai_reference:

1. READ_THIS_FIRST.md
2. AI_EXECUTION_CONTRACT.md
3. COMMIT_POLICY.md
4. RESOURCE_EXPENDITURE_POLICY.md
5. BEST_PRACTICES.md
6. AI_VIOLATION_CHECKLIST.md
7. INDEX.md

Use templates included in this starter pack.

### Step 3: Create continuity and startup scripts

Create these files:

- sessions/README.md
- scripts/maintenance/session_resume_guard.py
- scripts/maintenance/session_resume_guard.ps1

Use the exact code included in this starter pack.

### Step 4: Add startup trigger instructions

Merge the startup trigger section from:

- .github/copilot-instructions.md

into your repo's instruction file.

### Step 5: Run a first checkpoint test

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
```

Then confirm newest file:

```powershell
Get-ChildItem sessions -Filter "SESSION_RESUME_*.md" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 -ExpandProperty FullName
```

Expected result:

- command prints PASS
- new SESSION_RESUME_YYYY-MM-DD_HHMM.md exists
- file includes git and runtime sections

## Required Read Matrix

These files must be read during startup lock.

Core governance:

- docs/ai_reference/READ_THIS_FIRST.md
- docs/ai_reference/AI_EXECUTION_CONTRACT.md
- docs/ai_reference/COMMIT_POLICY.md
- docs/ai_reference/RESOURCE_EXPENDITURE_POLICY.md
- docs/ai_reference/BEST_PRACTICES.md
- docs/ai_reference/AI_VIOLATION_CHECKLIST.md
- docs/ai_reference/INDEX.md

Runtime and continuity:

- sessions/README.md
- newest sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md

Recommended context docs:

- docs/ai_reference/ARCHITECTURE.md
- docs/ai_reference/TOPOLOGY.md
- docs/ai_reference/STARTUP_GUIDE.md
- docs/ai_reference/STARTUP_MODES.md

## Exclusion Policy

By default, skip large historical and backup content unless user requests deep archive read:

- docs/ai_reference/DEV_LOG_FULL.txt
- docs/devlog/archive/*
- backups/**

The startup summary must list exclusions used.

## Required Summary Format

Before implementation, assistant must provide:

1. Scope priority.
2. Uncommitted working set.
3. Verification snapshot status.
4. Read matrix status.
5. Exclusion list.
6. Commit policy status (ready/blocked).
7. Resource expenditure status (approved/not-needed/blocked).

If any item is missing, startup lock is incomplete.

## Startup Script Code (Copy/Paste)

The full script code is included here and also in scripts/maintenance for convenience.

### session_resume_guard.py

```python
#!/usr/bin/env python3
"""Generate a traceable session resume checkpoint with runtime evidence."""

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
    parser = argparse.ArgumentParser(description="Generate a timestamped session resume checkpoint")
    parser.add_argument("--reason", default="Chat restart checkpoint to prevent drift and preserve continuity.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default="sessions")
    parser.add_argument("--api-base", default="http://127.0.0.1:5000")
    parser.add_argument(
        "--check",
        action="append",
        default=[],
        help='Repeatable value: --check "name=/path" or --check "name=http://host/path"',
    )
    parser.add_argument("--skip-api", action="store_true")
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
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, exc.code, None, body[:300]
    except Exception as exc:
        return False, None, None, str(exc)


def parse_checks(raw_checks: list[str], api_base: str) -> list[tuple[str, str]]:
    if not raw_checks:
        return [("health", f"{api_base.rstrip('/')}/health")]

    checks: list[tuple[str, str]] = []
    for item in raw_checks:
        if "=" not in item:
            raise ValueError(f"Invalid --check value '{item}'.")
        name, target = item.split("=", 1)
        name = name.strip()
        target = target.strip()
        if not name:
            raise ValueError(f"Invalid --check value '{item}'. Name cannot be empty")
        if target.startswith("http://") or target.startswith("https://"):
            url = target
        else:
            path = target if target.startswith("/") else f"/{target}"
            url = f"{api_base.rstrip('/')}{path}"
        checks.append((name, url))
    return checks


def format_working_set(status_text: str) -> list[str]:
    lines = [line.rstrip("\r") for line in status_text.splitlines() if line.strip()]
    if not lines:
        return ["- Working tree clean"]

    mapped: list[str] = []
    for line in lines:
        match = re.match(r"^(..)[ ](.*)$", line)
        if not match:
            mapped.append(f"- {line}")
            continue
        code, path = match.group(1), match.group(2)
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


def build_api_snapshot(api_base: str, raw_checks: list[str], skip_api: bool) -> list[str]:
    if skip_api:
        return ["- API smoke checks skipped by flag."]

    checks = parse_checks(raw_checks, api_base)
    lines: list[str] = []
    for name, url in checks:
        ok, status, payload, err = http_get_json(url)
        if not ok:
            lines.append(f"- {name}: FAIL status={status} error={err}")
            continue

        details: list[str] = []
        if isinstance(payload, dict):
            for key in ("status", "count", "source", "season", "success"):
                if key in payload:
                    details.append(f"{key}={payload.get(key)}")

        suffix = " " + " ".join(details) if details else ""
        lines.append(f"- {name}: PASS status={status}{suffix}")

    return lines


def main() -> int:
    args = parse_args()
    repo_root = pathlib.Path(args.repo_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now()
    stamp = now.strftime("%Y-%m-%d_%H%M")
    out_path = output_dir / f"SESSION_RESUME_{stamp}.md"

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

    try:
        api_snapshot = build_api_snapshot(args.api_base, args.check, args.skip_api)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 2

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

    commit_lines = [line.strip() for line in commits.splitlines() if line.strip()]
    if commit_lines:
        content.extend([f"  - {line}" for line in commit_lines])
    else:
        content.append("  - (no commit data available)")

    content.extend(
        [
            "",
            "## Current Local Working Set (Uncommitted)",
            *format_working_set(status),
            "",
            "## Verification Snapshot (Runtime)",
            *api_snapshot,
            "",
            "## Non-Negotiable User Directives (Carry Forward)",
            "1. Primary scope: <set this for your project>.",
            "2. Secondary scope: <set this for your project>.",
            "3. No trust-by-claim: include runtime proof before completion claims.",
            "4. One objective at a time to prevent drift.",
            "",
            "## Next Chat Start Procedure",
            "1. Read this resume file first.",
            "2. Confirm scope lock before code changes.",
            "3. Run backend health snapshot before implementation.",
            "4. Complete one concrete objective with proof output.",
            "",
            "## Fast Resume Commands",
            "- git status --short",
            "- git log -3 --oneline --decorate",
            f"- {sys.executable} scripts/maintenance/session_resume_guard.py --reason \"Manual checkpoint refresh\"",
            "",
        ]
    )

    out_path.write_text("\n".join(content), encoding="utf-8")
    print(f"PASS: Session resume written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### session_resume_guard.ps1

```powershell
param(
    [string]$Reason = "Chat restart checkpoint to prevent drift and preserve continuity.",
    [string]$PythonExe = ".venv/Scripts/python.exe",
    [string]$ApiBase = "http://127.0.0.1:5000",
    [string[]]$Check,
    [switch]$SkipApi
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $repoRoot

function Resolve-PythonPath {
    param([string]$Candidate, [string]$Repo)

    if (Test-Path $Candidate) {
        return (Resolve-Path $Candidate).Path
    }

    $joined = Join-Path $Repo $Candidate
    if (Test-Path $joined) {
        return (Resolve-Path $joined).Path
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return $pythonCmd.Source
    }

    return $null
}

$pythonPath = Resolve-PythonPath -Candidate $PythonExe -Repo $repoRoot
if (-not $pythonPath) {
    Write-Host "FAIL: Python executable not found." -ForegroundColor Red
    Write-Host "Tried: $PythonExe and PATH lookup for 'python'" -ForegroundColor Red
    exit 2
}

$scriptPath = Join-Path $repoRoot "scripts/maintenance/session_resume_guard.py"
if (-not (Test-Path $scriptPath)) {
    Write-Host "FAIL: Guard script not found: $scriptPath" -ForegroundColor Red
    exit 2
}

$args = @(
    $scriptPath,
    "--reason", $Reason,
    "--api-base", $ApiBase
)

if ($SkipApi) {
    $args += "--skip-api"
}

if ($Check) {
    foreach ($entry in $Check) {
        $args += "--check"
        $args += $entry
    }
}

& $pythonPath @args
exit $LASTEXITCODE
```
