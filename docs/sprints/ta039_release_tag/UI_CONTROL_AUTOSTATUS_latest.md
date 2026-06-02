# UI Control Coverage Autostatus (Latest)

Generated (UTC): 2026-06-02T04:18:00Z
Target: https://staging.d2fwv8daemi5y2.amplifyapp.com
Mode: Non-destructive interactive in-app control sweep

## Coverage Summary
- Side-menu route inventory: 11
- Side-menu routes reached in app: 11/11 (PASS)
- Total links observed across route snapshots: 132
- Total buttons observed across route snapshots: 48
- Total native select controls observed: 13
- Total input/textarea controls observed: 1
- Total select option changes executed: 301
- Network errors captured during sweep: 4

## Route Coverage (Interactive Navigation)
- PASS / Dashboard -> /
- PASS / Team Stats -> /team-stats
- PASS / Team Comparison -> /team-comparison
- PASS / Matchup Analyzer -> /matchup-analyzer
- PASS / Advanced Analytics -> /analytics
- PASS / Game Statistics -> /game-statistics
- PASS / Historical Data -> /historical-data
- PASS / AI Predictions -> /ml-predictions
- PASS / Model Performance -> /model-performance
- PASS / Admin -> /admin
- PASS / Settings -> /settings

## Control Exercise Evidence
- Every discovered native select dropdown was traversed through available options and restored.
- High-volume dropdown validation completed on:
  - Team Stats (33 options)
  - Team Comparison (120 option changes across 4 dropdowns)
  - Game Statistics (120 option changes across 4 dropdowns)
  - AI Predictions (25 option changes across 2 dropdowns)
- Theme dropdown on Dashboard validated (3 options).

## Captured Errors
- 500: /api/hcl/analytics/summary?season=2025
- 500: /api/hcl/analytics/summary?season=2024
- 500: /api/hcl/analytics/summary?season=2023
- 500: /api/hcl/analytics/summary?season=2022

## Combined Gate Status Before UI Work
- In-app interactive route and dropdown sweep: PASS with known backend errors.
- Full program route deep-link probe: FAIL (non-root route 404 at host level).
- Full program API probe: FAIL for analytics endpoints (HTTP 500 family).
- Destructive endpoints/actions (for example POST update-results): intentionally excluded.

Overall: NOT READY for strict "everything passes" gate until deep-link rewrite and analytics 500 failures are resolved.
