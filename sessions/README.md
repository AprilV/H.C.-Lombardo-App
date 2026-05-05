# Sessions Turnover Folder

This folder stores chat turnover and handoff markdown files.

## Required Location
- Place turnover files here: sessions/

## Required Naming Pattern
- SESSION_RESUME_YYYY-MM-DD_HHMM.md
- Use local date and 24-hour time in the filename.

## Required Format Reference
- Follow this reference structure:
  - docs/sessions/SESSION_RESUME_2026-04-24_CHAT_RESTART.md

## Traceability Rule
- Create a new file for each handoff.
- Do not overwrite previous turnover files.

## One-Command Session Guard (Recommended)
- Use this command at the start of any new chat or restart:
  - `./scripts/maintenance/session_resume_guard.ps1 -Reason "New chat startup checkpoint"`
- The command auto-generates `sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md` with:
  - current branch + recent commits
  - uncommitted working set
  - runtime API snapshot (`/health`, `/api/teams/count`, `/api/hcl/teams?season=2025`)
