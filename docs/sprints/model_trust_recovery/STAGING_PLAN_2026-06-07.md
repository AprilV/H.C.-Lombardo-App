# Commit-Ready Staging Plan (2026-06-07)

## Goal
Stage only model trust recovery code and evidence without pulling unrelated workspace changes.

## Group A: Code Fixes Only
Use this when you want a clean implementation commit.

```powershell
Set-Location "c:/ReactGitEC2/IS330/H.C Lombardo App"

git add api_routes_ml.py
git add frontend/src/ModelPerformance.js
git add frontend/src/ModelPerformance.css
git add ml/elo_tracker.py
git add scripts/verification/ta020_elo_stability_watch.py

git status --short
```

## Group B: Canonical Trust Evidence
Use this to add the final receipt and canonical logs/reports.

```powershell
Set-Location "c:/ReactGitEC2/IS330/H.C Lombardo App"

git add docs/sprints/model_trust_recovery/TRUST_RECEIPT_2026-06-07.md
git add docs/sprints/model_trust_recovery/core_backend_chain_20260607_183615.txt
git add docs/sprints/model_trust_recovery/elo_routes_20260607_183615.txt
git add docs/sprints/model_trust_recovery/frontend_build_20260607_183615.txt
git add docs/sprints/model_trust_recovery/ta020_elo_verify_20260607_183747.json
git add docs/sprints/model_trust_recovery/ta020_elo_verify_20260607_183747.md
git add docs/sprints/model_trust_recovery/subprocess_probe_after_fix.json
git add docs/sprints/model_trust_recovery/ta020_stability_20260608_014158_summary.json
git add docs/sprints/model_trust_recovery/ta020_stability_20260608_014158_report.md
git add docs/sprints/model_trust_recovery/STAGING_PLAN_2026-06-07.md

git status --short
```

## Group C: Decision-Gate Artifacts (Optional)
Use this if you want all generated retrain-decision artifacts in the same commit.

```powershell
Set-Location "c:/ReactGitEC2/IS330/H.C Lombardo App"

git add docs/sprints/ta018_winner_retrain/ta018_s18_1_20260608_013143_summary.json
git add docs/sprints/ta018_winner_retrain/ta018_s18_1_20260608_013143_report.md
git add docs/sprints/ta019_spread_retrain/ta019_s19_3_20260607_183146_summary.json
git add docs/sprints/ta019_spread_retrain/ta019_s19_3_20260607_183146_report.md
git add docs/sprints/ta077_multi_season_eval/ta077_run_20260608_013152/
git add docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260608_013158_summary.json
git add docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260608_013158_report.md
git add docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260608_013158_bias_scan.csv
git add docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260608_013158_validation_by_week.csv
git add docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260608_013158_validation_by_vegas_bin.csv
git add docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260608_013158_validation_game_deltas.csv
git add docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260608_013158_targeted_focus_week.csv
git add docs/sprints/ta078_vegas_tuning/ta078_vegas_tuning_20260608_013158_targeted_high_spread.csv

git status --short
```

## Recommended Commit Split
1. Commit 1: Group A (code fixes)
2. Commit 2: Group B (canonical trust receipt)
3. Commit 3: Group C (optional full artifact bundle)

## Safety Check
Before committing, ensure unrelated modified tracked files remain unstaged:
- README.md
- TEST_ENVIRONMENT_GUIDE.md
- docs/DASHBOARD_UPDATE_GUIDE.md
- docs/SPRINT_EXECUTION_PROCESS.md
- docs/ai_reference/TOPOLOGY.md
- docs/deployment/DEPLOYMENT_GUIDE.md
- docs/sprints/DEPLOYMENT_GUIDE.md

If needed:

```powershell
git restore --staged README.md TEST_ENVIRONMENT_GUIDE.md docs/DASHBOARD_UPDATE_GUIDE.md docs/SPRINT_EXECUTION_PROCESS.md docs/ai_reference/TOPOLOGY.md docs/deployment/DEPLOYMENT_GUIDE.md docs/sprints/DEPLOYMENT_GUIDE.md
```
