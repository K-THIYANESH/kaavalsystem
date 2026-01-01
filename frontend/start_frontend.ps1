#!/usr/bin/env powershell
<#
.SYNOPSIS
    Start the KAAVALCURSOR Frontend Static Server
.DESCRIPTION
    Starts a Python HTTP server to serve the frontend static files
    on http://127.0.0.1:8001
#>

param(
    [int]$Port = 8001
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = "$projectRoot\frontend"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "KAAVALCURSOR Frontend Server Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if frontend exists
if (-not (Test-Path $frontendDir)) {
    Write-Host "❌ Frontend directory not found at $frontendDir" -ForegroundColor Red
    exit 1
}

# Get Python from backend venv
$pythonExe = "$projectRoot\backend\.venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "❌ Python not found. Backend venv not initialized." -ForegroundColor Red
    Write-Host "Please run backend setup first." -ForegroundColor Yellow
    exit 1
}

Write-Host "🌐 Starting frontend static server on http://127.0.0.1:$Port" -ForegroundColor Green
Write-Host "📂 Serving files from: $frontendDir" -ForegroundColor Yellow
Write-Host "🔗 Main app: http://127.0.0.1:$Port" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

cd $frontendDir
& $pythonExe -m http.server $Port

Write-Host "Frontend server stopped." -ForegroundColor Red
