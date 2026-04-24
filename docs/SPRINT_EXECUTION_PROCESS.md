# Sprint Execution Process

## How We Work Through a Sprint

We go through each TA task one section at a time. Every section is completed before moving to the next. No batching.

---

## The Process — Every Time

**Step 1: Run the check**
Execute whatever the task requires — curl an endpoint, SSH the server, open the app in a browser, check a file. Do the actual work.

**Step 2: Log any issues found**
If a problem is discovered, add it to the Product Backlog immediately as a new TA item (next available TA-xxx ID) in `BACKLOG_DATA` inside `Dashboard/index.html`. Do NOT fix it during this sprint. Fixing goes in a future sprint.

**Step 3: Mark the subtasks done**
Add the completed task IDs to `COMPLETED_TASKS` and resolutions to `TASK_DETAILS` in `Dashboard/index.html` right now — not at the end.

**Step 4: Update ALL charts and metrics — every time, no exceptions**
- Count total tasks now in COMPLETED_TASKS. Remaining = 83 minus that count.
- Burndown `Actual Remaining` array — update current day's value to new remaining count
- Burndown insight text — update done/total and remaining list
- Burnup S12 value — update only when a full TA ticket flips to Done
- Velocity S12 — update only when a full TA ticket flips to Done
- BACKLOG_DATA status — flip ticket to Done when all its subtasks are complete
- "Dashboard last updated" line — update date/message

**Step 5: Commit and deploy**
```
git add Dashboard/index.html
git commit -m "TA-00X [section name] done"
git push origin master
```

`gh-pages` deploy is automated by workflow: `.github/workflows/dashboard-pages-deploy.yml`

Emergency fallback only (workflow unavailable):
```
git fetch origin
git worktree add .gh-pages-deploy-temp gh-pages
cp Dashboard/index.html .gh-pages-deploy-temp/index.html
git -C .gh-pages-deploy-temp add index.html
git -C .gh-pages-deploy-temp commit -m "Deploy: TA-00X [section name] done"
git -C .gh-pages-deploy-temp push origin gh-pages
git worktree remove .gh-pages-deploy-temp --force
```

Do not use `git show ... > index.html` redirection for deployment.

**Step 5: Move to the next section.**

---

## Rules

- **Never leave tasks done in your head without the dashboard reflecting it.**
- **Never fix problems discovered during audit tasks.** Log them to backlog, close the subtask, move on.
- **Never batch up multiple sections and update at the end.** One section = one commit = one deploy.
- **Sprint board, backlog status, and home page charts must all stay in sync.**

---

## Adding a New Backlog Item

Add to the `items` array in `Dashboard/index.html` after the last TA entry:

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

In `Dashboard/index.html`, find the `TASK_DETAILS` object and add an entry:

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
