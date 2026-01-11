"""
Modèle de données pour les candidats
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class ApplicationStatus(enum.Enum):
    """
    Statut d'une candidature
    """
    pending = "pending"
    cv_analyzed = "cv_analyzed"
    interview_scheduled = "interview_scheduled"
    interview_completed = "interview_completed"
    shortlisted = "shortlisted"
    rejected = "rejected"
    hired = "hired"


class Candidate(Base):
    """
    Table des candidats
    """
    __tablename__ = "candidates"
    
    # ============ Identifiants ============
    id = Column(Integer, primary_key=True, index=True)
    
    # ============ Informations personnelles ============
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    linkedin_url = Column(String(500))
    
    # ============ CV ============
    cv_filename = Column(String(500))
    cv_mongodb_id = Column(String(100))  # ID du document dans MongoDB
    cv_text = Column(Text)  # Texte extrait du CV
    
    # ============ Données extraites du CV (JSON) ============
    extracted_data = Column(JSON, default={})
    # Structure:
    # {
    #     "skills": ["Python", "Django"],
    #     "experience_years": 5,
    #     "education": [{"degree": "Master", "field": "Informatique"}],
    #     "languages": [{"language": "Anglais", "level": "B2"}],
    #     "work_history": [...]
    # }
    
    # ============ Scores ============
    cv_score = Column(Float, default=0.0)  # Score du CV sur 100
    interview_score = Column(Float, default=0.0)  # Score de l'entretien sur 100
    final_score = Column(Float, default=0.0)  # Score final sur 100
    
    # Score breakdown (JSON)
    score_breakdown = Column(JSON, default={})
    # {
    #     "skills_match": 85,
    #     "experience_match": 90,
    #     "education_match": 75,
    #     "languages_match": 80
    # }
    
    # ============ Offre d'emploi ============
    job_offer_id = Column(Integer, ForeignKey("job_offers.id"))
    
    # ============ Statut de la candidature ============
    application_status = Column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.pending
    )
    
    # ============ Classement ============
    final_ranking = Column(Integer)  # Position finale parmi tous les candidats
    
    # ============ Entretien ============
    interview_date = Column(DateTime)
    interview_notes = Column(Text)
    interview_mongodb_id = Column(String(100))  # Historique conversation dans MongoDB
    
    # ============ Métadonnées ============
    applied_at = Column(DateTime, server_default=func.now())
    cv_analyzed_at = Column(DateTime)
    interview_completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # ============ Notes du recruteur ============
    recruiter_notes = Column(Text)
    
    # ============ Relations ============
    interview_sessions = relationship("InterviewSession", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"
    
    def to_dict(self):
        """
        Convertit l'objet en dictionnaire
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "cv_score": self.cv_score,
            "interview_score": self.interview_score,
            "final_score": self.final_score,
            "application_status": self.application_status.value if self.application_status else None,
            "final_ranking": self.final_ranking,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "job_offer_id": self.job_offer_id
        }
    
    def get_recommendation(self):
        """
        Retourne une recommandation basée sur le score final
        """
        if self.final_score >= 80:
            return "Excellent candidat - À interviewer en priorité ⭐⭐⭐"
        elif self.final_score >= 65:
            return "Bon candidat - À considérer sérieusement ✓"
        elif self.final_score >= 50:
            return "Candidat moyen - Liste de réserve"
        else:
            return "Candidat insuffisant pour ce poste"