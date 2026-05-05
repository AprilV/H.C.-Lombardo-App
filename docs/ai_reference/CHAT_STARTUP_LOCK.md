# CHAT_STARTUP_LOCK

## Purpose
One-line anti-drift trigger for any chat. Use this when you want protocol lock before implementation.

## What To Type In Chat
RUN STARTUP LOCK

or

LOOK AT CHAT_STARTUP_LOCK AND EXECUTE

Alternative trigger:
- Reference this file directly: `docs/ai_reference/CHAT_STARTUP_LOCK.md`

## Required Assistant Behavior After Trigger
1. Run:
   - `./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"`
2. Read the newest `sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md` file.
3. Re-read the full startup lock matrix before coding:
   - Core governance (always):
     - `docs/ai_reference/READ_THIS_FIRST.md`
     - `docs/ai_reference/AI_EXECUTION_CONTRACT.md`
     - `docs/ai_reference/BEST_PRACTICES.md`
     - `docs/ai_reference/AI_VIOLATION_CHECKLIST.md`
     - `docs/ai_reference/INDEX.md`
   - App and architecture context (always):
     - `CLAUDE.md`
     - `README.md`
     - `docs/ai_reference/ARCHITECTURE.md`
     - `docs/ai_reference/TOPOLOGY.md`
     - `docs/ai_reference/STARTUP_MODES.md`
     - `docs/ai_reference/STARTUP_GUIDE.md`
   - Dashboard governance and operating context (always):
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
   - Dashboard automation phase context (always):
     - `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE0_KICKOFF.md`
     - `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE1_COVERAGE_MODEL.md`
     - `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE2_MIGRATION_VALIDATION.md`
     - `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE3_API_PERSISTENCE.md`
     - `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE4_FRONTEND_PERSISTED_WIRING.md`
     - `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE5_AUTOSYNC_METRICS_CHARTS.md`
   - Domain docs (required when touching matching domain):
     - `docs/ai_reference/LIVE_SCORE_SETUP.md`
     - `docs/ai_reference/NFL_SPREAD_BETTING_GUIDE.md`
     - `docs/ai_reference/PREDICTION_TRACKING_SYSTEM.md`
     - `docs/ai_reference/QUICK_START_HCL.md`
   - Turnover continuity (always):
     - `sessions/README.md`
4. Explicit exclusions unless user requests archive deep-read:
   - `docs/ai_reference/DEV_LOG_FULL.txt` (large historical archive)
   - `docs/devlog/archive/*` (historical logs)
   - `backups/**` (restore/debug only)
5. Return a startup lock summary before coding:
   - current scope priority (app-first vs dashboard)
   - current uncommitted working set
   - verification snapshot status
   - read matrix status (complete/blocked)
   - explicit exclusion list used for this startup lock

## Scope Rule
- App is primary delivery scope.
- Dashboard is secondary and must remain accurate for stakeholder/professor reporting.
