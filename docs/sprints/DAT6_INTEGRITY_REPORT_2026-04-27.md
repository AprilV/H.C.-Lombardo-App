# DAT-6 Integrity Report (2025 Season)

Date: April 27, 2026  
Database: `nfl_analytics`  
Scope: `hcl.games`, `hcl.team_game_stats`, `public.teams`

## Execution

Command used:

```powershell
py -3.14 scripts/data_loading/backfill_missing_scores_from_espn.py --season 2025
py -3.14 scripts/data_loading/update_public_teams_from_games.py --season 2025
py -3.14 scripts/verification/dat6_integrity_audit.py --season 2025
```

Audit script:

- `scripts/verification/dat6_integrity_audit.py`

## Summary Findings

| Check | Result | Status |
|---|---:|---|
| Games loaded for 2025 | 272 | PASS |
| Games with final scores | 272 | PASS |
| Games missing scores | 0 | PASS |
| Postseason games loaded | 0 | FAIL |
| team_game_stats rows (2025) | 468 | FAIL |
| Expected team_game_stats rows for completed games | 544 | FAIL |
| Missing team_game_stats rows for completed games | 76 | FAIL |
| team_game_stats rows with NULL `epa_per_play` | 80 | FAIL |
| Teams in `hcl.games` not in `public.teams` (raw) | `LA` | FAIL |
| Teams in `public.teams` not in `hcl.games` (raw) | `LAR` | FAIL |
| Teams in `hcl.games` not in `public.teams` (canonicalized) | none | PASS |
| Teams in `public.teams` not in `hcl.games` (canonicalized) | none | PASS |

## Key Integrity Details

1. Weekly game coverage is now complete through Week 18.
2. Missing-score blocker NEW-005 was resolved by ESPN backfill (34 updates applied).
3. `public.teams` had to be reseeded/synced again after backfill validation; standings now recomputed for all 32 teams.
4. Core blockers are now stats completeness, not game scores:
- `team_game_stats_expected_for_completed=544`
- `team_game_stats_actual_for_completed=468`
- `team_game_stats_missing_for_completed=76`
5. Raw abbreviation mismatch remains expected (`LA` vs `LAR`), while canonical mismatch checks are empty.

## Missing-Score Game Inventory

- None (all 2025 regular-season games in `hcl.games` now have final scores).

## Sprint Impact

- DAT-6 verification work is complete (integrity checks rerun after score backfill and standings sync).
- Data quality blockers remain for DAT-2, DAT-3, and DAT-4.
- NEW-005 is now fixed; remaining blockers are postseason game load plus team_game_stats/EPA completeness.
- Abbreviation normalization (`LA`->`LAR`, `WSH`->`WAS`) is now centralized and applied in core APIs and verification/data-loading scripts.
