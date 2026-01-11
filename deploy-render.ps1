# Render Deployment Script for AI Recruitment System
# This script pushes to GitHub and provides Render deployment instructions

param(
    [string]$GitHubUsername = "your-github-username",
    [string]$GitHubToken = "your-github-token",
    [string]$RepositoryName = "ai-recruitment-system"
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Deployment Render - Système de Recrutement IA" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$workspaceDir = "C:\Users\M.S.I\ai-recruitment-system"

# Function to handle errors
function Handle-Error {
    param([string]$message)
    Write-Host "ERROR: $message" -ForegroundColor Red
    exit 1
}

# Step 1: Verify Git is initialized
Write-Host "`n[1/4] Verifying Git repository..." -ForegroundColor Yellow
if (-not (Test-Path "$workspaceDir\.git")) {
    Handle-Error "Git repository not initialized. Run 'git init' first."
}
Write-Host "✓ Git repository found" -ForegroundColor Green

# Step 2: Push to GitHub
Write-Host "`n[2/4] Preparing GitHub push..." -ForegroundColor Yellow

# Add GitHub remote if not exists
$remoteUrl = "https://$GitHubUsername`:$GitHubToken@github.com/$GitHubUsername/$RepositoryName.git"
$existingRemote = git -C $workspaceDir remote get-url origin 2>$null

if ($null -eq $existingRemote -or $existingRemote -eq "origin") {
    Write-Host "Adding GitHub remote..."
    git -C $workspaceDir remote add origin $remoteUrl 2>$null
    if ($LASTEXITCODE -ne 0) {
        git -C $workspaceDir remote set-url origin $remoteUrl
    }
}

# Push to GitHub
Write-Host "Pushing code to GitHub..."
git -C $workspaceDir branch -M main
git -C $workspaceDir push -u origin main --force

if ($LASTEXITCODE -ne 0) {
    Handle-Error "Failed to push to GitHub"
}
Write-Host "✓ Code pushed to GitHub successfully" -ForegroundColor Green

# Step 3: Display Render deployment instructions
Write-Host "`n[3/4] Preparing for Render deployment..." -ForegroundColor Yellow

$renderInstructions = @"
========================================================
                RENDER DEPLOYMENT GUIDE
========================================================

1. Create Render Account:
   - Go to https://render.com
   - Sign up with GitHub account
   - Authorize Render to access your repositories

2. Deploy Backend Service:
   - Dashboard > New +
   - Select "Web Service"
   - Connect your GitHub repo: $GitHubUsername/$RepositoryName
   - Configuration:
     * Name: recruitment-backend
     * Root Directory: backend
     * Runtime: Python 3.11
     * Build Command: pip install -r requirements.txt
     * Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
     * Plan: Free (or Starter)
   - Environment Variables:
     * ENVIRONMENT=production
     * DEBUG=false
     * PYTHONUNBUFFERED=1
     * POSTGRES_URL=<from PostgreSQL service>
     * MONGODB_URL=<from MongoDB service>
     * JWT_SECRET=<generate secure value>
     * LINKEDIN_CLIENT_ID=<your value>
     * LINKEDIN_CLIENT_SECRET=<your value>

3. Deploy PostgreSQL Database:
   - Dashboard > New +
   - Select "PostgreSQL"
   - Name: recruitment-postgres
   - Copy connection URL to Backend env var POSTGRES_URL

4. Deploy MongoDB Database:
   - Dashboard > New +
   - Select "MongoDB"
   - Name: recruitment-mongo
   - Copy connection URL to Backend env var MONGODB_URL

5. Deploy Frontend Service:
   - Dashboard > New +
   - Select "Static Site"
   - Connect your GitHub repo
   - Configuration:
     * Name: recruitment-frontend
     * Root Directory: frontend
     * Build Command: npm install && npm run build
     * Publish Directory: dist
   - Environment Variables:
     * VITE_API_BASE_URL=<Backend Service URL>/api

6. Connect Services:
   - Update frontend API URL to match backend service URL
   - Wait 5-10 minutes for all services to deploy
   - Test at: https://recruitment-frontend.onrender.com

7. Verify Deployment:
   - Check logs in Render Dashboard
   - Test API endpoints
   - Verify database connectivity

========================================================
IMPORTANT NOTES:
- Free tier sleeps after 15 minutes of inactivity
- Use Starter plan ($7/mo) for 24/7 uptime
- Keep secrets in Render Environment Variables
- Monitor logs for errors
- Update CORS_ORIGINS in backend if needed

Next Steps:
1. Commit and push any remaining changes
2. Create Render account at https://render.com
3. Follow the steps above to deploy
4. Contact support: support@render.com
========================================================
"@

Write-Host $renderInstructions

# Step 4: Create deployment summary
Write-Host "`n[4/4] Creating deployment summary..." -ForegroundColor Yellow

$summaryPath = "$workspaceDir\RENDER_DEPLOYMENT_SUMMARY.txt"
$renderInstructions | Out-File -FilePath $summaryPath -Encoding UTF8
Write-Host "✓ Deployment summary saved to: $summaryPath" -ForegroundColor Green

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Deployment preparation completed!" -ForegroundColor Cyan
Write-Host "Next: Go to https://render.com and follow the guide" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
