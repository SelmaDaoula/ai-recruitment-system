# Déploiement sur Azure

## Prérequis

1. **Compte Azure** : https://azure.microsoft.com/fr-fr/
2. **Azure CLI** : https://learn.microsoft.com/fr-fr/cli/azure/install-azure-cli
3. **Docker Desktop** (déjà installé)
4. **GitHub account** avec ce repo
5. **Visual Studio Code** avec l'extension Azure

## Étape 1 : Créer un Resource Group

```bash
az login
az group create --name ai-recruitment-rg --location eastus
```

## Étape 2 : Créer les bases de données

### PostgreSQL
```bash
az postgres server create \
  --resource-group ai-recruitment-rg \
  --name recruitment-postgres \
  --location eastus \
  --admin-user dbadmin \
  --admin-password P@ssw0rd123456 \
  --sku-name B_Gen5_1 \
  --storage-size 51200
```

### MongoDB (Cosmos DB)
```bash
az cosmosdb create \
  --resource-group ai-recruitment-rg \
  --name recruitment-mongodb \
  --kind MongoDB
```

### Redis
```bash
az redis create \
  --resource-group ai-recruitment-rg \
  --name recruitment-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

## Étape 3 : Créer un Container Registry

```bash
az acr create \
  --resource-group ai-recruitment-rg \
  --name recruitmentregistry \
  --sku Basic
```

## Étape 4 : Obtenir les Connection Strings

```bash
# PostgreSQL
az postgres server connection-string-sqlalchemy \
  --server-name recruitment-postgres \
  --resource-group ai-recruitment-rg

# MongoDB
az cosmosdb keys list \
  --name recruitment-mongodb \
  --resource-group ai-recruitment-rg

# Redis
az redis show-connection-string \
  --name recruitment-redis \
  --resource-group ai-recruitment-rg
```

## Étape 5 : Configurer GitHub Actions

1. Allez sur GitHub → Settings → Secrets and variables → Actions
2. Ajoutez les secrets suivants :

```
AZURE_CREDENTIALS         # az ad sp create-for-rbac --role contributor --scopes /subscriptions/{subscription-id}
REGISTRY_LOGIN_SERVER     # recruitment-registry.azurecr.io
REGISTRY_USERNAME         # (du az acr credential show)
REGISTRY_PASSWORD         # (du az acr credential show)
DATABASE_URL              # postgresql://user:pass@host:5432/db
MONGODB_URL               # mongodb+srv://...
REDIS_URL                 # redis://:password@host:6379
AZURE_RESOURCE_GROUP      # ai-recruitment-rg
AZURE_STATIC_WEB_APPS_API_TOKEN  # (créé lors du déploiement SWA)
```

## Étape 6 : Déployer manuellement (optionnel)

### Backend

```bash
# Build Docker image
cd backend
docker build -t recruitmentregistry.azurecr.io/recruitment-backend:latest .

# Push au registry
az acr login --name recruitmentregistry
docker push recruitmentregistry.azurecr.io/recruitment-backend:latest

# Deploy sur Container Instances
az container create \
  --resource-group ai-recruitment-rg \
  --name recruitment-backend \
  --image recruitmentregistry.azurecr.io/recruitment-backend:latest \
  --cpu 2 --memory 2 \
  --registry-login-server recruitmentregistry.azurecr.io \
  --registry-username <USERNAME> \
  --registry-password <PASSWORD> \
  --environment-variables \
    DATABASE_URL="postgresql://..." \
    MONGODB_URL="mongodb+srv://..." \
    REDIS_URL="redis://..." \
    ENVIRONMENT=production \
  --ports 8000 \
  --protocol TCP \
  --dns-name-label recruitment-backend
```

### Frontend

```bash
# Build React app
cd frontend
npm install
npm run build

# Deploy sur Static Web Apps
az staticwebapp create \
  --name recruitment-frontend \
  --resource-group ai-recruitment-rg \
  --source https://github.com/yourusername/ai-recruitment-system \
  --location eastus \
  --branch main
```

## Étape 7 : Configuration post-déploiement

1. **Mettre à jour CORS** dans `backend/app/main.py` :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://recruitment-frontend.azurestaticapps.net",
        "https://recruitment-backend.eastus.azurecontainer.io"
    ],
    ...
)
```

2. **Configurer les variables d'environnement** dans Azure Container Instances

3. **Configurer le domaine personnalisé** (optionnel)

## URLs de production

- **Frontend** : `https://recruitment-frontend.azurestaticapps.net`
- **Backend API** : `https://recruitment-backend.eastus.azurecontainer.io:8000/api`
- **Swagger** : `https://recruitment-backend.eastus.azurecontainer.io:8000/docs`

## Coûts estimés (USD/mois)

- Azure Static Web Apps : $0 (gratuit tier)
- Container Instances : ~$10-20
- PostgreSQL (Basic B1) : ~$15
- Cosmos DB (Free tier) : ~$0
- Redis (Basic) : ~$14
- **Total** : ~$39-49/mois

## Troubleshooting

### Erreur de connexion à la base de données
```bash
# Vérifier les règles de pare-feu PostgreSQL
az postgres server firewall-rule create \
  --resource-group ai-recruitment-rg \
  --server recruitment-postgres \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Vérifier les logs
```bash
az container logs --resource-group ai-recruitment-rg --name recruitment-backend
```

### Redéployer
```bash
az container delete --resource-group ai-recruitment-rg --name recruitment-backend
# Puis re-exécuter la création
```
