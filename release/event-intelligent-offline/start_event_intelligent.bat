@echo off
setlocal
cd /d "%~dp0"

if not exist "app\event-intelligent-server.exe" (
    echo [ERROR] app\event-intelligent-server.exe was not found.
    echo Run install_offline.bat first, or copy the complete offline package again.
    pause
    exit /b 1
)

if not exist "app\uploads" mkdir "app\uploads"
if not exist "logs" mkdir "logs"

echo Starting event-intelligent...
echo URL: http://127.0.0.1:8001
echo Press Ctrl+C in this window to stop the service.
echo.

cd /d "%~dp0app"
"%~dp0app\event-intelligent-server.exe" 1>>"%~dp0logs\server.log" 2>>&1
set EXIT_CODE=%ERRORLEVEL%

echo.
echo Service stopped with exit code %EXIT_CODE%.
echo Log file: %~dp0logs\server.log
pause
exit /b %EXIT_CODE%
