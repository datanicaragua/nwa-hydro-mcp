# scripts/dev_gradio.ps1
# Cross-platform Gradio App launcher for Windows (PowerShell)
# Usage: .\scripts\dev_gradio.ps1

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

Write-Host "🧹 Cleaning up old Gradio processes..." -ForegroundColor Yellow
# Kill any process using Gradio port
$connection = Get-NetTCPConnection -LocalPort 7860 -ErrorAction SilentlyContinue | Select-Object -First 1
if ($connection) {
    $processId = $connection.OwningProcess
    Write-Host "  Killing process on port 7860 (PID: $processId)" -ForegroundColor Gray
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
}

Write-Host "🚀 Starting NWA Hydro Gradio App..." -ForegroundColor Green
$env:PYTHONPATH = "."
Set-Location $ProjectRoot
python app.py
