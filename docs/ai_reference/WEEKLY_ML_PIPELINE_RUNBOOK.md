# WEEKLY_ML_PIPELINE_RUNBOOK.md

## Purpose

Run a forward-only weekly ML operations cycle for XGBoost and Elo:

1. Generate missing predictions for target week.
2. Score only pending completed games.
3. Compute season snapshot and phase-4 gates.
4. Emit evidence artifacts (JSON + Markdown).

The workflow avoids rewriting existing prediction rows by default.

## Entry Point

- Script: scripts/maintenance/weekly_ml_pipeline.py

## Standard Command

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --fail-on-gate
```

This uses the `operational` gate profile by default.

## Optional Target Override

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --season 2026 --week 1 --fail-on-gate
```

## Read-Only Profile Advisor

Evaluate all gate profiles without generation/scoring updates:

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --recommend-profile
```

Advisor mode writes recommendation artifacts and reports the highest-strictness passing profile.

Compact console view (failed checks only):

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --recommend-profile --recommend-profile-compact
```

Compact output includes gap-to-pass values for each failed check.
Compact output also includes a target estimate summary showing the metric movement required to pass.
Compact output includes a priority ordering for failed checks to guide triage sequence.

Priority weights can be customized without code changes.

Use a JSON mapping file:

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --recommend-profile --recommend-profile-compact --priority-weights-file docs/sprints/phase4_weekly_ops/priority_weights.example.json
```

Or override individual checks inline (repeatable):

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --recommend-profile --recommend-profile-compact --priority-weight xgb_winner_accuracy_floor=3.0 --priority-weight ai_vs_vegas_delta_floor=9.0
```

## Gate Defaults

Profiles:

- `operational` (default): tuned for weekly operational continuity.
- `balanced`: tighter than operational, designed for routine QA checks.
- `strict-research`: tighter thresholds for quality stress testing.

`operational` profile defaults:

- XGBoost winner accuracy floor: 40.0%
- XGBoost spread MAE ceiling: 14.0
- XGBoost scored coverage minimum: 95.0%
- Elo winner accuracy floor: 50.0%
- Elo spread MAE ceiling: 14.0
- Elo scored coverage minimum: 95.0%
- AI-vs-Vegas minimum games: 32
- AI-vs-Vegas delta floor: -30.0 percentage points

`balanced` profile defaults:

- XGBoost winner accuracy floor: 40.25%
- XGBoost spread MAE ceiling: 13.9
- XGBoost scored coverage minimum: 98.0%
- Elo winner accuracy floor: 55.0%
- Elo spread MAE ceiling: 11.0
- Elo scored coverage minimum: 98.0%
- AI-vs-Vegas minimum games: 64
- AI-vs-Vegas delta floor: -29.0 percentage points

Default behavior when AI-vs-Vegas games are below the minimum: skip delta enforcement (does not fail the run).

Enable strict mode to fail on insufficient sample:

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --strict-ai-vs-vegas-sample --fail-on-gate
```

Run strict-research profile:

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --gate-profile strict-research --fail-on-gate
```

Run balanced profile:

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --gate-profile balanced --fail-on-gate
```

Override if needed:

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --winner-accuracy-floor 42 --spread-mae-ceiling 13.5 --coverage-min 98 --fail-on-gate
```

Profile plus explicit override example:

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --gate-profile strict-research --ai-vs-vegas-delta-floor -20 --no-strict-ai-vs-vegas-sample --fail-on-gate
```

Expanded override example:

```powershell
python scripts/maintenance/weekly_ml_pipeline.py --winner-accuracy-floor 42 --spread-mae-ceiling 13.5 --coverage-min 98 --elo-winner-accuracy-floor 54 --elo-spread-mae-ceiling 12.5 --elo-coverage-min 98 --ai-vs-vegas-min-games 96 --strict-ai-vs-vegas-sample --ai-vs-vegas-delta-floor -10 --fail-on-gate
```

## Artifact Output

Default folder:

- docs/sprints/phase4_weekly_ops/

Per run:

- weekly_ml_pipeline_YYYYMMDD_HHMMSS.json
- weekly_ml_pipeline_YYYYMMDD_HHMMSS.md

## Notes

1. Existing week predictions are preserved; generation is skipped when rows already exist.
2. Scoring updates pending rows only.
3. If no upcoming week exists, the script falls back to the latest regular-season week in data.
4. Use startup.py before running if app services are not already online.
