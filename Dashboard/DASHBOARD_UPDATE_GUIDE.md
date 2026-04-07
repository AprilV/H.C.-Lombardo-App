# Dashboard Update Guide
**Who:** April tells Claude what happened. Claude updates the file and deploys to gh-pages.
**Live site:** https://aprilv.github.io/H.C.-Lombardo-App/
**Rule:** Zero localStorage. Everything hardcoded. Everything visible to everyone.

---

## What April tells Claude each week:
1. Hours worked that week
2. What was worked on (1-2 sentences for notes)
3. Which sprint tasks got completed (by name or area)
4. Any issues that came up and how they were handled
5. Prevention — how could the issue have been avoided
6. Any new bugs discovered
7. Any new risks

---

## EVERY WEEK — Claude updates these:

| # | What | Where in code |
|---|------|--------------|
| 1 | `HOURS_DATA` — hours + notes for the week | JS ~line 3432 |
| 2 | `ISSUES_DATA` — issues + prevention text | JS ~line 3757 |
| 3 | `COMPLETED_TASKS` — task IDs checked off | JS ~line 3023 |
| 4 | Burndown chart — add actual data point | JS chart data ~line 3292 |
| 5 | RAG status message | HTML line 1680 |
| 6 | RAG "Updated" date | HTML line 1682 |

---

## AT SPRINT CLOSE ONLY — Claude updates these:

| # | What | Where |
|---|------|-------|
| 7  | Retrospective — hardcode three answers | Sprint tab retro HTML |
| 8  | Velocity chart — add closed issues count | JS chart data |
| 9  | Burnup chart — update completed work bar | JS chart data |
| 10 | Sprint card — active→completed, next→active | Sprint Plan tab HTML |
| 11 | Sprint board — replace with next sprint tasks | Sprint tab HTML |
| 12 | Nav tab label — e.g. ⚡ Sprint 12 → ⚡ Sprint 13 | Nav HTML |
| 13 | Open blockers — remove fixed, add new | Overview tab HTML |
| 14 | Backlog — update OPEN → FIXED | Backlog table HTML |
| 15 | Risk register — update status, add new risks | JS risks array |
| 16 | Definition of Done — mark sprint complete | Sprint Plan accordion |

---

## AUTOMATIC — never touch:
- Gantt today marker (date-calculated)
- Days remaining counter (date-calculated)
- Sprint task progress % and counts (reads COMPLETED_TASKS)
- Week selector default on Weekly Report tab (date-calculated)

---

## Deploy command — run every time, no exceptions:
```bash
cd "c:\ReactGitEC2\IS330\H.C Lombardo App"
git add Dashboard/index.html
git commit -m "Weekly update: Week N"
git checkout gh-pages
git show master:Dashboard/index.html > index.html
git add index.html
git commit -m "Deploy: Weekly update Week N"
git push origin gh-pages
git checkout master
git push origin master
```
**ALWAYS deploy to gh-pages. Master alone does nothing to the live site.**
