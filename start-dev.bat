@echo off
title Ubuntu Clinic - Dev Servers
echo Starting Ubuntu Clinic (backend + frontend)...
echo.
echo Pre-flight (optional): cd backend ^&^& python scripts/verify_deploy_ready.py
echo.

start "Ubuntu Clinic - BACKEND" cmd /k "cd /d %~dp0backend && python app.py"
timeout /t 3 /nobreak >nul
start "Ubuntu Clinic - FRONTEND" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Two CMD windows opened:
echo   1. Backend  - http://localhost:8000/api/v1/health/
echo   2. Frontend - http://localhost:5173/  (homepage)
echo      Login     - http://localhost:5173/login
echo.
echo Login: karabo.mabena / Clinic@123
echo Or click "One-click demo login" on the login page.
echo.
pause
