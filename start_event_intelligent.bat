@echo off
setlocal
cd /d "%~dp0"

where powershell >nul 2>nul
if errorlevel 1 (
    echo PowerShell was not found. Please install PowerShell or start backend/frontend manually.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_dev.ps1"
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Startup failed with exit code %EXIT_CODE%.
    pause
)
exit /b %EXIT_CODE%
