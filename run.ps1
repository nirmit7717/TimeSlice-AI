# TimeSlice AI Quick Start Script
$RootPath = Resolve-Path "$PSScriptRoot"

# Define Python paths correctly with quotes, handling paths with spaces
$Packages = @(
    "$RootPath\packages\database",
    "$RootPath\packages\scheduling-system",
    "$RootPath\packages\context-vault",
    "$RootPath\packages\execution-system",
    "$RootPath\packages\analytics-system",
    "$RootPath\packages\attention-kernel",
    "$RootPath\packages\adaptive-intelligence",
    "$RootPath\packages\notification-system",
    "$RootPath\packages\platform",
    "$RootPath\apps\backend"
)

$env:PYTHONPATH = $Packages -join ";"

Write-Host "--------------------------------------------" -ForegroundColor Cyan
Write-Host "  Starting TimeSlice AI Development Workspace  " -ForegroundColor White -BackgroundColor DarkCyan
Write-Host "--------------------------------------------" -ForegroundColor Cyan

# Start uvicorn server in a new window so logs are separated
Write-Host "Starting Backend (FastAPI)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='$env:PYTHONPATH'; cd '$RootPath\apps\backend'; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
Write-Host "Backend started in a separate window." -ForegroundColor Green
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Gray

# Start vite server in a new window
Write-Host "Starting Frontend (Vite/Tauri)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootPath\apps\desktop'; npm run dev"
Write-Host "Frontend dev server started in a separate window." -ForegroundColor Green
Write-Host "Web App Interface: http://localhost:1420" -ForegroundColor Gray
Write-Host "--------------------------------------------" -ForegroundColor Cyan
