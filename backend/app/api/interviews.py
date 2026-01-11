"""
Routes API pour le module d'entretien chatbot
Version corrigée et fonctionnelle
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from app.database import get_db
from app.modules.chatbot.interviewer import Interviewer
from app.models.interview import InterviewSession, InterviewStatus

logger = logging.getLogger(__name__)

router = APIRouter()


# ============ Schémas Pydantic ============

class StartInterviewRequest(BaseModel):
    """Requête pour démarrer un entretien"""
    candidate_id: int
    job_offer_id: int


class SubmitResponseRequest(BaseModel):
    """Requête pour soumettre une réponse"""
    question_id: str
    response_text: str
    response_time: Optional[int] = 0


# ============ Endpoints ============

@router.post("/start", status_code=status.HTTP_201_CREATED)
def start_interview(
    request: StartInterviewRequest,
    db: Session = Depends(get_db)
):
    """
    🚀 Démarrer un nouvel entretien
    
    - **candidate_id**: ID du candidat
    - **job_offer_id**: ID de l'offre d'emploi
    
    Returns:
        session_id et première question
    """
    try:
        interviewer = Interviewer(db)
        result = interviewer.start_interview(
            candidate_id=request.candidate_id,
            job_offer_id=request.job_offer_id
        )
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur start_interview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du démarrage: {str(e)}"
        )


@router.post("/{session_id}/respond")
def submit_response(
    session_id: str,
    request: SubmitResponseRequest,
    db: Session = Depends(get_db)
):
    """
    💬 Soumettre une réponse à une question
    
    - **session_id**: ID de la session d'entretien
    - **question_id**: ID de la question
    - **response_text**: Texte de la réponse
    - **response_time**: Temps de réponse en secondes (optionnel)
    
    Returns:
        Analyse de la réponse et prochaine question
    """
    try:
        interviewer = Interviewer(db)
        result = interviewer.submit_response(
            session_id=session_id,
            question_id=request.question_id,
            response_text=request.response_text,
            response_time=request.response_time
        )
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur submit_response: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la soumission: {str(e)}"
        )


@router.get("/{session_id}/status")
def get_session_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    📊 Obtenir l'état actuel d'une session
    
    - **session_id**: ID de la session
    
    Returns:
        État de la session (phase, questions, scores)
    """
    try:
        interviewer = Interviewer(db)
        result = interviewer.get_session_status(session_id)
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur get_status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/{session_id}/results")
def get_session_results(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtenir les résultats finaux
    
    - **session_id**: ID de la session
    
    Returns:
        Résultats complets: scores, feedback, détails
    """
    try:
        interviewer = Interviewer(db)
        result = interviewer.get_session_results(session_id)
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur get_results: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.put("/{session_id}/abandon")
def abandon_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    🚫 Abandonner une session
    
    - **session_id**: ID de la session
    
    Returns:
        Confirmation de l'abandon
    """
    try:
        interviewer = Interviewer(db)
        result = interviewer.abandon_session(session_id)
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur abandon: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/sessions")
def list_sessions(
    status_filter: Optional[str] = None,
    candidate_id: Optional[int] = None,
    job_offer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    📋 Lister toutes les sessions (avec filtres)
    
    - **status_filter**: Filtrer par statut
    - **candidate_id**: Filtrer par candidat
    - **job_offer_id**: Filtrer par offre
    - **skip**: Pagination
    - **limit**: Nombre max
    
    Returns:
        Liste des sessions
    """
    try:
        query = db.query(InterviewSession)
        
        # Filtres
        if status_filter:
            try:
                status_enum = InterviewStatus(status_filter.upper())
                query = query.filter(InterviewSession.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Statut invalide: {status_filter}"
                )
        
        if candidate_id:
            query = query.filter(InterviewSession.candidate_id == candidate_id)
        
        if job_offer_id:
            query = query.filter(InterviewSession.job_offer_id == job_offer_id)
        
        # Pagination
        total = query.count()
        sessions = query.offset(skip).limit(limit).all()
        
        # Formatter
        results = []
        for session in sessions:
            results.append({
                "session_id": str(session.id),
                "candidate_id": session.candidate_id,
                "candidate_name": f"{session.candidate.first_name} {session.candidate.last_name}" if session.candidate else "N/A",
                "job_offer_id": session.job_offer_id,
                "job_title": session.job_offer.title if session.job_offer else "N/A",
                "status": session.status.value if session.status else "unknown",
                "phase": session.current_phase.value if session.current_phase else "unknown",
                "overall_score": round(session.overall_score, 2),
                "questions_answered": session.questions_answered,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            })
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "sessions": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur list_sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/{session_id}/next-question")
def get_next_question(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    ➡️ Obtenir la prochaine question
    
    - **session_id**: ID de la session
    
    Returns:
        Prochaine question
    """
    try:
        interviewer = Interviewer(db)
        result = interviewer.get_next_question(session_id)
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur get_next_question: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/test")
async def test_chatbot():
    """Test simple du chatbot"""
    return {
        "message": "Chatbot d'entretien opérationnel !",
        "status": "ready",
        "version": "2.0",
        "features": [
            "12 questions (2 welcome + 6 tech + 4 behavioral)",
            "Analyse automatique des réponses",
            "Feedback en temps réel",
            "Score final (60% tech + 40% behavioral)"
        ]
    }