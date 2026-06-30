@echo off
setlocal
cd /d "%~dp0"

where powershell >nul 2>nul
if errorlevel 1 (
    echo PowerShell was not found. Please run scripts\build_offline_package.ps1 manually on a Windows machine.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_offline_package.ps1"
set EXIT_CODE=%ERRORLEVEL%

echo.
if not "%EXIT_CODE%"=="0" (
    echo Build failed with exit code %EXIT_CODE%.
) else (
    echo Build finished successfully.
)
pause
exit /b %EXIT_CODE%
