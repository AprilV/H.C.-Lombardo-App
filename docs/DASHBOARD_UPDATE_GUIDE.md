# Dashboard Update Guide

**File:** `Dashboard/index.html` (single file, ~4000+ lines, all data hardcoded)
**Live URL:** https://aprilv.github.io/H.C.-Lombardo-App/
**April does not edit this file directly — Claude owns all updates.**

---

## How Updates Work

April and Claude go through the dashboard together each session. April reports what happened (hours worked, tasks done, bugs found/fixed, decisions made, risks). Claude makes all the changes and deploys.

**One session = one topic.** Don't stack multiple unrelated changes.

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
git add Dashboard/index.html
git commit -m "Dashboard: description of changes"
git push origin master
```

`gh-pages` is published by workflow: `.github/workflows/dashboard-pages-deploy.yml`

Emergency fallback only (workflow unavailable):

```bash
git fetch origin
git worktree add .gh-pages-deploy-temp gh-pages
cp Dashboard/index.html .gh-pages-deploy-temp/index.html
git -C .gh-pages-deploy-temp add index.html
git -C .gh-pages-deploy-temp commit -m "Deploy: description"
git -C .gh-pages-deploy-temp push origin gh-pages
git worktree remove .gh-pages-deploy-temp --force
```

Never use `git show master:Dashboard/index.html > index.html` redirection for deployment.

---

## What to Update — Tab by Tab

### TAB 1: Dashboard (Overview)

| Item | Where in file | How to update |
|---|---|---|
| **Last updated bar** | Top of tab-overview div | Change date text and status note |
| **RAG banner** | `.rag-banner` div | Change class (green/amber/red), label, message, date |
| **Days remaining** | `id="days-remaining"` | Auto-calculated by JS — no update needed |
| **Target release countdown** | `id="release-days-sub"` | Auto-calculated by JS — no update needed |
| **P1 blocker count** | `.pm-metric` strip | Update value + sub-text |
| **Total open issues** | `.pm-metric` strip | Update value + sub-text |
| **Sprint tasks done %** | Driven by `COMPLETED_TASKS` array | Add task IDs to array |
| **Burndown actual data** | `chartInstances.burndown` data array | Update day-by-day remaining count |
| **Burnup completed** | `chartInstances.burnup` completed dataset | Update S12 value at sprint close |
| **Velocity bar** | `chartInstances.velocity` data array | Update current sprint bar (last value) |
| **Severity donut** | `chartInstances.severity` data array | Update `[P1, P2, P3, P4]` counts |
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
- `Copy JS Snippet` then paste into `TASK_DETAILS` in `Dashboard/index.html`.
- Commit/deploy to make the update visible to everyone.

No local storage:
- Dashboard task resolution edits do not use browser localStorage.
- Entries are shared only through committed code in `Dashboard/index.html`.

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
- [ ] Mark DoD items met/not-met
- [ ] Add final burndown value for closing sprint
- [ ] Update burnup S_N completed value
- [ ] Update velocity bar for closed sprint (final count)
- [ ] Update About tab sprint count

## At Sprint KICKOFF

- [ ] Replace placeholder board div with full task list
- [ ] Update sprint selector default value
- [ ] Update COMPLETED_TASKS comment header for new sprint
- [ ] Add week entries to HOURS_DATA for new sprint weeks
- [ ] Update metrics: sprint name, task count, dates
- [ ] Update RAG banner

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
