# Startup Lock Starter Pack

This folder is a copy-ready package for adding Execute Order 66 startup lock to another repository.

This package is documentation and scripts only.

- No installs required.
- No server changes required.
- No dependency changes required.

## What Is Included

```text
docs/ai_reference/
  CHAT_STARTUP_LOCK.md
  READ_THIS_FIRST.md
  AI_EXECUTION_CONTRACT.md
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
```

## Quick Port Steps

1. Copy this folder's contents into the target repo root.
2. Merge the `Single-Line Drift Reset Trigger` section from `.github/copilot-instructions.md` into the target repo instruction file.
3. Update placeholders in `docs/ai_reference/READ_THIS_FIRST.md` and `docs/ai_reference/AI_EXECUTION_CONTRACT.md`.
4. Run the checkpoint script once:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
```

5. Confirm a file is created in `sessions/` named `SESSION_RESUME_YYYY-MM-DD_HHMM.md`.

## Expected Outcome

After trigger phrase `EXECUTE ORDER 66`, your assistant should:

1. Run startup checkpoint script.
2. Read newest `sessions/SESSION_RESUME_*.md`.
3. Read required doc matrix.
4. Return startup lock summary before implementation.
