# TA-052 Teams Endpoint Fix Evidence

Date: 2026-05-27
Owner: GitHub Copilot (Developer)
Ticket: TA-052
Scope: Fix /api/hcl/teams returning 4 teams instead of 32

## Root Cause
The endpoint aggregated directly from `hcl.team_game_stats`, which only returns teams that already have rows for the selected season. In partial-season conditions, this can produce far fewer than 32 teams.

## Fix Implemented
Updated `api_routes_hcl.py` (`/api/hcl/teams`) to:
- Anchor on `public.teams` as the canonical 32-team source.
- Build a `season_stats` CTE from `hcl.team_game_stats` for the requested season.
- Left join `season_stats` onto `public.teams`.
- Use `COALESCE` defaults so teams with no season rows return zeroed stats.

This preserves full-team cardinality and keeps seasonal stats populated where data exists.

## Verification Command
```python
from api_server import app

client = app.test_client()
r = client.get('/api/hcl/teams')
print('status', r.status_code)
if r.is_json:
    data = r.get_json()
    print('success', data.get('success'))
    print('season', data.get('season'))
    print('count', data.get('count'))
    teams = data.get('teams') or []
    print('sample_first4', [t.get('team') for t in teams[:4]])
    print('sample_last4', [t.get('team') for t in teams[-4:]])
```

## Verification Output
```text
status 200
success True
season 2025
count 32
sample_first4 ['LAR', 'SEA', 'DEN', 'BUF']
sample_last4 ['TEN', 'CLE', 'NYG', 'LV']
```

## Acceptance Mapping
- Step 01: Reproduced and diagnosed team-count under-return condition.
- Step 02: Implemented full-team anchor query strategy with seasonal overlay.
- Step 03: Validated endpoint returns 32 teams in runtime test.
- Step 04: Published evidence bundle with command/output trace.
