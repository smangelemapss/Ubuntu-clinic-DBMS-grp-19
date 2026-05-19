@echo off
title Ubuntu Clinic - Demo Ready
echo.
echo === Ubuntu Clinic pre-demo check ===
echo.

cd /d %~dp0backend
python scripts\verify_deploy_ready.py --http
if errorlevel 1 (
  echo.
  echo Verify failed. Fix Oracle / .env / passwords, then retry.
  pause
  exit /b 1
)

cd /d %~dp0
echo.
echo === Starting dev servers ===
call start-dev.bat
