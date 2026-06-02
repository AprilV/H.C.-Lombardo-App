# PORTING_CHECKLIST

Use this checklist when copying this governance kit into a new repository.

## Copy Phase
- [ ] Copy entire folder contents into target repository root.
- [ ] Confirm target now contains `docs/ai_reference`, `scripts/maintenance`, `sessions`, and `.github`.

## Configuration Phase
- [ ] Fill project mission and scope in `docs/ai_reference/READ_THIS_FIRST.md`.
- [ ] Fill architecture/topology placeholders:
  - `docs/ai_reference/ARCHITECTURE.md`
  - `docs/ai_reference/TOPOLOGY.md`
- [ ] Confirm branch and merge conventions in topology doc.
- [ ] Adjust cost tiers if needed in `docs/ai_reference/RESOURCE_EXPENDITURE_POLICY.md`.

## Instruction Merge Phase
- [ ] Merge startup lock trigger section from `.github/copilot-instructions.md` into the repo instruction file used by your assistant.
- [ ] Verify trigger phrases include:
  - EXECUTE ORDER 66
  - RUN STARTUP LOCK
  - LOOK AT CHAT_STARTUP_LOCK AND EXECUTE

## Validation Phase
- [ ] Run guard script once:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
```

- [ ] Verify newest resume exists in `sessions/` with name `SESSION_RESUME_YYYY-MM-DD_HHMM.md`.
- [ ] Trigger startup lock in chat and verify summary includes:
  - scope priority
  - uncommitted working set
  - verification snapshot status
  - read matrix status
  - exclusion list
  - commit policy status
  - resource expenditure status
