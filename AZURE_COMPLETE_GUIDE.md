# 🚀 Guide Complet - Déploiement sur Azure

## Phase 1 : Préparation (10 min)

### 1.1 Installer Azure CLI
```powershell
# Windows PowerShell - télécharger depuis :
# https://aka.ms/installazurecliwindows

# Ou avec Chocolatey :
choco install azure-cli
```

### 1.2 Installer Docker Desktop
- Si déjà installé, c'est OK
- Sinon : https://www.docker.com/products/docker-desktop

### 1.3 Créer un compte Azure
- Aller sur https://azure.microsoft.com/fr-fr/free/
- Créer un compte (vous recevez $200 de crédit gratuit)

---

## Phase 2 : Configuration Azure (15 min)

### 2.1 Se connecter à Azure
```bash
az login
# Cela ouvrira votre navigateur pour vous identifier
```

### 2.2 Vérifier votre souscription
```bash
az account show
```

### 2.3 Créer un Resource Group
```bash
az group create --name ai-recruitment-rg --location eastus
```

---

## Phase 3 : Créer les services (20 min)

### 3.1 Créer Azure Container Registry (pour les images Docker)
```bash
az acr create \
  --resource-group ai-recruitment-rg \
  --name recruitmentregistry \
  --sku Basic
```

### 3.2 Créer PostgreSQL Database
```bash
az postgres server create \
  --resource-group ai-recruitment-rg \
  --name recruitment-postgres-db \
  --location eastus \
  --admin-user dbadmin \
  --admin-password "P@ssw0rd2026!" \
  --sku-name B_Gen5_1 \
  --storage-size 51200
```

**Important** : Notez bien le mot de passe !

### 3.3 Créer Cosmos DB (MongoDB)
```bash
az cosmosdb create \
  --resource-group ai-recruitment-rg \
  --name recruitment-cosmosdb \
  --kind MongoDB
```

### 3.4 Créer Redis Cache
```bash
az redis create \
  --resource-group ai-recruitment-rg \
  --name recruitment-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

---

## Phase 4 : Obtenir les Connection Strings (5 min)

### 4.1 PostgreSQL
```bash
# Récupérer l'hostname
az postgres server show \
  --resource-group ai-recruitment-rg \
  --name recruitment-postgres-db \
  --query fullyQualifiedDomainName -o tsv

# Connection string :
# postgresql://dbadmin:P@ssw0rd2026!@recruitment-postgres-db.postgres.database.azure.com:5432/recruitment
```

### 4.2 MongoDB (Cosmos DB)
```bash
# Récupérer les credentials
az cosmosdb keys list \
  --resource-group ai-recruitment-rg \
  --name recruitment-cosmosdb
```

### 4.3 Redis
```bash
# Récupérer l'hostname
az redis show \
  --resource-group ai-recruitment-rg \
  --name recruitment-redis \
  --query hostName -o tsv

# Connection string :
# redis://:PASSWORD@recruitment-redis.redis.cache.windows.net:6379
```

---

## Phase 5 : Déployer le Backend (15 min)

### 5.1 Build l'image Docker
```bash
cd C:\Users\M.S.I\ai-recruitment-system

# Build
docker build -f backend/Dockerfile -t recruitment-backend:latest .
```

### 5.2 Push vers Azure Container Registry
```bash
# Se connecter au registry
az acr login --name recruitmentregistry

# Tagger l'image
docker tag recruitment-backend:latest recruitmentregistry.azurecr.io/recruitment-backend:latest

# Push
docker push recruitmentregistry.azurecr.io/recruitment-backend:latest
```

### 5.3 Créer App Service Plan
```bash
az appservice plan create \
  --name recruitment-plan \
  --resource-group ai-recruitment-rg \
  --sku B1 \
  --is-linux
```

### 5.4 Créer Web App
```bash
az webapp create \
  --resource-group ai-recruitment-rg \
  --plan recruitment-plan \
  --name recruitment-backend-api \
  --deployment-container-image-name-user recruitment-backend:latest \
  --deployment-container-image-name recruitmentregistry.azurecr.io/recruitment-backend:latest
```

### 5.5 Configurer les variables d'environnement
```bash
az webapp config appsettings set \
  --resource-group ai-recruitment-rg \
  --name recruitment-backend-api \
  --settings \
    DATABASE_URL="postgresql://dbadmin:P@ssw0rd2026!@recruitment-postgres-db.postgres.database.azure.com:5432/recruitment" \
    MONGODB_URL="mongodb+srv://..." \
    REDIS_URL="redis://:PASSWORD@recruitment-redis.redis.cache.windows.net:6379" \
    ENVIRONMENT=production \
    DEBUG=false \
    PORT=8000
```

### 5.6 Configurer la connexion Docker Registry
```bash
REGISTRY_URL=$(az acr show --name recruitmentregistry --query loginServer -o tsv)
REGISTRY_USERNAME=$(az acr credential show --name recruitmentregistry --query username -o tsv)
REGISTRY_PASSWORD=$(az acr credential show --name recruitmentregistry --query "passwords[0].value" -o tsv)

az webapp config container set \
  --name recruitment-backend-api \
  --resource-group ai-recruitment-rg \
  --docker-custom-image-name-user $REGISTRY_USERNAME \
  --docker-custom-image-name $REGISTRY_URL/recruitment-backend:latest \
  --docker-registry-server-url https://$REGISTRY_URL \
  --docker-registry-server-user $REGISTRY_USERNAME \
  --docker-registry-server-password $REGISTRY_PASSWORD
```

### 5.7 Configurer les règles de pare-feu PostgreSQL
```bash
# Permettre les services Azure
az postgres server firewall-rule create \
  --resource-group ai-recruitment-rg \
  --server-name recruitment-postgres-db \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

---

## Phase 6 : Déployer le Frontend (10 min)

### 6.1 Build React
```bash
cd frontend
npm install
npm run build
```

### 6.2 Créer Static Web App
```bash
az staticwebapp create \
  --name recruitment-frontend \
  --resource-group ai-recruitment-rg \
  --source https://github.com/YOUR_USERNAME/ai-recruitment-system \
  --location westeurope \
  --branch main
```

**Important** : Remplacer `YOUR_USERNAME` par votre nom GitHub

### 6.3 Configurer la connexion au backend
Mettre à jour `frontend/src/services/api.ts` :
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  `https://recruitment-backend-api.azurewebsites.net/api`
```

---

## Phase 7 : Vérification et Tests (10 min)

### 7.1 Tester le backend
```bash
# Récupérer l'URL
az webapp show \
  --resource-group ai-recruitment-rg \
  --name recruitment-backend-api \
  --query defaultHostName -o tsv

# Test
curl https://recruitment-backend-api.azurewebsites.net/api/jobs/
```

### 7.2 Vérifier les logs
```bash
az webapp log tail \
  --resource-group ai-recruitment-rg \
  --name recruitment-backend-api
```

### 7.3 Voir le frontend
```
https://recruitment-frontend.staticapp.azure.com
```

---

## URLs Finales

```
🎨 Frontend : https://recruitment-frontend.staticapp.azure.com
⚙️ Backend API : https://recruitment-backend-api.azurewebsites.net/api
📚 Swagger : https://recruitment-backend-api.azurewebsites.net/docs
```

---

## Troubleshooting

### Erreur de connexion PostgreSQL
```bash
# Vérifier les règles de pare-feu
az postgres server firewall-rule list \
  --resource-group ai-recruitment-rg \
  --server-name recruitment-postgres-db

# Ajouter votre IP
az postgres server firewall-rule create \
  --resource-group ai-recruitment-rg \
  --server-name recruitment-postgres-db \
  --name ClientIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

### Container ne démarre pas
```bash
# Voir les logs
az webapp log show \
  --resource-group ai-recruitment-rg \
  --name recruitment-backend-api

# Redémarrer
az webapp restart \
  --resource-group ai-recruitment-rg \
  --name recruitment-backend-api
```

### Coûts
- App Service Plan B1: ~$15/mois
- PostgreSQL B1: ~$15/mois
- Cosmos DB (free tier): $0
- Redis Basic: ~$14/mois
- Static Web App: $0
- **Total**: ~$44/mois

---

## Déploiement Continu

Pour que GitHub déploie automatiquement :

1. Créer un Personal Access Token GitHub
2. Configurer Azure DevOps Pipeline
3. À chaque push, Azure redéploie automatiquement

---

## Nettoyage complet (si nécessaire)
```bash
# Supprimer tout
az group delete --name ai-recruitment-rg --yes
```

---

**Vous avez besoin d'aide ?** Contactez le support Azure : https://azure.microsoft.com/fr-fr/support/
