# TA-073 Fetcher Path Fix Evidence

Date: 2026-05-27
Owner: GitHub Copilot (Developer)
Ticket: TA-073
Scope: Fix `live_data_updater.py` fetcher path mismatch causing update loop errors

## Root Cause
`live_data_updater.py` attempted to execute `multi_source_data_fetcher.py` only from repository root. In this workspace, the fetcher exists at `scripts/maintenance/multi_source_data_fetcher.py`.

Resulting behavior: updater reported "fetcher not found" and repeated failed cycles.

## Fix Implemented
Updated both updater entrypoints:
- `live_data_updater.py`
- `scripts/maintenance/live_data_updater.py`

Changes:
- Added repository root resolver (`_resolve_repo_root`).
- Added ordered fetcher candidate resolution (`_fetcher_candidates`, `_resolve_fetcher_script`).
- Added explicit candidate-path error output when unresolved.
- Executed subprocess from repository root (`cwd=repo_root`) for stable relative-path behavior.

## Verification 1: Resolver Paths
```python
from live_data_updater import LiveDataUpdater as RootUpdater
from scripts.maintenance.live_data_updater import LiveDataUpdater as MaintUpdater

root = RootUpdater()
maint = MaintUpdater()

print('root_repo_root', root.repo_root)
print('root_fetcher', root._resolve_fetcher_script())
print('maint_repo_root', maint.repo_root)
print('maint_fetcher', maint._resolve_fetcher_script())
```

Output:
```text
root_repo_root C:\ReactGitEC2\IS330\H.C Lombardo App
root_fetcher C:\ReactGitEC2\IS330\H.C Lombardo App\scripts\maintenance\multi_source_data_fetcher.py
maint_repo_root C:\ReactGitEC2\IS330\H.C Lombardo App
maint_fetcher C:\ReactGitEC2\IS330\H.C Lombardo App\scripts\maintenance\multi_source_data_fetcher.py
```

## Verification 2: run_update Invocation (Mocked)
```python
from types import SimpleNamespace
from unittest.mock import patch

import live_data_updater
from scripts.maintenance import live_data_updater as maint_live

root = live_data_updater.LiveDataUpdater()
maint = maint_live.LiveDataUpdater()

with patch('live_data_updater.subprocess.run') as root_run:
    root_run.return_value = SimpleNamespace(returncode=0, stdout='ok\n', stderr='')
    root_ok = root.run_update()
    root_cmd = root_run.call_args[0][0]
    root_cwd = root_run.call_args[1].get('cwd')

with patch('scripts.maintenance.live_data_updater.subprocess.run') as maint_run:
    maint_run.return_value = SimpleNamespace(returncode=0, stdout='ok\n', stderr='')
    maint_ok = maint.run_update()
    maint_cmd = maint_run.call_args[0][0]
    maint_cwd = maint_run.call_args[1].get('cwd')

print('root_ok', root_ok)
print('root_script', root_cmd[1])
print('root_cwd', root_cwd)
print('maint_ok', maint_ok)
print('maint_script', maint_cmd[1])
print('maint_cwd', maint_cwd)
```

Output:
```text
root_ok True
root_script C:\ReactGitEC2\IS330\H.C Lombardo App\scripts\maintenance\multi_source_data_fetcher.py
root_cwd C:\ReactGitEC2\IS330\H.C Lombardo App
maint_ok True
maint_script C:\ReactGitEC2\IS330\H.C Lombardo App\scripts\maintenance\multi_source_data_fetcher.py
maint_cwd C:\ReactGitEC2\IS330\H.C Lombardo App
```

## Acceptance Mapping
- Step 01: Confirmed mismatch between expected root fetcher path and actual script location.
- Step 02: Implemented robust candidate resolution in both updater entrypoints.
- Step 03: Verified both updaters resolve and invoke correct script path.
- Step 04: Published this timestamped evidence bundle.
