# backend/app/modules/chatbot/question_bank.py
"""
Service de gestion de la banque de questions d'entretien
"""
import json
import os
from typing import List, Dict, Optional
import random
from sqlalchemy.orm import Session

from app.models.interview import (
    InterviewQuestion, QuestionCategory, QuestionDifficulty
)


class QuestionBankService:
    """Service pour gérer la banque de questions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.questions_cache = {}
        self.question_file = os.path.join(
            os.path.dirname(__file__),
            "../../../data/question_templates/interview_questions.json"
        )
    
    def load_questions_from_json(self) -> Dict:
        """Charger les questions depuis le fichier JSON"""
        try:
            with open(self.question_file, 'r', encoding='utf-8') as f:
                self.questions_cache = json.load(f)
            return self.questions_cache
        except FileNotFoundError:
            print(f"⚠️  Fichier {self.question_file} non trouvé")
            return self._get_default_questions()
        except Exception as e:
            print(f"❌ Erreur lors du chargement des questions: {e}")
            return self._get_default_questions()
    
    def _get_default_questions(self) -> Dict:
        """Questions par défaut si le fichier n'existe pas"""
        return {
            "welcome": [
                {
                    "text": "Bonjour ! Pouvez-vous vous présenter brièvement ?",
                    "category": "welcome",
                    "keywords": ["nom", "expérience", "formation", "compétences"],
                    "difficulty": "easy",
                    "weight": 0.5
                },
                {
                    "text": "Qu'est-ce qui vous motive à postuler pour ce poste ?",
                    "category": "welcome",
                    "keywords": ["motivation", "intérêt", "projet"],
                    "difficulty": "easy",
                    "weight": 0.5
                }
            ],
            "behavioral": [
                {
                    "text": "Parlez-moi d'une situation où vous avez résolu un problème complexe.",
                    "category": "behavioral",
                    "keywords": ["problème", "solution", "complexe"],
                    "difficulty": "medium",
                    "weight": 1.0
                },
                {
                    "text": "Comment gérez-vous le stress au travail ?",
                    "category": "behavioral",
                    "keywords": ["stress", "gestion", "pression"],
                    "difficulty": "medium",
                    "weight": 1.0
                },
                {
                    "text": "Décrivez une expérience de travail en équipe réussie.",
                    "category": "behavioral",
                    "keywords": ["équipe", "collaboration", "succès"],
                    "difficulty": "easy",
                    "weight": 1.0
                },
                {
                    "text": "Parlez-moi d'un échec et ce que vous en avez appris.",
                    "category": "behavioral",
                    "keywords": ["échec", "apprentissage", "leçon"],
                    "difficulty": "hard",
                    "weight": 1.2
                }
            ],
            "technical": {
                "default": [
                    {
                        "text": "Décrivez votre expérience avec les outils et technologies de votre domaine.",
                        "category": "technical",
                        "keywords": ["expérience", "outils", "technologies"],
                        "difficulty": "medium",
                        "weight": 1.0
                    }
                ]
            }
        }
    
    def get_welcome_questions(self) -> List[Dict]:
        """Récupérer les questions de bienvenue"""
        if not self.questions_cache:
            self.load_questions_from_json()
        
        return self.questions_cache.get("welcome", [])
    
    def get_technical_questions(
        self,
        job_title: str,
        count: int = 6,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupérer les questions techniques pour un job spécifique
        
        Args:
            job_title: Titre du poste (ex: "Python Developer")
            count: Nombre de questions à retourner
            difficulty: Filtrer par difficulté (optional)
        """
        if not self.questions_cache:
            self.load_questions_from_json()
        
        technical_questions = self.questions_cache.get("technical", {})
        
        # Chercher questions pour ce job
        job_questions = technical_questions.get(job_title, [])
        
        # Si pas de questions spécifiques, utiliser questions génériques
        if not job_questions:
            job_questions = technical_questions.get("default", [])
        
        # Filtrer par difficulté si demandé
        if difficulty:
            job_questions = [
                q for q in job_questions
                if q.get("difficulty") == difficulty
            ]
        
        # Sélectionner aléatoirement
        if len(job_questions) > count:
            selected = random.sample(job_questions, count)
        else:
            selected = job_questions
        
        return selected
    
    def get_behavioral_questions(
        self,
        count: int = 4,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """Récupérer les questions comportementales"""
        if not self.questions_cache:
            self.load_questions_from_json()
        
        behavioral_questions = self.questions_cache.get("behavioral", [])
        
        # Filtrer par difficulté si demandé
        if difficulty:
            behavioral_questions = [
                q for q in behavioral_questions
                if q.get("difficulty") == difficulty
            ]
        
        # Sélectionner aléatoirement
        if len(behavioral_questions) > count:
            selected = random.sample(behavioral_questions, count)
        else:
            selected = behavioral_questions
        
        return selected
    
    def adapt_difficulty(
        self,
        current_score: float,
        questions: List[Dict]
    ) -> List[Dict]:
        """
        Adapter la difficulté des questions selon le score actuel
        
        Args:
            current_score: Score actuel du candidat (0-100)
            questions: Liste de questions disponibles
        """
        if current_score >= 80:
            # Bon score → Questions difficiles
            preferred = [q for q in questions if q.get("difficulty") == "hard"]
            fallback = [q for q in questions if q.get("difficulty") == "medium"]
        elif current_score >= 60:
            # Score moyen → Questions moyennes
            preferred = [q for q in questions if q.get("difficulty") == "medium"]
            fallback = questions
        else:
            # Score faible → Questions faciles
            preferred = [q for q in questions if q.get("difficulty") == "easy"]
            fallback = [q for q in questions if q.get("difficulty") == "medium"]
        
        # Retourner questions préférées ou fallback si pas assez
        return preferred if len(preferred) >= 2 else fallback
    
    def create_question_in_db(
        self,
        text: str,
        category: str,
        keywords: List[str],
        difficulty: str = "medium",
        weight: float = 1.0,
        job_title: Optional[str] = None,
        job_offer_id: Optional[str] = None
    ) -> InterviewQuestion:
        """Créer une question dans la base de données"""
        
        question = InterviewQuestion(
            text=text,
            category=QuestionCategory(category),
            difficulty=QuestionDifficulty(difficulty),
            expected_keywords=keywords,
            weight=weight,
            job_title=job_title,
            job_offer_id=job_offer_id,
            is_generic=(job_offer_id is None)
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    def populate_db_from_json(self) -> int:
        """Peupler la DB avec les questions du JSON"""
        questions_data = self.load_questions_from_json()
        count = 0
        
        # Welcome questions
        for q_data in questions_data.get("welcome", []):
            self.create_question_in_db(
                text=q_data["text"],
                category="welcome",
                keywords=q_data.get("keywords", []),
                difficulty=q_data.get("difficulty", "easy"),
                weight=q_data.get("weight", 0.5)
            )
            count += 1
        
        # Behavioral questions
        for q_data in questions_data.get("behavioral", []):
            self.create_question_in_db(
                text=q_data["text"],
                category="behavioral",
                keywords=q_data.get("keywords", []),
                difficulty=q_data.get("difficulty", "medium"),
                weight=q_data.get("weight", 1.0)
            )
            count += 1
        
        # Technical questions
        technical = questions_data.get("technical", {})
        for job_title, questions in technical.items():
            for q_data in questions:
                self.create_question_in_db(
                    text=q_data["text"],
                    category="technical",
                    keywords=q_data.get("keywords", []),
                    difficulty=q_data.get("difficulty", "medium"),
                    weight=q_data.get("weight", 1.0),
                    job_title=job_title
                )
                count += 1
        
        print(f"✅ {count} questions ajoutées à la base de données")
        return count
    
    def get_questions_from_db(
        self,
        category: Optional[str] = None,
        job_title: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[InterviewQuestion]:
        """Récupérer les questions depuis la DB avec filtres"""
        query = self.db.query(InterviewQuestion)
        
        if category:
            query = query.filter(InterviewQuestion.category == category)
        if job_title:
            query = query.filter(
                (InterviewQuestion.job_title == job_title) |
                (InterviewQuestion.is_generic == True)
            )
        if difficulty:
            query = query.filter(InterviewQuestion.difficulty == difficulty)
        
        return query.all()