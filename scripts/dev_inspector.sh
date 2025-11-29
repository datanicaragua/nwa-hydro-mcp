#!/bin/bash
# scripts/dev_inspector.sh
# Cross-platform MCP Inspector launcher for Mac/Linux (Bash)
# Usage: ./scripts/dev_inspector.sh

set -e

# Get the project root directory (parent of scripts folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔧 Activating virtual environment..."
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "❌ Virtual environment not found. Run 'python -m venv .venv' first."
    exit 1
fi

echo "🧹 Cleaning up old Python processes..."
pkill -f "python.*server.py" 2>/dev/null || true

# Kill any processes using MCP Inspector ports
for port in 6274 6277; do
    pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo "  Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
    fi
done

echo "🚀 Starting NWA Hydro MCP Inspector..."
cd "$PROJECT_ROOT"
export PYTHONPATH="src"
fastmcp dev src/nwa_hydro/server.py
