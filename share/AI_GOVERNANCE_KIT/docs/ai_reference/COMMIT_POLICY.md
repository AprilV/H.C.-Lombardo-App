# COMMIT_POLICY

## Purpose
Define clear, repeatable git commit controls for AI-assisted execution.

## Non-Negotiable Rules
1. No automatic commits unless explicitly requested by the user.
2. No amend, rebase, reset, or force-push unless explicitly requested.
3. Do not include unrelated files in the same commit.
4. Keep commit scope to one objective whenever possible.

## Pre-Commit Gate
- Confirm requested scope is complete.
- Confirm staged files are only in-scope.
- Run relevant verification checks or record why skipped.
- Ensure generated artifacts are intentional for version control.

## Commit Message Standard
Use imperative style and include task intent.

Examples:
- Add startup lock read matrix validation
- Fix session resume guard check parsing
- Update governance docs for resource policy thresholds

## Post-Commit Proof
After each commit, report:
- Commit hash
- Commit title
- Changed files summary
- Any remaining uncommitted files

## Push Policy
- Push only when requested.
- After push, confirm branch sync state with remote.

## Unsafe Patterns To Reject By Default
- Bulk committing all untracked files
- Combining feature work and unrelated cleanup
- Rewriting published history without approval
