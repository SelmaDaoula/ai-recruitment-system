"""
Service d'orchestration des entretiens chatbot
Version avec chargement dynamique depuis JSON
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.models.interview import (
    InterviewSession, InterviewQuestion, InterviewResponse,
    InterviewStatus, InterviewPhase, QuestionCategory, QuestionDifficulty
)
from app.models.candidate import Candidate
from app.models.job_offer import JobOffer
from app.modules.chatbot.dataset_loader import DatasetLoader

logger = logging.getLogger(__name__)


class Interviewer:
    """Service principal pour gérer les entretiens"""
    
    def __init__(self, db: Session):
        self.db = db
        # ✅ CHARGER LE DATASET JSON
        self.dataset_loader = DatasetLoader()
        logger.info("✅ Interviewer initialisé avec dataset JSON")
    
    def start_interview(
        self,
        candidate_id: int,
        job_offer_id: int
    ) -> Dict:
        """Démarrer un entretien avec questions personnalisées"""
        logger.info(f"🚀 Démarrage - Candidat #{candidate_id}, Job #{job_offer_id}")
        
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        job_offer = self.db.query(JobOffer).filter(JobOffer.id == job_offer_id).first()
        
        if not candidate:
            raise ValueError(f"Candidat {candidate_id} non trouvé")
        if not job_offer:
            raise ValueError(f"Job {job_offer_id} non trouvé")
        
        # Vérifier session existante
        existing = self.db.query(InterviewSession).filter(
            InterviewSession.candidate_id == candidate_id,
            InterviewSession.job_offer_id == job_offer_id,
            InterviewSession.status.in_([InterviewStatus.STARTED, InterviewStatus.IN_PROGRESS])
        ).first()
        
        if existing:
            logger.info(f"📌 Session existante : #{existing.id}")
            next_q = self.get_next_question(str(existing.id))
            return {
                "session_id": str(existing.id),
                "status": "resumed",
                "message": "Session reprise",
                **next_q
            }
        
        # ✅ CHARGER LES QUESTIONS DEPUIS LE JSON
        logger.info(f"📥 Chargement questions pour : {job_offer.title}")
        custom_questions = self._load_questions_from_dataset(job_offer)
        logger.info(f"✅ {len(custom_questions)} questions chargées")
        
        # Créer session
        session = InterviewSession(
            candidate_id=candidate_id,
            job_offer_id=job_offer_id,
            status=InterviewStatus.IN_PROGRESS,
            current_phase=InterviewPhase.WELCOME,
            started_at=datetime.now(),
            questions_total=len(custom_questions),
            questions_answered=0
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # ✅ SAUVEGARDER LES QUESTIONS EN DB
        for q_data in custom_questions:
            question = InterviewQuestion(
                text=q_data['text'],
                category=QuestionCategory[q_data['category'].upper()],
                difficulty=QuestionDifficulty[q_data.get('difficulty', 'medium').upper()],
                expected_keywords=q_data.get('keywords', []),
                weight=q_data.get('weight', 1.0),
                job_offer_id=job_offer_id,
                job_title=job_offer.title,
                is_generic=False
            )
            self.db.add(question)
        
        self.db.commit()
        logger.info(f"✅ Session #{session.id} créée avec questions personnalisées")
        
        first_q = self.get_next_question(str(session.id))
        
        return {
            "session_id": str(session.id),
            "status": "started",
            "message": f"Entretien pour {job_offer.title}",
            **first_q
        }
    
    def get_next_question(self, session_id: str) -> Dict:
        """Obtenir la prochaine question depuis la DB"""
        session = self.db.query(InterviewSession).filter(
            InterviewSession.id == int(session_id)
        ).first()
        
        if not session:
            raise ValueError(f"Session {session_id} non trouvée")
        
        if session.status == InterviewStatus.COMPLETED:
            return {
                "status": "completed",
                "message": "Entretien terminé",
                "total_questions": session.questions_total,
                "answered": session.questions_answered
            }
        
        # ✅ CHARGER DEPUIS LA DB (PAS HARDCODÉ)
        questions = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.job_offer_id == session.job_offer_id,
            InterviewQuestion.is_generic == False
        ).order_by(InterviewQuestion.id).all()
        
        if not questions or session.questions_answered >= len(questions):
            return self._complete_interview(session)
        
        current = questions[session.questions_answered]
        
        self._update_phase(session, current.category)
        self.db.commit()
        
        return {
            "status": "in_progress",
            "question_id": str(current.id),
            "question_text": current.text,
            "category": current.category.value,
            "difficulty": current.difficulty.value,
            "current_question": session.questions_answered + 1,
            "total_questions": len(questions),
            "phase": session.current_phase.value
        }
    
    def submit_response(
        self,
        session_id: str,
        question_id: str,
        response_text: str,
        response_time: int = 0
    ) -> Dict:
        """Soumettre une réponse"""
        logger.info(f"💬 Réponse - Session #{session_id}, Q #{question_id}")
        
        session = self.db.query(InterviewSession).filter(
            InterviewSession.id == int(session_id)
        ).first()
        
        question = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.id == int(question_id)
        ).first()
        
        if not session or not question:
            raise ValueError("Session ou question non trouvée")
        
        analysis = self._analyze_response(response_text, question.expected_keywords or [])
        feedback = self._generate_feedback(analysis)
        
        response = InterviewResponse(
            session_id=session.id,
            question_id=question.id,
            response_text=response_text,
            response_time=response_time,
            keyword_score=analysis["keyword_score"],
            sentiment_score=analysis["sentiment_score"],
            relevance_score=analysis["relevance_score"],
            confidence_score=analysis["confidence_score"],
            overall_response_score=analysis["overall_score"],
            ai_feedback=feedback,
            responded_at=datetime.now()
        )
        
        self.db.add(response)
        session.questions_answered += 1
        self._update_scores(session)
        self.db.commit()
        
        next_q = self.get_next_question(session_id)
        
        return {
            "response_received": True,
            "analysis": {
                "keyword_score": round(analysis["keyword_score"], 2),
                "sentiment_score": round(analysis["sentiment_score"], 2),
                "relevance_score": round(analysis["relevance_score"], 2),
                "confidence_score": round(analysis["confidence_score"], 2),
                "overall_score": round(analysis["overall_score"], 2)
            },
            "feedback": feedback,
            "next_question": next_q
        }
    
    def get_session_status(self, session_id: str) -> Dict:
        """Status de la session"""
        session = self.db.query(InterviewSession).filter(
            InterviewSession.id == int(session_id)
        ).first()
        
        if not session:
            raise ValueError(f"Session {session_id} non trouvée")
        
        return {
            "session_id": str(session.id),
            "status": session.status.value,
            "phase": session.current_phase.value,
            "questions_answered": session.questions_answered,
            "questions_total": session.questions_total,
            "technical_score": round(session.technical_score, 2),
            "behavioral_score": round(session.behavioral_score, 2),
            "overall_score": round(session.overall_score, 2)
        }
    
    def get_session_results(self, session_id: str) -> Dict:
        """Résultats finaux"""
        session = self.db.query(InterviewSession).filter(
            InterviewSession.id == int(session_id)
        ).first()
        
        if not session:
            raise ValueError(f"Session {session_id} non trouvée")
        
        responses = self.db.query(InterviewResponse).filter(
            InterviewResponse.session_id == int(session_id)
        ).all()
        
        stats = {"technical": [], "behavioral": [], "welcome": []}
        
        for resp in responses:
            cat = resp.question.category.value.lower()
            if cat in stats:
                stats[cat].append({
                    "question": resp.question.text,
                    "score": round(resp.overall_response_score, 2),
                    "feedback": resp.ai_feedback
                })
        
        return {
            "session_id": str(session.id),
            "status": session.status.value,
            "scores": {
                "technical": round(session.technical_score, 2),
                "behavioral": round(session.behavioral_score, 2),
                "overall": round(session.overall_score, 2)
            },
            "responses_by_category": stats
        }
    
    def abandon_session(self, session_id: str) -> Dict:
        """Abandonner"""
        session = self.db.query(InterviewSession).filter(
            InterviewSession.id == int(session_id)
        ).first()
        
        if not session:
            raise ValueError(f"Session {session_id} non trouvée")
        
        session.status = InterviewStatus.ABANDONED
        session.completed_at = datetime.now()
        self.db.commit()
        
        return {
            "session_id": str(session.id),
            "status": "abandoned"
        }
    
    # ============ MÉTHODES PRIVÉES ============
    
    def _load_questions_from_dataset(self, job_offer: JobOffer) -> List[Dict]:
        """✅ CHARGER DEPUIS LE JSON (PAS HARDCODÉ)"""
        
        # Questions de bienvenue
        welcome = self.dataset_loader.get_questions_for_job(
            job_title=job_offer.title,
            num_questions=2,
            category='welcome'
        )
        
        # Questions techniques
        technical = self.dataset_loader.get_questions_for_job(
            job_title=job_offer.title,
            num_questions=6,
            category='technical'
        )
        
        # Questions comportementales
        behavioral = self.dataset_loader.get_questions_for_job(
            job_title=job_offer.title,
            num_questions=2,
            category='behavioral'
        )
        
        all_q = welcome + technical + behavioral
        
        logger.info(f"📊 Chargées : {len(welcome)} welcome, {len(technical)} tech, {len(behavioral)} behavioral")
        
        return all_q[:10]
    
    def _update_phase(self, session: InterviewSession, category: QuestionCategory):
        """Mettre à jour la phase"""
        if category == QuestionCategory.WELCOME:
            session.current_phase = InterviewPhase.WELCOME
        elif category == QuestionCategory.TECHNICAL:
            session.current_phase = InterviewPhase.TECHNICAL
        elif category == QuestionCategory.BEHAVIORAL:
            session.current_phase = InterviewPhase.BEHAVIORAL
    
    def _analyze_response(self, response: str, keywords: List[str]) -> Dict:
        """Analyser la réponse"""
        response_lower = response.lower()
        
        keyword_count = sum(1 for kw in keywords if kw.lower() in response_lower)
        keyword_score = (keyword_count / len(keywords) * 100) if keywords else 70
        
        word_count = len(response.split())
        length_score = 90 if word_count > 50 else (75 if word_count > 20 else 60)
        
        overall = (keyword_score * 0.4 + length_score * 0.6)
        
        return {
            "keyword_score": min(keyword_score, 100),
            "sentiment_score": 70,
            "relevance_score": length_score,
            "confidence_score": 75,
            "overall_score": overall
        }
    
    def _generate_feedback(self, analysis: Dict) -> str:
        """Feedback"""
        score = analysis["overall_score"]
        
        if score >= 80:
            return "Excellente réponse !"
        elif score >= 65:
            return "Bonne réponse."
        elif score >= 50:
            return "Réponse correcte."
        else:
            return "Développez davantage."
    
    def _update_scores(self, session: InterviewSession):
        """Mettre à jour les scores"""
        responses = self.db.query(InterviewResponse).filter(
            InterviewResponse.session_id == session.id
        ).all()
        
        if not responses:
            return
        
        tech = [r.overall_response_score * r.question.weight 
                for r in responses 
                if r.question.category == QuestionCategory.TECHNICAL]
        
        beh = [r.overall_response_score * r.question.weight 
               for r in responses 
               if r.question.category == QuestionCategory.BEHAVIORAL]
        
        if tech:
            session.technical_score = sum(tech) / len(tech)
        if beh:
            session.behavioral_score = sum(beh) / len(beh)
        
        session.overall_score = (session.technical_score * 0.6) + (session.behavioral_score * 0.4)
    
    def _complete_interview(self, session: InterviewSession) -> Dict:
        """Terminer"""
        session.status = InterviewStatus.COMPLETED
        session.completed_at = datetime.now()
        
        if session.started_at:
            session.total_duration = int((session.completed_at - session.started_at).total_seconds())
        
        feedback = self._final_feedback(session)
        session.ai_feedback = feedback
        
        candidate = session.candidate
        if candidate:
            candidate.interview_score = session.overall_score
            if candidate.cv_score:
                candidate.final_score = (candidate.cv_score * 0.4) + (session.overall_score * 0.6)
        
        self.db.commit()
        
        return {
            "status": "completed",
            "message": "Terminé",
            "final_score": round(session.overall_score, 2),
            "feedback": feedback
        }
    
    def _final_feedback(self, session: InterviewSession) -> str:
        """Feedback final"""
        score = session.overall_score
        
        if score >= 85:
            return "Excellent entretien ! 🌟"
        elif score >= 70:
            return "Très bon entretien ! 👍"
        else:
            return "Bon entretien."