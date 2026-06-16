# Session Resume Note - 2026-05-20 0954

## Reason
Crash-safe handover for next chat

## Current Git State Snapshot
- Branch: master
- Latest commits:
  - 949394cc (HEAD -> master, origin/master) Close TA-026 with mobile responsiveness hardening
  - 5b6cd9c1 Set TA-078 priority to Critical
  - 71f19c0c Push app and PM dashboard updates

## Current Local Working Set (Uncommitted)
- Modified: docs/ai_reference/WEEKLY_ML_PIPELINE_RUNBOOK.md
- Modified: docs/devlog/archive/2026-05-18.json
- Modified: docs/devlog/archive/index.json
- Modified: ml/predict_week.py
- Modified: ml/predictions_week_18.json
- Modified: pmforge_dashboard/index.html
- Modified: scripts/maintenance/weekly_ml_pipeline.py
- Untracked: .deploy-worktree/
- Untracked: .git_remaining_report.txt
- Untracked: docs/devlog/archive/2026-05-19.json
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_213343.json
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_213343.md
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_213414.json
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_213414.md
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_213429.json
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_213429.md
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_214812.json
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_214812.md
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_220813.json
- Untracked: docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_220813.md
- Untracked: docs/sprints/ta078_vegas_tuning/
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
- Untracked: scripts/verification/ta078_vegas_gap_tuning.py
- Untracked: sessions/SESSION_RESUME_2026-05-19_1349.md
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

## What Was In Progress At Crash Time
- TA-078 hardening was actively extended from aggregate-only tuning into diagnostic-rich evidence output.
- TA-078 now emits grouped validation artifacts (week bins, Vegas spread bins) and game-level delta diagnostics.
- Weekly pipeline integration was updated to parse and publish all TA-078 artifact paths in pipeline markdown/json outputs.
- Product backlog update was made in dashboard source-of-truth: TA-079 CloudWatch EC2 configuration ticket added and expanded to execution-ready subtasks.

## Key File Changes To Resume
- scripts/verification/ta078_vegas_gap_tuning.py
  - Added: validation_by_week, validation_by_vegas_bin, validation_game_deltas artifacts.
  - Added markdown summary sections for best/worst weeks, spread-bin deltas, and game-level improvement/regression counts.
- scripts/maintenance/weekly_ml_pipeline.py
  - Parses additional TA-078 stdout keys and forwards artifact paths into report output.
- docs/ai_reference/WEEKLY_ML_PIPELINE_RUNBOOK.md
  - Documents the expanded TA-078 artifact set.
- pmforge_dashboard/index.html
  - Added TA-079 backlog ticket (CloudWatch EC2 observability) and expanded with assignee/description/subtasks/history.
- ml/predict_week.py
  - Supports optional TA-078 runtime calibration flags for local runs.

## Latest Evidence Artifacts (Most Recent)
- TA-078 tuning run:
  - docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260519_220810_summary.json
  - docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260519_220810_report.md
  - docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260519_220810_validation_by_week.csv
  - docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260519_220810_validation_by_vegas_bin.csv
  - docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260519_220810_validation_game_deltas.csv
- Weekly pipeline run with TA-078 integration:
  - docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_220813.json
  - docs/sprints/phase4_weekly_ops/weekly_ml_pipeline_20260519_220813.md

## Last Verified TA-078 Outcomes
- Recommended method remains: linear
- Recommended runtime values:
  - AI_SPREAD_CAL_BIAS=-1.5093
  - AI_SPREAD_CAL_SCALE=-0.5048
- Validation game-level delta summary (latest run):
  - Improved vs baseline: 141 games
  - Regressed vs baseline: 83 games
  - Flat: 0 games
  - Largest improvement game: 2025_08_TEN_IND
  - Largest regression game: 2025_05_DAL_NYJ

## Resume Sequence (Crash-Safe)
1. Re-open this file and confirm scope lock: continue TA-078 app work first.
2. Run quick status:
   - git status --short -- scripts/verification/ta078_vegas_gap_tuning.py scripts/maintenance/weekly_ml_pipeline.py docs/ai_reference/WEEKLY_ML_PIPELINE_RUNBOOK.md pmforge_dashboard/index.html
3. Re-run TA-078 script:
   - C:\ReactGitEC2\IS330\H.C Lombardo App\.venv\Scripts\python.exe scripts/verification/ta078_vegas_gap_tuning.py --schema hcl --seasons 2021,2022,2023,2024,2025
4. Re-run pipeline integration proof:
   - C:\ReactGitEC2\IS330\H.C Lombardo App\.venv\Scripts\python.exe scripts/maintenance/weekly_ml_pipeline.py --season 2025 --week 18 --ta078-tune
5. Next planned increment after restore:
   - Add targeted diagnostics for worst-week cluster (2025-W10) and high-spread bin behavior into TA-078 follow-up output.

## Important Guardrails For Next Chat
- Do not commit automatically unless explicitly requested.
- Keep TA-078 artifact generation reproducible and timestamped.
- Preserve existing unrelated untracked frontend zip/build artifacts; do not clean them without user approval.
