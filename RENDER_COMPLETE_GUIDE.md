# Guide Complet de Déploiement sur Render

## Vue d'ensemble
Ce guide vous montrera comment déployer le système de recrutement IA sur **Render**, une plateforme de déploiement simple et gratuite compatible avec GitHub.

## Avantages de Render
- ✅ Plan gratuit disponible
- ✅ Déploiement automatique depuis GitHub
- ✅ Support PostgreSQL, MongoDB, Redis
- ✅ SSL/HTTPS automatique
- ✅ Scaling automatique
- ✅ Pas de carte de crédit requise pour essayer

## Architecture Déploiée
```
├── recruitment-backend (Python FastAPI)
│   └── Port: 8000
│   └── Runtime: Python 3.11
│   └── Database: PostgreSQL
│
├── recruitment-frontend (React Vite)
│   └── Static Site
│   └── Serveur web Render
│   └── API URL: https://recruitment-backend.onrender.com
│
├── PostgreSQL Database
│   └── Pour: Users, Jobs, Candidates
│
└── MongoDB Database
    └── Pour: Interview data, Chat history
```

## Étape 1 : Préparer le dépôt GitHub

### 1.1 Créer un dépôt GitHub
```bash
# Si vous n'avez pas encore pushé votre code
git remote add origin https://github.com/YOUR-USERNAME/ai-recruitment-system.git
git branch -M main
git push -u origin main
```

### 1.2 Vérifier les fichiers de configuration
Les fichiers suivants doivent être présents à la racine du projet:
- ✓ `render.yaml` - Configuration de déploiement
- ✓ `.env.render` - Variables d'environnement (modèle)
- ✓ `backend/requirements.txt` - Dépendances Python
- ✓ `frontend/package.json` - Dépendances Node.js
- ✓ `docker-compose.yml` - Configuration des services locaux

## Étape 2 : Créer un compte Render

1. Allez sur https://render.com
2. Cliquez sur "Sign Up"
3. **Option A:** Connectez-vous avec GitHub (recommandé pour l'intégration)
4. **Option B:** Créez un compte par email
5. Confirmez votre email
6. Vous recevrez $5 de crédit gratuit par mois

## Étape 3 : Déployer le Backend

### 3.1 Créer le service Web Backend

1. Dans le tableau de bord Render, cliquez sur **"New +" → "Web Service"**
2. Sélectionnez **"Connect a repository"**
3. Autorisez Render à accéder à vos dépôts GitHub
4. Sélectionnez le dépôt `ai-recruitment-system`

### 3.2 Configurer le service Web Backend

**Configuration Générale:**
- **Name:** `recruitment-backend`
- **Root Directory:** `backend`
- **Runtime:** `Python 3.11`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Plan:** `Free` (ou Starter pour 24/7)
- **Auto-Deploy:** Coché

**Régions disponibles:**
- Ohio (recommandé pour USA)
- Frankfurt (recommandé pour Europe)
- Singapore (recommandé pour Asie)

### 3.3 Ajouter les variables d'environnement Backend

Cliquez sur **"Environment"** et ajoutez:

```
ENVIRONMENT=production
DEBUG=false
PYTHONUNBUFFERED=1
PYTHONIOENCODING=utf-8
POSTGRES_URL=postgresql://user:password@localhost:5432/recruitment_db
MONGODB_URL=mongodb://localhost:27017/recruitment_db
API_BASE_URL=https://recruitment-backend.onrender.com
FRONTEND_URL=https://recruitment-frontend.onrender.com
JWT_SECRET=change_this_to_a_very_secure_random_string
JWT_ALGORITHM=HS256
CORS_ORIGINS=*
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=https://recruitment-frontend.onrender.com/linkedin/callback
```

### 3.4 Ajouter la base de données PostgreSQL

1. Retour au tableau de bord Render
2. Cliquez sur **"New +" → "PostgreSQL"**
3. Configuration:
   - **Name:** `recruitment-postgres`
   - **Database:** `recruitment_db`
   - **User:** `postgres`
   - **Plan:** `Free`

4. Une fois créée, copiez l'**Internal Database URL**
5. Retournez au service Backend et mettez à jour:
   - `POSTGRES_URL` = L'URL interne copiée

### 3.5 Ajouter la base de données MongoDB

1. Cliquez sur **"New +" → "MongoDB"**
2. Configuration:
   - **Name:** `recruitment-mongo`
   - **Plan:** `Free`

3. Une fois créée, copiez la **Connection String**
4. Retournez au service Backend et mettez à jour:
   - `MONGODB_URL` = Connection string copiée

## Étape 4 : Déployer le Frontend

### 4.1 Créer le service Frontend

1. Cliquez sur **"New +" → "Static Site"**
2. Sélectionnez le même dépôt GitHub
3. Configuration:
   - **Name:** `recruitment-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`

### 4.2 Configurer les variables d'environnement Frontend

Ajoutez l'URL du backend déployé:

```
VITE_API_BASE_URL=https://recruitment-backend.onrender.com/api
```

## Étape 5 : Vérifier le déploiement

### 5.1 Vérifier les logs

Pour chaque service (Backend, Frontend, BD):
1. Cliquez sur le service dans le tableau de bord
2. Allez dans **"Logs"**
3. Vérifiez qu'il n'y a pas d'erreurs

### 5.2 Tester les endpoints Backend

```bash
# Test basique
curl https://recruitment-backend.onrender.com/api/health

# Lister les candidats
curl https://recruitment-backend.onrender.com/api/candidates

# Lister les offres d'emploi
curl https://recruitment-backend.onrender.com/api/jobs
```

### 5.3 Accéder au frontend

```
https://recruitment-frontend.onrender.com
```

## Étape 6 : Configuration avancée

### 6.1 Mise à jour automatique sur push GitHub

Render fait cela automatiquement. Chaque push sur `main` déclenche:
1. Reconstruction de l'image
2. Redéploiement des services
3. Pas d'interruption si en mode Starter+

### 6.2 Ajouter un domaine personnalisé

1. Dans le service, allez dans **"Settings"**
2. Trouvez **"Custom Domains"**
3. Ajoutez votre domaine
4. Suivez les instructions DNS

### 6.3 Configurer les sauvegardes PostgreSQL

1. Service PostgreSQL → **"Backups"**
2. Render sauvegarde automatiquement
3. Stockage: jusqu'à 7 jours gratuit

## Dépannage

### ❌ Erreur: "Build failed"
**Causes possibles:**
- Dépendances manquantes dans requirements.txt
- Version Python incompatible
- Syntaxe erreur dans le code

**Solution:**
```bash
# Vérifiez localement
python -m pip install -r backend/requirements.txt
uvicorn app.main:app
```

### ❌ Erreur: "Connection refused to database"
**Causes possibles:**
- Variables d'environnement mal configurées
- Base de données pas prête
- Firewall bloquant la connexion

**Solution:**
1. Vérifiez POSTGRES_URL dans Environment
2. Attendez 2-3 minutes après création de la base
3. Utilisez l'URL **interne** pour les services Render

### ❌ Frontend: "Cannot reach API"
**Solution:**
1. Vérifiez VITE_API_BASE_URL dans frontend
2. Vérifiez que Backend est accessible (test curl)
3. Vérifiez CORS_ORIGINS dans Backend (devrait être "*")

### ❌ Déploiement lent
- Plan Free: 3-5 minutes normales
- Plan Starter: 1-2 minutes
- Attendre les premiers déploiements (cache froid)

## Coûts et Limites

### Plan Free
- ✓ Gratuit
- ✓ 5 GB RAM partagé
- ✓ Service dors après 15 min d'inactivité
- ❌ Redémarrage au réveil (cold start ~30s)

### Plan Starter ($7/mois)
- ✓ 24/7 uptime
- ✓ 2 GB RAM dédié
- ✓ Déploiement prioritaire
- ✓ Parfait pour MVP/démo

### Bases de données gratuites
- 256 MB PostgreSQL (Free)
- 512 MB MongoDB (Free)
- Suffisant pour démarrage

## Monitoring et Alertes

1. Tableau de bord Render affiche:
   - État des services (UP/DOWN)
   - Derniers déploiements
   - Logs en temps réel
   - Usage des ressources

2. Email d'alerte sur:
   - Erreurs de déploiement
   - Service down (plan Starter+)
   - Limites de quota

## Intégration GitHub Actions (Optionnel)

Créez `.github/workflows/render-deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Render Deploy
        run: |
          curl --request POST \
            --url https://api.render.com/v1/services/RENDER_SERVICE_ID/deploys \
            --header "authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
```

## Prochaines étapes

1. ✅ Créer compte Render
2. ✅ Déployer Backend + Databases
3. ✅ Déployer Frontend
4. ✅ Tester les endpoints
5. 🔄 Configurer domaine personnalisé (optionnel)
6. 🔄 Ajouter monitoring (optionnel)
7. 🔄 Augmenter à plan Starter pour production (optionnel)

## Support

**Besoin d'aide?**
- Render Docs: https://render.com/docs
- Render Support: https://support.render.com
- Community: https://community.render.com

**Problèmes de déploiement?**
- Vérifiez les logs Render
- Testez localement d'abord avec Docker
- Contactez support@render.com

---

**Estimation de temps:** 15-20 minutes
**Coût:** Gratuit pendant 30 jours (avec crédit $5), puis gratuit si plan Free
**Uptime:** 99.9% garanti (plan Starter+)
