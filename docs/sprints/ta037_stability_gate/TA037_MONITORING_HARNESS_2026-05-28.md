# TA-037 Monitoring Harness Setup

Date: 2026-05-28
Owner: GitHub Copilot (Developer)
Ticket: TA-037
Status: In Progress (Gate still blocked)

## What Was Added
- Checkpoint collector script:
  - `scripts/verification/ta037_stability_watch.py`
- Output target (JSONL):
  - `docs/sprints/ta037_stability_gate/ta037_stability_checkpoints.jsonl`

## Purpose
Provide repeatable, timestamped API/frontend health snapshots required to execute and prove the 48-hour stability gate.

## Default Probe Targets
- `http://127.0.0.1:5000/health`
- `http://127.0.0.1:5000/api/teams`
- `http://127.0.0.1:3000`

## Recommended Run Commands
Single snapshot smoke check:
```bash
python scripts/verification/ta037_stability_watch.py --duration-hours 0
```

48-hour run (5-minute interval):
```bash
python scripts/verification/ta037_stability_watch.py --duration-hours 48 --interval-seconds 300
```

## Smoke Run Result (2026-05-28)
- Command executed: `python scripts/verification/ta037_stability_watch.py --duration-hours 0`
- Output file created: `docs/sprints/ta037_stability_gate/ta037_stability_checkpoints.jsonl`
- Result: `all_ok=false` with connection-refused status on API and frontend targets while services were not running.
- Interpretation: harness is functioning and captures gate-relevant failures truthfully; full 48-hour gate run must be executed with services up.

## Live Window Start (2026-05-28)
- 48-hour monitor launched:
  - `python scripts/verification/ta037_stability_watch.py --duration-hours 48 --interval-seconds 300`
- Active terminal ID: `ea0cd0fc-5ddf-4412-9820-a2d724f92d6e`
- Initial live snapshot: `all_ok=true` with HTTP 200 on all default targets.

## Gate Truth
This does not close TA-037 by itself. Ticket remains blocked until:
1. Full 48+ hour run completes,
2. Checkpoints are reviewed,
3. Incident/recovery handling is documented,
4. Final evidence pack is published.
