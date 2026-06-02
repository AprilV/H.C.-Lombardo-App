# START_HERE

Use this folder as a portable governance kit for any coding project.

## What You Copy
Copy all contents of this folder into the target project root.

Minimum expected structure after copy:

```text
docs/ai_reference/
scripts/maintenance/
sessions/
.github/
```

## One-Time Setup In New Project
1. Copy this kit into the new repository root.
2. Merge `.github/copilot-instructions.md` snippet into the instruction file used by your assistant.
3. Fill placeholders in:
   - `docs/ai_reference/READ_THIS_FIRST.md`
   - `docs/ai_reference/ARCHITECTURE.md`
   - `docs/ai_reference/TOPOLOGY.md`
4. Run startup checkpoint once:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
```

5. Confirm a new session file exists in `sessions/`:

```powershell
Get-ChildItem sessions -Filter "SESSION_RESUME_*.md" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 -ExpandProperty FullName
```

## Trigger In Chat
Use any trigger phrase:
- EXECUTE ORDER 66
- RUN STARTUP LOCK
- LOOK AT CHAT_STARTUP_LOCK AND EXECUTE

## Required Startup Summary Fields
Before coding begins, the assistant must report:
1. Scope priority
2. Uncommitted working set
3. Verification snapshot status
4. Read matrix status
5. Exclusion list
6. Commit policy status
7. Resource expenditure status
