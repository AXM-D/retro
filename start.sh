#!/bin/bash
echo "========================================"
echo "  RETRO - Active Defense Platform"
echo "  v0.1.0 | Powered by TaQ Engine v1.0.1"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[*] Activating virtual environment..."
source venv/bin/activate

echo "[*] Installing dependencies..."
pip install -q -r requirements.txt 2>/dev/null

echo "[*] Starting RETRO API server on http://127.0.0.1:8500"
echo "[*] Dashboard UI: http://localhost:5173 (run 'npm run dev' in ui/)"
echo "[*] Landing page: file://$(pwd)/landing/index.html"
echo "[*] API Docs: http://127.0.0.1:8500/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m uvicorn retro.api.server:app --host 127.0.0.1 --port 8500 --reload
