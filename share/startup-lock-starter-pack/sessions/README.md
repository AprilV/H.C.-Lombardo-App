# Sessions Folder Guide

## Purpose
This folder stores startup checkpoint handoff files.

## Naming Convention
Use this exact filename pattern:

- SESSION_RESUME_YYYY-MM-DD_HHMM.md

Examples:

- SESSION_RESUME_2026-05-12_0953.md
- SESSION_RESUME_2026-05-13_1410.md

## Rules
1. Never overwrite old session resume files.
2. Always create a new timestamped file.
3. New chat starts by reading the newest session resume file.

## Generate A Resume File

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
./scripts/maintenance/session_resume_guard.ps1 -Reason "New chat startup checkpoint"
```
