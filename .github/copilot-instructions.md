# Workspace Copilot Instructions

## Session Turnover Naming

- Store turnover files in sessions/
- Filename format: SESSION_RESUME_YYYY-MM-DD_HHMM.md
- Never overwrite previous turnover files

## Mandatory Startup Guard

At start of every new chat or restart:

- Run ./scripts/maintenance/session_resume_guard.ps1 -Reason "New chat startup checkpoint"
- Read newest sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md
- Return startup lock summary before implementation with:
  - workstream scope
  - current uncommitted working set
  - verification snapshot status

## Startup Read Set (Current Only)

Read these current references before implementation:

1. CODEX_START_HERE.md
2. docs/DEPLOY_AND_ARCHITECTURE.md
3. docs/DASHBOARD_UPDATE_GUIDE.md (only when touching dashboard scope)

Do not treat historical/archive docs as current startup requirements.

## Single-Line Drift Reset Trigger (Order 66)

If user message includes EXECUTE ORDER 66, RUN STARTUP LOCK, LOOK AT CHAT_STARTUP_LOCK AND EXECUTE, or references docs/ai_reference/CHAT_STARTUP_LOCK.md:

1. Run ./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
2. Read newest sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md
3. Read startup read set listed above
4. Report startup lock summary before implementation with:
   - workstream scope
   - current uncommitted working set
   - verification snapshot status
   - read-set status (complete/blocked)

## Report-Back Requirement (Every Task)

End each task with:

1. Files changed
2. What was done (plain summary)
3. Proof output (commands/results)
4. What was not touched (out-of-scope confirmation)
5. Any uncertainty that needs user confirmation
