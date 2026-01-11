"""
Gestion des connexions aux bases de données
PostgreSQL, MongoDB, Redis
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pymongo import MongoClient
import redis
from typing import Generator
import logging

from app.config import get_settings

# Configuration
settings = get_settings()
logger = logging.getLogger(__name__)

# ============ PostgreSQL ============

# Créer le moteur SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Vérifie la connexion avant de l'utiliser
    echo=settings.debug  # Log les requêtes SQL en mode debug
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session de base de données PostgreSQL
    Utilisé comme dépendance FastAPI
    
    Yields:
        Session: Session SQLAlchemy
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ MongoDB ============

try:
    mongo_client = MongoClient(
        settings.mongodb_url,
        serverSelectionTimeoutMS=5000  # Timeout de 5 secondes
    )
    # Tester la connexion
    mongo_client.server_info()
    mongodb = mongo_client[settings.mongodb_db_name]
    logger.info("✅ MongoDB connecté")
except Exception as e:
    logger.warning(f"⚠️  MongoDB non disponible : {e}")
    mongo_client = None
    mongodb = None


def get_mongodb():
    """
    Retourne la base de données MongoDB
    
    Returns:
        Database: Base MongoDB ou None
    
    Example:
        db = get_mongodb()
        if db:
            collection = db["cvs"]
            documents = collection.find()
    """
    return mongodb


# ============ Redis ============

try:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,  # Décoder automatiquement en string
        socket_connect_timeout=5  # Timeout de 5 secondes
    )
    # Tester la connexion
    redis_client.ping()
    logger.info("✅ Redis connecté")
except Exception as e:
    logger.warning(f"⚠️  Redis non disponible : {e}")
    redis_client = None


def get_redis():
    """
    Retourne le client Redis
    
    Returns:
        Redis: Client Redis ou None
    
    Example:
        redis_db = get_redis()
        if redis_db:
            redis_db.set("key", "value", ex=3600)
            value = redis_db.get("key")
    """
    return redis_client


# ============ Test des connexions ============

async def test_connections() -> dict:
    """
    Teste toutes les connexions aux bases de données
    
    Returns:
        dict: Statut de chaque connexion
        {
            "postgresql": True/False,
            "mongodb": True/False,
            "redis": True/False
        }
    """
    from sqlalchemy import text
    
    results = {
        "postgresql": False,
        "mongodb": False,
        "redis": False
    }
    
    # Test PostgreSQL
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        results["postgresql"] = True
    except Exception as e:
        logger.error(f"Erreur PostgreSQL: {e}")
    
    # Test MongoDB
    try:
        if mongo_client:
            mongo_client.server_info()
            results["mongodb"] = True
    except Exception as e:
        logger.error(f"Erreur MongoDB: {e}")
    
    # Test Redis
    try:
        if redis_client:
            redis_client.ping()
            results["redis"] = True
    except Exception as e:
        logger.error(f"Erreur Redis: {e}")
    
    return results


# ============ Initialisation des tables ============

def init_db():
    """
    Crée toutes les tables PostgreSQL si elles n'existent pas
    
    Usage:
        from app.database import init_db
        init_db()
    """
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tables PostgreSQL créées")


# ============ Nettoyage ============

def close_connections():
    """
    Ferme toutes les connexions aux bases de données
    Utilisé lors de l'arrêt de l'application
    """
    try:
        if mongo_client:
            mongo_client.close()
            logger.info("✅ MongoDB déconnecté")
    except Exception as e:
        logger.error(f"Erreur fermeture MongoDB: {e}")
    
    try:
        if redis_client:
            redis_client.close()
            logger.info("✅ Redis déconnecté")
    except Exception as e:
        logger.error(f"Erreur fermeture Redis: {e}")
    
    try:
        engine.dispose()
        logger.info("✅ PostgreSQL déconnecté")
    except Exception as e:
        logger.error(f"Erreur fermeture PostgreSQL: {e}")


# ============ Exemple d'utilisation ============

if __name__ == "__main__":
    """
    Test des connexions
    """
    import asyncio
    
    print("\n" + "="*60)
    print("TEST DES CONNEXIONS AUX BASES DE DONNÉES")
    print("="*60)
    
    async def test():
        results = await test_connections()
        
        print("\nRésultats:")
        print(f"  PostgreSQL: {'✅ Connecté' if results['postgresql'] else '❌ Déconnecté'}")
        print(f"  MongoDB:    {'✅ Connecté' if results['mongodb'] else '❌ Déconnecté'}")
        print(f"  Redis:      {'✅ Connecté' if results['redis'] else '❌ Déconnecté'}")
        
        print("\n" + "="*60 + "\n")
    
    asyncio.run(test())