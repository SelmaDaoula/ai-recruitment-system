# Guide de Déploiement sur Render

## 1. Prérequis
- Compte GitHub avec ton repo pushé
- Compte Render (render.com)

## 2. Étapes de déploiement

### A. Push ton code sur GitHub
```bash
git add .
git commit -m "Fix routes API et préparation Render deployment"
git push origin main
```

### B. Créer un Web Service sur Render
1. Accède à https://render.com
2. Clique sur **"New" → "Web Service"**
3. Connecte ton repo GitHub
4. Remplis les paramètres :
   - **Name** : ai-recruitment-system
   - **Runtime** : Python 3.11
   - **Build Command** : 
     ```
     pip install -r backend/requirements.txt && python -m spacy download fr_core_news_md && cd frontend && npm install && npm run build && cd ..
     ```
   - **Start Command** : 
     ```
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

### C. Variables d'environnement à configurer dans Render
Ajoute ces variables dans **Environment** :

```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
PORT=10000

DATABASE_URL=postgresql://user:password@host/db
MONGODB_URL=mongodb://...
REDIS_URL=redis://...

LINKEDIN_CLIENT_ID=77vd1mn5f8dnxy
LINKEDIN_CLIENT_SECRET=ta_clé_secrète
LINKEDIN_REDIRECT_URI=https://ai-recruitment-system.onrender.com/api/linkedin/callback

FRONTEND_URL=https://ai-recruitment-system.onrender.com
```

### D. Configuration du frontend après déploiement
Ajoute la variable dans frontend/.env (après le déploiement) :
```
VITE_API_URL=https://ai-recruitment-system.onrender.com/api
```

## 3. Déploiement final
1. Clique sur **"Create Web Service"**
2. Render va builder et déployer automatiquement
3. L'app sera accessible sur `https://ai-recruitment-system.onrender.com`

## 4. Vérifier que tout fonctionne
- API Docs : https://ai-recruitment-system.onrender.com/docs
- Frontend : https://ai-recruitment-system.onrender.com

## 5. Troubleshooting
- Vérifier les logs dans Render Dashboard
- S'assurer que les variables d'environnement sont correctes
- Vérifier que les services PostgreSQL/MongoDB/Redis sont accessibles
