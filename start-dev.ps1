# Script pour lancer backend et frontend en développement

Write-Host "====================================" -ForegroundColor Green
Write-Host "Démarrage du système AI Recruitment" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Lancer le backend
Write-Host ""
Write-Host "Lancement du backend FastAPI..." -ForegroundColor Cyan
Write-Host "http://localhost:8000" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Attendre
Start-Sleep -Seconds 5

# Lancer le frontend
Write-Host ""
Write-Host "Lancement du frontend React..." -ForegroundColor Cyan
Write-Host "http://localhost:5173" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "Services lancés avec succès!" -ForegroundColor Green
Write-Host "Frontend:  http://localhost:5173" -ForegroundColor Yellow
Write-Host "Backend:   http://localhost:8000" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Green
Write-Host "Ferme les fenêtres PowerShell pour arrêter" -ForegroundColor Cyan
