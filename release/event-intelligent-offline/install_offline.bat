@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   event-intelligent offline deployment
echo ============================================
echo.

if not exist "app\event-intelligent-server.exe" (
    echo [ERROR] app\event-intelligent-server.exe was not found.
    echo Please copy the whole offline package directory, then run this script again.
    pause
    exit /b 1
)

if not exist "app\uploads" mkdir "app\uploads"
if not exist "logs" mkdir "logs"

if not exist "app\meeting_assistant.db" (
    echo [WARN] app\meeting_assistant.db was not found.
    echo        A new SQLite database will be created on first start.
)

echo [OK] Package files are ready.
echo [OK] No Python, Node.js, npm, or pip installation is required on this offline computer.
echo.
echo Run start_event_intelligent.bat to start the app.
echo.
pause
exit /b 0
