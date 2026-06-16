@echo off
setlocal
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\maintenance\publish_pmforge_live.ps1" %*
endlocal
