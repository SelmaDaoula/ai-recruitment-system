"""
Routes API pour la gestion des offres d'emploi
Module 1 : Générateur d'annonces
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_db
from app.models.job_offer import JobOffer
from app.modules.job_generator.generator import JobOfferGenerator

# Créer le routeur
router = APIRouter()

# Initialiser le générateur (une seule fois)
generator = JobOfferGenerator()


# ============ MODÈLES PYDANTIC (Validation des données) ============

class JobOfferCreate(BaseModel):
    """
    Schéma pour créer une offre d'emploi
    """
    title: str = Field(..., example="Développeur Python Senior")
    industry: str = Field(..., example="tech")
    location: str = Field(..., example="Paris / Remote")
    contract_type: str = Field(default="CDI", example="CDI")
    
    description: str = Field(default="", example="Poste de développeur backend")
    responsibilities: str = Field(default="", example="Développement d'APIs REST")
    
    required_skills: List[str] = Field(..., example=["Python", "Django", "PostgreSQL"])
    nice_to_have_skills: List[str] = Field(default=[], example=["Docker", "Redis"])
    
    experience_min_years: int = Field(..., example=3)
    experience_max_years: int = Field(default=None, example=5)
    experience_level: str = Field(default="Mid", example="Mid")
    
    education_level: str = Field(default="", example="Bac+5")
    education_field: str = Field(default="", example="Informatique")
    
    languages: List[dict] = Field(
        default=[],
        example=[{"language": "Français", "level": "Natif"}, {"language": "Anglais", "level": "B2"}]
    )
    
    salary_min: Optional[int] = Field(default=None, example=45000)
    salary_max: Optional[int] = Field(default=None, example=55000)
    benefits: str = Field(default="", example="Télétravail, tickets restaurant")
    
    created_by: str = Field(default="admin", example="recruteur@company.com")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Développeur Python Senior",
                "industry": "tech",
                "location": "Paris / Remote",
                "contract_type": "CDI",
                "required_skills": ["Python", "Django", "PostgreSQL"],
                "experience_min_years": 3,
                "experience_max_years": 5,
                "salary_min": 45000,
                "salary_max": 55000
            }
        }


class JobOfferResponse(BaseModel):
    """Schéma de réponse pour une offre d'emploi"""
    id: int
    reference: str
    title: str
    industry: str
    location: str
    required_skills: List[str]
    experience_min_years: int
    salary_min: Optional[int] = None  # ✅ CORRIGÉ
    salary_max: Optional[int] = None  # ✅ CORRIGÉ
    is_active: bool
    linkedin_post: Optional[str] = None
    created_at: datetime
    total_applications: int

    class Config:
        from_attributes = True


class LinkedInPostRequest(BaseModel):
    """
    Schéma pour demander la génération d'une annonce LinkedIn
    """
    job_offer_id: int = Field(..., example=1)


class LinkedInPostResponse(BaseModel):
    """
    Schéma de réponse pour une annonce LinkedIn générée
    """
    job_offer_id: int
    linkedin_post: str
    generated_at: datetime


# ============ ROUTES API ============

@router.post("/create", response_model=JobOfferResponse, status_code=201)
async def create_job_offer(
    job_data: JobOfferCreate,
    db: Session = Depends(get_db)
):
    """
    ✨ Crée une nouvelle offre d'emploi
    
    Cette route crée une offre dans la base de données.
    L'annonce LinkedIn peut être générée séparément avec /generate-linkedin
    
    Args:
        job_data: Données de l'offre d'emploi
        db: Session de base de données (injection automatique)
    
    Returns:
        JobOfferResponse: Offre créée avec son ID
    
    Exemple:
        POST /api/jobs/create
        {
            "title": "Développeur Python",
            "industry": "tech",
            "required_skills": ["Python", "Django"],
            "experience_min_years": 3
        }
    """
    # Générer une référence unique
    import random
    import string
    reference = f"JOB-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    
    # Créer l'objet JobOffer
    new_job = JobOffer(
        reference=reference,
        title=job_data.title,
        industry=job_data.industry,
        location=job_data.location,
        contract_type=job_data.contract_type,
        description=job_data.description,
        responsibilities=job_data.responsibilities,
        required_skills=job_data.required_skills,
        nice_to_have_skills=job_data.nice_to_have_skills,
        experience_min_years=job_data.experience_min_years,
        experience_max_years=job_data.experience_max_years,
        experience_level=job_data.experience_level,
        education_level=job_data.education_level,
        education_field=job_data.education_field,
        languages=job_data.languages,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        benefits=job_data.benefits,
        created_by=job_data.created_by,
        is_active=True
    )
    
    # Sauvegarder en base de données
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job


@router.post("/generate-linkedin", response_model=LinkedInPostResponse)
async def generate_linkedin_post(
    request: LinkedInPostRequest,
    db: Session = Depends(get_db)
):
    """
    🚀 Génère une annonce LinkedIn pour une offre d'emploi
    
    Cette route utilise le générateur NLP pour créer automatiquement
    une annonce LinkedIn professionnelle et optimisée.
    
    Args:
        request: ID de l'offre d'emploi
        db: Session de base de données
    
    Returns:
        LinkedInPostResponse: Annonce générée
    
    Exemple:
        POST /api/jobs/generate-linkedin
        {
            "job_offer_id": 1
        }
    """
    # Récupérer l'offre d'emploi
    job_offer = db.query(JobOffer).filter(JobOffer.id == request.job_offer_id).first()
    
    if not job_offer:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    # Préparer les paramètres pour le générateur
    params = {
        "title": job_offer.title,
        "industry": job_offer.industry,
        "skills": job_offer.required_skills,
        "experience": f"{job_offer.experience_min_years}-{job_offer.experience_max_years or job_offer.experience_min_years + 2} ans",
        "location": job_offer.location,
        "salary_min": job_offer.salary_min,
        "salary_max": job_offer.salary_max
    }
    
    # Générer l'annonce LinkedIn
    linkedin_post = generator.generate_offer(params)
    
    # Sauvegarder l'annonce dans la base de données
    job_offer.linkedin_post = linkedin_post
    job_offer.published_at = datetime.now()
    db.commit()
    
    return LinkedInPostResponse(
        job_offer_id=job_offer.id,
        linkedin_post=linkedin_post,
        generated_at=datetime.now()
    )


@router.get("/", response_model=List[JobOfferResponse])
async def list_job_offers(
    skip: int = 0,
    limit: int = 10,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """
    📋 Liste toutes les offres d'emploi
    
    Args:
        skip: Nombre d'offres à sauter (pagination)
        limit: Nombre maximum d'offres à retourner
        is_active: Filtrer par statut actif/inactif
        db: Session de base de données
    
    Returns:
        List[JobOfferResponse]: Liste des offres
    
    Exemple:
        GET /api/jobs/?skip=0&limit=10&is_active=true
    """
    query = db.query(JobOffer)
    
    # Filtrer par statut si spécifié
    if is_active is not None:
        query = query.filter(JobOffer.is_active == is_active)
    
    # Pagination
    jobs = query.offset(skip).limit(limit).all()
    
    return jobs


@router.get("/{job_id}", response_model=JobOfferResponse)
async def get_job_offer(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    🔍 Récupère une offre d'emploi spécifique
    
    Args:
        job_id: ID de l'offre d'emploi
        db: Session de base de données
    
    Returns:
        JobOfferResponse: Détails de l'offre
    
    Exemple:
        GET /api/jobs/1
    """
    job = db.query(JobOffer).filter(JobOffer.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    return job


@router.put("/{job_id}", response_model=JobOfferResponse)
async def update_job_offer(
    job_id: int,
    job_data: JobOfferCreate,
    db: Session = Depends(get_db)
):
    """
    ✏️ Met à jour une offre d'emploi
    
    Args:
        job_id: ID de l'offre à modifier
        job_data: Nouvelles données
        db: Session de base de données
    
    Returns:
        JobOfferResponse: Offre mise à jour
    
    Exemple:
        PUT /api/jobs/1
        {
            "title": "Nouveau titre",
            ...
        }
    """
    job = db.query(JobOffer).filter(JobOffer.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    # Mettre à jour les champs
    for field, value in job_data.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    return job


@router.delete("/{job_id}")
async def delete_job_offer(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    🗑️ Supprime une offre d'emploi (soft delete)
    
    Args:
        job_id: ID de l'offre à supprimer
        db: Session de base de données
    
    Returns:
        dict: Message de confirmation
    
    Exemple:
        DELETE /api/jobs/1
    """
    job = db.query(JobOffer).filter(JobOffer.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    # Soft delete : on désactive l'offre au lieu de la supprimer
    job.is_active = False
    job.closed_at = datetime.now()
    db.commit()
    
    return {
        "message": "Offre d'emploi désactivée avec succès",
        "job_id": job_id
    }


@router.get("/{job_id}/linkedin-post")
async def get_linkedin_post(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    📄 Récupère l'annonce LinkedIn d'une offre
    
    Args:
        job_id: ID de l'offre d'emploi
        db: Session de base de données
    
    Returns:
        dict: Annonce LinkedIn
    
    Exemple:
        GET /api/jobs/1/linkedin-post
    """
    job = db.query(JobOffer).filter(JobOffer.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    if not job.linkedin_post:
        raise HTTPException(
            status_code=404,
            detail="Aucune annonce LinkedIn générée pour cette offre. Utilisez POST /generate-linkedin"
        )
    
    return {
        "job_id": job_id,
        "linkedin_post": job.linkedin_post,
        "published_at": job.published_at
    }
    
    
@router.post("/{job_id}/publish-linkedin")
async def publish_job_to_linkedin(
    job_id: int,
    regenerate: bool = False,
    db: Session = Depends(get_db)
):
    """Publication automatique sur LinkedIn"""
    from app.modules.linkedin.linkedin_service import LinkedInService
    from app.models.linkedin_account import LinkedInAccount
    import os
    
    # Récupérer l'offre d'emploi
    job_offer = db.query(JobOffer).filter(JobOffer.id == job_id).first()
    if not job_offer:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    # Vérifier qu'un compte LinkedIn est connecté
    linkedin_account = db.query(LinkedInAccount).filter(
        LinkedInAccount.is_active == True
    ).first()
    
    if not linkedin_account:
        raise HTTPException(
            status_code=400,
            detail="Aucun compte LinkedIn connecté."
        )
    
    # ✅ VÉRIFIER QUE person_id existe
    if not linkedin_account.person_id:
        raise HTTPException(
            status_code=400,
            detail="ID person LinkedIn manquant. Reconnectez votre compte dans Settings."
        )
    
    # Générer l'annonce LinkedIn (si besoin)
    if not job_offer.linkedin_post or regenerate:
        params = {
            "title": job_offer.title,
            "industry": job_offer.industry,
            "skills": job_offer.required_skills or [],
            "experience": f"{job_offer.experience_min_years}-{job_offer.experience_max_years or job_offer.experience_min_years+2} ans",
            "location": job_offer.location,
            "salary_min": job_offer.salary_min,
            "salary_max": job_offer.salary_max
        }
        
        linkedin_post = generator.generate_offer(params)
        job_offer.linkedin_post = linkedin_post
        db.commit()
    
    # Initialiser le service LinkedIn
    linkedin_service = LinkedInService(
        client_id=os.getenv("LINKEDIN_CLIENT_ID"),
        client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
        redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI")
    )
    
    # ✅ UTILISER person_id au lieu de linkedin_id
    result = linkedin_service.publish_post(
        access_token=linkedin_account.access_token,
        linkedin_id=linkedin_account.person_id,  # ✅ CHANGÉ ICI
        text=job_offer.linkedin_post,
        visibility="PUBLIC"
    )
    
    # Mettre à jour timestamps
    linkedin_account.last_used_at = datetime.now()
    job_offer.published_at = datetime.now()
    db.commit()
    
    if result["success"]:
        return {
            "success": True,
            "message": "🎉 Annonce générée et publiée sur LinkedIn !",
            "job_id": job_offer.id,
            "linkedin_post": job_offer.linkedin_post,
            "post_id": result.get("post_id"),
            "linkedin_url": "https://www.linkedin.com/feed/"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Échec de la publication : {result.get('error')}"
        )