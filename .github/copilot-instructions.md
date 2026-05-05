# Workspace Copilot Instructions

## Session Turnover Location And Naming
- Turnover and handoff markdown files must be stored in the top-level sessions folder: sessions/
- For each new chat restart or handoff, create a new timestamped turnover file in sessions/.
- Use this filename pattern with date plus time: SESSION_RESUME_YYYY-MM-DD_HHMM.md
- Example: SESSION_RESUME_2026-04-27_1540.md

## Turnover Format Reference
- Use docs/sessions/SESSION_RESUME_2026-04-24_CHAT_RESTART.md as the structure and content-quality reference.
- Preserve the same section style and execution-ready detail level.
- Update all sections with current, verifiable state instead of copying stale values.

## Traceability Requirement
- Never overwrite a previous turnover file.
- Always create a new timestamped file so each handoff remains traceable.

## Mandatory New-Chat Startup Guard
- At the start of every new chat or restart, run:
	- `./scripts/maintenance/session_resume_guard.ps1 -Reason "New chat startup checkpoint"`
- This command must run before implementation work so startup state is evidence-backed and drift-resistant.
- After running the command, read the newest file in `sessions/` matching `SESSION_RESUME_YYYY-MM-DD_HHMM.md`.
- Before implementation, provide a brief startup lock summary that includes:
	- current scope priority (app-first vs dashboard)
	- current uncommitted working set
	- verification snapshot status

## Full-Scope Startup Lock Read Matrix (Required)
- Read all files in this matrix before implementation unless listed under explicit exclusions.

Core governance (always):
- `docs/ai_reference/READ_THIS_FIRST.md`
- `docs/ai_reference/AI_EXECUTION_CONTRACT.md`
- `docs/ai_reference/BEST_PRACTICES.md`
- `docs/ai_reference/AI_VIOLATION_CHECKLIST.md`
- `docs/ai_reference/INDEX.md`

App and architecture context (always):
- `CLAUDE.md`
- `README.md`
- `docs/ai_reference/ARCHITECTURE.md`
- `docs/ai_reference/TOPOLOGY.md`
- `docs/ai_reference/STARTUP_MODES.md`
- `docs/ai_reference/STARTUP_GUIDE.md`

Dashboard governance and operating context (always):
- `docs/DASHBOARD_UPDATE_GUIDE.md`
- `docs/SPRINT_EXECUTION_PROCESS.md`
- `docs/dashboard_product/README.md`
- `docs/dashboard_product/DASHBOARD_CHARTER.md`
- `docs/dashboard_product/DASHBOARD_BACKLOG.md`
- `docs/dashboard_product/DASHBOARD_RELEASE_NOTES.md`
- `docs/dashboard_product/DASHBOARD_OPERATING_SOP.md`
- `docs/dashboard_product/DASHBOARD_DATA_OWNERSHIP.md`
- `docs/dashboard_product/DASHBOARD_METRICS.md`
- `docs/dashboard_product/DASHBOARD_SPRINT_ROLLOVER_AUTOMATION_RUNBOOK.md`

Dashboard automation phase context (always):
- `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE0_KICKOFF.md`
- `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE1_COVERAGE_MODEL.md`
- `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE2_MIGRATION_VALIDATION.md`
- `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE3_API_PERSISTENCE.md`
- `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE4_FRONTEND_PERSISTED_WIRING.md`
- `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE5_AUTOSYNC_METRICS_CHARTS.md`

Domain docs (required when touching matching domain):
- `docs/ai_reference/LIVE_SCORE_SETUP.md`
- `docs/ai_reference/NFL_SPREAD_BETTING_GUIDE.md`
- `docs/ai_reference/PREDICTION_TRACKING_SYSTEM.md`
- `docs/ai_reference/QUICK_START_HCL.md`

Turnover continuity (always):
- `sessions/README.md`
- Newest `sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md`

Explicit exclusions unless user explicitly requests archive deep-read:
- `docs/ai_reference/DEV_LOG_FULL.txt` (large historical archive)
- `docs/devlog/archive/*` (historical logs)
- `backups/**` (recovery artifacts; read only for restore/debug tasks)
- If exclusions are used, startup lock summary must name each excluded path class and why it was excluded.

## Single-Line Drift Reset Trigger
- If the user message includes `RUN STARTUP LOCK` OR `LOOK AT CHAT_STARTUP_LOCK AND EXECUTE` OR references `docs/ai_reference/CHAT_STARTUP_LOCK.md`, execute this protocol immediately before any other work:
	1. Run `./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"`.
	2. Read the newest `sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md` file.
	3. Re-read the Full-Scope Startup Lock Read Matrix above (excluding only explicit archive exclusions unless user requests otherwise).
	4. Return a startup lock summary before implementation with:
		- current scope priority (app-first vs dashboard)
		- current uncommitted working set
		- verification snapshot status
		- read matrix status (complete/blocked)
		- explicit exclusion list used for this startup lock
