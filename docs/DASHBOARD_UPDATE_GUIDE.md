# Dashboard Update Guide

**Primary file:** `pmforge_dashboard/index.html` (single file, all dashboard runtime data hardcoded)
**Legacy archive:** `backups/legacy_dashboard/index.html` (reference-only, not deployed)
**Live URL:** https://aprilv.github.io/H.C.-Lombardo-App/
**April does not edit this file directly - Claude owns all updates.**

---

## How Updates Work

April and Claude go through the dashboard together each session. April reports what happened (hours worked, tasks done, bugs found/fixed, decisions made, risks). Claude makes all the changes and deploys.

**One session = one topic.** Don't stack multiple unrelated changes.

---

## Dashboard Truth Map (Read First)

These are the exact data sources for the top strip and the 4 charts.

### Overview metrics source-of-truth

| Metric | Source of truth | What Claude must update |
|---|---|---|
| Current Sprint | `SPRINT_SCHEDULE` + `getCurrentSprint()` | Nothing unless sprint calendar changes |
| Days Remaining | `SPRINT_SCHEDULE` date math | Nothing unless sprint dates change |
| Sprint Tasks Done % / count | `syncDashMetrics()` reading active sprint board checkboxes seeded from `COMPLETED_TASKS` | Update `COMPLETED_TASKS` task IDs |
| Open P1 Blockers | `computeLiveTaskCounts()` from `window.PB_ITEMS` where status=`Blocked` | Update PB item `status` fields |
| Total Open Tasks | `computeLiveTaskCounts()` from `window.PB_ITEMS` where status!=`Done` | Update PB item `status` fields |
| Target release countdown | JS date math to Jun 13, 2026 | Nothing unless target date changes |

### Four charts source-of-truth

All 4 charts are rendered from the active sprint's `SPRINT_ARCHIVE[N]` object:

- Burndown: `SPRINT_ARCHIVE[N].burndown`
- Burnup: `SPRINT_ARCHIVE[N].burnup`
- Velocity: `SPRINT_ARCHIVE[N].velocity`
- Severity donut: `SPRINT_ARCHIVE[N].severity`

If these arrays are not updated, the chart will be stale even when tasks/backlog are current.

---

## Daily Update Order (Mandatory)

1. Update completed subtasks in `COMPLETED_TASKS`.
2. Add/refresh resolution entries in `TASK_DETAILS` (resolution, date, timestamp, updatedBy).
3. Update Product Backlog item statuses (`Done`, `In Progress`, `Blocked`, `To Do`) in `PB_ITEMS`.
4. Update active sprint archive (`SPRINT_ARCHIVE[N]`) for:
	- `rag.msg` / `rag.detail`
	- `metrics.taskPct` / `metrics.taskCount` narrative text
	- `burndown`, `burnup`, `velocity`, `severity` arrays
	- chart insight text fields (`burndownInsight`, `burnupInsight`, `velocityInsight`, `severityInsight`)
5. Update Open Blockers list UI (`.blocker-list`) to match current risks.
6. Reload dashboard and verify top strip + all four charts match the board/backlog state.
7. Commit + push.

---

## Dashboard Product Governance (Required)

Dashboard platform work is tracked separately from app delivery work.

1. Log dashboard enhancement work as `DSH-` tickets in `docs/dashboard_product/DASHBOARD_BACKLOG.md`.
2. Add dashboard release entries to `docs/dashboard_product/DASHBOARD_RELEASE_NOTES.md`.
3. Follow execution rules in `docs/dashboard_product/DASHBOARD_OPERATING_SOP.md`.
4. Use source-of-truth ownership rules in `docs/dashboard_product/DASHBOARD_DATA_OWNERSHIP.md`.

Reference set:
- `docs/dashboard_product/README.md`
- `docs/dashboard_product/DASHBOARD_CHARTER.md`
- `docs/dashboard_product/DASHBOARD_BACKLOG.md`
- `docs/dashboard_product/DASHBOARD_RELEASE_NOTES.md`
- `docs/dashboard_product/DASHBOARD_OPERATING_SOP.md`
- `docs/dashboard_product/DASHBOARD_DATA_OWNERSHIP.md`
- `docs/dashboard_product/DASHBOARD_METRICS.md`

---

## Deploy Process — source push plus automated `gh-pages` publish

```bash
git add pmforge_dashboard/index.html pmforge_dashboard/version.json
git commit -m "Dashboard: description of changes"
git push origin master
```

`gh-pages` is published by workflow: `.github/workflows/dashboard-pages-deploy.yml`

Emergency fallback only (workflow unavailable):

```bash
git fetch origin
git worktree add .gh-pages-deploy-temp gh-pages
cp pmforge_dashboard/index.html .gh-pages-deploy-temp/index.html
git -C .gh-pages-deploy-temp add index.html
git -C .gh-pages-deploy-temp commit -m "Deploy: description"
git -C .gh-pages-deploy-temp push origin gh-pages
git worktree remove .gh-pages-deploy-temp --force
```

Never use `git show master:pmforge_dashboard/index.html > index.html` redirection for deployment.

---

## What to Update — Tab by Tab

### TAB 1: Dashboard (Overview)

| Item | Where in file | How to update |
|---|---|---|
| **Last updated bar** | Top of tab-overview div | Change date text and status note |
| **RAG banner** | `.rag-banner` div | Change class (green/amber/red), label, message, date |
| **Days remaining** | `id="days-remaining"` | Auto-calculated by JS — no update needed |
| **Target release countdown** | `id="release-days-sub"` | Auto-calculated by JS — no update needed |
| **P1 blocker count** | `computeLiveTaskCounts()` from `PB_ITEMS` | Keep backlog statuses accurate (`Blocked`) |
| **Total open issues** | `computeLiveTaskCounts()` from `PB_ITEMS` | Keep backlog statuses accurate (`Done` vs non-Done) |
| **Sprint tasks done %** | `syncDashMetrics()` from active sprint board checkboxes | Add task IDs to `COMPLETED_TASKS` |
| **Burndown actual data** | `SPRINT_ARCHIVE[N].burndown.actual` | Update day-by-day remaining count |
| **Burnup completed** | `SPRINT_ARCHIVE[N].burnup.completed` | Update cumulative completed values |
| **Velocity bar** | `SPRINT_ARCHIVE[N].velocity.data` | Update active sprint delivered TA count |
| **Severity donut** | `SPRINT_ARCHIVE[N].severity` | Update `[P1, P2, P3, P4]` counts |
| **Open blockers list** | `.blocker-list` div | Add/remove blocker-item divs |

### TAB 2: Architecture

| Item | When to update |
|---|---|
| **arch-info-cards** | If new files, services, or record counts change |
| **3D node descriptions** | If infrastructure changes |

### TAB 3: Sprints

| Item | Where | When |
|---|---|---|
| **COMPLETED_TASKS array** | ~line 3180 | As sprint tasks are completed |
| **BLOCKED_TASKS array** | ~line 3189 | As tasks get blocked/unblocked |
| **TASK_DETAILS entries** | Task modal data object | Add/update per completed subtask |
| **Sprint cards** | `spage-board` div | Flip status at sprint boundaries |
| **Retrospective** | `spage-retro` div | Fill 3 cards at sprint close |
| **DoD accordion** | `spage-dod` div | Mark items met at sprint close |

Task detail requirements for each completed subtask:
- `resolution`
- `date`
- `timestamp`
- `updatedBy`

Use the Task Resolution modal manual fields:
- Enter resolution text, completion date, timestamp, and who updated it.
- `Apply In Memory` updates the page session only.
- `Copy JS Snippet` then paste into `TASK_DETAILS` in `pmforge_dashboard/index.html`.
- Commit/deploy to make the update visible to everyone.

No local storage:
- Dashboard task resolution edits do not use browser localStorage.
- Entries are shared only through committed code in `pmforge_dashboard/index.html`.

### TAB 4: Backlog

| Item | Where | When |
|---|---|---|
| **Bug status** | `#backlog-tbody` rows | Change `OPEN` → `FIXED` as bugs resolved |
| **New bugs** | Add `<tr>` to `#backlog-tbody` | When new bugs discovered |
| **Backlog stats** | `.backlog-stats` div | Update total, P1/P2/P3/P4, open, fixed counts |

### TAB 5: Risk Register

| Item | Where | When |
|---|---|---|
| **`risks[]` array** | ~line 3812 | Add new risks; change `status` open→resolved |
| **likelihood/impact** | Same array | Update if situation changes |

### TAB 6: Hours Log

| Item | Where | When |
|---|---|---|
| **`HOURS_DATA` array** | ~line 3548 | Update current week `hours` and `notes` |

### TAB 7: Decisions

| Item | Where | When |
|---|---|---|
| **`decisions[]` array** | ~line 3844 | Add new entry when architectural decision made |

### TAB 8: Weekly Report

Auto-generates from `HOURS_DATA` + `COMPLETED_TASKS`. No manual update needed unless generated text is wrong.

### TAB 9: About

| Item | When |
|---|---|
| Sprint count | Update at each sprint close |
| Infrastructure list | Update if services change |

---

## At Sprint CLOSE

- [ ] Fill Retrospective (3 cards: what went well, what didn't, what to do differently)
- [ ] Flip sprint card: closing sprint → "Done", next sprint → "Active Now"
- [ ] Update RAG banner for new sprint
- [ ] Update metrics strip sprint number + sub-text
- [ ] Verify PB item statuses are accurate (especially `Blocked` and `Done`)
- [ ] Mark DoD items met/not-met
- [ ] Add final burndown value for closing sprint
- [ ] Update burnup S_N completed value
- [ ] Update velocity bar for closed sprint (final count)
- [ ] Update About tab sprint count

## At Sprint KICKOFF

- [ ] Replace placeholder board div with full task list
- [ ] Update sprint selector default value
- [ ] Update COMPLETED_TASKS comment header for new sprint
- [ ] Confirm active sprint board checkboxes map to correct task IDs
- [ ] Add week entries to HOURS_DATA for new sprint weeks
- [ ] Update metrics: sprint name, task count, dates
- [ ] Update RAG banner

---

## Drift Checks Before Push

- `Sprint Tasks Done` top strip must match active sprint board checked count.
- `Open P1 Blockers` and `Total Open Tasks` must match PB item status counts.
- Burndown insight sentence must match current burndown array values.
- Severity insight sentence must match current severity array values.
- Blocker list text must match current active risks in sprint.

---

## Key JS Arrays (all hardcoded — Claude owns these)

```js
COMPLETED_TASKS = ['t1_1', 't1_2', ...]   // sprint task IDs marked done
BLOCKED_TASKS   = []                        // sprint task IDs that are blocked
HOURS_DATA      = [{ num, dates, sprint, hours, notes }, ...]
risks           = [{ id, risk, like, impact, mitigation, sprint, status }, ...]
decisions       = [{ id, date, sprint, title, chosen, considered, why }, ...]
```

## What Is Automatic (Never Needs Manual Update)

- Sprint days remaining countdown (JS)
- Target release countdown (JS)
- Live clock (JS)
- Weekly Report text (generates from arrays)
- Gantt today marker position (JS)
- Sprint task % / progress bar (reads COMPLETED_TASKS)

---

## EC2 / Infrastructure Notes

- **SSH:** `ssh -i /c/Users/april/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249`
- **Start EC2 via CLI (if console locked):** `aws ec2 start-instances --region us-east-1 --instance-ids i-076502f470ab36343`
- **Health check:** `curl http://34.198.25.249:5000/health`
- **AWS root MFA locked** — call 1-800-879-2747 to reset (as of Apr 10, 2026)
