#!/usr/bin/env powershell
<#
.SYNOPSIS
    Start the KAAVALCURSOR Backend Server
.DESCRIPTION
    Initializes the Python virtual environment and starts the FastAPI backend
    on http://127.0.0.1:8000
#>

param(
    [switch]$NoReload,
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "KAAVALCURSOR Backend Server Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if venv exists, create if missing
if (-not (Test-Path "$backendDir\.venv")) {
    Write-Host "Virtual environment not found at $backendDir\.venv - creating..." -ForegroundColor Yellow
    try {
        & python -m venv "$backendDir\.venv"
        Write-Host "Virtual environment created." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to create virtual environment: $_" -ForegroundColor Red
        exit 1
    }
}

# Set Python path
$env:PYTHONPATH = $backendDir

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "$backendDir\.venv\Scripts\Activate.ps1"

# Install dependencies if needed (use requirements.txt when present)
Write-Host "Checking and installing dependencies..." -ForegroundColor Green
try {
    $venvPython = "$backendDir\.venv\Scripts\python.exe"
    & $venvPython -m pip install --upgrade pip
    if (Test-Path "$backendDir\requirements.txt") {
        & $venvPython -m pip install -r "$backendDir\requirements.txt"
    }
    else {
        & $venvPython -m pip install -e .
    }
}
catch {
    Write-Host "Dependency installation failed: $_" -ForegroundColor Yellow
}

# Build reload flag
$reloadFlag = if ($NoReload) { "" } else { "--reload" }

# Start the server
Write-Host "Starting FastAPI backend on http://127.0.0.1:$Port" -ForegroundColor Green
Write-Host "API Documentation: http://127.0.0.1:$Port/docs" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

& uvicorn app.main:app --host 127.0.0.1 --port $Port $reloadFlag

Write-Host "Backend stopped." -ForegroundColor Red
