# CHAT_STARTUP_LOCK (Execute Order 66 Portable Build Guide)

## Purpose
This is a complete, copy/paste build guide to add a startup lock protocol to any repository.

The startup lock exists to prevent chat drift at the beginning of each new conversation by forcing:
- fresh runtime evidence,
- a current git snapshot,
- required document reload,
- and an explicit lock summary before implementation.

If your assistant follows this document, typing `EXECUTE ORDER 66` should run a repeatable startup sequence every time.

## Audience
Use this guide if you are new to the process and need exact files, exact scripts, and exact setup steps.

## What You Will Create
You will create the following directories and files.

```text
docs/
  ai_reference/
	CHAT_STARTUP_LOCK.md
	READ_THIS_FIRST.md
	AI_EXECUTION_CONTRACT.md
	COMMIT_POLICY.md
	RESOURCE_EXPENDITURE_POLICY.md
	BEST_PRACTICES.md
	AI_VIOLATION_CHECKLIST.md
	INDEX.md
	STARTUP_GUIDE.md
	STARTUP_MODES.md
	ARCHITECTURE.md
	TOPOLOGY.md
sessions/
  README.md
scripts/
  maintenance/
	session_resume_guard.py
	session_resume_guard.ps1
.github/
  copilot-instructions.md   (or your agent instruction file)
```

## Trigger Phrases
Use any of these in chat:
- `EXECUTE ORDER 66`
- `RUN STARTUP LOCK`
- `LOOK AT CHAT_STARTUP_LOCK AND EXECUTE`

You can also trigger by explicitly referencing this file path.

## Step 1: Create Directories

Run from repository root.

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "docs/ai_reference" | Out-Null
New-Item -ItemType Directory -Force -Path "sessions" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts/maintenance" | Out-Null
New-Item -ItemType Directory -Force -Path ".github" | Out-Null
```

macOS/Linux shell:

```bash
mkdir -p docs/ai_reference sessions scripts/maintenance .github
```

## Step 2: Create Required Governance Documents

These files are read by the assistant before coding. Without them, startup lock should report blocked or incomplete.

### 2.1 Create docs/ai_reference/READ_THIS_FIRST.md
Why it exists:
- One-screen orientation for every new chat.
- Defines project mission, current priority, and failure conditions.

Template:

```md
# READ_THIS_FIRST

## Project Mission
Describe the product and the primary objective in 2-4 lines.

## Current Priority
1. Primary scope: <fill in>
2. Secondary scope: <fill in>

## Definition Of Done
- What must be true before a task is considered complete.

## Top Failure Modes To Avoid
1. <failure mode>
2. <failure mode>
3. <failure mode>

## Startup Sequence (Plain Language)
1. Run startup lock checkpoint script.
2. Read newest session resume.
3. Read required governance docs.
4. Return startup lock summary.
5. Begin implementation only after summary is accepted.
```

### 2.2 Create docs/ai_reference/AI_EXECUTION_CONTRACT.md
Why it exists:
- Non-negotiable operating rules.
- Defines safety boundaries and proof requirements.

Template:

```md
# AI_EXECUTION_CONTRACT

## Hard Rules
1. No destructive commands without explicit user approval.
2. No silent scope expansion.
3. No claim of completion without evidence.
4. If blocked, stop and explain blocker clearly.

## Change Control
- Read impacted files before editing.
- Keep edits minimal and scoped.
- Do not revert unrelated local changes.

## Evidence Requirements
- Provide command output summary for checks/tests run.
- Name exactly which files changed.
- Report what was not run and why.

## Escalation Rules
- If required files are missing, report and request approval to create.
- If runtime is unavailable, report current status and next safe action.
```

### 2.3 Create docs/ai_reference/COMMIT_POLICY.md
Why it exists:
- Prevents unauthorized or low-signal commits.
- Keeps commit scope and proof output consistent.

Template:

```md
# COMMIT_POLICY

## Non-Negotiable Rules
1. No auto-commit without explicit user approval.
2. No amend/rebase/reset/force-push without explicit user approval.
3. Stage only in-scope files.

## Pre-Commit Gate
- Scope complete for the requested objective.
- Staged files are in-scope.
- Verification evidence captured or skipped with reason.

## Post-Commit Reporting
- Commit hash
- Title
- Changed files summary
- Remaining working set
```

### 2.4 Create docs/ai_reference/RESOURCE_EXPENDITURE_POLICY.md
Why it exists:
- Prevents unapproved paid spend.
- Standardizes cost-aware decision making.

Template:

```md
# RESOURCE_EXPENDITURE_POLICY

## Default Stance
- Prefer zero-cost options first.
- Require approval before paid services or infrastructure.

## Cost Tiers (editable)
- Tier 0: $0 (allowed)
- Tier 1: $1-$99 (explicit approval)
- Tier 2: $100-$999 (approval + options)
- Tier 3: $1000+ (formal decision)

## Required Approval Package
1. Problem statement
2. Free alternatives considered
3. Cost estimate
4. Risks and lock-in
5. Exit strategy
```

### 2.5 Create docs/ai_reference/BEST_PRACTICES.md
Why it exists:
- Consistent execution quality.
- Standardizes coding, testing, and documentation behavior.

Template:

```md
# BEST_PRACTICES

## Coding
- Prefer small targeted changes.
- Preserve existing style.
- Avoid unrelated refactors.

## Validation
- Run smallest relevant checks first.
- Add or update tests for behavior changes.

## Git Hygiene
- Keep commits focused.
- Do not include unrelated files in task commits.

## Documentation
- Update docs when behavior or process changes.
- Keep runbooks executable and current.
```

### 2.6 Create docs/ai_reference/AI_VIOLATION_CHECKLIST.md
Why it exists:
- Fast pre-flight sanity check.
- Catches policy and process mistakes before they ship.

Template:

```md
# AI_VIOLATION_CHECKLIST

## Before Starting
- [ ] Required startup lock files exist.
- [ ] Startup lock summary has been produced.
- [ ] Scope priority is explicitly stated.

## Before Claiming Completion
- [ ] All requested requirements were handled.
- [ ] Evidence for verification is included.
- [ ] Unrun checks are explicitly listed.
- [ ] No unrelated files were changed.
```

### 2.7 Create docs/ai_reference/INDEX.md
Why it exists:
- Single source of truth for document order and ownership.

Template:

```md
# AI Reference Index

## Required Read Order
1. READ_THIS_FIRST.md
2. AI_EXECUTION_CONTRACT.md
3. COMMIT_POLICY.md
4. RESOURCE_EXPENDITURE_POLICY.md
5. BEST_PRACTICES.md
6. AI_VIOLATION_CHECKLIST.md
7. INDEX.md

## Supporting Context
- ARCHITECTURE.md
- TOPOLOGY.md
- STARTUP_MODES.md
- STARTUP_GUIDE.md

## Ownership
- Owner: <name>
- Last updated: <YYYY-MM-DD>
```

## Step 3: Create Startup Continuity Documents

### 3.1 Create sessions/README.md
Why it exists:
- Prevents handoff ambiguity.
- Enforces naming convention and traceability.

Template:

```md
# Sessions Folder Guide

## Purpose
Stores session handoff checkpoints generated by startup lock.

## Naming Convention
Use: SESSION_RESUME_YYYY-MM-DD_HHMM.md

Examples:
- SESSION_RESUME_2026-05-12_0953.md
- SESSION_RESUME_2026-05-13_1410.md

## Rules
1. Never overwrite old session resume files.
2. Always create a new timestamped file.
3. New chat starts by reading the newest file.

## How To Generate
PowerShell:
./scripts/maintenance/session_resume_guard.ps1 -Reason "New chat startup checkpoint"
```

### 3.2 Keep this file as the master trigger doc
File: `docs/ai_reference/CHAT_STARTUP_LOCK.md`

Why it exists:
- Defines trigger phrases and exact startup protocol.
- Serves as the portable runbook you are reading now.

## Step 4: Create Startup Checkpoint Scripts

These two files are the operational core.

- `scripts/maintenance/session_resume_guard.py`: builds runtime checkpoint evidence and writes session resume markdown.
- `scripts/maintenance/session_resume_guard.ps1`: stable wrapper for Windows users and chat-trigger calls.

### 4.1 Create scripts/maintenance/session_resume_guard.py

Copy this full file:

```python
#!/usr/bin/env python3
"""Generate a traceable session resume checkpoint with runtime evidence.

Creates sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md and captures:
- current git branch / recent commits / working set
- optional API smoke checks
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
		"--check",
		action="append",
		default=[],
		help='Optional repeated checks: --check "name=/path" or --check "name=http://host/path"',
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


def parse_checks(raw_checks: list[str], api_base: str) -> list[tuple[str, str]]:
	if not raw_checks:
		return [("health", f"{api_base.rstrip('/')}/health")]

	checks: list[tuple[str, str]] = []
	for item in raw_checks:
		if "=" not in item:
			raise ValueError(
				f"Invalid --check value '{item}'. Use name=/path or name=http://host/path"
			)
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

		detail = []
		if isinstance(payload, dict):
			for key in ("status", "count", "source", "season", "success"):
				if key in payload:
					detail.append(f"{key}={payload.get(key)}")

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
	try:
		api_snapshot_lines = build_api_snapshot(args.api_base, args.check, args.skip_api)
	except ValueError as e:
		print(f"FAIL: {e}")
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
	])

	out_path.write_text("\n".join(content), encoding="utf-8")
	print(f"PASS: Session resume written: {out_path}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
```

### 4.2 Create scripts/maintenance/session_resume_guard.ps1

Copy this full file:

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

## Step 5: Wire Trigger Behavior Into Agent Instructions

Edit your agent instruction file (usually `.github/copilot-instructions.md`) and add this block.

Why this is required:
- The scripts only generate evidence.
- This instruction block tells the assistant exactly when and how to execute startup lock.

Copy/paste block:

```md
## Single-Line Drift Reset Trigger
If the user message includes `EXECUTE ORDER 66` OR `RUN STARTUP LOCK` OR `LOOK AT CHAT_STARTUP_LOCK AND EXECUTE` OR references `docs/ai_reference/CHAT_STARTUP_LOCK.md`, execute this protocol immediately before any other work:
1. Run `./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"`.
2. Read the newest `sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md` file.
3. Re-read the startup lock read matrix.
4. Return a startup lock summary before implementation with:
   - current scope priority
   - current uncommitted working set
   - verification snapshot status
   - read matrix status (complete/blocked)
   - explicit exclusion list
```

## Step 6: Define Your Read Matrix

A read matrix is the exact list of docs the assistant must read during startup lock.

Why this matters:
- Without a fixed matrix, startup quality drifts by session and by model.

Minimum read matrix:
- `docs/ai_reference/READ_THIS_FIRST.md`
- `docs/ai_reference/AI_EXECUTION_CONTRACT.md`
- `docs/ai_reference/COMMIT_POLICY.md`
- `docs/ai_reference/RESOURCE_EXPENDITURE_POLICY.md`
- `docs/ai_reference/BEST_PRACTICES.md`
- `docs/ai_reference/AI_VIOLATION_CHECKLIST.md`
- `docs/ai_reference/INDEX.md`
- `sessions/README.md`
- newest `sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md`

Recommended contextual docs when they exist:
- `docs/ai_reference/ARCHITECTURE.md`
- `docs/ai_reference/TOPOLOGY.md`
- `docs/ai_reference/STARTUP_MODES.md`
- `docs/ai_reference/STARTUP_GUIDE.md`

## Step 7: Set Exclusion Policy

Exclude these by default unless user asks for deep archive reading:
- `docs/ai_reference/DEV_LOG_FULL.txt`
- `docs/devlog/archive/*`
- `backups/**`

Why this exists:
- Prevents token waste and irrelevant context pollution.
- Keeps startup lock deterministic and fast.

## Step 8: First Execution Test (No Code Changes)

Run from repository root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
```

Find newest resume:

```powershell
Get-ChildItem sessions -Filter "SESSION_RESUME_*.md" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 -ExpandProperty FullName
```

Expected result:
- command prints `PASS: Session resume written: ...`
- new file appears in `sessions/`
- file contains git snapshot and verification snapshot sections.

## Step 9: Required Startup Lock Summary Format

When trigger phrase is used, assistant summary must include all items below before coding:

1. Current scope priority.
2. Current uncommitted working set.
3. Verification snapshot status.
4. Read matrix status (complete or blocked).
5. Explicit exclusion list used.

If any item is missing, startup lock is incomplete.

## Step 10: Porting Checklist For Another Project

Use this checklist in order:

1. Copy this file to `docs/ai_reference/CHAT_STARTUP_LOCK.md`.
2. Create all required governance docs from templates in Step 2.
3. Create `sessions/README.md` from Step 3.
4. Create both guard scripts from Step 4.
5. Add trigger block to `.github/copilot-instructions.md` (Step 5).
6. Define your project read matrix (Step 6).
7. Keep exclusions explicit (Step 7).
8. Run the first execution test (Step 8).
9. Verify startup summary includes all required fields (Step 9).

## Troubleshooting

### Error: running scripts is disabled on this system
Use process-scope bypass only for current shell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

### Error: Python executable not found
Run with explicit interpreter path:

```powershell
./scripts/maintenance/session_resume_guard.ps1 -PythonExe "C:/Path/To/python.exe" -Reason "Startup lock trigger"
```

### Error: git branch not detected
Make sure command is run from inside a git repository root.

### API checks fail
This is allowed if API is currently down. The resume should record FAIL evidence.
If you want startup lock without runtime probes, pass `-SkipApi`.

## Final Notes
- This process is intentionally strict.
- Startup lock is complete only after the summary is returned.
- Implementation starts only after startup lock is complete.
