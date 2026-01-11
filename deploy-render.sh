#!/bin/bash
# Script de déploiement sur Render (bash pour Linux/Mac)

echo "🚀 Préparation du déploiement sur Render..."
echo ""

# Vérifier que nous sommes sur la branche main
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
  echo "⚠️  Tu n'es pas sur la branche 'main'. Checkouts: git checkout main"
  exit 1
fi

# Vérifier le statut git
echo "📝 Vérification du statut git..."
if ! git diff-index --quiet HEAD --; then
  echo "⚠️  Tu as des changements non committés. Commit d'abord:"
  echo "   git add ."
  echo "   git commit -m 'Changements avant déploiement Render'"
  exit 1
fi

# Push vers GitHub
echo "📤 Push des changements vers GitHub..."
git push origin main

echo ""
echo "✅ Déploiement préparé !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Accède à https://render.com"
echo "2. Crée un nouveau Web Service"
echo "3. Connecte ton repo GitHub"
echo "4. Configure les variables d'environnement (voir RENDER_DEPLOYMENT.md)"
echo "5. Lance le déploiement"
echo ""
echo "💡 Ton application sera disponible sur : https://ai-recruitment-system.onrender.com"
