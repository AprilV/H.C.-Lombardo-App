# Copilot Startup Lock Snippet

Merge this section into your repository instruction file.

## Session Turnover Requirements
- Store handoff files in `sessions/`.
- Use filename pattern `SESSION_RESUME_YYYY-MM-DD_HHMM.md`.
- Never overwrite prior session files.

## Mandatory New-Chat Startup Guard
At start of every new chat or restart:

1. Run `./scripts/maintenance/session_resume_guard.ps1 -Reason "New chat startup checkpoint"`.
2. Read newest file in `sessions/` matching `SESSION_RESUME_YYYY-MM-DD_HHMM.md`.
3. Return startup lock summary before implementation.

## Single-Line Drift Reset Trigger
If user message includes `EXECUTE ORDER 66` OR `RUN STARTUP LOCK` OR `LOOK AT CHAT_STARTUP_LOCK AND EXECUTE` OR references `docs/ai_reference/CHAT_STARTUP_LOCK.md`, run this protocol before any other work:

1. Run `./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"`.
2. Read newest `sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md`.
3. Re-read startup matrix documents:
   - `docs/ai_reference/READ_THIS_FIRST.md`
   - `docs/ai_reference/AI_EXECUTION_CONTRACT.md`
   - `docs/ai_reference/COMMIT_POLICY.md`
   - `docs/ai_reference/RESOURCE_EXPENDITURE_POLICY.md`
   - `docs/ai_reference/BEST_PRACTICES.md`
   - `docs/ai_reference/AI_VIOLATION_CHECKLIST.md`
   - `docs/ai_reference/INDEX.md`
   - `sessions/README.md`
4. Return startup lock summary before implementation with:
   - current scope priority
   - current uncommitted working set
   - verification snapshot status
   - read matrix status (complete or blocked)
   - explicit exclusion list used
   - commit policy status (ready/blocked)
   - resource expenditure status (approved/not-needed/blocked)

## Exclusions Unless User Requests Deep Archive Read
- `docs/ai_reference/DEV_LOG_FULL.txt`
- `docs/devlog/archive/*`
- `backups/**`
