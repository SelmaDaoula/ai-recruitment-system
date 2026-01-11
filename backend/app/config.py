"""
Configuration de l'application
Gestion des variables d'environnement avec pydantic-settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Configuration de l'application
    Les valeurs sont chargées depuis le fichier .env
    """
    
    # ============ Application ============
    app_name: str = "AI Recruitment System"
    app_version: str = "1.0.0"
    environment: str = os.environ.get("ENVIRONMENT", "development")
    debug: bool = os.environ.get("DEBUG", "true").lower() == "true"
    host: str = "0.0.0.0"
    port: int = int(os.environ.get("PORT", 8000))
    reload: bool = os.environ.get("ENVIRONMENT", "development") != "production"
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # ============ Base de données PostgreSQL ============
    database_url: str = os.environ.get("DATABASE_URL", "postgresql://recruitment_user:recruitment_password_2024@localhost:5432/recruitment_db")
    db_host: str = os.environ.get("DB_HOST", "localhost")
    db_port: int = int(os.environ.get("DB_PORT", "5432"))
    db_user: str = os.environ.get("DB_USER", "recruitment_user")
    db_password: str = os.environ.get("DB_PASSWORD", "recruitment_password_2024")
    db_name: str = os.environ.get("DB_NAME", "recruitment_db")
    
    # ============ MongoDB ============
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "recruitment_documents"
    
    # ============ Redis ============
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # ============ JWT Authentication ============
    secret_key: str = "votre-cle-secrete-changez-moi-en-production-123456789"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # ============ NLP Configuration ============
    spacy_model: str = "fr_core_news_md"
    sentence_transformer_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    use_gpu: bool = False
    
    # ============ File Upload ============
    max_upload_size_mb: int = 10
    allowed_extensions: list = ["pdf", "docx", "jpg", "jpeg", "png"]
    
    # ============ Scoring Configuration ============
    cv_score_weight: float = 0.6
    interview_score_weight: float = 0.4
    
    skill_match_threshold: float = 0.7
    experience_weight: float = 0.3
    skills_weight: float = 0.4
    education_weight: float = 0.2
    languages_weight: float = 0.1
    
    # ============ Chatbot Configuration ============
    welcome_questions: int = 2
    technical_questions: int = 6
    behavioral_questions: int = 4
    adaptive_difficulty: bool = True
    
    # ============ Cache Configuration ============
    enable_cache: bool = True
    cache_ttl: int = 3600
    
    # ============ Performance ============
    max_workers: int = 4
    batch_size: int = 10
    
    # ============ Templates ============
    templates_dir: str = "data/templates"
    question_bank_path: str = "data/question_bank.json"
    
    class Config:
        """
        Configuration de pydantic-settings
        """
        # Charger depuis le .env dans le dossier parent (backend/)
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne une instance unique de Settings (singleton)
    Utilise le cache pour éviter de recharger à chaque appel
    
    Returns:
        Settings: Configuration de l'application
    """
    return Settings()


# ============ Validation de la configuration ============

def validate_config(settings: Settings) -> bool:
    """
    Valide que la configuration est correcte
    
    Args:
        settings: Instance de Settings
    
    Returns:
        bool: True si la config est valide
    
    Raises:
        ValueError: Si la configuration est invalide
    """
    # Vérifier que les poids de scoring font 1.0
    total_weight = (
        settings.experience_weight +
        settings.skills_weight +
        settings.education_weight +
        settings.languages_weight
    )
    
    if abs(total_weight - 1.0) > 0.01:
        raise ValueError(
            f"Les poids de scoring doivent faire 1.0, actuellement: {total_weight}"
        )
    
    # Vérifier que cv_weight + interview_weight = 1.0
    total_final_weight = settings.cv_score_weight + settings.interview_score_weight
    
    if abs(total_final_weight - 1.0) > 0.01:
        raise ValueError(
            f"CV weight + Interview weight doivent faire 1.0, actuellement: {total_final_weight}"
        )
    
    return True


# ============ Helper functions ============

def get_database_url(settings: Settings) -> str:
    """
    Construit l'URL de connexion PostgreSQL
    
    Args:
        settings: Configuration
    
    Returns:
        str: URL de connexion
    """
    return (
        f"postgresql://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


def is_production() -> bool:
    """
    Vérifie si on est en environnement de production
    
    Returns:
        bool: True si production
    """
    settings = get_settings()
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """
    Vérifie si on est en environnement de développement
    
    Returns:
        bool: True si development
    """
    settings = get_settings()
    return settings.environment.lower() == "development"


# ============ Exemple d'utilisation ============

if __name__ == "__main__":
    """
    Test de la configuration
    """
    print("\n" + "="*60)
    print("TEST DE LA CONFIGURATION")
    print("="*60)
    
    # Charger la configuration
    settings = get_settings()
    
    print(f"\nApplication: {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    
    print(f"\nPostgreSQL:")
    print(f"  Host: {settings.db_host}:{settings.db_port}")
    print(f"  Database: {settings.db_name}")
    print(f"  User: {settings.db_user}")
    print(f"  URL: {settings.database_url}")
    
    print(f"\nMongoDB:")
    print(f"  URL: {settings.mongodb_url}")
    print(f"  Database: {settings.mongodb_db_name}")
    
    print(f"\nRedis:")
    print(f"  Host: {settings.redis_host}:{settings.redis_port}")
    
    print(f"\nNLP:")
    print(f"  spaCy Model: {settings.spacy_model}")
    print(f"  Use GPU: {settings.use_gpu}")
    
    print(f"\nScoring:")
    print(f"  CV Weight: {settings.cv_score_weight}")
    print(f"  Interview Weight: {settings.interview_score_weight}")
    print(f"  Skills Weight: {settings.skills_weight}")
    print(f"  Experience Weight: {settings.experience_weight}")
    
    # Valider la configuration
    try:
        validate_config(settings)
        print("\n✅ Configuration valide")
    except ValueError as e:
        print(f"\n❌ Configuration invalide: {e}")
    
    print("="*60 + "\n")