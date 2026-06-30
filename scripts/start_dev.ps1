$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$BackendUrl = "http://127.0.0.1:8001/health"
$FrontendUrl = "http://127.0.0.1:3000"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Require-Command {
    param([string]$Name, [string]$Hint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found. $Hint"
    }
}

function Test-Port {
    param([int]$Port)
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

function Wait-Url {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 60
    )
    for ($i = 0; $i -lt $TimeoutSeconds; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    return $false
}

Write-Host "event-intelligent one-click startup" -ForegroundColor Green
Write-Host "Project root: $Root"

Write-Step "Checking local tools"
Require-Command "python" "Please install Python, then run this script again."
Require-Command "npm" "Please install Node.js, then run this script again."

Write-Step "Checking backend dependencies"
Push-Location $Backend
try {
    python -c "import fastapi, uvicorn, sqlalchemy, pydantic_settings, jose, passlib, aiofiles, websockets, httpx, dotenv" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing backend dependencies..."
        python -m pip install -r requirements.txt
    } else {
        Write-Host "Backend dependencies are ready."
    }
} finally {
    Pop-Location
}

Write-Step "Checking frontend dependencies"
Push-Location $Frontend
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing frontend dependencies..."
        if (Test-Path "package-lock.json") {
            npm ci
        } else {
            npm install
        }
    } else {
        Write-Host "Frontend dependencies are ready."
    }
} finally {
    Pop-Location
}

Write-Step "Starting backend"
if (Test-Port 8001) {
    Write-Host "Backend port 8001 is already in use. Reusing the existing service."
} else {
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        "chcp 65001 > `$null; Set-Location -LiteralPath `"$Backend`"; `$env:PYTHONIOENCODING='utf-8'; `$env:DEBUG='false'; python main.py"
    ) -WorkingDirectory $Backend
}

Write-Step "Starting frontend"
if (Test-Port 3000) {
    Write-Host "Frontend port 3000 is already in use. Reusing the existing service."
} else {
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        "chcp 65001 > `$null; Set-Location -LiteralPath `"$Frontend`"; npm run dev -- --host 127.0.0.1"
    ) -WorkingDirectory $Frontend
}

Write-Step "Opening browser"
$frontendReady = Wait-Url $FrontendUrl 90
if (-not $frontendReady) {
    Write-Warning "Frontend did not respond within 90 seconds. Opening the URL anyway."
}

Start-Process $FrontendUrl

Write-Host ""
Write-Host "Started. Frontend: $FrontendUrl" -ForegroundColor Green
Write-Host "Backend health: $BackendUrl"
Write-Host "Close the backend/frontend PowerShell windows to stop the project."
