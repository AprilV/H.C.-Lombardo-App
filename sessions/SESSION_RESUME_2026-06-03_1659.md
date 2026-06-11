# Session Resume Note - 2026-06-03 1659

## Reason
Startup lock trigger

## Current Git State Snapshot
- Branch: master
- Latest commits:
  - d329237d (HEAD -> master, origin/master) Unify ATS contracts and fail-closed frontend ATS displays
  - 41562b1b Enforce single denominator for model performance outputs
  - 099cfaf3 Prefer simulation when tracked model coverage is sparse

## Current Local Working Set (Uncommitted)
- Modified: frontend/src/GameStatistics.js
- Modified: frontend/src/MLPredictionsRedesign.js
- Modified: frontend/src/MatchupAnalyzer.js
- Modified: frontend/src/TeamComparison.js
- Modified: frontend/src/TeamDetail.js
- Untracked: frontend/src/utils/teamLogos.js
- Untracked: frontend_build_upload_posix_live_20260602_143918.zip
- Untracked: sessions/SESSION_RESUME_2026-06-02_1816.md
- Untracked: sessions/SESSION_RESUME_2026-06-03_1314.md
- Untracked: sessions/SESSION_RESUME_2026-06-03_1651.md
- Untracked: sessions/SESSION_RESUME_2026-06-03_1652.md

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
