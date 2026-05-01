# PM Forge Split Workflow

This repo (H.C. Lombardo) is the consumer/demo host.
PM Forge Suite is developed independently at C:\PMForgeSuite.

## Current Policy

- Suite development happens only in C:\PMForgeSuite.
- H.C. keeps a consumer copy at pmforge_dashboard/index.html.
- Legacy dashboard archive mirroring is optional and disabled by default.
- AI scope rules for this workspace are defined in docs/suite/AI_SCOPE_BOUNDARY.md.

## Import Approved Suite Into H.C.

Run from H.C. repo root:

```powershell
.\scripts\suite\import_pmforge_suite.ps1 -SuiteRoot "C:\PMForgeSuite" -Version "v1.0.0"
```

To also mirror into backups/legacy_dashboard/index.html (opt-in):

```powershell
.\scripts\suite\import_pmforge_suite.ps1 -SuiteRoot "C:\PMForgeSuite" -Version "v1.0.0" -UpdateLegacyDashboard true
```

## Files Updated By Import

- pmforge_dashboard/index.html
- pmforge_dashboard/version.json
- backups/legacy_dashboard/index.html (only when `-UpdateLegacyDashboard true`)

## Rollback

Use git checkout on imported files, or import a prior Suite version.

## AI Scope Boundary

Read and follow:

- docs/suite/AI_SCOPE_BOUNDARY.md
