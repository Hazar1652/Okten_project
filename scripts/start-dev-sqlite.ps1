# Okten без Docker — SQLite (Windows PowerShell)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "=== Okten: SQLite (без Docker) ===" -ForegroundColor Cyan
$env:USE_SQLITE = "1"

Set-Location "$root\backend"
& .\.venv\Scripts\python.exe manage.py migrate
& .\.venv\Scripts\python.exe manage.py seed_demo

Write-Host ""
Write-Host "Додай USE_SQLITE=1 у backend\.env щоб не вказувати змінну щоразу." -ForegroundColor Yellow
Write-Host ""
Write-Host "Запусти в ДВОХ терміналах:" -ForegroundColor Green
Write-Host "  Backend:  cd backend; `$env:USE_SQLITE='1'; .\.venv\Scripts\python.exe manage.py runserver"
Write-Host "  Frontend: cd frontend; npm run dev"
Write-Host ""
Write-Host "  Сайт: http://localhost:5173" -ForegroundColor Green
