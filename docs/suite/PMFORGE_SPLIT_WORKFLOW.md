# PM Forge Split Workflow

This repo (H.C. Lombardo) is the consumer/demo host.
PM Forge Suite is developed independently at C:\PMForgeSuite.

## Current Policy

- Suite development happens only in C:\PMForgeSuite.
- H.C. keeps a consumer copy at pmforge_dashboard/index.html.
- Legacy Dashboard mirroring is optional and disabled by default.

## Import Approved Suite Into H.C.

Run from H.C. repo root:

```powershell
.\scripts\suite\import_pmforge_suite.ps1 -SuiteRoot "C:\PMForgeSuite" -Version "v1.0.0"
```

To also mirror into Dashboard/index.html (opt-in):

```powershell
.\scripts\suite\import_pmforge_suite.ps1 -SuiteRoot "C:\PMForgeSuite" -Version "v1.0.0" -UpdateLegacyDashboard true
```

## Files Updated By Import

- pmforge_dashboard/index.html
- pmforge_dashboard/version.json
- Dashboard/index.html (only when `-UpdateLegacyDashboard true`)

## Rollback

Use git checkout on imported files, or import a prior Suite version.
