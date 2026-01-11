"""
Chargeur de questions d'entretien depuis JSON
"""
import json
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Charge des questions d'entretien depuis un fichier JSON"""
    
    def __init__(self, dataset_path: str = None):
        """
        Args:
            dataset_path: Chemin vers le fichier JSON
        """
        if dataset_path is None:
            # Chemin par défaut
            dataset_path = os.path.join(
                os.path.dirname(__file__),
                "../../../data/question_templates/interview_questions.json"
            )
        
        self.dataset_path = dataset_path
        self.questions_bank = {}
        self.load_dataset()
    
    def load_dataset(self) -> Dict:
        """Charger le dataset depuis JSON"""
        try:
            if not os.path.exists(self.dataset_path):
                logger.warning(f"⚠️  Dataset non trouvé : {self.dataset_path}")
                logger.info("💡 Exécutez : python scripts/scrape_interview_questions.py")
                self.questions_bank = self._get_fallback_questions()
                return self.questions_bank
            
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                self.questions_bank = json.load(f)
            
            logger.info(f"✅ Dataset chargé depuis {self.dataset_path}")
            logger.info(f"📊 Catégories disponibles : {list(self.questions_bank.keys())}")
            
            return self.questions_bank
        
        except Exception as e:
            logger.error(f"❌ Erreur chargement dataset : {e}")
            self.questions_bank = self._get_fallback_questions()
            return self.questions_bank
    
    def get_questions_for_job(
        self, 
        job_title: str, 
        num_questions: int = 10,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupérer des questions pour un job spécifique
        
        Args:
            job_title: Titre du poste (ex: "Python Developer")
            num_questions: Nombre de questions à retourner
            category: Filtrer par catégorie (technical, behavioral, welcome)
        
        Returns:
            List[Dict]: Questions filtrées
        """
        questions = []
        
        # Normaliser le job title
        job_key = self._normalize_job_title(job_title)
        
        # 1. Questions de bienvenue
        if category is None or category == 'welcome':
            welcome = self.questions_bank.get('welcome', [])
            questions.extend(welcome)
        
        # 2. Questions techniques spécifiques au job
        if category is None or category == 'technical':
            technical = self.questions_bank.get('technical', {})
            
            # Chercher correspondance exacte
            if job_key in technical:
                questions.extend(technical[job_key])
                logger.info(f"✅ Questions trouvées pour : {job_key}")
            else:
                # Chercher correspondance partielle
                matched_questions = self._find_similar_job(job_title, technical)
                questions.extend(matched_questions)
        
        # 3. Questions comportementales
        if category is None or category == 'behavioral':
            behavioral = self.questions_bank.get('behavioral', [])
            questions.extend(behavioral)
        
        # Filtrer par catégorie si demandé
        if category:
            questions = [q for q in questions if q.get('category') == category]
        
        # Retourner le nombre demandé
        return questions[:num_questions]
    
    def _normalize_job_title(self, job_title: str) -> str:
        """Normaliser le titre pour le matching"""
        # Mappings courants
        mappings = {
            'développeur python': 'Python Developer',
            'dev python': 'Python Developer',
            'python dev': 'Python Developer',
            'développeur javascript': 'Frontend Developer',
            'dev javascript': 'Frontend Developer',
            'développeur frontend': 'Frontend Developer',
            'data scientist': 'Data Scientist',
            'data analyst': 'Data Scientist',
            'analyste de données': 'Data Scientist'
        }
        
        job_lower = job_title.lower()
        
        # Chercher mapping exact
        if job_lower in mappings:
            return mappings[job_lower]
        
        # Chercher par mots-clés
        if 'python' in job_lower or 'django' in job_lower:
            return 'Python Developer'
        elif 'javascript' in job_lower or 'react' in job_lower or 'frontend' in job_lower:
            return 'Frontend Developer'
        elif 'data' in job_lower:
            return 'Data Scientist'
        
        # Retourner le titre original capitalisé
        return ' '.join(word.capitalize() for word in job_title.split())
    
    def _find_similar_job(self, job_title: str, technical_dict: Dict) -> List[Dict]:
        """Trouver des questions pour un job similaire"""
        job_lower = job_title.lower()
        
        # Chercher par mots-clés
        for key, questions in technical_dict.items():
            if any(keyword in job_lower for keyword in key.lower().split()):
                logger.info(f"🔍 Match partiel : '{job_title}' → '{key}'")
                return questions
        
        logger.warning(f"⚠️  Aucune question spécifique pour '{job_title}', utilisation questions génériques")
        return []
    
    def _get_fallback_questions(self) -> Dict:
        """Questions par défaut si le dataset n'existe pas"""
        logger.warning("⚠️  Utilisation des questions de fallback")
        
        return {
            "welcome": [
                {
                    "text": "Bonjour ! Pouvez-vous vous présenter brièvement ?",
                    "category": "welcome",
                    "keywords": ["parcours", "expérience", "formation"],
                    "difficulty": "easy",
                    "weight": 0.5
                },
                {
                    "text": "Qu'est-ce qui vous motive à postuler pour ce poste ?",
                    "category": "welcome",
                    "keywords": ["motivation", "intérêt"],
                    "difficulty": "easy",
                    "weight": 0.5
                }
            ],
            "technical": {
                "Generic": [
                    {
                        "text": "Décrivez votre expérience professionnelle principale.",
                        "category": "technical",
                        "keywords": ["expérience", "projet", "compétences"],
                        "difficulty": "medium",
                        "weight": 1.0
                    }
                ]
            },
            "behavioral": [
                {
                    "text": "Comment gérez-vous le travail en équipe ?",
                    "category": "behavioral",
                    "keywords": ["équipe", "collaboration", "communication"],
                    "difficulty": "medium",
                    "weight": 1.0
                }
            ]
        }