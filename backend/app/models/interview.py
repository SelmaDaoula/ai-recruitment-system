# backend/app/models/interview.py
"""
Modèles pour le système d'entretien chatbot
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class InterviewStatus(str, enum.Enum):
    """Statut de la session d'entretien"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class InterviewPhase(str, enum.Enum):
    """Phase actuelle de l'entretien"""
    WELCOME = "welcome"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    COMPLETED = "completed"


class QuestionCategory(str, enum.Enum):
    """Catégorie de question"""
    WELCOME = "welcome"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"


class QuestionDifficulty(str, enum.Enum):
    """Difficulté de la question"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewSession(Base):
    """Session d'entretien pour un candidat"""
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_offer_id = Column(Integer, ForeignKey("job_offers.id", ondelete="CASCADE"), nullable=False)
    
    # État de la session
    status = Column(SQLEnum(InterviewStatus), default=InterviewStatus.STARTED, nullable=False)
    current_phase = Column(SQLEnum(InterviewPhase), default=InterviewPhase.WELCOME, nullable=False)
    current_question_index = Column(Integer, default=0, nullable=False)
    
    # Scores
    technical_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    # Feedback IA
    ai_feedback = Column(Text, nullable=True)
    
    # Métadonnées
    questions_total = Column(Integer, default=12)
    questions_answered = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    total_duration = Column(Integer, default=0)  # En secondes
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    candidate = relationship("Candidate", back_populates="interview_sessions")
    job_offer = relationship("JobOffer", back_populates="interview_sessions")
    responses = relationship("InterviewResponse", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InterviewSession {self.id} - Candidate {self.candidate_id} - Score {self.overall_score}>"

    def calculate_overall_score(self):
        """Calculer le score global (60% technique, 40% comportemental)"""
        if self.technical_score > 0 and self.behavioral_score > 0:
            self.overall_score = (self.technical_score * 0.6) + (self.behavioral_score * 0.4)
        elif self.technical_score > 0:
            self.overall_score = self.technical_score
        elif self.behavioral_score > 0:
            self.overall_score = self.behavioral_score
        else:
            self.overall_score = 0.0
        return self.overall_score

    def increment_question(self):
        """Passer à la question suivante"""
        self.questions_answered += 1
        self.current_question_index += 1
        
        # Changer de phase si nécessaire
        if self.current_phase == InterviewPhase.WELCOME and self.questions_answered >= 2:
            self.current_phase = InterviewPhase.TECHNICAL
        elif self.current_phase == InterviewPhase.TECHNICAL and self.questions_answered >= 8:
            self.current_phase = InterviewPhase.BEHAVIORAL
        elif self.questions_answered >= self.questions_total:
            self.current_phase = InterviewPhase.COMPLETED

    def complete_session(self):
        """Marquer la session comme complétée"""
        self.status = InterviewStatus.COMPLETED
        self.current_phase = InterviewPhase.COMPLETED
        self.completed_at = datetime.utcnow()
        
        # Calculer durée totale
        if self.started_at:
            self.total_duration = int((self.completed_at - self.started_at).total_seconds())
        
        # Calculer score final
        self.calculate_overall_score()

    def abandon_session(self):
        """Marquer la session comme abandonnée"""
        self.status = InterviewStatus.ABANDONED
        self.completed_at = datetime.utcnow()


class InterviewQuestion(Base):
    """Question d'entretien"""
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Contenu
    text = Column(Text, nullable=False)
    category = Column(SQLEnum(QuestionCategory), nullable=False)
    difficulty = Column(SQLEnum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM)
    
    # Mots-clés attendus pour l'analyse
    expected_keywords = Column(JSONB, nullable=True)  # Liste de mots-clés
    
    # Pondération
    weight = Column(Float, default=1.0)
    
    # Spécifique à un job ou générique
    job_offer_id = Column(Integer, ForeignKey("job_offers.id", ondelete="CASCADE"), nullable=True)
    is_generic = Column(Boolean, default=True)
    
    # Metadata
    job_title = Column(String, nullable=True)  # Ex: "Python Developer"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    job_offer = relationship("JobOffer", back_populates="interview_questions")
    responses = relationship("InterviewResponse", back_populates="question")

    def __repr__(self):
        return f"<InterviewQuestion {self.id} - {self.category} - {self.difficulty}>"


class InterviewResponse(Base):
    """Réponse à une question d'entretien avec analyse ML"""
    __tablename__ = "interview_responses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    
    # Réponse
    response_text = Column(Text, nullable=False)
    response_time = Column(Integer, default=0)  # Temps de réponse en secondes
    
    # Scores ML
    keyword_score = Column(Float, default=0.0)      # 0-100: Match avec mots-clés attendus
    sentiment_score = Column(Float, default=0.0)     # -1 à 1: Sentiment (négatif à positif)
    relevance_score = Column(Float, default=0.0)     # 0-100: Pertinence de la réponse
    confidence_score = Column(Float, default=0.0)    # 0-100: Confiance dans l'expression
    overall_response_score = Column(Float, default=0.0)  # Score global de la réponse
    
    # Feedback
    ai_feedback = Column(Text, nullable=True)
    
    # Metadata
    responded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    session = relationship("InterviewSession", back_populates="responses")
    question = relationship("InterviewQuestion", back_populates="responses")

    def __repr__(self):
        return f"<InterviewResponse {self.id} - Score {self.overall_response_score}>"

    def calculate_overall_response_score(self):
        """Calculer le score global de la réponse"""
        # Pondération :
        # - Keyword: 40%
        # - Relevance: 30%
        # - Confidence: 20%
        # - Sentiment: 10%
        
        # Normaliser sentiment de -1/1 vers 0-100
        sentiment_normalized = (self.sentiment_score + 1) * 50
        
        self.overall_response_score = (
            self.keyword_score * 0.4 +
            self.relevance_score * 0.3 +
            self.confidence_score * 0.2 +
            sentiment_normalized * 0.1
        )
        
        return self.overall_response_score