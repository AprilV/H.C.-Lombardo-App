# TA-037 Live Window Start Evidence

Date: 2026-05-28
Owner: GitHub Copilot (Developer)
Ticket: TA-037
Status: Blocked (window in progress)

## What Changed
- Fixed startup launcher interpreter resolution in `startup.py` to use workspace venv python path.
- Started local services via `startup.py` with DB password set in environment for this session.
- Started 48-hour stability monitor process.

## Active 48-Hour Monitor Run
- Command:
  - `python scripts/verification/ta037_stability_watch.py --duration-hours 48 --interval-seconds 300`
- Terminal ID:
  - `ea0cd0fc-5ddf-4412-9820-a2d724f92d6e`
- Run start timestamp (UTC):
  - `2026-05-28T19:17:02.243395+00:00`

## Checkpoint Evidence
- Checkpoint file:
  - `docs/sprints/ta037_stability_gate/ta037_stability_checkpoints.jsonl`
- Latest checkpoint at run start:
  - `all_ok=true`
  - `5000/health=200`
  - `5000/api/teams=200`
  - `3000=200`

## Interim Window Metrics (2026-05-28)
- Total checkpoint rows in file: 33
- Live-window checkpoint rows: 32
- Live-window all_ok true: 32/32
- Live window span (UTC):
  - First: `2026-05-28T19:17:02.243395+00:00`
  - Latest: `2026-05-28T21:52:09.981515+00:00`
- Latency snapshot (ms):
  - `/health`: min 57, max 3164, avg 174.9
  - `/api/teams`: min 54, max 90, avg 65.7
  - `frontend /`: min 2, max 26, avg 3.1

## Interim Health Snapshot (2026-05-28)
- Current endpoint check: `5000/health=200`, `5000/api/teams=200`, `3000=200`.
- Monitor process remains active under workspace venv python.

## Current Gate Truth
- TA-037 remains blocked until the full 48+ hour window completes and evidence review is finalized.
