# Suite Window Handoff Prompt (Pre-H.C. Cleanup)

Paste this entire message into the Suite-only VS Code chat.

---

You are working only in the standalone PM Forge Suite repository at C:\PMForgeSuite.

Mission:
Run a strict pre-cleanup readiness audit so we can safely clean Suite-related items from the H.C. Lombardo environment afterward.

Important context from the other window (already completed):
1. Suite has been split to standalone at C:\PMForgeSuite.
2. H.C. acts as consumer via pmforge_dashboard import flow.
3. H.C. runtime decoupling check was done: no suite route registration in api_server.py.
4. Bridge markers were removed from dashboard copies.
5. Known editor-only warning exists in H.C. for import script diagnostics, but script parse and execution succeed.
6. AI guardrail docs were copied into Suite docs/ai_reference.

Hard constraints:
1. Non-destructive only. No deletes, no resets, no force checkout.
2. Verify first, fix only if clearly needed and minimal.
3. Use evidence-based checks, not assumptions.
4. If anything is inconsistent, stop and report before additional edits.

Required first action:
Read and confirm these Suite docs before any other step:
1. docs/ai_reference/AI_EXECUTION_CONTRACT.md
2. docs/ai_reference/READ_THIS_FIRST.md
3. docs/ai_reference/BEST_PRACTICES.md
4. docs/ai_reference/AI_VIOLATION_CHECKLIST.md

Audit checklist:

1. Repository baseline
1. Confirm working root is C:\PMForgeSuite.
2. Report git status summary (modified/untracked only). Do not discard changes.

2. Required Suite assets
1. Confirm these files exist and are non-empty:
  - src/pmforge_dashboard/index.html
  - VERSION
  - scripts/export_pmforge_suite.ps1
  - docs/ai_reference/AI_EXECUTION_CONTRACT.md
  - docs/ai_reference/READ_THIS_FIRST.md
  - docs/ai_reference/BEST_PRACTICES.md
  - docs/ai_reference/AI_VIOLATION_CHECKLIST.md

3. Version and package export
1. Read VERSION and report the value.
2. Run scripts/export_pmforge_suite.ps1 for that version.
3. Confirm dist package exists for that version and report file size and timestamp.

4. Dashboard integrity in Suite source
1. Verify src/pmforge_dashboard/index.html does not contain:
  - Suite Phase 1/2 bridge
  - SUITE_API_BASE
  - suite-bridge-status
2. Verify src/pmforge_dashboard/index.html does not contain common mojibake tokens:
  - Ã
  - â”€
  - â€¢
  - ðŸ
  - â†
3. Verify UTF-8 BOM status for src/pmforge_dashboard/index.html.

5. Import readiness for H.C. consumer
1. Confirm Suite source path expected by importer exists:
  - src/pmforge_dashboard/index.html
2. Confirm latest export artifact is available in dist for import.
3. Do not perform H.C. cleanup actions in this window.

Response format required:
1. PASS/FAIL for each checklist section.
2. Exact evidence used for each section (commands and key outputs).
3. Blockers with severity:
  - blocker
  - warning
  - info
4. If any fixes were applied, list each changed file and reason.
5. Final recommendation:
  - GO for H.C. cleanup
  - NO-GO with clear reasons

Do not begin cleanup. This window is Suite readiness verification only.
