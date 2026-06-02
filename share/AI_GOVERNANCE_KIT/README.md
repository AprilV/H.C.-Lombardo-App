# Portable AI Governance Kit

This folder is a copy-ready, project-agnostic governance system for AI coding sessions.

Core capability:
- Startup drift prevention via Execute Order 66 startup lock.
- Repeatable session continuity via checkpoint resumes.
- Explicit commit-control and resource-expenditure guardrails.

This pack is docs + scripts only.

## Included Structure

```text
docs/ai_reference/
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
scripts/maintenance/
  session_resume_guard.py
  session_resume_guard.ps1
sessions/
  README.md
.github/
  copilot-instructions.md
CHAT_STARTUP_LOCK.md
PORTING_CHECKLIST.md
```

## One-Time Port Steps (Any Repository)

1. Copy this folder's contents into the target repository root.
2. Merge startup trigger content from `.github/copilot-instructions.md` into the target repo instruction file.
3. Fill placeholders in:
   - `docs/ai_reference/READ_THIS_FIRST.md`
   - `docs/ai_reference/ARCHITECTURE.md`
   - `docs/ai_reference/TOPOLOGY.md`
4. Optionally tune policy thresholds in:
   - `docs/ai_reference/COMMIT_POLICY.md`
   - `docs/ai_reference/RESOURCE_EXPENDITURE_POLICY.md`
5. Run first checkpoint:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
```

6. Confirm a file exists in `sessions/` with pattern `SESSION_RESUME_YYYY-MM-DD_HHMM.md`.

## Execute Order 66 Outcome

When the trigger phrase is used, the assistant should:

1. Run checkpoint guard script.
2. Read newest `sessions/SESSION_RESUME_*.md`.
3. Re-read required governance matrix.
4. Return startup lock summary before implementation.
5. Enforce commit and resource policy constraints during execution.
