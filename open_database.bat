@echo off
echo 🗄️ Opening H.C. Lombardo NFL Database...
echo 📍 Database: enhanced_nfl_betting.db
echo.

REM Open the database with the correct path
set DB_PATH="%~dp0nfl_betting_database\enhanced_nfl_betting.db"
if exist %DB_PATH% (
    echo ✅ Opening database with data...
    echo 📊 Contains: 32 Teams, 14 Games, Collection Logs
    start "" "%DB_PATH%"
) else (
    echo ❌ Database not found at: %DB_PATH%
    echo 💡 Make sure you're running this from the H.C. Lombardo App folder
    pause
)