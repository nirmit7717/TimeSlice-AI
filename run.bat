@echo off
set "ROOT_PATH=%~dp0"
set "ROOT_PATH=%ROOT_PATH:~0,-1%"

set "PYTHONPATH=%ROOT_PATH%\packages\database;%ROOT_PATH%\packages\scheduling-system;%ROOT_PATH%\packages\context-vault;%ROOT_PATH%\packages\execution-system;%ROOT_PATH%\packages\analytics-system;%ROOT_PATH%\packages\attention-kernel;%ROOT_PATH%\packages\adaptive-intelligence;%ROOT_PATH%\packages\notification-system;%ROOT_PATH%\packages\platform;%ROOT_PATH%\apps\backend"

echo ----------------------------------------------------
echo   Starting TimeSlice AI Development Workspace
echo ----------------------------------------------------

echo Starting Backend (FastAPI)...
start cmd /k "cd /d "%ROOT_PATH%\apps\backend" && set "PYTHONPATH=%PYTHONPATH%" && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
echo Backend started in a separate window.
echo API Documentation: http://127.0.0.1:8000/docs

echo.
echo Starting Frontend (Vite/Tauri)...
start cmd /k "cd /d "%ROOT_PATH%\apps\desktop" && npm run dev"
echo Frontend dev server started in a separate window.
echo Web App Interface: http://localhost:1420
echo ----------------------------------------------------
