# Session Resume Note - 2026-06-16 1548

## Reason
Post-doc-cleanup checkpoint

## Current Git State Snapshot
- Branch: master
- Latest commits:
  - 34c149ea (HEAD -> master, origin/master) Dashboard: restore Netlify architecture/about stack wording
  - e9aff39f Dashboard: close out Sprint 13-16 archive metrics and statuses
  - dec52343 Restore PM Forge live updater/dashboard behavior

## Current Local Working Set (Uncommitted)
- Modified: .github/copilot-instructions.md
- Modified: docs/ai_reference/ARCHITECTURE.md
- Modified: docs/ai_reference/TOPOLOGY.md
- Deleted: docs/deployment/AWS_ACCOUNT_RECOVERY_RUNBOOK.md
- Deleted: docs/deployment/AWS_ACCOUNT_RECOVERY_STATUS.md
- Modified: docs/deployment/DEPLOYMENT_GUIDE.md
- Modified: docs/deployment/QUICK_START.md
- Deleted: sessions/SESSION_RESUME_2026-04-27_1743.md
- Deleted: sessions/SESSION_RESUME_2026-04-30_1604.md
- Deleted: sessions/SESSION_RESUME_2026-04-30_1954.md
- Deleted: sessions/SESSION_RESUME_2026-05-01_0034.md
- Deleted: sessions/SESSION_RESUME_2026-05-01_1348.md
- Deleted: sessions/SESSION_RESUME_2026-05-04_1431.md
- Deleted: sessions/SESSION_RESUME_2026-05-04_1525.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1151.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1438.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1440.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1441.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1442.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1443.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1445.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1452.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1458.md
- Deleted: sessions/SESSION_RESUME_2026-05-05_1821.md
- Deleted: sessions/SESSION_RESUME_2026-05-06_2150.md
- Deleted: sessions/SESSION_RESUME_2026-05-06_2152.md
- Deleted: sessions/SESSION_RESUME_2026-05-07_1217.md
- Deleted: sessions/SESSION_RESUME_2026-05-07_1936.md
- Deleted: sessions/SESSION_RESUME_2026-05-08_1247.md
- Deleted: sessions/SESSION_RESUME_2026-05-11_1243.md
- Deleted: sessions/SESSION_RESUME_2026-05-11_1249.md
- Deleted: sessions/SESSION_RESUME_2026-05-11_1417.md
- Deleted: sessions/SESSION_RESUME_2026-05-11_1635.md
- Deleted: sessions/SESSION_RESUME_2026-05-11_1636.md
- Deleted: sessions/SESSION_RESUME_2026-05-11_1906.md
- Deleted: sessions/SESSION_RESUME_2026-05-12_0924.md
- Deleted: sessions/SESSION_RESUME_2026-05-12_0944.md
- Deleted: sessions/SESSION_RESUME_2026-05-12_0953.md
- Deleted: sessions/SESSION_RESUME_2026-05-12_1039.md
- Deleted: sessions/SESSION_RESUME_2026-05-12_1102.md
- Deleted: sessions/SESSION_RESUME_2026-05-12_1423.md
- Deleted: sessions/SESSION_RESUME_2026-05-14_1316.md
- Deleted: sessions/SESSION_RESUME_2026-05-14_1505.md
- Deleted: sessions/SESSION_RESUME_2026-05-15_2333.md
- Deleted: sessions/SESSION_RESUME_2026-05-16_1234.md
- Deleted: sessions/SESSION_RESUME_2026-05-18_1203.md
- Deleted: sessions/SESSION_RESUME_2026-05-18_1250.md
- Deleted: sessions/SESSION_RESUME_2026-05-19_1349.md
- Deleted: sessions/SESSION_RESUME_2026-05-20_0954.md
- Deleted: sessions/SESSION_RESUME_2026-05-20_1018.md
- Deleted: sessions/SESSION_RESUME_2026-05-20_1144.md
- Deleted: sessions/SESSION_RESUME_2026-05-26_1112.md
- Deleted: sessions/SESSION_RESUME_2026-05-26_1153.md
- Deleted: sessions/SESSION_RESUME_2026-05-26_1315.md
- Deleted: sessions/SESSION_RESUME_2026-05-26_1501.md
- Deleted: sessions/SESSION_RESUME_2026-05-26_1754.md
- Deleted: sessions/SESSION_RESUME_2026-05-27_2117.md
- Deleted: sessions/SESSION_RESUME_2026-05-28_1304.md
- Deleted: sessions/SESSION_RESUME_2026-06-01_1708.md
- Deleted: sessions/SESSION_RESUME_2026-06-01_2010.md
- Deleted: sessions/SESSION_RESUME_2026-06-01_2056.md
- Untracked: CODEX_START_HERE.md
- Untracked: docs/DEPLOY_AND_ARCHITECTURE.md
- Untracked: docs/archive/AWS_ACCOUNT_RECOVERY_RUNBOOK.md
- Untracked: docs/archive/AWS_ACCOUNT_RECOVERY_STATUS.md
- Untracked: sessions/SESSION_RESUME_2026-06-16_1545.md
- Untracked: sessions/archive/

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
