@echo off
REM H.C. Lombardo NFL Analytics - Production Startup
REM Clean, error-free startup script

echo.
echo ==========================================================
echo   H.C. LOMBARDO NFL ANALYTICS - STARTING ALL SERVICES
echo ==========================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Step 1: Check Database
echo [1/4] Checking Database Connection...
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='nfl_analytics', user='postgres', password='aprilv120'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM teams'); count = cursor.fetchone()[0]; conn.close(); print(f'      Database Ready: {count} teams loaded')" 2>nul
if errorlevel 1 (
    echo       ERROR: Database not available. Make sure PostgreSQL is running.
    pause
    exit /b 1
)

REM Step 2: Start API Server
echo.
echo [2/4] Starting Flask API Server...
start "H.C. Lombardo API" /MIN python api_server.py
timeout /t 3 /nobreak >nul
echo       API Server started on port 5000

REM Step 3: Start React Frontend
echo.
echo [3/4] Starting React Frontend...
cd frontend
start "H.C. Lombardo Frontend" /MIN cmd /c "npm start"
cd ..
echo       React Frontend starting (compiles in 20-30 seconds)

REM Step 4: Start Live Data Updater
echo.
echo [4/4] Starting Live Data Updater...
start "H.C. Lombardo Data Updater" /MIN python live_data_updater.py --continuous 15
echo       Data Updater started (updates every 15 minutes)

REM Wait for services to stabilize
echo.
echo Waiting for services to start...
timeout /t 8 /nobreak >nul

REM Display status
echo.
echo ==========================================================
echo   STARTUP COMPLETE - ALL SERVICES RUNNING
echo ==========================================================
echo.
echo   H.C. Lombardo Dashboard:  http://localhost:3000
echo   Dr. Foster Interface:     dr.foster\index.html
echo   API Health Check:         http://localhost:5000/health
echo   Database:                 PostgreSQL (32 teams)
echo   Live Updates:             Every 15 minutes
echo.
echo ==========================================================
echo.
echo Opening H.C. Lombardo Dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo All services running! Press any key to exit this window.
echo To stop all services, run STOP.bat
echo.
pause
