# STARTUP_GUIDE

This file lists practical startup and verification commands for this repository.

## Prerequisites
- Git repository is available.
- Local runtime is available (if API checks are expected).

## Startup Lock Command

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
```

Trigger phrase in chat:

- EXECUTE ORDER 66

## Find Newest Session Resume

```powershell
Get-ChildItem sessions -Filter "SESSION_RESUME_*.md" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 -ExpandProperty FullName
```

## Optional: Skip API checks during checkpoint

```powershell
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger" -SkipApi
```

## Optional: Add custom API checks

```powershell
./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger" `
  -Check "health=/health" `
  -Check "teams_count=/api/teams/count"
```

## Policy File Sanity Check

```powershell
Test-Path docs/ai_reference/COMMIT_POLICY.md
Test-Path docs/ai_reference/RESOURCE_EXPENDITURE_POLICY.md
```

## Troubleshooting

### Script execution disabled

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

### Python not found

```powershell
./scripts/maintenance/session_resume_guard.ps1 -PythonExe "C:/Path/To/python.exe" -Reason "Startup lock trigger"
```

### No git branch detected
Run command from repository root.
