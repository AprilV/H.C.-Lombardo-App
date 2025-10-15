@echo off
REM H.C. Lombardo App - Quick Shutdown
REM Double-click this file to stop all services

echo.
echo ============================================
echo   H.C. LOMBARDO APP - SHUTDOWN
echo ============================================
echo.

cd /d "%~dp0"
python shutdown.py

echo.
echo All services stopped.
pause
