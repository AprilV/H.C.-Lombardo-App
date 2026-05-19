# TA-077 Sprint 15 Evaluation Plan

## Objective
Deliver an evidence-grade, multi-season verification program for AI predictions versus Vegas baselines, covering winner picks, ATS spread picks, and totals over/under outcomes, with reproducible metrics and closure-gate traceability.

## Scope
1. Seasons: 2021-2025 (default several-years window for Sprint 15).
2. Bet types:
- Head-to-head winner picks.
- ATS spread picks.
- Totals over/under picks.
3. Comparison:
- AI performance metrics by season and aggregate.
- AI-vs-Vegas spread head-to-head outcomes using existing app logic.
4. Integrity checks:
- Prediction timestamp validity (predicted_at <= game_date for live benchmark cohort).
- Line-lock detection for totals (predicted_total should not mirror vegas_total at scale).

## Dependencies
1. TA-076 (ML reliability umbrella).
2. TA-054 (/api/ml/model-performance route reliability).
3. TA-055 (/api/elo/predict-week route reliability).

## Deliverables
1. Multi-season run artifacts under docs/sprints/ta077_multi_season_eval.
2. Per-season metric table (CSV).
3. Consolidated JSON summary with gate results and findings.
4. Advisor-ready markdown report.
5. Dashboard traceability via TA-077 closure-gate updates.

## Execution Phases
1. Phase 1: Baseline and contract lock
- Confirm season window and metric definitions.
- Confirm pass/fail thresholds for leakage, line-lock, and totals coverage.

2. Phase 2: Multi-season pipeline execution
- Run TA-070 extraction/metrics/root-cause/publish pipeline per season.
- Persist all intermediate artifacts per season.

3. Phase 3: Comparison and scoring matrix
- Compute AI spread versus Vegas spread head-to-head outcomes.
- Aggregate accuracy, MAE/RMSE, and coverage outcomes across seasons.

4. Phase 4: Integrity gates
- Evaluate leakage threshold.
- Evaluate totals line-lock threshold.
- Evaluate totals coverage threshold.
- Mark season pass/fail per gate set.

5. Phase 5: Publish evidence
- Produce consolidated report and summary.
- Reference artifacts in dashboard task evidence notes.

## Metrics
1. Winner:
- winner_accuracy_pct
- winner_coverage_pct

2. Spread:
- spread_accuracy_pct
- spread_coverage_pct
- margin_mae_points

3. Totals:
- total_accuracy_pct
- total_coverage_pct
- total_mae_points

4. AI vs Vegas (spread logic parity with API):
- ai_wins
- vegas_wins
- ties
- ai_win_pct
- vegas_win_pct

5. Integrity diagnostics:
- predicted_after_game_date_pct
- predicted_total_equals_vegas_total_pct
- total_pick_evaluable_rows

## Thresholds (initial Sprint 15 defaults)
1. max_leakage_pct: 5.0
2. max_line_lock_pct: 95.0
3. min_total_coverage_pct: 5.0

## Run Command
```powershell
python scripts/verification/ta077_multi_season_evaluation.py --schema hcl --seasons 2021 2022 2023 2024 2025
```

## Gate-Enforced Run (optional)
```powershell
python scripts/verification/ta077_multi_season_evaluation.py --schema hcl --seasons 2021 2022 2023 2024 2025 --fail-on-threshold
```

## Acceptance Criteria
1. Per-season and aggregate artifacts are generated successfully.
2. AI-vs-Vegas spread comparison is included for each season with non-null totals.
3. Winner/spread/totals metrics are populated where evaluable.
4. Gate statuses are computed and reported per season.
5. TA-077 dashboard bookkeeping references generated artifacts before completion claims.

## Out of Scope (TA-077)
1. Major model architecture redesign unrelated to measurement validity.
2. New betting product features not required for Sprint 15 verification objectives.
3. Infrastructure migration work outside route reliability dependencies.
