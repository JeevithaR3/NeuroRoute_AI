#!/usr/bin/env bash
# NeuroRoute — Open CLI Dashboard (Layer 3)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ⬡  NeuroRoute — CLI Dashboard               ║"
echo "║     Layer 3 — Monitoring & Dataset System    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

cd "$BACKEND_DIR"

if [ "$1" == "--watch" ]; then
  python3 dashboard.py --watch
elif [ "$1" == "--queries" ]; then
  python3 dashboard.py --queries --limit "${2:-30}"
elif [ "$1" == "--stats" ]; then
  python3 dashboard.py --stats
elif [ "$1" == "--dataset" ]; then
  python3 dataset_builder.py
else
  python3 dashboard.py
fi
