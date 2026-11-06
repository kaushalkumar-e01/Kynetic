#!/usr/bin/env bash
set -e

echo "==================================================="
echo "            KYNETIC DEVELOPER RUNNER"
echo "==================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    exit 1
fi
PYTHON_CMD=$(command -v python3 || command -v python)

# 2. Check Node
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed or not in PATH."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 3. Setup backend environment
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    echo "[INFO] Creating backend/.env from template..."
    cp "$SCRIPT_DIR/backend/.env.example" "$SCRIPT_DIR/backend/.env"
fi

# 3.5. Run database migrations
echo "[INFO] Applying database migrations..."
(cd "$SCRIPT_DIR/backend" && $PYTHON_CMD -m alembic upgrade head > /dev/null 2>&1 || true)

# 4. Setup frontend environment
if [ ! -f "$SCRIPT_DIR/frontend/.env.local" ]; then
    echo "[INFO] Creating frontend/.env.local from template..."
    cp "$SCRIPT_DIR/frontend/.env.example" "$SCRIPT_DIR/frontend/.env.local"
fi

# 5. Install frontend dependencies if missing
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    (cd "$SCRIPT_DIR/frontend" && npm install)
fi

echo ""
echo "==================================================="
echo " Starting Backend & Frontend servers..."
echo " - Backend:  http://127.0.0.1:8000 (Docs: /docs)"
echo " - Frontend: http://localhost:3000"
echo " - Health:   http://127.0.0.1:8000/api/v1/health"
echo "==================================================="
echo ""

# Trap to kill background backend on exit
trap 'kill $(jobs -p) 2>/dev/null || true' EXIT

# Launch Backend in background
(cd "$SCRIPT_DIR/backend" && $PYTHON_CMD -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &

# Launch Frontend in foreground
(cd "$SCRIPT_DIR/frontend" && npm run dev)

