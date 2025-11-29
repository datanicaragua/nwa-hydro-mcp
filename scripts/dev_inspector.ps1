# scripts/dev_inspector.ps1
# Cross-platform MCP Inspector launcher for Windows (PowerShell)
# Usage: .\scripts\dev_inspector.ps1

$ErrorActionPreference = "Stop"

# Get the project root directory (parent of scripts folder)
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
$ActivateScript = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    . $ActivateScript
}
else {
    Write-Host "❌ Virtual environment not found. Run 'python -m venv .venv' first." -ForegroundColor Red
    exit 1
}

Write-Host "🧹 Cleaning up old Python processes..." -ForegroundColor Yellow
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue

# Kill any processes using MCP Inspector ports
$ports = @(6274, 6277)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($connection) {
        $processId = $connection.OwningProcess
        Write-Host "  Killing process on port $port (PID: $processId)" -ForegroundColor Gray
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "🚀 Starting NWA Hydro MCP Inspector..." -ForegroundColor Green
$env:PYTHONPATH = "src"
Set-Location $ProjectRoot
fastmcp dev src/nwa_hydro/server.py
