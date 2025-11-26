@echo off
REM Start Automated NFL Data Update Service
REM This runs continuously in background updating data every 15 minutes

echo ========================================
echo  AUTO UPDATE SERVICE - STARTING
echo ========================================
echo.
echo This will run continuously in a new window
echo updating NFL data every 15 minutes.
echo.
echo To stop: Close the auto-update window
echo.

start "NFL Auto-Update Service" python auto_update_service.py --continuous 15

echo.
echo ========================================
echo  Service started in background window
echo ========================================
echo.
pause
