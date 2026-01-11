# 🚀 Déploiement Render - Guide Simple

## Étape 1 : Préparer le code

```bash
# Depuis C:\Users\M.S.I\ai-recruitment-system
cd C:\Users\M.S.I\ai-recruitment-system
git init
git add .
git commit -m "Projet prêt pour Render"
git remote add origin https://github.com/YOUR_USERNAME/ai-recruitment-system.git
git push -u origin main
```

## Étape 2 : Créer un compte Render

1. Allez sur https://render.com
2. Cliquez sur **Sign Up** avec GitHub
3. Autorisez Render à accéder à vos repos

## Étape 3 : Créer la Web Service

1. Dans le dashboard Render : **+ New** → **Web Service**
2. Connectez le repo GitHub
3. Configurez :
   - **Name** : `ai-recruitment-system`
   - **Runtime** : `Docker`
   - **Build Command** : Laisser vide (Render le détecte)
   - **Start Command** : `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan** : `Free` (gratuit avec limitations)

## Étape 4 : Configurer les variables d'environnement

Aller dans **Settings** → **Environment Variables** et ajouter :

```
ENVIRONMENT = production
DEBUG = false
DATABASE_URL = postgresql://... (voir étape 5)
MONGODB_URL = mongodb+srv://... (voir étape 5)
REDIS_URL = redis://... (voir étape 5)
```

## Étape 5 : Ajouter les bases de données

### PostgreSQL gratuit sur Render
1. Render Dashboard → **Databases** → **New Database**
2. Créer une base PostgreSQL gratuite
3. Copier la connection string

### MongoDB gratuit sur MongoDB Atlas
1. Aller sur https://www.mongodb.com/cloud/atlas
2. Créer un cluster gratuit M0
3. Copier la connection string

### Redis (optionnel pour le free plan)
- On peut utiliser la version en mémoire de Render ou sauter pour maintenant

## Étape 6 : Déployer

1. Cliquer sur **Create Web Service**
2. Render va builder et déployer (5-10 minutes)
3. C'est live ! 🎉

## URLs finales

```
Frontend : https://ai-recruitment-system.onrender.com
Backend API : https://ai-recruitment-system.onrender.com/api
Swagger : https://ai-recruitment-system.onrender.com/docs
```

## Troubleshooting

### Le build échoue
- Vérifier les logs dans Render Dashboard
- Vérifier que render.yaml existe
- Vérifier backend/Dockerfile

### Erreur "spaCy model not found"
- Render va télécharger le modèle automatiquement pendant le build
- Si ça timeout, augmenter le timeout du build dans Render

### API retourne 404
- Vérifier que DATABASE_URL est correct
- Vérifier les logs : Render Dashboard → Logs
- Tester avec curl : `curl https://your-app.onrender.com/api/jobs/`

## Coûts

- **Free Plan** : Gratuit (peut sleep après 15 min inactivité)
- **Starter** : $7/mois (toujours actif)
- Bases de données : À payer selon utilisation

## Déploiement continu

À chaque push sur GitHub, Render redéploie automatiquement !

```bash
# Faire un changement
git add .
git commit -m "Nouvelle feature"
git push origin main

# → Render redéploie en ~5 min
```
