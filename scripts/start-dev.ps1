# Локальний запуск Okten (Windows PowerShell)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "=== Okten: перевірка Docker ===" -ForegroundColor Cyan
docker info 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Desktop не запущений!" -ForegroundColor Red
    Write-Host "Варіант А: відкрий Docker Desktop і запусти скрипт знову"
    Write-Host "Варіант Б: без Docker → .\scripts\start-dev-sqlite.ps1"
    exit 1
}

Write-Host "=== Postgres ===" -ForegroundColor Cyan
Set-Location "$root\infra"
docker compose up db -d
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "=== Backend migrate + seed ===" -ForegroundColor Cyan
Set-Location "$root\backend"
& .\.venv\Scripts\python.exe manage.py migrate
& .\.venv\Scripts\python.exe manage.py seed_demo

Write-Host ""
Write-Host "=== Готово. Запусти в ДВОХ терміналах: ===" -ForegroundColor Green
Write-Host "  Backend:  cd backend; .\.venv\Scripts\python.exe manage.py runserver"
Write-Host "  Frontend: cd frontend; npm run dev"
Write-Host ""
Write-Host "  Сайт: http://localhost:5173" -ForegroundColor Green
Write-Host "  API:  http://localhost:8000/api/docs/" -ForegroundColor Green
