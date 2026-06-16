# Session Resume Note - 2026-05-26 1153

## Reason
Startup lock trigger

## Current Git State Snapshot
- Branch: master
- Latest commits:
  - a7c2a05e (HEAD -> master, origin/master) Dashboard/devlog: add TA-079 and session continuity records
  - 2fa6ccfa TA-078: persist tuning artifacts and calibrated week 18 outputs
  - 65a6cc22 TA-078: add targeted week and high-spread diagnostics

## Current Local Working Set (Uncommitted)
- Modified: api_routes_ml.py
- Modified: docs/devlog/archive/2026-05-20.json
- Modified: docs/devlog/archive/index.json
- Modified: frontend/src/ModelPerformance.css
- Modified: pmforge_dashboard/index.html
- Deleted: share/startup-lock-starter-pack/.github/copilot-instructions.md
- Deleted: share/startup-lock-starter-pack/CHAT_STARTUP_LOCK.md
- Deleted: share/startup-lock-starter-pack/README.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/AI_EXECUTION_CONTRACT.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/AI_VIOLATION_CHECKLIST.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/ARCHITECTURE.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/BEST_PRACTICES.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/CHAT_STARTUP_LOCK.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/INDEX.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/READ_THIS_FIRST.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/STARTUP_GUIDE.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/STARTUP_MODES.md
- Deleted: share/startup-lock-starter-pack/docs/ai_reference/TOPOLOGY.md
- Deleted: share/startup-lock-starter-pack/scripts/maintenance/session_resume_guard.ps1
- Deleted: share/startup-lock-starter-pack/scripts/maintenance/session_resume_guard.py
- Deleted: share/startup-lock-starter-pack/sessions/README.md
- Untracked: .deploy-worktree/
- Untracked: .git_remaining_report.txt
- Untracked: docs/devlog/archive/2026-05-21.json
- Untracked: docs/sprints/phase4_weekly_ops/historical_recalc_20260521_134623.json
- Untracked: docs/sprints/ta076_reliability_data/
- Untracked: docs/sprints/ta077_multi_season_eval/ta077_step1_lock/
- Untracked: docs/sprints/ta077_multi_season_eval/ta077_step2_metrics/
- Untracked: docs/sprints/ta077_multi_season_eval/ta077_step3_guardrails/
- Untracked: docs/sprints/ta077_multi_season_eval/ta077_step4_plan/
- Untracked: docs/sprints/ta077_multi_season_eval/ta077_step5_evidence_pack/
- Untracked: docs/sprints/ta077_multi_season_eval/ta077_step6_decision/
- Untracked: frontend/.env.development
- Untracked: frontend/frontend_build_upload_posix_v2.zip
- Untracked: frontend/frontend_build_upload_posix_v3.zip
- Untracked: frontend/index.html
- Untracked: frontend/main.js
- Untracked: frontend_build_upload.zip
- Untracked: frontend_build_upload_posix.zip
- Untracked: frontend_build_upload_posix_live_20260516.zip
- Untracked: frontend_build_upload_posix_live_20260516_v2.zip
- Untracked: frontend_build_upload_posix_live_current.zip
- Untracked: frontend_build_upload_posix_v3.zip
- Untracked: scripts/maintenance/recalculate_historical_predictions.py
- Untracked: sessions/SESSION_RESUME_2026-05-20_1144.md
- Untracked: sessions/SESSION_RESUME_2026-05-26_1112.md
- Untracked: share/AI_GOVERNANCE_KIT/
- Untracked: task_script.py
- Untracked: temp_js_extract/

## Verification Snapshot (Runtime)
- health: FAIL status=None error=<urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- teams_count: FAIL status=None error=<urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- hcl_teams_2025: FAIL status=None error=<urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>

## Non-Negotiable User Directives (Carry Forward)
1. App is primary project scope.
2. Dashboard is secondary but must stay accurate for stakeholder/professor review.
3. No trust-by-claim: include runtime proof before completion claims.
4. One objective at a time to prevent drift.

## Next Chat Start Procedure
1. Read this resume file first.
2. Confirm scope lock (app-first unless user explicitly selects dashboard work).
3. Run backend health snapshot before code changes.
4. Complete one concrete fix with proof output before moving on.

## Fast Resume Commands
- git status --short
- git log -3 --oneline --decorate
- C:\ReactGitEC2\IS330\H.C Lombardo App\.venv\Scripts\python.exe scripts/maintenance/session_resume_guard.py --reason "Manual checkpoint refresh"
