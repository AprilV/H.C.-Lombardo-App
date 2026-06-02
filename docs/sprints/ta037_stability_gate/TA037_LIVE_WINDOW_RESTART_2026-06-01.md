# TA-037 Live Window Restart Evidence

Date: 2026-06-01
Owner: GitHub Copilot (Developer)
Ticket: TA-037
Status: Blocked (48-hour run active, monitor lock-hardened)

## Why Restarted
Previous TA-037 checkpoint stream did not contain a full 48-hour continuous window, so the gate remained blocked.

## New 48-Hour Monitor Run
Command:
- `c:/ReactGitEC2/IS330/H.C Lombardo App/.venv/Scripts/python.exe scripts/verification/ta037_stability_watch.py --duration-hours 48 --interval-seconds 300`

Initial terminal ID:
- `0e617a3f-dab2-4f1b-abf1-8a2b0a66508b`

Run start timestamp (UTC):
- `2026-06-01T20:49:18.444800+00:00`

## Early Checkpoint Continuity
From `docs/sprints/ta037_stability_gate/ta037_stability_checkpoints.jsonl`:
- `2026-06-01T20:49:18.444800+00:00` snapshot `1` all_ok=`true`
- `2026-06-01T20:54:18.579285+00:00` snapshot `2` all_ok=`true`
- `2026-06-01T20:59:18.747637+00:00` snapshot `3` all_ok=`true`
- `2026-06-01T21:04:18.879594+00:00` snapshot `4` all_ok=`true`
- `2026-06-01T21:09:19.029109+00:00` snapshot `5` all_ok=`true`

## Monitor Session Hygiene Update
- Duplicate terminal/session state from earlier attempts was cleaned up to prevent ambiguous process ownership.
- Active monitoring was relaunched in a single terminal session.

Active terminal ID:
- `7e213038-7fce-4d2c-b73a-dcf0b5c578c7`

Clean continuation start (UTC):
- `2026-06-01T21:14:14.649574+00:00` snapshot `1` all_ok=`true`

Process integrity note:
- Windows venv launch can appear as parent/child `python.exe` pair for one invocation; this reflects one active monitor invocation path.

## Gate Truth
TA-037 remains blocked until this run reaches full 48+ hour completion and final checkpoint review confirms threshold compliance.

## 2026-06-01 Lock-Hardened Baseline Update

### Why this hardening pass was required
- Multiple launch attempts could still create overlapping monitor invocations in Windows parent/child process scenarios.
- Overlapping runs made ownership ambiguous and risked index resets in evidence continuity.

### Script hardening now in place
- `scripts/verification/ta037_stability_watch.py` now enforces an OS-level lock on `docs/sprints/ta037_stability_gate/ta037_stability_watch.lock`.
- Snapshot index resumes from existing JSONL tail instead of resetting.
- Each checkpoint includes `run_id` for per-run traceability.

### Validation evidence
- Primary hardened run launched and recorded:
	- `2026-06-01T21:32:30.421803+00:00` snapshot `8` all_ok=`true`
- Concurrent launch test was rejected with lock-busy runtime error:
	- `RuntimeError: TA-037 monitor already running (lock busy: docs\\sprints\\ta037_stability_gate\\ta037_stability_watch.lock).`
- JSONL continuity shows index resume and run tagging:
	- `2026-06-01T21:30:35.720623+00:00` snapshot `7` run_id present
	- `2026-06-01T21:32:30.421803+00:00` snapshot `8` run_id present

Active hardened monitor terminal ID:
- `29c9d535-aef1-4307-a3f0-d06861568719`

### Interim liveness checkpoint (2026-06-01T21:37Z)
- Latest JSONL row observed:
	- `2026-06-01T21:37:30.562884+00:00` snapshot `9` all_ok=`true`
	- run_id: `2026-06-01T21:32:30.282011+00:00_34989901-b86c-4ffc-9d33-8cbb5e6d33ee`
- Active process topology remains one invocation path on Windows:
	- `TOTAL_PROC_MATCHES=2` (expected parent/child pair)
	- `ROOT_INVOCATIONS=1`

Gate status remains unchanged: monitor is healthy and progressing, but TA-037 stays Blocked until full 48+ hour completion and final review.

### 48-hour target window marker
- Active run start (from current run_id): `2026-06-01T21:32:30.282011+00:00`
- Latest observed checkpoint in this run: `2026-06-01T21:37:30.562884+00:00`
- Elapsed in-window runtime: `0.083` hours
- Earliest 48-hour completion threshold timestamp: `2026-06-03T21:32:30.282011+00:00`

### Auto-status checkpoint (2026-06-01T21:51Z)
- Executed evaluator:
	- `python scripts/verification/ta037_gate_status.py`
- Generated artifacts:
	- `docs/sprints/ta037_stability_gate/ta037_gate_status_latest.json`
	- `docs/sprints/ta037_stability_gate/TA037_GATE_AUTOSTATUS_latest.md`
- Evaluated run_id:
	- `2026-06-01T21:32:30.282011+00:00_34989901-b86c-4ffc-9d33-8cbb5e6d33ee`
- Result summary:
	- `closure_ready=false`
	- `run_rows=4`
	- `elapsed_hours=0.250124`
	- `all_ok_rows=4`
	- `failed_rows=0`
	- blocking reason: elapsed window below 48 hours.

Latest checkpoint tail during this evaluation window:
- `2026-06-01T21:42:30.737058+00:00` snapshot `10` all_ok=`true`
- `2026-06-01T21:47:30.867082+00:00` snapshot `11` all_ok=`true`

### Orchestrator checkpoint (2026-06-01T21:55Z)
Executed:
- `powershell -ExecutionPolicy Bypass -File scripts/verification/s16_blocker_autostatus.ps1`

Output:
- `TA016_BLOCKED=True`
- `TA037_CLOSURE_READY=False`
- `TA037_ELAPSED_HOURS=0.333494`
- `S16_EXTERNAL_GATES_COMPLETE=False`

Latest observed checkpoint in active run now includes:
- `2026-06-01T21:52:30.998933+00:00` snapshot `12` all_ok=`true`

### Auto-cycle checkpoint (2026-06-01T22:05Z)
Executed combined blocker evaluator:
- `./scripts/verification/s16_blocker_autostatus.ps1`

Output:
- `TA016_BLOCKED=True`
- `TA037_CLOSURE_READY=False`
- `TA037_ELAPSED_HOURS=0.500233`
- `S16_EXTERNAL_GATES_COMPLETE=False`
- `EXIT_CODE=2`

Updated TA-037 gate status artifact summary (`ta037_gate_status_latest.json`):
- `generated_utc=2026-06-01T22:05:20.439642+00:00`
- `run_rows=7`
- `elapsed_hours=0.500233`
- `all_ok_rows=7`
- `failed_rows=0`
- blocking reason: elapsed window below 48 hours.

Latest checkpoint tail during this cycle:
- `2026-06-01T21:57:31.131394+00:00` snapshot `13` all_ok=`true`
- `2026-06-01T22:02:31.260398+00:00` snapshot `14` all_ok=`true`

### Auto-cycle checkpoint (2026-06-02T00:07Z)
Executed combined blocker evaluator:
- `./scripts/verification/s16_blocker_autostatus.ps1`

Output:
- `TA016_BLOCKED=True`
- `TA037_CLOSURE_READY=False`
- `TA037_ELAPSED_HOURS=2.501129`
- `S16_EXTERNAL_GATES_COMPLETE=False`
- `EXIT_CODE=2`

Updated TA-037 gate status artifact summary (`ta037_gate_status_latest.json`):
- `generated_utc=2026-06-02T00:07:17.043041+00:00`
- `run_rows=31`
- `elapsed_hours=2.501129`
- `all_ok_rows=31`
- `failed_rows=0`
- `max_gap_seconds=300.174`
- blocking reason: elapsed window below 48 hours.

Latest checkpoint tail during this cycle:
- `2026-06-01T23:52:34.226657+00:00` snapshot `36` all_ok=`true`
- `2026-06-01T23:57:34.352227+00:00` snapshot `37` all_ok=`true`
- `2026-06-02T00:02:34.486595+00:00` snapshot `38` all_ok=`true`

Dashboard closure gate check (Sprint 16) during this cycle:
- Command: `python scripts/maintenance/dashboard_closure_gate.py check --sprint 16`
- Result: `PASS: Closure gate passed. Sprint bookkeeping is aligned.`

### Auto-cycle checkpoint (2026-06-02T01:31Z)
Executed combined blocker evaluator:
- `./scripts/verification/s16_blocker_autostatus.ps1`

Output:
- `TA016_BLOCKED=True`
- `TA037_CLOSURE_READY=False`
- `TA037_ELAPSED_HOURS=3.918463`
- `S16_EXTERNAL_GATES_COMPLETE=False`
- `EXIT_CODE=2`

Updated TA-037 gate status artifact summary (`ta037_gate_status_latest.json`):
- `generated_utc=2026-06-02T01:31:07.690799+00:00`
- `run_rows=48`
- `elapsed_hours=3.918463`
- `all_ok_rows=48`
- `failed_rows=0`
- `max_gap_seconds=300.174`
- blocking reason: elapsed window below 48 hours.

Latest checkpoint tail during this cycle:
- `2026-06-02T01:17:36.626517+00:00` snapshot `53` all_ok=`true`
- `2026-06-02T01:22:36.750458+00:00` snapshot `54` all_ok=`true`
- `2026-06-02T01:27:36.887399+00:00` snapshot `55` all_ok=`true`

Dashboard closure gate check (Sprint 16) during this cycle:
- Command: `python scripts/maintenance/dashboard_closure_gate.py check --sprint 16`
- Result: `PASS: Closure gate passed. Sprint bookkeeping is aligned.`

### Auto-cycle checkpoint (2026-06-02T01:12Z)
Executed combined blocker evaluator:
- `./scripts/verification/s16_blocker_autostatus.ps1`

Output:
- `TA016_BLOCKED=True`
- `TA037_CLOSURE_READY=False`
- `TA037_ELAPSED_HOURS=3.668355`
- `S16_EXTERNAL_GATES_COMPLETE=False`
- `EXIT_CODE=2`

Updated TA-037 gate status artifact summary (`ta037_gate_status_latest.json`):
- `generated_utc=2026-06-02T01:12:48.028077+00:00`
- `run_rows=45`
- `elapsed_hours=3.668355`
- `all_ok_rows=45`
- `failed_rows=0`
- `max_gap_seconds=300.174`
- blocking reason: elapsed window below 48 hours.

Latest checkpoint tail during this cycle:
- `2026-06-02T01:02:36.224337+00:00` snapshot `50` all_ok=`true`
- `2026-06-02T01:07:36.359679+00:00` snapshot `51` all_ok=`true`
- `2026-06-02T01:12:36.500132+00:00` snapshot `52` all_ok=`true`

Dashboard closure gate check (Sprint 16) during this cycle:
- Command: `python scripts/maintenance/dashboard_closure_gate.py check --sprint 16`
- Result: `PASS: Closure gate passed. Sprint bookkeeping is aligned.`
