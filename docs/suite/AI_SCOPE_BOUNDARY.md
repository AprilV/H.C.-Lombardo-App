# AI Scope Boundary: H.C. Workspace vs PM Forge Suite Workspace

Status: Active
Applies to: All AI assistants and developers

## Intent

PM Forge is a standalone software suite product.
H.C. Lombardo is a consumer/integration host.

This workspace (`H.C Lombardo`) is not the canonical development location for PM Forge Suite source.

## Mandatory Boundary

1. Do not perform PM Forge Suite feature development in this workspace.
2. Do not treat H.C. as the PM Forge source of truth.
3. Perform PM Forge Suite development only in `C:\PMForgeSuite` (standalone repo).

## Allowed Work in This Workspace (H.C.)

1. Import approved PM Forge Suite output into H.C. (`pmforge_dashboard/*`).
2. Validate H.C. integration behavior after import.
3. Update H.C.-specific app code, docs, and deployment workflows.
4. Optionally mirror into `backups/legacy_dashboard/index.html` only when explicitly requested.

## Prohibited Work in This Workspace (H.C.)

1. Building new PM Forge Suite features directly in H.C.
2. Maintaining parallel PM Forge logic in H.C. and standalone Suite.
3. Treating H.C. dashboard edits as upstream PM Forge source.

## Operating Model

1. Develop PM Forge Suite in standalone repo (`C:\PMForgeSuite`).
2. Export/prepare approved Suite version in standalone repo.
3. Import into H.C. using `scripts/suite/import_pmforge_suite.ps1`.
4. Validate H.C. runtime and UI after import.
5. Deploy H.C. when ready.

## Default Safety Rule

Importer default updates `pmforge_dashboard/*` only.
Legacy archive overwrite (`backups/legacy_dashboard/index.html`) is opt-in.

## Decision Rule for AI

If requested work is a PM Forge Suite feature change:

1. Stop in H.C. workspace.
2. State that change belongs in `C:\PMForgeSuite`.
3. Proceed only with import/integration steps in H.C. unless explicitly redirected.