# Agile Process Guide — H.C. Lombardo App
**Applies to:** Spring 2026 Term (Sprints 12–16)
**Owner:** April V. Sykes

---

## WHY AGILE

This project has a hard deadline (end of term), shifting requirements (the app is broken and we don't know exactly how broken until we look), and one developer. A lightweight Scrum-inspired process keeps work visible, prevents scope creep, and makes sure every session moves the needle.

---

## OUR PROCESS

### The Basics

- **Sprint length:** 2 weeks
- **Sprint ceremony:** Start-of-sprint planning (with Claude), end-of-sprint review
- **Backlog:** `docs/sprints/PRODUCT_BACKLOG.md` — all work items, prioritized
- **Sprint plan:** `docs/sprints/SPRINT_PLAN_S12_S16.md` — what goes in each sprint
- **Sprint reports:** One file per sprint in `docs/sprints/` after it completes
- **Working agreement:** AI_EXECUTION_CONTRACT.md governs all code changes

---

## SPRINT LIFECYCLE

### 1. Sprint Planning (start of each sprint)
- Review the sprint backlog in SPRINT_PLAN_S12_S16.md
- Confirm which items carry over from the previous sprint
- Add any new issues discovered (update PRODUCT_BACKLOG.md)
- Assign P1 items first — they must complete before P2s start

### 2. Daily Work Sessions
- Open VS Code — chat session continues if window was not closed
- If starting a new session, say: **"Continue Sprint [N]"**
  - Claude will load memory and pick up where we left off
- Work through the sprint backlog top-to-bottom
- After each completed item: update status in PRODUCT_BACKLOG.md
- Before closing VS Code: say **"save our context"**
  - Claude saves current state to memory files

### 3. Sprint Review (end of each sprint)
- Go through every item in the sprint
- Mark DONE in PRODUCT_BACKLOG.md
- Write sprint report (use previous sprint reports as template)
- Identify blockers and carry-overs for the next sprint
- Demo any new features (even if just to yourself)

### 4. Between Sprints
- One-day buffer for any carry-overs or cleanup
- Update SPRINT_PLAN_S12_S16.md for the upcoming sprint
- Commit everything to GitHub before starting the next sprint

---

## WORKING WITH CLAUDE

### Starting a Session
Say one of these to orient Claude:
- `"Continue Sprint 12"` — picks up where you left off
- `"Let's start Sprint 13"` — begins new sprint planning
- `"What's the status on [task]"` — check current state
- `"What should I do next?"` — Claude will consult backlog

### During Work
- Claude will **always read required docs first** before making changes
  (AI_EXECUTION_CONTRACT.md → READ_THIS_FIRST.md → BEST_PRACTICES.md)
- Claude will **ask before assuming** scope, environment, or intent
- Claude will **identify all impacted files** before changing anything
- Claude will **not leave dead code** — if something is removed, it's gone

### Before Closing VS Code
Always say: **"save our context"**
Claude will update memory files so the next session starts with full context.

### When Something Breaks
Say: **"Stop — [describe what broke]"**
Claude will stop, diagnose, and confirm the fix before proceeding.

---

## DEFINITION OF DONE

A task is DONE when:
1. Code is written and works correctly
2. No dead code, debug prints, or commented-out code left behind
3. Change is tested (locally and/or in production)
4. PRODUCT_BACKLOG.md is updated (status → DONE)
5. Changes are committed to GitHub

A sprint is DONE when:
1. All P1 items are DONE
2. P2 items that were started are DONE or explicitly moved to next sprint
3. Sprint report is written and committed
4. CLAUDE.md is updated if project state changed significantly

---

## DEFINITION OF READY

An item is READY to work on when:
1. It has a clear description and acceptance criteria
2. Dependencies are met (e.g., can't retrain ML until data is loaded)
3. It's not blocked by an unresolved issue
4. Size is understood (S / M / L)

---

## BACKLOG MANAGEMENT RULES

1. **New bugs found** → Add to PRODUCT_BACKLOG.md immediately with P1/P2/P3
2. **Scope creep** → Add to backlog, do NOT start until current sprint is done
3. **Priority changes** → Discuss and update backlog; don't silently reprioritize
4. **Done items** → Mark DONE in backlog; do not delete (history matters)
5. **Carry-overs** → Move to next sprint with a note explaining why

---

## DEPENDENCY MAP

Some items can't start until others are done. Key dependencies:

```
PRD-1, PRD-2, PRD-8 (verify EC2 is up)
    ↓
PRD-4 (test all API endpoints)
    ↓
PRD-5, PRD-6 (audit production, create issue log)

DAT-1 (find data source)
    ↓
DAT-2 (load hcl.games)
    ↓
DAT-3 (load team_game_stats)
    ↓
DAT-4, DAT-5, DAT-6 (verify integrity)
    ↓
ML-1, ML-2, ML-4 (retrain models)
    ↓
ML-3, ML-7 (validate + display results)
```

**Don't retrain ML until 2025 data is loaded and verified.**
**Don't mark production fixed until you've tested in the actual browser.**

---

## RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| EC2 instance stopped/terminated | Medium | High | Check AWS console first session |
| 2025 data hard to get in right format | Medium | High | Budget a full sprint day for DAT-2/3 |
| ML accuracy doesn't improve after retrain | Medium | Medium | Document honestly; accuracy analysis is the deliverable |
| Production deployment breaks something new | Low | High | Always test locally before pushing to master |
| VS Code context lost between sessions | High | Low | Memory files + "save our context" habit |
| Scope grows beyond 10 weeks | Medium | Medium | Strict P1-only focus if behind schedule |

---

## ESCALATION PATH

If something is stuck or unclear:
1. Stop — don't keep pushing broken code
2. Say: **"I'm stuck on [X] — what are my options?"**
3. Claude will present options, you decide
4. If involving Dr. Foster (class requirement), document it in sprint notes

---

## COMMUNICATION LOG (with Dr. Foster)

Keep a brief record of any instructor conversations that affect scope or priorities.

| Date | Topic | Decision |
|------|-------|---------|
| April 2026 | Continuing app development as senior project | Approved by Dr. Foster |

Add to this table whenever course requirements change.

---

## SPRINT REPORT TEMPLATE

Copy this for each completed sprint:

```markdown
# Sprint [N]: [Theme] — COMPLETE
**Dates:** [start] – [end]
**Goal:** [one sentence]

## Completed
- [item] — [brief note]

## Carry-Over to Sprint [N+1]
- [item] — [why it moved]

## Blockers Encountered
- [what was blocking] — [how resolved or still open]

## Metrics
- Items completed: X / Y
- P1s completed: X / Y

## Notes
[anything worth remembering for future sprints]
```

---

*Last updated: April 3, 2026*
*Owner: April V. Sykes*
*Course: IS330 — Olympic College*
