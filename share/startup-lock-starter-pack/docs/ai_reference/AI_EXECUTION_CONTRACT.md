# AI_EXECUTION_CONTRACT

## Authority
This contract defines non-negotiable operating rules for AI execution in this repository.

## Hard Rules
1. Do not run destructive commands without explicit approval.
2. Do not silently expand task scope.
3. Do not claim completion without verification evidence.
4. Do not revert unrelated user changes.
5. If blocked, stop and report blocker clearly.

## Change Control
- Read relevant files before editing.
- Make smallest viable change first.
- Preserve existing style and public behavior unless change request says otherwise.
- Keep unrelated files untouched.

## Verification Rules
- Run the smallest relevant runtime checks for the change.
- Summarize check output in final report.
- State explicitly what was not run and why.

## Startup Lock Requirement
- Trigger phrase `EXECUTE ORDER 66` requires startup lock before implementation.
- Startup lock is incomplete if summary fields are missing.

## Escalation
- Missing required docs: report missing files, request approval to create.
- Runtime unavailable: report current status and safe next action.
