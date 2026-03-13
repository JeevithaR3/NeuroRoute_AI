#!/usr/bin/env bash
# NeuroRoute — Start Middleware Server (Layer 2)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIDDLEWARE_DIR="$SCRIPT_DIR/middleware"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ⬡  NeuroRoute Green AI Middleware           ║"
echo "║     Layer 2 — Starting server on :3000       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌ python3 not found. Please install Python 3.8+"
  exit 1
fi

# Check Flask
if ! python3 -c "import flask" 2>/dev/null; then
  echo "📦 Installing Flask..."
  pip install flask --break-system-packages || pip3 install flask
fi

# Check yaml
if ! python3 -c "import yaml" 2>/dev/null; then
  echo "📦 Installing PyYAML..."
  pip install pyyaml --break-system-packages || pip3 install pyyaml
fi

echo "✓ Dependencies OK"
echo "✓ Starting server at http://localhost:3000"
echo ""

cd "$MIDDLEWARE_DIR"
python3 server.py
