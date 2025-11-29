#!/bin/bash
# scripts/dev_gradio.sh
# Cross-platform Gradio App launcher for Mac/Linux (Bash)
# Usage: ./scripts/dev_gradio.sh

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

echo "🧹 Cleaning up old Gradio processes..."
# Kill any process using Gradio port
pid=$(lsof -ti:7860 2>/dev/null || true)
if [ -n "$pid" ]; then
    echo "  Killing process on port 7860 (PID: $pid)"
    kill -9 $pid 2>/dev/null || true
fi

echo "🚀 Starting NWA Hydro Gradio App..."
cd "$PROJECT_ROOT"
export PYTHONPATH="."
python app.py
