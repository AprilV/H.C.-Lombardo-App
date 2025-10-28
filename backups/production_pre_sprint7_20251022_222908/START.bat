@echo off
REM H.C. Lombardo NFL Analytics - PRODUCTION MODE
REM Optimized build - fast startup, no hot reload

echo.
echo ==========================================================
echo   H.C. LOMBARDO - PRODUCTION MODE (Optimized)
echo ==========================================================
echo   Everything on Port 5000 (single server)
echo   Perfect for: Demos, testing, deployment
echo ==========================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Step 1: Check Database
echo [1/5] Checking Database Connection...
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='nfl_analytics', user='postgres', password='aprilv120'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM teams'); count = cursor.fetchone()[0]; conn.close(); print(f'      Database Ready: {count} teams loaded')" 2>nul
if errorlevel 1 (
    echo       ERROR: Database not available. Make sure PostgreSQL is running.
    pause
    exit /b 1
)

REM Step 2: Build React Frontend (Production)
echo.
echo [2/5] Building React Frontend (this may take 30-60 seconds)...
cd frontend
call npm run build
if errorlevel 1 (
    echo       ERROR: React build failed. Check for syntax errors.
    cd ..
    pause
    exit /b 1
)
cd ..
echo       React build complete! (optimized and minified)

REM Step 3: Start Flask API + Frontend Server
echo.
echo [3/5] Starting Flask Server (API + Frontend)...
start "H.C. Lombardo Server" /MIN python api_server.py
timeout /t 3 /nobreak >nul
echo       Server started on port 5000

REM Step 4: Start Live Data Updater
echo.
echo [4/5] Starting Live Data Updater...
start "H.C. Lombardo Data Updater" /MIN python live_data_updater.py --continuous 15
echo       Data Updater started (updates every 15 minutes)

REM Wait for services to stabilize
echo.
echo [5/5] Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Display status
echo.
echo ==========================================================
echo   ALL SERVICES RUNNING!
echo ==========================================================
echo   App URL: http://localhost:5000
echo   Mode: PRODUCTION (optimized build)
echo.
echo   To make changes:
echo   1. Stop this server (STOP.bat)
echo   2. Edit your code
echo   3. Run START.bat again (rebuilds automatically)
echo.
echo   For hot reload during development:
echo   - Use START-DEV.bat instead
echo ==========================================================
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:5000

echo.
echo Press any key to view health check status...
pause >nul

REM Health check
python -c "import requests; r = requests.get('http://localhost:5000/health'); print('\n' + '='*50); print('HEALTH CHECK'); print('='*50); print(r.json()); print('='*50)" 2>nul

echo.
echo System is running! Leave this window open.
echo To stop all services, run STOP.bat
echo.
pause
