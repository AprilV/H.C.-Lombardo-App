@echo off
REM ==============================================================================
REM H.C. LOMBARDO APP - TESTBED DATA LOADER
REM ==============================================================================
REM Purpose: Quick start script to load historical data into testbed
REM Author: April V. Sykes
REM Created: October 28, 2025
REM ==============================================================================

echo.
echo ================================================================================
echo H.C. LOMBARDO APP - TESTBED HISTORICAL DATA LOADER
echo ================================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo Step 1: Verify Python environment...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo Step 2: Check nfl_data_py installation...
python -c "import nfl_data_py; print('nfl_data_py version:', nfl_data_py.__version__)"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo nfl_data_py not found. Installing...
    pip install nfl_data_py
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install nfl_data_py
        pause
        exit /b 1
    )
)

echo.
echo Step 3: Verify database connection...
python check_db_schema.py > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Could not connect to database. Check .env file!
    echo Press any key to continue anyway...
    pause > nul
) else (
    echo Database connection OK
)

echo.
echo ================================================================================
echo TESTBED DATA LOAD OPTIONS
echo ================================================================================
echo.
echo [1] Load 2024 season only (RECOMMENDED for first test)
echo     - Quick test: ~3-5 minutes
echo     - ~270 games, 540 team-game records
echo.
echo [2] Load ALL seasons 2022-2025 (Full historical dataset)
echo     - Longer: ~10-20 minutes
echo     - ~1100 games, 2200+ team-game records
echo.
echo [3] Load specific seasons (custom)
echo.
echo [4] Exit
echo.

choice /C 1234 /N /M "Select option (1-4): "
set OPTION=%ERRORLEVEL%

if %OPTION%==4 goto :END
if %OPTION%==3 goto :CUSTOM
if %OPTION%==2 goto :FULL
if %OPTION%==1 goto :QUICK

:QUICK
echo.
echo ================================================================================
echo LOADING 2024 SEASON ONLY (TEST MODE)
echo ================================================================================
echo.
echo This will:
echo - Create HCL testbed schema (if not exists)
echo - Load 2024 regular season games
echo - Load team-game statistics
echo - Refresh materialized views
echo - Run data verification
echo.
echo Estimated time: 3-5 minutes
echo.
pause

python ingest_historical_games.py --testbed --seasons 2024

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo SUCCESS! 2024 season loaded into testbed
    echo ================================================================================
    echo.
    echo Next steps:
    echo 1. Open pgAdmin or psql
    echo 2. Run verification queries from TEST_HCL_SCHEMA.md
    echo 3. Check v_game_matchup_display view
    echo 4. If all looks good, run option [2] to load full history
    echo.
) else (
    echo.
    echo ERROR: Data load failed! Check historical_data_load.log for details
    echo.
)
goto :END

:FULL
echo.
echo ================================================================================
echo LOADING FULL HISTORICAL DATA (2022-2025)
echo ================================================================================
echo.
echo This will:
echo - Create HCL testbed schema (if not exists)
echo - Load 2022, 2023, 2024, 2025 seasons
echo - Load ~1100 games and ~2200 team-game records
echo - Refresh materialized views
echo - Run data verification
echo.
echo Estimated time: 10-20 minutes
echo.
echo WARNING: This downloads large datasets from nflverse (~500MB per season)
echo Make sure you have stable internet connection!
echo.
pause

python ingest_historical_games.py --testbed --seasons 2022 2023 2024 2025

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo SUCCESS! Full historical data loaded into testbed
    echo ================================================================================
    echo.
    echo Next steps:
    echo 1. Run verification queries (see TEST_HCL_SCHEMA.md)
    echo 2. Validate data quality
    echo 3. Test API endpoints with testbed data
    echo 4. If all checks pass, migrate to production
    echo.
) else (
    echo.
    echo ERROR: Data load failed! Check historical_data_load.log for details
    echo.
)
goto :END

:CUSTOM
echo.
echo Enter seasons to load (space-separated, e.g., 2023 2024):
set /p SEASONS="Seasons: "

if "%SEASONS%"=="" (
    echo ERROR: No seasons specified
    goto :END
)

echo.
echo Loading seasons: %SEASONS%
echo.
pause

python ingest_historical_games.py --testbed --seasons %SEASONS%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Custom seasons loaded into testbed
    echo.
) else (
    echo.
    echo ERROR: Data load failed! Check historical_data_load.log for details
    echo.
)
goto :END

:END
echo.
echo ================================================================================
echo TESTBED DATA LOADER - COMPLETE
echo ================================================================================
echo.
echo Log file: historical_data_load.log
echo Documentation: TEST_HCL_SCHEMA.md
echo.
pause
