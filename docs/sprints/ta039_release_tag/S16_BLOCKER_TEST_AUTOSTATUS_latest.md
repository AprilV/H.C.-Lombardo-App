# Sprint 16 Blocker Test Automation Status

Generated UTC: 2026-06-02T04:13:59.177463+00:00

## Summary
- all_automatable_checks_passing: false
- blocker_count: 4
- ta016_blocked: True
- ta037_closure_ready: False
- api_probe_ok: false

## Blockers
- TA-016 remains blocked (no reachable production endpoint)
- TA-037 remains blocked (stability gate not closure-ready)
- Frontend deep-link route probe has 10 failing routes
- API probe endpoint did not return HTTP 200

## Route Probes
Base: https://staging.d2fwv8daemi5y2.amplifyapp.com
- path=/ ok=true status=200 error=None
- path=/team-stats ok=false status=404 error=None
- path=/team-comparison ok=false status=404 error=None
- path=/matchup-analyzer ok=false status=404 error=None
- path=/analytics ok=false status=404 error=None
- path=/game-statistics ok=false status=404 error=None
- path=/historical-data ok=false status=404 error=None
- path=/ml-predictions ok=false status=404 error=None
- path=/model-performance ok=false status=404 error=None
- path=/admin ok=false status=404 error=None
- path=/settings ok=false status=404 error=None

## API Probe
- url=https://9dkkj5n2rc.execute-api.us-east-2.amazonaws.com/api/hcl/analytics/summary?season=2025
- ok=false status=500

## Individual Checks
- name=ta016_probe_step ok=true detail=ta016_probe_status.py completed
- name=ta037_gate_step ok=true detail=ta037_gate_status.py completed
- name=ta016_artifact_present ok=true detail=ta016_probe_status_latest.json parsed
- name=ta037_artifact_present ok=true detail=ta037_gate_status_latest.json parsed
- name=frontend_deep_link_routes ok=false detail=10 failing routes
- name=api_probe ok=false detail=status=500
