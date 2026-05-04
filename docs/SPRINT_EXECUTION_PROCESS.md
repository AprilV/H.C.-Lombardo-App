# Sprint Execution Process

## How We Work Through a Sprint

We go through each TA task one section at a time. Every section is completed before moving to the next. No batching.

---

## The Process — Every Time

**Step 1: Run the check**
Execute whatever the task requires — curl an endpoint, SSH the server, open the app in a browser, check a file. Do the actual work.

**Step 2: Log any issues found**
If a problem is discovered, add it to the Product Backlog immediately as a new TA item (next available TA-xxx ID) in `BACKLOG_DATA` inside `pmforge_dashboard/index.html`. Do NOT fix it during this sprint. Fixing goes in a future sprint.

**Step 3: Mark the subtasks done**
Add the completed task IDs to `COMPLETED_TASKS` and resolutions to `TASK_DETAILS` in `pmforge_dashboard/index.html` right now - not at the end.

**Step 4: Update ALL charts and metrics — every time, no exceptions**
- Determine active sprint (`CURRENT_DASH_SPRINT`) and use that sprint's board totals.
- Update active sprint done-state: `COMPLETED_TASKS` + matching `TASK_DETAILS` entry.
- Update backlog ticket statuses in `PB_ITEMS` (`Done`, `In Progress`, `Blocked`, `To Do`).
- Verify top-strip metrics are consistent:
	- Sprint Tasks Done = active sprint board checked count
	- Open P1 Blockers = count of `PB_ITEMS` with status `Blocked`
	- Total Open Tasks = count of `PB_ITEMS` with status != `Done`
- Update active `SPRINT_ARCHIVE[N]` chart data:
	- `burndown.actual`
	- `burnup.completed`
	- `velocity.data`
	- `severity`
- Update chart insight text and RAG message so narrative matches the chart values.
- Update open blockers list text so it matches current active risks.
- Update "Dashboard last updated" line/date context.
- Run rollover verification gate in `docs/dashboard_product/DASHBOARD_SPRINT_ROLLOVER_AUTOMATION_RUNBOOK.md` before declaring chart automation complete.

**Step 5: Commit and deploy**
```
git add pmforge_dashboard/index.html pmforge_dashboard/version.json
git commit -m "TA-00X [section name] done"
git push origin master
```

`gh-pages` deploy is automated by workflow: `.github/workflows/dashboard-pages-deploy.yml`

Emergency fallback only (workflow unavailable):
```
git fetch origin
git worktree add .gh-pages-deploy-temp gh-pages
cp pmforge_dashboard/index.html .gh-pages-deploy-temp/index.html
git -C .gh-pages-deploy-temp add index.html
git -C .gh-pages-deploy-temp commit -m "Deploy: TA-00X [section name] done"
git -C .gh-pages-deploy-temp push origin gh-pages
git worktree remove .gh-pages-deploy-temp --force
```

Do not use `git show ... > index.html` redirection for deployment.

**Step 5: Move to the next section.**

Note: The section numbering above intentionally keeps historical commit-message format. Deploy step remains required before moving on.

---

## Rules

- **Never leave tasks done in your head without the dashboard reflecting it.**
- **Never fix problems discovered during audit tasks.** Log them to backlog, close the subtask, move on.
- **Never batch up multiple sections and update at the end.** One section = one commit = one deploy.
- **Sprint board, backlog status, and home page charts must all stay in sync.**
- **Never update only text.** Arrays (`COMPLETED_TASKS`, `PB_ITEMS`, `SPRINT_ARCHIVE`) must be updated first, then narrative text.
- **Never push with drift.** If top-strip numbers disagree with board/backlog counts, stop and fix before commit.

---

## Adding a New Backlog Item

Add to the `items` array in `pmforge_dashboard/index.html` after the last TA entry:

```javascript
{ id:'TA-054', feature:'Description of issue found', cat:'Backend', pri:'High', effort:'S', sprint:'TBD', status:'Backlog' },
```

Priority: Critical / High / Medium / Low  
Effort: XS / S / M / L  
Sprint: always TBD until sprint planning assigns it.

---

## Task Resolution Modal

Each task on the Sprint Board is clickable. Clicking a task title opens a modal showing:
- TA ticket it belongs to
- Task title
- Status (Done / To Do / Blocked)
- Resolution — what was done to complete it
- Date completed
- Any issues logged to backlog as a result

**How to add a resolution when marking a task done:**

In `pmforge_dashboard/index.html`, find the `TASK_DETAILS` object and add an entry:

```javascript
t3_4: { resolution: 'What was done to complete this task.', date: 'Apr 17, 2026' },
// If issues were found and logged:
t3_5: { resolution: 'Tested endpoint — returned error. Issue logged.', date: 'Apr 17, 2026', issues: ['TA-054'] },
```

The key is the task ID (matches the checkbox id in the HTML, e.g. `t3_4`).
Resolution is always added at the same time the task is moved to COMPLETED_TASKS.

---

## At Sprint Close

1. Fill in the Retrospective (3 cards: what went well, what didn't, what to do differently)
2. Flip closing sprint card → Done, next sprint card → Active
3. Update RAG banner
4. Update velocity chart with final sprint count
5. Update burnup with final value
6. Update HOURS_DATA for any remaining hours
