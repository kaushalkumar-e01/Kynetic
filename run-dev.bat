@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo             KYNETIC DEVELOPER RUNNER
echo ===================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.11 or higher from https://python.org
    pause
    exit /b 1
)

:: 2. Check Node
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in your PATH.
    echo Please install Node.js 18 or higher from https://nodejs.org
    pause
    exit /b 1
)

:: 3. Setup backend environment
if not exist "backend\.env" (
    echo [INFO] Creating backend\.env from template...
    copy "backend\.env.example" "backend\.env" >nul
)

:: 4. Setup frontend environment
if not exist "frontend\.env.local" (
    echo [INFO] Creating frontend\.env.local from template...
    copy "frontend\.env.example" "frontend\.env.local" >nul
)

:: 5. Install frontend dependencies if missing
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo ===================================================
echo  Starting Backend and Frontend servers...
echo ===================================================
echo  - Backend:  http://127.0.0.1:8000 (API & Docs: /docs)
echo  - Frontend: http://localhost:3000
echo  - Health:   http://127.0.0.1:8000/api/v1/health
echo ===================================================
echo.

:: Launch Backend in a separate window
start "Kynetic Backend (FastAPI)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: Launch Frontend in current window
cd /d %~dp0frontend
call npm run dev

