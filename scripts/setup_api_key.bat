@echo off
REM Set API-SPORTS NFL API Key
REM Replace "your_actual_api_key_here" with your real API key

echo Setting API-SPORTS NFL API Key...
set API_SPORTS_NFL_KEY=your_actual_api_key_here

echo API key has been set for this session.
echo To make it permanent, add this to your system environment variables:
echo Variable: API_SPORTS_NFL_KEY
echo Value: your_actual_api_key_here

echo.
echo Testing API configuration...
python external_apis\nfl_data_integration.py

pause