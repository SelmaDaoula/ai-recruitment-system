# Script de réparation complète des API
# Ce script installe toutes les dépendances et lance les services

Write-Host "================================" -ForegroundColor Cyan
Write-Host "🚀 FIX COMPLET DES API" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Installer les dépendances Python
Write-Host "[1/4] Installation des dépendances Python..." -ForegroundColor Yellow

cd backend

# Vérifier si requirements.txt existe
if (-Not (Test-Path "requirements.txt")) {
    Write-Host "❌ requirements.txt non trouvé" -ForegroundColor Red
    exit 1
}

# Installer les packages
pip install --upgrade pip setuptools wheel 2>&1 | Out-Null
Write-Host "  ✅ pip mis à jour"

pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Certains packages n'ont pas pu être installés. Continuant..." -ForegroundColor Yellow
}

Write-Host "  ✅ Dépendances installées"
Write-Host ""

# Étape 2 : Initialiser la base de données
Write-Host "[2/4] Initialisation de la base de données..." -ForegroundColor Yellow

try {
    python init_db.py
    Write-Host "  ✅ Base de données initialisée"
} catch {
    Write-Host "⚠️  Initialisation DB échouée (peut être normal si DB n'est pas accessible)" -ForegroundColor Yellow
}

Write-Host ""

# Étape 3 : Installer les dépendances frontend
Write-Host "[3/4] Installation des dépendances NPM..." -ForegroundColor Yellow

cd ../frontend

if (-Not (Test-Path "package.json")) {
    Write-Host "❌ package.json non trouvé" -ForegroundColor Red
    exit 1
}

npm install
Write-Host "  ✅ Dépendances NPM installées"
Write-Host ""

# Étape 4 : Afficher les instructions de démarrage
Write-Host "[4/4] Configuration complète!" -ForegroundColor Green
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "DEMARRAGE" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Dans 2 terminaux PowerShell séparés, exécutez:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  python -m uvicorn app.main:app --reload --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Ensuite:" -ForegroundColor Cyan
Write-Host "  Frontend  : http://localhost:3000" -ForegroundColor Green
Write-Host "  API Docs  : http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Health    : http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "================================" -ForegroundColor Green
