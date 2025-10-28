# Workspace Cleanup Test Plan

## Objective
Test moving test files to testbed/ and renaming dr.foster.md to 00_DR_FOSTER.md for visibility

## Changes to Test
1. Move all test_*.py files from root → testbed/
2. Rename dr.foster.md → 00_DR_FOSTER.md

## Test Steps

### Step 1: Verify Test Files Don't Break
- Copy test files to testbed/workspace_cleanup_test/
- Try running them from new location
- Check if they can still import from root (api_server, db_config, etc.)

### Step 2: Verify Rename Works
- Test that 00_DR_FOSTER.md sorts to top of file list
- Ensure content is preserved

### Step 3: Production Rollout
- Only proceed if ALL tests pass
- Create git commit before changes
- Move files one at a time
- Verify after each move
- Commit and push

## Success Criteria
✅ Test files run successfully from testbed/
✅ Imports work correctly from new location  
✅ 00_DR_FOSTER.md appears at top of file list
✅ No errors, no broken paths

## Rollback Plan
- Git reset if needed: `git reset --hard HEAD~1`
- All changes are reversible
