# Azure Deployment PowerShell Script - Windows
# À exécuter depuis C:\Users\M.S.I\ai-recruitment-system

param(
    [string]$ResourceGroup = "ai-recruitment-rg",
    [string]$Location = "eastus",
    [string]$RegistryName = "recruitmentregistry",
    [string]$WebAppName = "recruitment-backend-api",
    [string]$PostgresServer = "recruitment-postgres-db",
    [string]$CosmosDbName = "recruitment-cosmosdb",
    [string]$RedisName = "recruitment-redis",
    [string]$AppServicePlan = "recruitment-plan"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 AI Recruitment System - Azure Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Login Azure
Write-Host "1️⃣  Logging in to Azure..." -ForegroundColor Yellow
az login

# 2. Create Resource Group
Write-Host "2️⃣  Creating Resource Group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location

# 3. Create Container Registry
Write-Host "3️⃣  Creating Container Registry..." -ForegroundColor Yellow
az acr create `
    --resource-group $ResourceGroup `
    --name $RegistryName `
    --sku Basic

# 4. Build Docker image
Write-Host "4️⃣  Building Docker image..." -ForegroundColor Yellow
docker build -f backend/Dockerfile -t recruitment-backend:latest .

# 5. Push to ACR
Write-Host "5️⃣  Pushing to Azure Container Registry..." -ForegroundColor Yellow
$registryUrl = az acr show --name $RegistryName --query loginServer -o tsv
az acr login --name $RegistryName
docker tag recruitment-backend:latest "$registryUrl/recruitment-backend:latest"
docker push "$registryUrl/recruitment-backend:latest"

# 6. Create PostgreSQL
Write-Host "6️⃣  Creating PostgreSQL Server..." -ForegroundColor Yellow
$postgresPassword = "P@ssw0rd$(Get-Date -Format 'yyyyMMdd')"
az postgres server create `
    --resource-group $ResourceGroup `
    --name $PostgresServer `
    --location $Location `
    --admin-user dbadmin `
    --admin-password $postgresPassword `
    --sku-name B_Gen5_1 `
    --storage-size 51200

Write-Host "PostgreSQL Password: $postgresPassword" -ForegroundColor Green

# 7. Create Cosmos DB
Write-Host "7️⃣  Creating Cosmos DB..." -ForegroundColor Yellow
az cosmosdb create `
    --resource-group $ResourceGroup `
    --name $CosmosDbName `
    --kind MongoDB

# 8. Create Redis
Write-Host "8️⃣  Creating Redis Cache..." -ForegroundColor Yellow
az redis create `
    --resource-group $ResourceGroup `
    --name $RedisName `
    --location $Location `
    --sku Basic `
    --vm-size c0

# 9. Create App Service Plan
Write-Host "9️⃣  Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
    --name $AppServicePlan `
    --resource-group $ResourceGroup `
    --sku B1 `
    --is-linux

# 10. Create Web App
Write-Host "🔟 Creating Web App..." -ForegroundColor Yellow
az webapp create `
    --resource-group $ResourceGroup `
    --plan $AppServicePlan `
    --name $WebAppName `
    --deployment-container-image-name-user recruitment-backend:latest `
    --deployment-container-image-name "$registryUrl/recruitment-backend:latest"

# 11. Configure Docker Registry
Write-Host "1️⃣1️⃣  Configuring Docker Registry..." -ForegroundColor Yellow
$registryUsername = az acr credential show --name $RegistryName --query username -o tsv
$registryPassword = az acr credential show --name $RegistryName --query "passwords[0].value" -o tsv

az webapp config container set `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --docker-custom-image-name-user $registryUsername `
    --docker-custom-image-name "$registryUrl/recruitment-backend:latest" `
    --docker-registry-server-url "https://$registryUrl" `
    --docker-registry-server-user $registryUsername `
    --docker-registry-server-password $registryPassword

# 12. Get connection strings
Write-Host "1️⃣2️⃣  Getting connection strings..." -ForegroundColor Yellow
$postgresHost = az postgres server show -g $ResourceGroup -n $PostgresServer --query fullyQualifiedDomainName -o tsv
$redisHost = az redis show -g $ResourceGroup -n $RedisName --query hostName -o tsv
$redisKey = az redis list-keys -g $ResourceGroup -n $RedisName --query primaryKey -o tsv

$databaseUrl = "postgresql://dbadmin:$postgresPassword@$postgresHost`:5432/recruitment"
$redisUrl = "redis://:$redisKey@$redisHost`:6379"

# 13. Set environment variables
Write-Host "1️⃣3️⃣  Setting environment variables..." -ForegroundColor Yellow
az webapp config appsettings set `
    --resource-group $ResourceGroup `
    --name $WebAppName `
    --settings `
        DATABASE_URL=$databaseUrl `
        REDIS_URL=$redisUrl `
        ENVIRONMENT=production `
        DEBUG=false `
        PORT=8000

# 14. Configure PostgreSQL firewall
Write-Host "1️⃣4️⃣  Configuring PostgreSQL firewall..." -ForegroundColor Yellow
az postgres server firewall-rule create `
    --resource-group $ResourceGroup `
    --server-name $PostgresServer `
    --name AllowAzureServices `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 0.0.0.0

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend URL: https://$WebAppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Swagger UI: https://$WebAppName.azurewebsites.net/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connection Strings:" -ForegroundColor Yellow
Write-Host "DATABASE_URL: $databaseUrl"
Write-Host "REDIS_URL: $redisUrl"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Deploy frontend: npm run build"
Write-Host "2. Test API: curl https://$WebAppName.azurewebsites.net/api/jobs/"
Write-Host "3. View logs: az webapp log tail -g $ResourceGroup -n $WebAppName"
