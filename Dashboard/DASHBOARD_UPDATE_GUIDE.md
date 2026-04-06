# Dashboard Update Guide
**Who does what:** April tells Claude what happened. Claude updates the file and deploys to gh-pages. Professor and employers see everything at https://aprilv.github.io/H.C.-Lombardo-App/

---

## Every Week — April tells Claude:
1. **Hours worked** that week + brief description of what was worked on
2. **Sprint tasks completed** (or just say "check off X, Y, Z on the board")
3. **Any new blockers or bugs** discovered
4. **Any risks that came up** (for risk register)

Claude then updates everything and deploys in one shot.

---

## What Claude Updates Each Week

### Hours Log (hardcoded — replaces localStorage)
- `Week N hours` — the number April provides
- `Week N notes` — what was worked on
- `Total hours` — running sum
- **Location:** Hours Log tab data array in the JS

### Weekly Report Tab
- Pre-renders the current week's report from live data
- Pulls: hours, tasks done, tasks not done, next week goals
- April fills in: issues + prevention (the only manual part)
- **Location:** Report JS data / rendered output

### Sprint Board (Overview + Sprint 12 tab)
- `Sprint Tasks Done` count on Overview metrics strip
- `Progress %` bar on Sprint 12 board
- Burndown chart — actual remaining tasks line (one data point per day)
- Burnup chart — completed work bar for S12
- **Location:** Chart data arrays in JS (~line 3200)

### Sprint Status (end of each sprint)
- Sprint card status: active → completed, next sprint → active
- RAG status message (green/amber/red banner)
- "Updated" date on RAG banner
- Sprint tab label (e.g. ⚡ Sprint 12 → ⚡ Sprint 13)
- Velocity chart — add S12 bar at sprint close
- **Location:** Sprint Plan tab HTML + nav tab HTML + chart data

### Open Blockers (as bugs are fixed)
- Remove fixed blockers from the blocker list
- Update bug status in Backlog tab (OPEN → CLOSED)
- **Location:** Overview tab blocker-list HTML + Backlog table

### Retrospective (end of each sprint)
- April dictates the three answers (what went well, what didn't, what changes)
- Claude hardcodes them into the retro panel — no longer localStorage
- **Location:** Sprint 12 retro textarea values → hardcoded text

### Risk Register (as risks change)
- Update status: open → resolved / accepted
- Add new risks discovered during the sprint
- **Location:** risks array in JS (~line 3560)

### Gantt Chart
- Sprint bars auto-calculate from dates — no update needed
- Today marker is automatic
- Completion % pulls from sprint board checkboxes — automatic

### KPIs / Metrics Strip (as data becomes available)
- "Days remaining" — auto-calculates from today's date (automatic)
- "Sprint Tasks Done" — syncs from sprint board checkboxes (automatic)
- Live app URL — update once production is confirmed (Sprint 12 PRD-3)
- **Location:** Overview JS syncDashMetrics()

---

## End of Each Sprint — Additional Updates

| Item | What changes |
|------|-------------|
| Sprint card | active → completed (green), next → active (red) |
| Sprint tab in nav | Update to next sprint number |
| Sprint board | Replace S12 board content with next sprint tasks |
| Definition of Done | Mark sprint as complete in accordion |
| Velocity chart | Add closed issues count for completed sprint |
| Retrospective | Hardcode April's answers, add retro for next sprint |
| Burndown | Reset for new sprint |

---

## What NEVER needs updating (static/automatic)
- Gantt bar positions (date-calculated)
- Today marker on Gantt
- Days remaining counter
- Decision Log (set once, stable)
- Architecture diagram
- About tab
- Sprint Plan dates
- Definition of Done criteria

---

## Deploy Command (Claude runs this every time)
```bash
cd "c:\ReactGitEC2\IS330\H.C Lombardo App"
git add Dashboard/index.html
git commit -m "message"
git checkout gh-pages
git show master:Dashboard/index.html > index.html
git add index.html
git commit -m "Deploy: message"
git push origin gh-pages
git checkout master
git push origin master
```
**Always deploy to gh-pages — that is the live site. Master alone does nothing.**
