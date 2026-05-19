@echo off
title Ubuntu Clinic - Complete Website
setlocal EnableDelayedExpansion

cd /d %~dp0
echo.
echo ============================================================
echo   Ubuntu Clinic - Deploy complete website (single URL)
echo ============================================================
echo.

REM --- Pre-flight ---
if not exist "backend\.env" (
  echo [INFO] Creating backend\.env from .env.example
  copy "backend\.env.example" "backend\.env" >nul
)

echo [1/4] Checking Oracle + API readiness...
cd backend
python scripts\verify_database.py
if errorlevel 1 (
  echo.
  echo [FAIL] Database not ready. Run sql\00_RUN_ALL.sql in SQL Developer first.
  cd ..
  pause
  exit /b 1
)

echo.
echo [2/4] Building production frontend (same-origin API)...
cd ..\frontend
set "NPM_CMD=C:\Program Files\nodejs\npm.cmd"
if not exist "%NPM_CMD%" set NPM_CMD=npm
call "%NPM_CMD%" run build
if errorlevel 1 (
  echo [FAIL] Frontend build failed. Install Node.js 18+ and run: npm install
  cd ..
  pause
  exit /b 1
)

echo.
echo [3/4] Quick API smoke test...
cd ..\backend
python -c "from app import create_app; c=create_app().test_client(); r=c.get('/api/v1/health/'); print('health', r.status_code, r.get_json().get('database'))"

echo.
echo [4/4] Starting website server...
cd ..
set SERVE_WEBSITE=true
set FLASK_ENV=development
set WEBSITE_PORT=8080
set CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

echo.
echo   Website URL:  http://localhost:%WEBSITE_PORT%/
echo   API health:   http://localhost:%WEBSITE_PORT%/api/v1/health/
echo   Login:        karabo.mabena / Clinic@123
echo.
echo   Press Ctrl+C to stop.
echo ============================================================
echo.

cd backend
python -m waitress --host=0.0.0.0 --port=%WEBSITE_PORT% --call "app:create_app"

pause
