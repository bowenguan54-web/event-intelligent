param(
    [switch]$SkipInstall,
    [switch]$NoZip,
    [string]$PackageName = "event-intelligent-offline"
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Require-Command {
    param(
        [string]$CommandName,
        [string]$InstallHint
    )
    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        throw "$CommandName was not found. $InstallHint"
    }
}

function Reset-Directory {
    param([string]$Path)
    $rootResolved = (Resolve-Path $Root).Path
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $fullPath.StartsWith($rootResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the project: $fullPath"
    }
    if (Test-Path $fullPath) {
        Remove-Item -LiteralPath $fullPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $fullPath | Out-Null
}

function Copy-DirectoryIfExists {
    param(
        [string]$Source,
        [string]$Destination
    )
    if (Test-Path $Source) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    }
}

$Root = Split-Path -Parent $PSScriptRoot
$Frontend = Join-Path $Root "frontend"
$Backend = Join-Path $Root "backend"
$Release = Join-Path $Root "release"
$PackageDir = Join-Path $Release $PackageName
$AppDir = Join-Path $PackageDir "app"
$PyInstallerDist = Join-Path $Backend "dist\event-intelligent-server"
$ExePath = Join-Path $PyInstallerDist "event-intelligent-server.exe"

Write-Host "event-intelligent offline package builder" -ForegroundColor Green
Write-Host "Project root: $Root"

Write-Step "Checking build tools"
Require-Command "python" "Install Python on the build machine, then run this script again."
Require-Command "npm" "Install Node.js on the build machine, then run this script again."

if (-not $SkipInstall) {
    Write-Step "Checking frontend dependencies"
    Push-Location $Frontend
    try {
        if (Test-Path "node_modules") {
            Write-Host "frontend\node_modules already exists. Skipping npm install."
        } else {
            if (Test-Path "package-lock.json") {
                npm ci
            } else {
                npm install
            }
        }
    } finally {
        Pop-Location
    }

    Write-Step "Checking backend build dependencies"
    Push-Location $Backend
    try {
        python -c "import fastapi, uvicorn, sqlalchemy, pydantic_settings, jose, passlib, aiofiles, websockets, httpx, dotenv; import PyInstaller" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Backend runtime dependencies and PyInstaller are already available."
        } else {
            python -m pip install -r requirements.txt
            python -m pip install pyinstaller
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Step "Skipping dependency installation by request"
}

Write-Step "Building frontend static files"
Push-Location $Frontend
try {
    npm run build
} finally {
    Pop-Location
}

if (-not (Test-Path (Join-Path $Frontend "dist\index.html"))) {
    throw "frontend\dist\index.html was not generated."
}

Write-Step "Building backend executable with PyInstaller"
Push-Location $Backend
try {
    python -m PyInstaller portable.spec --noconfirm --clean
} finally {
    Pop-Location
}

if (-not (Test-Path $ExePath)) {
    throw "PyInstaller output was not found: $ExePath"
}

Write-Step "Assembling offline package"
if (-not (Test-Path $Release)) {
    New-Item -ItemType Directory -Path $Release | Out-Null
}
Reset-Directory $PackageDir
Copy-Item -LiteralPath $PyInstallerDist -Destination $AppDir -Recurse -Force

$DbPath = Join-Path $Backend "meeting_assistant.db"
if (Test-Path $DbPath) {
    Copy-Item -LiteralPath $DbPath -Destination (Join-Path $AppDir "meeting_assistant.db") -Force
} else {
    Write-Warning "backend\meeting_assistant.db was not found. The app will create a new SQLite DB on first start."
}

$EnvPath = Join-Path $Backend ".env"
if (Test-Path $EnvPath) {
    Copy-Item -LiteralPath $EnvPath -Destination (Join-Path $AppDir ".env") -Force
}

$UploadsSource = Join-Path $Backend "uploads"
$UploadsDest = Join-Path $AppDir "uploads"
if (Test-Path $UploadsSource) {
    Copy-Item -LiteralPath $UploadsSource -Destination $UploadsDest -Recurse -Force
} else {
    New-Item -ItemType Directory -Path $UploadsDest | Out-Null
}

New-Item -ItemType Directory -Path (Join-Path $PackageDir "logs") | Out-Null

$InstallBat = @'
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
'@
Set-Content -LiteralPath (Join-Path $PackageDir "install_offline.bat") -Value $InstallBat -Encoding ASCII

$StartBat = @'
@echo off
setlocal
chcp 65001 >nul
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
"%~dp0app\event-intelligent-server.exe" 1>"%~dp0logs\server.log" 2>&1
set EXIT_CODE=%ERRORLEVEL%

echo.
echo Service stopped with exit code %EXIT_CODE%.
echo Log file: %~dp0logs\server.log
pause
exit /b %EXIT_CODE%
'@
Set-Content -LiteralPath (Join-Path $PackageDir "start_event_intelligent.bat") -Value $StartBat -Encoding ASCII

$Readme = @'
# event-intelligent offline package

This package is designed for a Windows computer without Python, Node.js, npm, pip, or project dependencies installed.

## Files

- `install_offline.bat`: checks that the offline package is complete and prepares local folders.
- `start_event_intelligent.bat`: starts the app.
- `app\event-intelligent-server.exe`: bundled backend executable.
- `app\meeting_assistant.db`: SQLite database copied from the build machine when available.
- `app\uploads`: uploaded files copied from the build machine when available.
- `logs\server.log`: runtime log after starting the app.

## Offline deployment

1. Copy this whole folder to the offline computer.
2. Double-click `install_offline.bat`.
3. Double-click `start_event_intelligent.bat`.
4. Open `http://127.0.0.1:8001` if the browser does not open automatically.

Default account, when created by the backend: `admin / 123456`.
'@
Set-Content -LiteralPath (Join-Path $PackageDir "README_OFFLINE.md") -Value $Readme -Encoding UTF8

if (-not $NoZip) {
    Write-Step "Creating zip archive"
    $ZipPath = Join-Path $Release "$PackageName.zip"
    if (Test-Path $ZipPath) {
        Remove-Item -LiteralPath $ZipPath -Force
    }
    Compress-Archive -Path (Join-Path $PackageDir "*") -DestinationPath $ZipPath -Force
    Write-Host "Zip: $ZipPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "Offline package ready: $PackageDir" -ForegroundColor Green
Write-Host "Copy that folder or the zip file to the offline computer."
