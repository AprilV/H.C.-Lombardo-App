# Session Resume Note - 2026-04-27 1743

## Reason
User requested a hard-process turnover that prevents repeated reset/re-explanation across new chats.
This handoff captures a reusable execution model for PM Forge + H.C. app work, plus a point-in-time snapshot of active sprint/ticket state.

## Non-Negotiable Startup Checklist (Use At Start Of Every New Chat)
Do not implement code until all items are explicitly completed in-chat:
1. Confirm active scope from PM Forge source-of-truth, do not assume prior chat scope:
  - identify active sprint from dashboard state
  - identify active TA ticket and approved subtask ID
  - identify scope boundary (app, dashboard, backend, or mixed)
2. Read required docs in full and state they were read:
  - docs/ai_reference/AI_EXECUTION_CONTRACT.md
  - docs/ai_reference/READ_THIS_FIRST.md
  - docs/ai_reference/BEST_PRACTICES.md
  - docs/ai_reference/AI_VIOLATION_CHECKLIST.md
3. Read PM Forge operating docs and state they were read:
  - docs/DASHBOARD_UPDATE_GUIDE.md
  - docs/SPRINT_EXECUTION_PROCESS.md
  - docs/sprints/AGILE_PROCESS.md
  - docs/dashboard_product/DASHBOARD_OPERATING_SOP.md
  - docs/dashboard_product/DASHBOARD_DATA_OWNERSHIP.md
4. Read app-context docs and state they were read:
  - CLAUDE.md
  - README.md
  - docs/ai_reference/ARCHITECTURE.md
5. Confirm working rule: one approved subtask at a time, no batching.
6. Confirm evidence rule: local timestamps and in-file evidence first, git second.
7. Confirm dashboard update rule after each completed subtask:
  - update COMPLETED_TASKS
  - update TASK_DETAILS with resolution/date/timestamp/updatedBy
  - align PB_ITEMS status if needed
  - validate chart/metric consistency
8. Name the single next subtask ID before editing.
9. Ask for explicit approval to execute that one subtask.
10. After completion, stop and request confirmation before moving to the next subtask.

## Accountability And Violation Gate
If any startup checklist item is skipped, execution must stop.
Trigger phrase for correction: Violation detected - Stop, reassess, and resume only after checklist completion.

## Required Read Matrix (No Skimming)
AI accountability and contract:
- docs/ai_reference/AI_EXECUTION_CONTRACT.md
- docs/ai_reference/READ_THIS_FIRST.md
- docs/ai_reference/BEST_PRACTICES.md
- docs/ai_reference/AI_VIOLATION_CHECKLIST.md

PM Forge process and dashboard source-of-truth:
- docs/DASHBOARD_UPDATE_GUIDE.md
- docs/SPRINT_EXECUTION_PROCESS.md
- docs/sprints/AGILE_PROCESS.md
- docs/dashboard_product/README.md
- docs/dashboard_product/DASHBOARD_CHARTER.md
- docs/dashboard_product/DASHBOARD_BACKLOG.md
- docs/dashboard_product/DASHBOARD_RELEASE_NOTES.md
- docs/dashboard_product/DASHBOARD_OPERATING_SOP.md
- docs/dashboard_product/DASHBOARD_DATA_OWNERSHIP.md
- docs/dashboard_product/DASHBOARD_METRICS.md

H.C. app context and architecture:
- CLAUDE.md
- README.md
- docs/ai_reference/ARCHITECTURE.md

Turnover format and traceability:
- docs/sessions/SESSION_RESUME_2026-04-24_CHAT_RESTART.md
- sessions/README.md

## Current Git State
- Branch: master
- HEAD: e77c0a41
- HEAD message: Dashboard charts: render sprint burndown by workdays (exclude weekends)
- Snapshot time: 2026-04-27 17:43:19
- Working tree is dirty with many existing modified/untracked files.
- Files changed in this chat:
  - frontend/src/GameStatistics.js
  - pmforge_dashboard/index.html

## What Was In Progress
1. User clarified execution policy:
   - Keep work under TA-059.
   - Update dashboard after each completed subtask/task.
   - Discuss and confirm before moving to unrelated/new topic work.
2. App-scope season cleanup was started one subtask at a time.
3. Subtask completed in this chat:
   - TA-059 s59_6 (GameStatistics app season hardcode cleanup).

## Verification Snapshot
- frontend/src/GameStatistics.js now uses shared season utility:
  - import getDefaultSeason, MIN_NFL_SEASON
  - defaults use String(currentSeason)
  - season loop uses currentSeason..MIN_NFL_SEASON
  - subtitle range uses dynamic values
- Hardcoded 2025 check in GameStatistics: none found.
- pmforge_dashboard/index.html updated under TA-059:
  - Added s59_6, s59_7, s59_8 app subtasks in Sprint 13 board.
  - Added s59_6 to COMPLETED_TASKS.
  - Added TASK_DETAILS entry for s59_6 with resolution/date/timestamp/updatedBy.
- Editor diagnostics:
  - No errors in frontend/src/GameStatistics.js.
  - No errors in pmforge_dashboard/index.html.

## Important Process Notes
Mandatory behavior for next chats:
1. Read required docs in full before implementation:
   - docs/ai_reference/AI_EXECUTION_CONTRACT.md
   - docs/ai_reference/READ_THIS_FIRST.md
   - docs/ai_reference/BEST_PRACTICES.md
   - docs/ai_reference/AI_VIOLATION_CHECKLIST.md
2. Use PM Forge as operational control plane for the currently active sprint.
3. Execute one approved subtask at a time (no batching).
4. After each completed subtask, update dashboard source-of-truth immediately:
   - COMPLETED_TASKS
   - TASK_DETAILS (resolution, date, timestamp, updatedBy)
   - PB_ITEMS status alignment (if ticket status changes)
   - Sprint/charts/metrics consistency checks per docs
5. Use local file timestamp/code evidence first; git history is secondary corroboration only.
6. Respect scope boundary set by user for the current run (app/dashboard/backend) and do not silently expand scope.
7. Before moving to next subtask, get explicit user confirmation.
8. Before switching to a new workstream (example: broader ML work), discuss first.

## Scope Transition Rule (Sprint And TA Can Change)
This file is not a permanent lock to Sprint 13 or TA-059.
At each new chat start:
1. Re-identify active sprint and active TA from PM Forge.
2. Confirm with user which ticket/subtask is next.
3. Proceed only on that approved subtask.

Current snapshot in this turnover is historical context, not a fixed forever scope.

## Current TA-059 State (Sprint 13)
Defined TA-059 subtasks now include backend + app cleanup:
- Existing backend set: s59_1, s59_2, s59_3, s59_4, s59_5
- Added app set: s59_6, s59_7, s59_8

Completion status:
- Done: s59_1, s59_2, s59_3, s59_4, s59_6
- Pending: s59_5, s59_7, s59_8

## Next Subtask Queue (One At A Time)
1. s59_7: App cleanup for frontend/src/TeamComparison.js (remove hardcoded season defaults/range)
2. s59_8: App cleanup for frontend/src/HistoricalData.js (remove hardcoded season range text/loop)
3. s59_5: Endpoint verification for current season data (timestamp-first evidence)

## User Escalation Context (Sanitized)
User emphasized repeated chat resets caused significant time loss and asked for a strict, reusable handoff process with no skimming, no assumptions, and contract-aligned execution tied to PM Forge Sprint 13 TA workflow.

## Copy-Paste Kickoff Prompt For Next Chat
Read the required AI contract documents and PM Forge process docs in full before any code action. Then identify the currently active sprint and approved TA/subtask from PM Forge source-of-truth and confirm it with me. Execute one approved subtask at a time with no batching. After each completed subtask, immediately update pmforge_dashboard/index.html source-of-truth (COMPLETED_TASKS, TASK_DETAILS with resolution/date/timestamp/updatedBy, PB_ITEMS alignment when needed, and chart/metric consistency checks). Use local timestamp and in-file evidence first and treat git history as secondary corroboration. Stop after each completed subtask and ask for approval before moving to the next. Do not expand scope without discussion.

## Handoff File Policy
- Turnover files live in sessions/
- Naming pattern: SESSION_RESUME_YYYY-MM-DD_HHMM.md
- Never overwrite prior handoff files
- Use docs/sessions/SESSION_RESUME_2026-04-24_CHAT_RESTART.md as structure reference

## Safe Resume Commands
- Check current TA-059 board block quickly:
  - Select-String -Path pmforge_dashboard/index.html -Pattern 'TA-059|s59_6|s59_7|s59_8'
- Check app hardcoded season literals quickly:
  - Select-String -Path frontend/src/GameStatistics.js,frontend/src/TeamComparison.js,frontend/src/HistoricalData.js -Pattern '2025|1999-2025|for \(let year = 2025|useState\(''2025''\)' -CaseSensitive:$false
- Verify local modified times for target files:
  - Get-Item frontend/src/GameStatistics.js,frontend/src/TeamComparison.js,frontend/src/HistoricalData.js,pmforge_dashboard/index.html | Select-Object LastWriteTime,FullName
