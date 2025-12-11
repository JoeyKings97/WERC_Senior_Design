$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Write-Host "Starting Cooling Tower Control Stack..." -ForegroundColor Cyan
Write-Host "Repo root: $repoRoot`n"

# Ensure venv exists
if (!(Test-Path "$repoRoot\.venv")) {
    Write-Error ".venv not found. Run scripts/run-backend.ps1 first to create it."
    exit 1
}

# Start Backend in new window
Write-Host "Starting Backend (FastAPI on port 8000)..." -ForegroundColor Green
$backendCmd = "& '.\.venv\Scripts\Activate.ps1'; python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WorkingDirectory $repoRoot -WindowStyle Normal

Start-Sleep -Seconds 2

# Start Simulator in new window
Write-Host "Starting Simulator (pushing fake telemetry)..." -ForegroundColor Green
$simCmd = "& '.\.venv\Scripts\Activate.ps1'; python sim\simulator.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $simCmd -WorkingDirectory $repoRoot -WindowStyle Normal

Start-Sleep -Seconds 2

# Start Frontend in new window
Write-Host "Starting Frontend (React/Vite on port 5173/5174)..." -ForegroundColor Green
$frontendCmd = "`$env:Path = 'C:\Program Files\nodejs;' + `$env:Path; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WorkingDirectory "$repoRoot\frontend" -WindowStyle Normal

Write-Host "`nStack started in 3 new windows!" -ForegroundColor Green
Write-Host "`nDashboard URL: http://localhost:5173/ (or 5174 if 5173 is taken)" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "Data saved to: ./data/telemetry.db" -ForegroundColor Cyan
Write-Host "`nTo stop: close the three PowerShell windows or press Ctrl+C in each.`n" -ForegroundColor Yellow
