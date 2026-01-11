"""
Routes API pour la gestion des candidats et analyse de CV
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import shutil
from pathlib import Path
import logging

from app.database import get_db
from app.models.candidate import Candidate
from app.models.job_offer import JobOffer
from app.modules.cv_analyzer import CVParser, CVMatcher
from app.modules.cv_analyzer.scorer import CVScorer
from app.modules.cv_analyzer.extractor_ml import CVExtractorML
from app.modules.cv_analyzer.statistics import RecruitmentStats
from app.modules.cv_analyzer.excel_exporter import ExcelExporter

from app.modules.cv_analyzer.improved_analyzer import ImprovedCVAnalyzer
from pydantic import BaseModel, EmailStr
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialiser les modules NLP
cv_parser = CVParser()
cv_extractor = CVExtractorML(custom_model_path="models/skill_ner_v2")
cv_matcher = CVMatcher(use_bert=True)
cv_scorer = CVScorer()
excel_exporter = ExcelExporter()

# Dossier pour stocker les CVs
UPLOAD_DIR = Path("data/uploads/cvs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============ Schémas Pydantic ============

class CandidateUploadResponse(BaseModel):
    """Réponse après upload du CV"""
    candidate_id: int
    name: Optional[str]
    email: Optional[str]
    cv_filename: str
    status: str
    message: str


class CandidateAnalysisResponse(BaseModel):
    """Réponse avec l'analyse complète"""
    candidate_id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    extracted_data: dict
    cv_score: float
    score_breakdown: dict
    recommendation: str
    category: str


class CandidateListResponse(BaseModel):
    """Candidat dans une liste"""
    id: int
    name: Optional[str] = "Nom non trouvé"
    email: Optional[str]
    cv_score: float
    final_score: float
    application_status: str
    applied_at: datetime
    recommendation: str


class CandidateRankingResponse(BaseModel):
    """Classement des candidats"""
    candidate_id: int
    ranking: int
    name: Optional[str]
    email: Optional[str]
    final_score: float
    cv_score: float
    category: str
    recommendation: str


# ============ Routes d'Upload et Analyse ============

@router.post("/upload-cv", response_model=CandidateUploadResponse, status_code=201)
async def upload_and_analyze_cv(
    job_offer_id: int,
    cv_file: UploadFile = File(...),
    use_improved: bool = Query(True, description="Utiliser le nouvel analyseur (True) ou l'ancien (False)"),
    db: Session = Depends(get_db)
):
    """
    📤 Upload et analyse d'un CV
    
    Cette route :
    1. Sauvegarde le fichier PDF
    2. Extrait le texte avec pdfplumber
    3. Extrait les données (NLP)
    4. Match avec l'offre d'emploi
    5. Calcule le score
    6. Sauvegarde le candidat en base
    
    Args:
        job_offer_id: ID de l'offre d'emploi
        cv_file: Fichier PDF du CV
        use_improved: True = nouvel analyseur, False = ancien (défaut)
    
    Returns:
        CandidateUploadResponse: Données du candidat créé
    
    Example:
        curl -X POST "http://localhost:8000/api/candidates/upload-cv?job_offer_id=1&use_improved=true" \
             -F "cv_file=@mon_cv.pdf"
    """
    logger.info(f"📤 Upload CV pour offre #{job_offer_id} (Improved: {use_improved})")
    
    # ========== 1. Vérifier que l'offre existe ==========
    job_offer = db.query(JobOffer).filter(JobOffer.id == job_offer_id).first()
    if not job_offer:
        raise HTTPException(status_code=404, detail=f"Offre d'emploi #{job_offer_id} introuvable")
    
    # ========== 2. Vérifier que c'est un PDF ==========
    if not cv_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")
    
    try:
        # ========== 3. Sauvegarder le fichier ==========
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{cv_file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(cv_file.file, buffer)
        
        logger.info(f"✅ CV sauvegardé : {safe_filename}")
        
        # ========== 4. Extraire le texte du PDF ==========
        cv_text = cv_parser.extract_text_from_pdf(str(file_path))
        logger.info(f"📄 Texte extrait : {len(cv_text)} caractères")
        
        # ========== 5. Analyser selon la méthode choisie ==========
        if use_improved:
            # NOUVEAU ANALYSEUR
            from app.modules.cv_analyzer.improved_analyzer import ImprovedCVAnalyzer
            
            analyzer = ImprovedCVAnalyzer()
            analysis = analyzer.analyze(cv_text, {
                "required_skills": job_offer.required_skills or [],
                "nice_to_have_skills": job_offer.nice_to_have_skills or [],
                "experience_min_years": job_offer.experience_min_years or 0,
                "education_level": job_offer.education_level or ""
            })
            
            extracted_data = analysis["extracted_data"]
            cv_score = analysis["cv_score"]
            score_breakdown = analysis["score_breakdown"]
            
            logger.info(f"🆕 Nouvel analyseur utilisé - Score: {cv_score}")
        
        else:
            # ANCIEN ANALYSEUR
            extracted_data = cv_extractor.extract_all(cv_text)
            logger.info(f"🧠 Données extraites : {len(extracted_data['skills'])} compétences")
            
            skills_match = cv_matcher.match_skills(
                cv_skills=extracted_data['skills'],
                required_skills=job_offer.required_skills or [],
                threshold=0.7
            )
            
            experience_match = cv_matcher.match_experience(
                cv_years=extracted_data['experience_years'],
                required_min_years=job_offer.experience_min_years or 0,
                required_max_years=job_offer.experience_max_years
            )
            
            score_result = cv_scorer.calculate_final_score(
                skills_match=skills_match,
                experience_match=experience_match,
                education=extracted_data['education'],
                languages=extracted_data['languages']
            )
            
            cv_score = score_result['final_score']
            score_breakdown = score_result['breakdown']
            
            logger.info(f"📊 Ancien analyseur - Score: {cv_score}")
        
        # ========== 6. Créer le candidat en base ==========
        new_candidate = Candidate(
            first_name=extracted_data['contact']['name'].split()[0] if extracted_data.get('contact', {}).get('name') else "Prénom",
            last_name=extracted_data['contact']['name'].split()[-1] if extracted_data.get('contact', {}).get('name') else "Nom",
            email=extracted_data.get('contact', {}).get('email') or f"candidate_{timestamp}@temp.com",
            phone=extracted_data.get('contact', {}).get('phone'),
            cv_filename=safe_filename,
            cv_text=cv_text,
            extracted_data=extracted_data,
            cv_score=cv_score,
            score_breakdown=score_breakdown,
            job_offer_id=job_offer_id
        )
        
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)
        
        logger.info(f"✅ Candidat créé : ID #{new_candidate.id}")
        
        return CandidateUploadResponse(
            candidate_id=new_candidate.id,
            name=extracted_data.get('contact', {}).get('name'),
            email=extracted_data.get('contact', {}).get('email'),
            cv_filename=safe_filename,
            status="analyzed",
            message=f"CV analysé avec succès. Score: {cv_score}/100 ({'Improved' if use_improved else 'Standard'})"
        )
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du CV : {str(e)}")


# ============ Routes d'Analyse ============

@router.get("/{candidate_id}/analysis", response_model=CandidateAnalysisResponse)
async def get_candidate_analysis(
    candidate_id: int,
    use_improved: bool = Query(False, description="Utiliser le nouvel analyseur pour recalculer"),
    db: Session = Depends(get_db)
):
    """
    📊 Récupère l'analyse complète d'un candidat
    
    Args:
        candidate_id: ID du candidat
        use_improved: Si True, recalcule avec le nouvel analyseur
    
    Returns:
        CandidateAnalysisResponse: Analyse complète
    
    Example:
        GET /api/candidates/1/analysis?use_improved=true
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidat #{candidate_id} introuvable")
    
    # Si on veut recalculer avec le nouvel analyseur
    if use_improved:
        job = db.query(JobOffer).filter(JobOffer.id == candidate.job_offer_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
        
        from app.modules.cv_analyzer.improved_analyzer import ImprovedCVAnalyzer
        
        analyzer = ImprovedCVAnalyzer()
        analysis = analyzer.analyze(candidate.cv_text, {
            "required_skills": job.required_skills or [],
            "nice_to_have_skills": job.nice_to_have_skills or [],
            "experience_min_years": job.experience_min_years or 0,
            "education_level": job.education_level or ""
        })
        
        return CandidateAnalysisResponse(
            candidate_id=candidate.id,
            name=f"{candidate.first_name} {candidate.last_name}",
            email=candidate.email,
            phone=candidate.phone,
            extracted_data=analysis["extracted_data"],
            cv_score=analysis["cv_score"],
            score_breakdown=analysis["score_breakdown"],
            recommendation=analysis["recommendation"],
            category=analysis["category"]
        )
    
    # Sinon, retourner l'analyse stockée
    return CandidateAnalysisResponse(
        candidate_id=candidate.id,
        name=f"{candidate.first_name} {candidate.last_name}",
        email=candidate.email,
        phone=candidate.phone,
        extracted_data=candidate.extracted_data or {},
        cv_score=candidate.cv_score,
        score_breakdown=candidate.score_breakdown or {},
        recommendation=candidate.get_recommendation(),
        category="A" if candidate.cv_score >= 80 else "B" if candidate.cv_score >= 65 else "C" if candidate.cv_score >= 50 else "D"
    )


@router.get("/{candidate_id}/analysis-improved", response_model=dict)
async def get_improved_analysis(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    🆕 Analyse AMÉLIORÉE du CV avec matching réel
    
    - Extraction intelligente des compétences (filtrée)
    - Score basé sur la correspondance avec l'offre d'emploi
    - Recommandation réaliste
    
    Args:
        candidate_id: ID du candidat
    
    Returns:
        dict: Analyse complète avec le nouvel algorithme
    
    Example:
        GET /api/candidates/1/analysis-improved
    """
    from app.modules.cv_analyzer.improved_analyzer import ImprovedCVAnalyzer
    
    # Récupérer le candidat
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidat non trouvé")
    
    # Récupérer l'offre d'emploi
    job = db.query(JobOffer).filter(JobOffer.id == candidate.job_offer_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    # Analyser le CV avec le nouvel analyseur
    analyzer = ImprovedCVAnalyzer()
    analysis = analyzer.analyze(candidate.cv_text, {
        "required_skills": job.required_skills or [],
        "nice_to_have_skills": job.nice_to_have_skills or [],
        "experience_min_years": job.experience_min_years or 0,
        "education_level": job.education_level or ""
    })
    
    return {
        "candidate_id": candidate.id,
        "name": f"{candidate.first_name} {candidate.last_name}",
        "email": candidate.email,
        "phone": candidate.phone,
        "job_title": job.title,
        "job_required_skills": job.required_skills or [],
        **analysis
    }


@router.get("/{candidate_id}/comparison", response_model=dict)
async def compare_analyzers(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    📊 Compare l'ancien et le nouveau analyseur
    
    Montre la différence entre :
    - Ancien score (sans matching réel)
    - Nouveau score (avec matching réel avec l'offre)
    
    Args:
        candidate_id: ID du candidat
    
    Returns:
        dict: Comparaison détaillée des deux méthodes
    
    Example:
        GET /api/candidates/1/comparison
    """
    from app.modules.cv_analyzer.improved_analyzer import ImprovedCVAnalyzer
    
    # Récupérer le candidat
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidat non trouvé")
    
    # Récupérer l'offre
    job = db.query(JobOffer).filter(JobOffer.id == candidate.job_offer_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Offre d'emploi non trouvée")
    
    # Ancien score (depuis la DB)
    old_analysis = {
        "cv_score": candidate.cv_score,
        "score_breakdown": candidate.score_breakdown or {},
        "extracted_skills": candidate.extracted_data.get("skills", []) if candidate.extracted_data else [],
        "method": "Ancien (sans matching réel)"
    }
    
    # Nouveau score (avec matching)
    analyzer = ImprovedCVAnalyzer()
    new_analysis = analyzer.analyze(candidate.cv_text, {
        "required_skills": job.required_skills or [],
        "nice_to_have_skills": job.nice_to_have_skills or [],
        "experience_min_years": job.experience_min_years or 0,
        "education_level": job.education_level or ""
    })
    
    new_result = {
        "cv_score": new_analysis["cv_score"],
        "score_breakdown": new_analysis["score_breakdown"],
        "extracted_skills": new_analysis["extracted_data"]["skills"],
        "recommendation": new_analysis["recommendation"],
        "category": new_analysis["category"],
        "method": "Nouveau (avec matching réel)"
    }
    
    # Comparaison
    score_diff = new_result["cv_score"] - old_analysis["cv_score"]
    
    return {
        "candidate": {
            "id": candidate.id,
            "name": f"{candidate.first_name} {candidate.last_name}",
            "email": candidate.email
        },
        "job": {
            "id": job.id,
            "title": job.title,
            "required_skills": job.required_skills or []
        },
        "old_analysis": old_analysis,
        "new_analysis": new_result,
        "difference": {
            "score_diff": round(score_diff, 1),
            "score_change": "augmentation" if score_diff > 0 else "diminution" if score_diff < 0 else "identique",
            "score_change_percentage": round(abs(score_diff / old_analysis["cv_score"] * 100), 1) if old_analysis["cv_score"] > 0 else 0,
            "skills_comparison": {
                "old_count": len(old_analysis["extracted_skills"]),
                "new_count": len(new_result["extracted_skills"]),
                "old_sample": old_analysis["extracted_skills"][:10],
                "new_sample": new_result["extracted_skills"][:10]
            },
            "recommendation_change": {
                "old": candidate.get_recommendation(),
                "new": new_result["recommendation"]
            }
        },
        "conclusion": {
            "is_more_realistic": abs(score_diff) > 10,
            "message": f"Le nouveau score est {'plus bas' if score_diff < 0 else 'plus élevé'} de {abs(score_diff):.1f} points, ce qui {'reflète mieux' if abs(score_diff) > 10 else 'est similaire à'} la correspondance réelle avec l'offre."
        }
    }


# ============ Routes de Liste et Recherche ============

@router.get("/by-job/{job_id}", response_model=List[CandidateListResponse])
async def get_candidates_by_job(
    job_id: int,
    skip: int = 0,
    limit: int = 20,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    📋 Liste des candidats pour une offre d'emploi
    
    Args:
        job_id: ID de l'offre
        skip: Nombre à ignorer (pagination)
        limit: Nombre maximum à retourner
        min_score: Score minimum (optionnel)
    
    Returns:
        List[CandidateListResponse]: Liste des candidats
    
    Example:
        GET /api/candidates/by-job/1?min_score=65
    """
    query = db.query(Candidate).filter(Candidate.job_offer_id == job_id)
    
    if min_score:
        query = query.filter(Candidate.cv_score >= min_score)
    
    candidates = query.order_by(Candidate.cv_score.desc()).offset(skip).limit(limit).all()
    
    return [
        CandidateListResponse(
            id=c.id,
            name=f"{c.first_name} {c.last_name}",
            email=c.email,
            cv_score=c.cv_score,
            final_score=c.final_score,
            application_status=c.application_status.value if c.application_status else "pending",
            applied_at=c.applied_at,
            recommendation=c.get_recommendation()
        )
        for c in candidates
    ]


@router.get("/ranking/{job_id}", response_model=List[CandidateRankingResponse])
async def get_candidates_ranking(
    job_id: int,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    """
    🏆 Classement des meilleurs candidats pour une offre
    
    Args:
        job_id: ID de l'offre
        top_n: Nombre de candidats à retourner (défaut: 10)
    
    Returns:
        List[CandidateRankingResponse]: Top N candidats classés
    
    Example:
        GET /api/candidates/ranking/1?top_n=5
    """
    candidates = db.query(Candidate)\
        .filter(Candidate.job_offer_id == job_id)\
        .order_by(Candidate.cv_score.desc())\
        .limit(top_n)\
        .all()
    
    return [
        CandidateRankingResponse(
            candidate_id=c.id,
            ranking=idx + 1,
            name=f"{c.first_name} {c.last_name}",
            email=c.email,
            final_score=c.final_score,
            cv_score=c.cv_score,
            category="A" if c.cv_score >= 80 else "B" if c.cv_score >= 65 else "C" if c.cv_score >= 50 else "D",
            recommendation=c.get_recommendation()
        )
        for idx, c in enumerate(candidates)
    ]


@router.get("/{candidate_id}")
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    👤 Récupère un candidat spécifique
    
    Args:
        candidate_id: ID du candidat
    
    Returns:
        dict: Données complètes du candidat
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidat #{candidate_id} introuvable")
    
    return candidate.to_dict()


@router.get("/")
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    📋 Liste tous les candidats
    
    Args:
        skip: Nombre à ignorer
        limit: Nombre maximum
    
    Returns:
        List: Liste des candidats
    """
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    
    return [c.to_dict() for c in candidates]


@router.put("/{candidate_id}")
async def update_candidate(
    candidate_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """
    ✏️ Met à jour un candidat
    
    Args:
        candidate_id: ID du candidat
        data: Données à mettre à jour
    
    Returns:
        dict: Candidat mis à jour
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidat #{candidate_id} introuvable")
    
    # Mettre à jour les champs autorisés
    allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'application_status']
    for field in allowed_fields:
        if field in data:
            setattr(candidate, field, data[field])
    
    db.commit()
    db.refresh(candidate)
    
    return candidate.to_dict()


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    🗑️ Supprime un candidat
    
    Args:
        candidate_id: ID du candidat
    
    Returns:
        dict: Message de confirmation
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidat #{candidate_id} introuvable")
    
    # Supprimer le fichier CV
    cv_path = UPLOAD_DIR / candidate.cv_filename
    if cv_path.exists():
        cv_path.unlink()
        logger.info(f"🗑️ Fichier CV supprimé : {candidate.cv_filename}")
    
    db.delete(candidate)
    db.commit()
    
    return {
        "message": f"Candidat #{candidate_id} supprimé avec succès",
        "candidate_id": candidate_id
    }


# ============ Routes de Statistiques ============

@router.get("/stats/job/{job_id}")
async def get_job_statistics(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    📊 Statistiques complètes pour une offre d'emploi
    
    Retourne :
    - Nombre total de candidats
    - Scores (min, max, moyenne, médiane)
    - Distribution par catégories (A, B, C, D)
    - Top compétences des candidats
    - Recommandations
    
    Args:
        job_id: ID de l'offre
    
    Returns:
        dict: Statistiques détaillées
    
    Example:
        GET /api/candidates/stats/job/1
    """
    # Vérifier que l'offre existe
    job = db.query(JobOffer).filter(JobOffer.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Offre #{job_id} introuvable")
    
    stats = RecruitmentStats.get_job_statistics(db, job_id)
    
    return {
        "job_id": job_id,
        "job_title": job.title,
        "statistics": stats
    }


@router.get("/stats/comparison/{candidate_id}")
async def compare_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    📊 Compare un candidat avec les autres
    
    Retourne :
    - Position dans le classement
    - Percentile
    - Comparaison avec la moyenne
    
    Args:
        candidate_id: ID du candidat
    
    Returns:
        dict: Comparaison détaillée
    
    Example:
        GET /api/candidates/stats/comparison/1
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidat #{candidate_id} introuvable")
    
    comparison = RecruitmentStats.get_candidate_comparison(
        db, 
        candidate_id, 
        candidate.job_offer_id
    )
    
    return comparison


@router.get("/stats/global")
async def get_global_statistics(db: Session = Depends(get_db)):
    """
    📊 Statistiques globales du système
    
    Retourne :
    - Nombre total d'offres
    - Nombre total de candidats
    - Score moyen global
    - Répartition par qualité
    
    Returns:
        dict: Statistiques globales
    
    Example:
        GET /api/candidates/stats/global
    """
    stats = RecruitmentStats.get_global_statistics(db)
    
    return stats


# ============ Routes d'Export ============

@router.get("/export/excel/{job_id}")
async def export_candidates_to_excel(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    📥 Exporte les candidats en fichier Excel
    
    Génère un fichier Excel avec :
    - Liste complète des candidats
    - Scores détaillés
    - Statistiques
    - Graphiques de distribution
    - Formatage professionnel
    
    Args:
        job_id: ID de l'offre
    
    Returns:
        FileResponse: Fichier Excel à télécharger
    
    Example:
        GET /api/candidates/export/excel/1
    """
    # Vérifier que l'offre existe
    job = db.query(JobOffer).filter(JobOffer.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Offre #{job_id} introuvable")
    
    # Récupérer les candidats
    candidates = db.query(Candidate)\
        .filter(Candidate.job_offer_id == job_id)\
        .order_by(Candidate.cv_score.desc())\
        .all()
    
    if not candidates:
        raise HTTPException(status_code=404, detail="Aucun candidat pour cette offre")
    
    # Générer le fichier Excel
    try:
        filepath = excel_exporter.export_candidates(candidates, job.title)
        
        logger.info(f"✅ Export Excel généré : {filepath}")
        
        return FileResponse(
            path=filepath,
            filename=Path(filepath).name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logger.error(f"❌ Erreur export Excel : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export : {str(e)}")


@router.get("/{candidate_id}/download-cv")
async def download_cv(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    📥 Télécharge le CV original d'un candidat
    
    Args:
        candidate_id: ID du candidat
    
    Returns:
        FileResponse: Fichier PDF du CV
    
    Example:
        GET /api/candidates/1/download-cv
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidat #{candidate_id} introuvable")
    
    cv_path = UPLOAD_DIR / candidate.cv_filename
    
    if not cv_path.exists():
        raise HTTPException(status_code=404, detail="Fichier CV introuvable")
    
    return FileResponse(
        path=str(cv_path),
        filename=f"CV_{candidate.first_name}_{candidate.last_name}.pdf",
        media_type="application/pdf"
    )