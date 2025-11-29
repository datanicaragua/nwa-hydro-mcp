# Script para ejecutar MCP Inspector
Set-Location C:\Dev\nwa-hydro-mcp
& .\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
fastmcp dev src/nwa_hydro/server.py
