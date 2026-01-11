"""
Modèle de données pour les offres d'emploi
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class JobOffer(Base):
    """
    Table des offres d'emploi
    """
    __tablename__ = "job_offers"
    
    # ============ Identifiants ============
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, index=True, nullable=False)
    
    # ============ Informations de base ============
    title = Column(String(200), nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    location = Column(String(200), nullable=False)
    contract_type = Column(String(50), default="CDI")
    
    # ============ Description ============
    description = Column(Text)
    responsibilities = Column(Text)
    
    # ============ Compétences (JSON) ============
    required_skills = Column(JSON, default=[])
    nice_to_have_skills = Column(JSON, default=[])
    
    # ============ Expérience ============
    experience_min_years = Column(Integer, nullable=False)
    experience_max_years = Column(Integer)
    experience_level = Column(String(50))  # Junior, Mid, Senior, Lead
    
    # ============ Formation ============
    education_level = Column(String(100))
    education_field = Column(String(200))
    
    # ============ Langues (JSON) ============
    languages = Column(JSON, default=[])
    
    # ============ Rémunération ============
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    benefits = Column(Text)
    
    # ============ Annonce LinkedIn ============
    linkedin_post = Column(Text)
    published_at = Column(DateTime)
    
    # ============ Métadonnées ============
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    
    # ============ Statut ============
    is_active = Column(Boolean, default=True)
    closed_at = Column(DateTime)
    
    # ============ Statistiques ============
    total_applications = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    
    # ============ Relations ============
    interview_sessions = relationship("InterviewSession", back_populates="job_offer", cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="job_offer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobOffer(id={self.id}, title='{self.title}', reference='{self.reference}')>"
    
    def to_dict(self):
        """
        Convertit l'objet en dictionnaire
        """
        return {
            "id": self.id,
            "reference": self.reference,
            "title": self.title,
            "industry": self.industry,
            "location": self.location,
            "contract_type": self.contract_type,
            "required_skills": self.required_skills,
            "experience_min_years": self.experience_min_years,
            "experience_max_years": self.experience_max_years,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "is_active": self.is_active,
            "linkedin_post": self.linkedin_post,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "total_applications": self.total_applications
        }