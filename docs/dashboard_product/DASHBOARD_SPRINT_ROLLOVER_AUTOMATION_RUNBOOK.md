# Dashboard Sprint Rollover Automation Runbook

## Purpose

This runbook defines exactly what is automated at sprint rollover, what is not automated, and the mandatory verification steps before saying "done".

This exists to protect app delivery time. The dashboard is a support artifact and must not consume large blocks of sprint execution time.

## Trigger Schedule

- Sprint rollover cadence: every other Monday (per `SPRINT_SCHEDULE` in `pmforge_dashboard/index.html`).
- Rollover trigger source: date-based `getCurrentSprint()` and `watchSprintDateRollover()`.
- Check frequency in-app: every 5 minutes (`setInterval(watchSprintDateRollover, 300000)`).

## Automation Contract

### Fully automated in runtime

1. Active sprint detection from schedule dates.
2. Selected sprint follow-current behavior (when enabled).
3. Top-strip open counts from `PB_ITEMS` (`computeLiveTaskCounts`).
4. Sprint progress fallback when board subtasks are empty:
   - Uses sprint-assigned ticket counts from `PB_ITEMS`.
   - Prevents `0 of 0` collapse on kickoff day.
5. Burndown ideal line generation for active sprint:
   - Generated from active scope and active sprint workday count.
6. Burndown current-day actual point:
   - Set from current remaining scope.
7. Velocity historical backfill for prior sprints from live backlog done counts.

### Not automated (must be maintained intentionally)

1. Sprint planning decisions:
   - Which tickets are assigned to the new sprint in `PB_ITEMS`.
2. Final subtask wording quality for generated sprint boards.
3. Task resolution narratives in `TASK_DETAILS`.
4. Human narrative text that is not generated from arrays.

## CLI Rollover Generator (new)

Use the generator to create sprint boards from assigned backlog tickets instead of hand-authoring HTML.

Script location:
- `scripts/maintenance/dashboard_sprint_rollover.py`

### Commands

1. Check current sprint coverage:

```bash
python scripts/maintenance/dashboard_sprint_rollover.py check --sprint 14
```

2. Generate next sprint board from `PB_ITEMS` assignments:

```bash
python scripts/maintenance/dashboard_sprint_rollover.py apply --sprint 15
```

3. If replacing a previously generated board intentionally:

```bash
python scripts/maintenance/dashboard_sprint_rollover.py apply --sprint 15 --force
```

### Generator behavior

1. Reads sprint schedule metadata from `SPRINT_SCHEDULE`.
2. Reads sprint ticket assignments from `PB_ITEMS`.
3. Creates grouped sprint board subtasks and progress widgets for the target sprint.
4. Preserves existing dashboard wiring so runtime sync/metrics continue to work.

### Required post-generation review

1. Verify generated subtasks match actual execution intent (edit wording if needed).
2. Run the mandatory verification gate below before declaring rollover complete.

## Mandatory Verification Gate (before declaring done)

Run this every rollover and every backlog reassignment affecting the current sprint.

### Step 1: Hard refresh runtime

- Reload dashboard page to clear stale in-memory state.
- Confirm page is reading latest `pmforge_dashboard/index.html` content.

### Step 2: Run console verification

Paste into browser console:

```javascript
(() => {
  const sprint = getCurrentSprint();
  const items = window.PB_ITEMS || [];
  const sprintTag = `S${sprint}`;
  const assigned = items.filter(i => String(i.sprint || '').trim().toUpperCase() === sprintTag);
  const done = assigned.filter(i => String(i.status || '').trim().toLowerCase() === 'done');
  const board = getBoardCompletionCounts(sprint);
  const ticket = getCommittedSprintTicketCounts(items, sprint);
  const snap = getEffectiveSprintSnapshot(sprint);

  return {
    sprint,
    assignedCount: assigned.length,
    doneCount: done.length,
    board,
    ticket,
    taskPctCard: document.getElementById('dash-task-pct')?.textContent || null,
    taskCountCard: document.getElementById('dash-task-count')?.textContent || null,
    burndownIdealLength: snap?.burndown?.ideal?.length ?? null,
    burndownIdealStart: snap?.burndown?.ideal?.[0] ?? null,
    burndownActualStart: snap?.burndown?.actual?.[0] ?? null
  };
})();
```

### Step 3: Expected pass criteria

1. `assignedCount > 0` for an active sprint with planned work.
2. If `board.total === 0`, card text must read ticket fallback format:
   - `X of Y sprint tickets complete (auto from backlog until board subtasks are added)`.
3. `burndownIdealLength > 0` for active sprint.
4. `burndownIdealStart === ticket.total` when fallback is active.
5. `burndownActualStart === ticket.remaining` on workday 1 when fallback is active.
6. `Open P1 Blockers` and `Total Open Tasks` cards match backlog status counts.

If any check fails, do not declare done.

## Known Failure Modes And Required Fix

| Symptom | Typical root cause | Required fix |
|---|---|---|
| Sprint card shows `Sprint Active` with `0 of 0` | No fallback from assigned sprint tickets | Ensure active snapshot uses ticket fallback when board subtasks are empty |
| Burndown has no ideal line | Active scope resolved to zero | Verify sprint-assigned ticket counts and fallback math |
| Sprint 13 bar disappears in Sprint 14 velocity | Stale snapshot values for prior sprint | Backfill historical velocity from live done ticket counts |
| Ticket unexpectedly moves to older sprint | Legacy board mapping overrides explicit sprint assignment | Preserve explicit assigned sprint when it differs from mapped board sprint |

## Enforcement Rule

Before any "fixed" claim, provide:

1. Verification output summary from the console check.
2. Visible metric confirmation (task card + burndown status line).
3. Commit hash containing the fix.

No verification evidence means not done.

## Fast Rollover Routine (2-3 minutes)

1. Assign sprint tickets in `PB_ITEMS`.
2. Run generator: `python scripts/maintenance/dashboard_sprint_rollover.py apply --sprint <next_sprint_num>`.
3. Hard refresh dashboard.
4. Run verification snippet.
5. Confirm top-strip Sprint Tasks Done text and Burndown insight sentence.
6. If values pass, continue app work.
7. If values fail, fix immediately before continuing sprint feature work.

## Scope Reminder

Dashboard automation exists to reduce overhead, not create it.

- If a dashboard task is not directly blocking app delivery, capture it as backlog and continue app execution.
- Only sprint-rollover correctness and data integrity checks are mandatory at kickoff.
