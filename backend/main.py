#!/usr/bin/env python
"""
Entry point pour démarrer l'application FastAPI
Utilise uvicorn pour servir l'application
"""

import uvicorn
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Démarrer le serveur Uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
