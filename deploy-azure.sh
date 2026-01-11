#!/bin/bash

# Azure Deployment Script - Complete Setup
# Ce script déploie l'application entière sur Azure

set -e

echo "=========================================="
echo "🚀 AI Recruitment System - Azure Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="ai-recruitment-rg"
LOCATION="eastus"
REGISTRY_NAME="recruitmentregistry"
APP_SERVICE_PLAN="recruitment-plan"
WEB_APP_NAME="recruitment-backend"
FRONTEND_APP_NAME="recruitment-frontend"
CONTAINER_NAME="recruitment-backend"
POSTGRES_SERVER="recruitment-postgres"
COSMOSDB_NAME="recruitment-mongodb"
REDIS_NAME="recruitment-redis"

echo -e "${YELLOW}1️⃣  Logging into Azure...${NC}"
az login

echo -e "${YELLOW}2️⃣  Creating Resource Group...${NC}"
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION || true

echo -e "${YELLOW}3️⃣  Creating Azure Container Registry...${NC}"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic || true

echo -e "${YELLOW}4️⃣  Building and pushing Docker image...${NC}"
docker build -t recruitment-backend:latest ./backend
az acr build \
  --registry $REGISTRY_NAME \
  --image recruitment-backend:latest \
  ./backend

echo -e "${YELLOW}5️⃣  Creating App Service Plan...${NC}"
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux || true

echo -e "${YELLOW}6️⃣  Creating Web App...${NC}"
REGISTRY_URL=$(az acr show --name $REGISTRY_NAME --query loginServer -o tsv)
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $WEB_APP_NAME \
  --deployment-container-image-name-user recruitment-backend:latest \
  --deployment-container-image-name $REGISTRY_URL/recruitment-backend:latest || true

echo -e "${YELLOW}7️⃣  Configuring Docker settings...${NC}"
az webapp config container set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $REGISTRY_URL/recruitment-backend:latest \
  --docker-registry-server-url https://$REGISTRY_URL \
  --docker-registry-server-user $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
  --docker-registry-server-password $(az acr credential show --name $REGISTRY_NAME --query 'passwords[0].value' -o tsv)

echo -e "${YELLOW}8️⃣  Creating PostgreSQL Database...${NC}"
az postgres server create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER \
  --location $LOCATION \
  --admin-user dbadmin \
  --admin-password P@ssw0rd$(date +%s) \
  --sku-name B_Gen5_1 \
  --storage-size 51200 || true

echo -e "${YELLOW}9️⃣  Creating Cosmos DB (MongoDB)...${NC}"
az cosmosdb create \
  --resource-group $RESOURCE_GROUP \
  --name $COSMOSDB_NAME \
  --kind MongoDB \
  --default-consistency-level Eventual || true

echo -e "${YELLOW}🔟 Creating Redis Cache...${NC}"
az redis create \
  --resource-group $RESOURCE_GROUP \
  --name $REDIS_NAME \
  --location $LOCATION \
  --sku Basic \
  --vm-size c0 || true

echo ""
echo -e "${GREEN}✅ All Azure resources created!${NC}"
echo ""
echo "=========================================="
echo "📝 Next Steps:"
echo "=========================================="
echo ""
echo "1. Get connection strings:"
echo ""
echo -e "${YELLOW}PostgreSQL:${NC}"
PSQL_HOST=$(az postgres server show -g $RESOURCE_GROUP -n $POSTGRES_SERVER --query fullyQualifiedDomainName -o tsv)
echo "Host: $PSQL_HOST"
echo "Username: dbadmin"
echo "Connection string:"
echo "postgresql://dbadmin:PASSWORD@$PSQL_HOST:5432/recruitment"
echo ""

echo -e "${YELLOW}MongoDB (Cosmos DB):${NC}"
az cosmosdb keys list --name $COSMOSDB_NAME --resource-group $RESOURCE_GROUP

echo ""
echo -e "${YELLOW}Redis:${NC}"
REDIS_HOST=$(az redis show -g $RESOURCE_GROUP -n $REDIS_NAME --query hostName -o tsv)
echo "Host: $REDIS_HOST"
echo "Port: 6379"
echo ""

echo "2. Set environment variables in Web App:"
echo ""
echo "   az webapp config appsettings set \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --name $WEB_APP_NAME \\"
echo "     --settings \\"
echo "       DATABASE_URL='postgresql://dbadmin:PASSWORD@$PSQL_HOST:5432/recruitment' \\"
echo "       MONGODB_URL='mongodb+srv://...' \\"
echo "       REDIS_URL='redis://:PASSWORD@$REDIS_HOST:6379' \\"
echo "       ENVIRONMENT='production' \\"
echo "       DEBUG='false'"
echo ""

echo "3. Deploy frontend:"
echo ""
echo "   npm run build"
echo "   az staticwebapp create --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --source https://github.com/YOUR_REPO"
echo ""

echo -e "${GREEN}Deployment script completed!${NC}"
