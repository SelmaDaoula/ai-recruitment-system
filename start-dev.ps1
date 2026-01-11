# Script pour lancer backend et frontend en développement

Write-Host "🚀 Démarrage du système AI Recruitment..." -ForegroundColor Green
Write-Host ""

# Activer l'environnement virtuel
Write-Host "📦 Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Lancer le backend en arrière-plan
Write-Host "🔧 Lancement du backend FastAPI sur http://localhost:8000..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Attendre que le backend soit prêt
Write-Host "⏳ Attente du démarrage du backend (5 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Lancer le frontend en arrière-plan
Write-Host "🎨 Lancement du frontend React sur http://localhost:5173..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# Afficher le statut
Write-Host ""
Write-Host "✅ Services lancés !" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend:  http://localhost:5173" -ForegroundColor Yellow
Write-Host "⚙️  Backend:   http://localhost:8000" -ForegroundColor Yellow
Write-Host "📚 API Docs:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Pour arrêter les services, ferme les deux fenêtres PowerShell" -ForegroundColor Cyan
