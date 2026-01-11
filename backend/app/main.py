"""
AI Recruitment System - Application principale FastAPI
Système intelligent de recrutement automatisé basé sur le NLP
"""

import sys
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import get_settings
from app.database import engine, Base, get_db, test_connections

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Charger la configuration
settings = get_settings()


# ============ Lifespan : Gestion du cycle de vie de l'application ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du démarrage et de l'arrêt de l'application
    """
    # ========== DÉMARRAGE ==========
    print("\n" + "="*50)
    print("[START] AI RECRUITMENT SYSTEM")
    print("="*50)
    
    try:
        # Valider la configuration
        print("[OK] Configuration validée")
        
        # Tester les connexions aux bases de données
        connections_ok = await test_connections()
        
        if connections_ok["postgresql"]:
            print("[OK] PostgreSQL connecte")
        else:
            print("[ERROR] PostgreSQL non connecte")
        
        if connections_ok["mongodb"]:
            print("[OK] MongoDB connecte")
        else:
            print("[WARN] MongoDB non connecte (optionnel)")
        
        if connections_ok["redis"]:
            print("[OK] Redis connecte")
        else:
            print("[WARN] Redis non connecte (optionnel)")
        
        # Créer les tables PostgreSQL si elles n'existent pas
        if connections_ok["postgresql"]:
            Base.metadata.create_all(bind=engine)
            print("[OK] Base de donnees PostgreSQL initialisee")
        
        # Initialiser le générateur d'annonces (Module 1)
        try:
            from app.modules.job_generator.generator import JobOfferGenerator
            generator = JobOfferGenerator()
            print("[OK] Module 1 (Generateur d'annonces) initialise")
        except Exception as e:
            print(f"[WARN] Erreur initialisation Module 1 : {e}")
        
        # Message de démarrage
        print(f"[OK] Application demarree en mode {settings.environment}")
        print(f"[INFO] Documentation disponible sur: http://localhost:{settings.port}/docs")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Erreur lors du demarrage : {e}")
        logger.error(f"Erreur de demarrage: {e}", exc_info=True)
    
    yield  # L'application tourne
    
    # ========== ARRÊT ==========
    print("\n" + "="*50)
    print("[STOP] SYSTEM SHUTDOWN")
    print("="*50)
    print("[OK] Arret propre de l'application")
    print("="*50 + "\n")


# ============ Création de l'application FastAPI ============

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Système intelligent de recrutement automatisé basé sur le NLP",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============ Configuration CORS ============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Middleware de logging des requêtes ============

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log toutes les requêtes HTTP avec leur durée
    """
    start_time = datetime.now()
    
    # Traiter la requête
    response = await call_next(request)
    
    # Calculer la durée
    duration = (datetime.now() - start_time).total_seconds()
    
    # Logger
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response


# ============ Gestion globale des erreurs ============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Gère toutes les exceptions non capturées
    """
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "Une erreur s'est produite",
            "path": request.url.path
        }
    )


# ============ Import et enregistrement des routes ============

## ============ Import et enregistrement des routes API ============

# Module 1 : Gestion des offres d'emploi
try:
    from app.api import jobs
    app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
    logger.info("✅ Module Jobs chargé et routes /api/jobs enregistrées")
except ImportError as e:
    logger.error(f"❌ Erreur import jobs: {e}")
    raise

# Module 2 : Analyse de CV
try:
    from app.api import candidates
    app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
    logger.info("✅ Module Candidates chargé et routes /api/candidates enregistrées")
except ImportError as e:
    logger.error(f"❌ Erreur import candidates: {e}")
    raise

# Module 3 : Chatbot d'entretien
try:
    from app.api import interviews
    app.include_router(interviews.router, prefix="/api/interviews", tags=["Interviews"])
    logger.info("✅ Module Interviews chargé et routes /api/interviews enregistrées")
except ImportError as e:
    logger.warning(f"⚠️  Module Interviews non disponible : {e}")

# Module LinkedIn OAuth
try:
    from app.routers import linkedin
    # ✅ NE PAS ajouter de prefix ici car linkedin.py l'a déjà !
    app.include_router(linkedin.router)
    logger.info("✅ Module LinkedIn OAuth chargé et routes /api/linkedin enregistrées")
except ImportError as e:
    logger.warning(f"⚠️  Module LinkedIn non disponible : {e}")

# Log all registered routes for debug
for route in app.routes:
    logger.info(f"Route registered: {route.path} [{route.name}]")
# ============ Routes de base ============

@app.get("/")
async def root():
    """
    🏠 Page d'accueil de l'API
    """
    linkedin_available = "linkedin" in sys.modules or any(
        "linkedin" in str(route.path) for route in app.routes
    )
    
    return {
        "message": "Bienvenue sur le système de recrutement IA",
        "version": settings.app_version,
        "environment": settings.environment,
        "documentation": "/docs",
        "modules": {
            "module_1": {
                "name": "Générateur d'annonces LinkedIn",
                "status": "✅ Actif",
                "endpoints": [
                    "POST /api/jobs/create",
                    "POST /api/jobs/generate-linkedin-post",
                    "GET /api/jobs/"
                ]
            },
            "module_2": {
                "name": "Analyse de CV",
                "status": "✅ Actif",
                "endpoints": [
                    "POST /api/candidates/upload-cv",
                    "GET /api/candidates/{candidate_id}/analysis"
                ]
            },
            "module_3": {
                "name": "Chatbot d'entretien",
                "status": "✅ Actif" if "interviews" in sys.modules else "⚠️ Non disponible",
                "endpoints": [
                    "POST /api/interviews/start",
                    "POST /api/interviews/{session_id}/answer"
                ]
            },
            "module_linkedin": {
                "name": "LinkedIn OAuth Integration",
                "status": "✅ Actif" if linkedin_available else "⚠️ Non disponible",
                "endpoints": [
                    "GET /api/linkedin/connect",
                    "GET /api/linkedin/callback",
                    "POST /api/linkedin/publish",
                    "GET /api/linkedin/status"
                ]
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """
    🏥 Endpoint de health check
    """
    connections = await test_connections()
    
    if connections["postgresql"]:
        status = "healthy"
    else:
        status = "degraded"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "connections": {
            "postgresql": "✅ Connected" if connections["postgresql"] else "❌ Disconnected",
            "mongodb": "✅ Connected" if connections["mongodb"] else "⚠️  Disconnected",
            "redis": "✅ Connected" if connections["redis"] else "⚠️  Disconnected"
        }
    }


@app.get("/config")
async def get_config():
    """
    ⚙️ Récupère la configuration de l'application
    """
    if not settings.debug:
        return {
            "error": "Configuration endpoint disabled in production",
            "debug_mode": False
        }
    
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "database": {
            "postgresql": {
                "host": settings.db_host,
                "port": settings.db_port,
                "database": settings.db_name,
                "user": settings.db_user
            }
        }
    }


# ============ Point d'entrée ============

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )