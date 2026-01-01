# KAAVAL AI System - Unified Startup Script
# Starts both Backend (FastAPI) and Frontend (Simple HTTP) services

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

# Configuration
$VenvPath = Join-Path $ScriptRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$BackendPort = 8000
$FrontendPort = 8001

# Helper Functions
function Show-Header {
    param([string]$Title)
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "   $Title" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Show-Step {
    param([string]$Message)
    Write-Host "`n>> $Message" -ForegroundColor Yellow
}

function Show-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Show-Error {
    param([string]$Message)
    Write-Host "  [ERROR] $Message" -ForegroundColor Red
}

# Main Execution
Clear-Host
Show-Header "KAAVAL AI SYSTEM - STARTUP SEQUENCE"

# 1. Check Virtual Environment
Show-Step "Checking Environment..."
if (-not (Test-Path $PythonExe)) {
    Show-Step "Virtual environment not found at: $VenvPath. Creating venv..."
    try {
        & python -m venv $VenvPath
        Show-Success "Virtual environment created at: $VenvPath"
    }
    catch {
        Show-Error "Failed to create virtual environment: $_"
        exit 1
    }

    # Ensure the Python executable exists now
    if (-not (Test-Path $PythonExe)) {
        Show-Error "Virtual environment creation did not produce python executable at: $PythonExe"
        exit 1
    }

    # Upgrade pip and install backend requirements
    Show-Step "Installing dependencies into virtual environment..."
    try {
        & $PythonExe -m pip install --upgrade pip
        & $PythonExe -m pip install -r "$ScriptRoot\backend\requirements.txt"
        Show-Success "Dependencies installed successfully"
    }
    catch {
        Show-Error "Failed to install dependencies into virtualenv: $_"
        exit 1
    }
}
else {
    Show-Success "Found Python environment: $PythonExe"
}

# 2. Verify Core Dependencies
Show-Step "Verifying Core Dependencies..."
try {
    & $PythonExe -c "import fastapi, uvicorn, torch; print('Dependencies OK')" | Out-Null
    Show-Success "Core dependencies verified (FastAPI, Uvicorn, PyTorch)"
}
catch {
    Show-Error "Missing dependencies. Attempting to install..."
    try {
        & $PythonExe -m pip install -r "$ScriptRoot\backend\requirements.txt"
        Show-Success "Dependencies installed successfully"
    }
    catch {
        Show-Error "Failed to install dependencies. Please check logs."
        exit 1
    }
}

# 3. Start Frontend (Background Process)
Show-Step "Starting Frontend Service..."
$FrontendDir = Join-Path $ScriptRoot "frontend"
try {
    $FrontendProcess = Start-Process -FilePath $PythonExe -ArgumentList "-m http.server $FrontendPort --directory `"$FrontendDir`"" -PassThru -WindowStyle Minimized
    Show-Success "Frontend running at http://localhost:$FrontendPort"
}
catch {
    Show-Error "Failed to start frontend: $_"
}

# 4. Start Backend (Foreground Process)
Show-Step "Starting Backend Service..."
Write-Host "  API Documentation: http://localhost:$BackendPort/docs" -ForegroundColor Gray
Write-Host "  Backend API:       http://localhost:$BackendPort" -ForegroundColor Gray
Write-Host "`n  [PRESS CTRL+C TO STOP SERVER]`n" -ForegroundColor White

try {
    # Run uvicorn as a module to avoid path issues
    $Env:PYTHONPATH = "$ScriptRoot\backend"
    & $PythonExe -m uvicorn app.main:app --host 0.0.0.0 --port $BackendPort --reload
}
finally {
    # Cleanup Frontend when Backend stops
    if ($FrontendProcess -and -not $FrontendProcess.HasExited) {
        Stop-Process -Id $FrontendProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "`nStopped Frontend Service." -ForegroundColor Gray
    }
}
