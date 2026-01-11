"""
Module 3 - CV Scorer
Calcul du score final du candidat
Combine : compétences, expérience, formation, langues
"""

import logging
from typing import Dict, List
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class CVScorer:
    """
    Calculateur de score de CV
    Score final = pondération des différents critères
    """
    
    def __init__(self):
        """
        Initialise le scorer avec les poids depuis la config
        """
        # Poids depuis config.py
        self.weights = {
            "skills": settings.skills_weight,          # 0.4 (40%)
            "experience": settings.experience_weight,  # 0.3 (30%)
            "education": settings.education_weight,    # 0.2 (20%)
            "languages": settings.languages_weight     # 0.1 (10%)
        }
        
        logger.info(f"📊 CVScorer initialisé avec poids: {self.weights}")
    
    def calculate_skills_score(self, match_result: Dict) -> float:
        """
        Calcule le score des compétences
        
        Args:
            match_result: Résultat du matching (depuis CVMatcher)
        
        Returns:
            float: Score entre 0 et 100
        """
        # Le match_score est déjà entre 0 et 1
        score = match_result.get("match_score", 0.0) * 100
        
        logger.debug(f"  🎯 Score compétences: {score:.1f}/100")
        
        return score
    
    def calculate_experience_score(self, match_result: Dict) -> float:
        """
        Calcule le score de l'expérience
        
        Args:
            match_result: Résultat du matching expérience
        
        Returns:
            float: Score entre 0 et 100
        """
        score = match_result.get("score", 0.0) * 100
        
        logger.debug(f"  📊 Score expérience: {score:.1f}/100")
        
        return score
    
    def calculate_education_score(self, education: List[Dict]) -> float:
        """
        Calcule le score de la formation
        
        Args:
            education: Liste des formations
        
        Returns:
            float: Score entre 0 et 100
        
        Logique:
        - Doctorat/PhD: 100
        - Master/Ingénieur: 90
        - Licence/Bachelor: 75
        - BTS/DUT: 60
        - BAC: 40
        - Aucun: 20
        """
        if not education:
            return 20.0
        
        # Scores par diplôme
        degree_scores = {
            "doctorat": 100,
            "phd": 100,
            "master": 90,
            "ingénieur": 90,
            "mba": 90,
            "licence": 75,
            "bachelor": 75,
            "bts": 60,
            "dut": 60,
            "bac": 40
        }
        
        # Prendre le plus haut diplôme
        max_score = 0
        
        for edu in education:
            degree = edu.get("degree", "").lower()
            for key, score in degree_scores.items():
                if key in degree:
                    max_score = max(max_score, score)
        
        # Si aucun diplôme reconnu, score minimal
        if max_score == 0:
            max_score = 30
        
        logger.debug(f"  🎓 Score formation: {max_score}/100")
        
        return float(max_score)
    
    def calculate_languages_score(self, languages: List[Dict]) -> float:
        """
        Calcule le score des langues
        
        Args:
            languages: Liste des langues
        
        Returns:
            float: Score entre 0 et 100
        
        Logique:
        - Bilingue/Natif: 100
        - Courant/C1/C2: 80
        - Intermédiaire/B1/B2: 60
        - Débutant/A1/A2: 40
        - Aucune langue étrangère: 30
        """
        if not languages:
            return 30.0
        
        # Scores par niveau
        level_scores = {
            "natif": 100,
            "bilingue": 100,
            "c2": 90,
            "c1": 80,
            "courant": 80,
            "b2": 70,
            "b1": 60,
            "intermédiaire": 60,
            "a2": 50,
            "a1": 40,
            "débutant": 40
        }
        
        # Prendre la meilleure langue
        max_score = 0
        
        for lang in languages:
            # Ignorer le français (langue native supposée)
            if lang.get("language", "").lower() == "français":
                continue
            
            level = lang.get("level", "").lower()
            for key, score in level_scores.items():
                if key in level:
                    max_score = max(max_score, score)
        
        # Si aucune langue étrangère
        if max_score == 0:
            max_score = 30
        
        logger.debug(f"  🌍 Score langues: {max_score}/100")
        
        return float(max_score)
    
    def calculate_final_score(
        self,
        skills_match: Dict,
        experience_match: Dict,
        education: List[Dict],
        languages: List[Dict]
    ) -> Dict:
        """
        Calcule le score final du candidat
        
        Args:
            skills_match: Résultat du matching des compétences
            experience_match: Résultat du matching de l'expérience
            education: Liste des formations
            languages: Liste des langues
        
        Returns:
            dict: {
                "final_score": 82.5,
                "breakdown": {
                    "skills": 85.0,
                    "experience": 90.0,
                    "education": 75.0,
                    "languages": 80.0
                },
                "recommendation": "Excellent candidat",
                "category": "A"
            }
        """
        logger.info("🧮 Calcul du score final...")
        
        # Calculer chaque score
        skills_score = self.calculate_skills_score(skills_match)
        experience_score = self.calculate_experience_score(experience_match)
        education_score = self.calculate_education_score(education)
        languages_score = self.calculate_languages_score(languages)
        
        # Score pondéré final
        final_score = (
            skills_score * self.weights["skills"] +
            experience_score * self.weights["experience"] +
            education_score * self.weights["education"] +
            languages_score * self.weights["languages"]
        )
        
        # Déterminer la catégorie
        if final_score >= 80:
            category = "A"
            recommendation = "Excellent candidat - À interviewer en priorité ⭐⭐⭐"
        elif final_score >= 65:
            category = "B"
            recommendation = "Bon candidat - À considérer sérieusement ✓"
        elif final_score >= 50:
            category = "C"
            recommendation = "Candidat moyen - Liste de réserve"
        else:
            category = "D"
            recommendation = "Candidat insuffisant pour ce poste"
        
        result = {
            "final_score": round(final_score, 1),
            "breakdown": {
                "skills": round(skills_score, 1),
                "experience": round(experience_score, 1),
                "education": round(education_score, 1),
                "languages": round(languages_score, 1)
            },
            "weights": self.weights,
            "recommendation": recommendation,
            "category": category
        }
        
        logger.info(f"✅ Score final: {result['final_score']}/100 (Catégorie {category})")
        
        return result


# ============ Test du scorer ============

if __name__ == "__main__":
    """
    Test du scorer avec différents profils
    """
    print("\n" + "="*60)
    print("TEST DU CV SCORER")
    print("="*60)
    
    scorer = CVScorer()
    
    print(f"\n⚖️  Poids configurés:")
    for criterion, weight in scorer.weights.items():
        print(f"  {criterion}: {weight:.0%}")
    
    # ========== PROFIL 1 : Excellent candidat ==========
    print("\n" + "="*60)
    print("PROFIL 1 : EXCELLENT CANDIDAT")
    print("="*60)
    
    skills_match = {
        "match_score": 0.90,  # 90% des compétences
        "match_percentage": 90
    }
    
    experience_match = {
        "score": 1.0,  # Expérience parfaite
        "message": "5 ans, parfait"
    }
    
    education = [
        {"degree": "Master", "field": "Informatique", "year": "2019"}
    ]
    
    languages = [
        {"language": "Anglais", "level": "Courant"},
        {"language": "Espagnol", "level": "Intermédiaire"}
    ]
    
    result1 = scorer.calculate_final_score(
        skills_match, experience_match, education, languages
    )
    
    print(f"\n📊 SCORES:")
    print(f"  🎯 Compétences: {result1['breakdown']['skills']}/100 (poids: {scorer.weights['skills']:.0%})")
    print(f"  📊 Expérience: {result1['breakdown']['experience']}/100 (poids: {scorer.weights['experience']:.0%})")
    print(f"  🎓 Formation: {result1['breakdown']['education']}/100 (poids: {scorer.weights['education']:.0%})")
    print(f"  🌍 Langues: {result1['breakdown']['languages']}/100 (poids: {scorer.weights['languages']:.0%})")
    print(f"\n🎯 SCORE FINAL: {result1['final_score']}/100")
    print(f"📋 Catégorie: {result1['category']}")
    print(f"💡 Recommandation: {result1['recommendation']}")
    
    # ========== PROFIL 2 : Candidat moyen ==========
    print("\n" + "="*60)
    print("PROFIL 2 : CANDIDAT MOYEN")
    print("="*60)
    
    skills_match2 = {
        "match_score": 0.60,
        "match_percentage": 60
    }
    
    experience_match2 = {
        "score": 0.70,
        "message": "2 ans, un peu juste"
    }
    
    education2 = [
        {"degree": "Licence", "field": "Informatique", "year": "2021"}
    ]
    
    languages2 = [
        {"language": "Anglais", "level": "Intermédiaire"}
    ]
    
    result2 = scorer.calculate_final_score(
        skills_match2, experience_match2, education2, languages2
    )
    
    print(f"\n📊 SCORES:")
    print(f"  🎯 Compétences: {result2['breakdown']['skills']}/100")
    print(f"  📊 Expérience: {result2['breakdown']['experience']}/100")
    print(f"  🎓 Formation: {result2['breakdown']['education']}/100")
    print(f"  🌍 Langues: {result2['breakdown']['languages']}/100")
    print(f"\n🎯 SCORE FINAL: {result2['final_score']}/100")
    print(f"📋 Catégorie: {result2['category']}")
    print(f"💡 Recommandation: {result2['recommendation']}")
    
    # ========== PROFIL 3 : Candidat insuffisant ==========
    print("\n" + "="*60)
    print("PROFIL 3 : CANDIDAT INSUFFISANT")
    print("="*60)
    
    skills_match3 = {
        "match_score": 0.30,
        "match_percentage": 30
    }
    
    experience_match3 = {
        "score": 0.40,
        "message": "Débutant"
    }
    
    education3 = [
        {"degree": "BTS", "field": "Informatique", "year": "2023"}
    ]
    
    languages3 = []
    
    result3 = scorer.calculate_final_score(
        skills_match3, experience_match3, education3, languages3
    )
    
    print(f"\n📊 SCORES:")
    print(f"  🎯 Compétences: {result3['breakdown']['skills']}/100")
    print(f"  📊 Expérience: {result3['breakdown']['experience']}/100")
    print(f"  🎓 Formation: {result3['breakdown']['education']}/100")
    print(f"  🌍 Langues: {result3['breakdown']['languages']}/100")
    print(f"\n🎯 SCORE FINAL: {result3['final_score']}/100")
    print(f"📋 Catégorie: {result3['category']}")
    print(f"💡 Recommandation: {result3['recommendation']}")
    
    print("\n" + "="*60 + "\n")