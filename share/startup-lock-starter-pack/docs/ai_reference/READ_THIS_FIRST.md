# READ_THIS_FIRST

## Project Mission
Describe the product in 2-4 lines.

Example:
This project provides <core outcome> for <primary users>.
The near-term objective is <current release objective>.

## Current Priority Lock
1. Primary scope: <fill this in>
2. Secondary scope: <fill this in>

## Definition Of Done
- Scope requirements are fully implemented.
- Runtime evidence exists for key behavior.
- Required docs are updated.
- Risks and unverified areas are explicitly listed.

## Failure Modes To Avoid
1. Silent scope drift.
2. Claiming completion without runtime evidence.
3. Editing unrelated files.
4. Skipping startup lock and operating on stale context.

## Startup Sequence
1. Run startup checkpoint script.
2. Read newest session resume in sessions/.
3. Read startup matrix documents in required order.
4. Return startup summary before implementation.
5. Only then start coding.
