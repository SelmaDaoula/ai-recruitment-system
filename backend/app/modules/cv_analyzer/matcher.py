"""
Module 3 - CV Matcher
Matching sémantique entre CV et offre d'emploi
Utilise : BERT Sentence Transformers
"""

import logging
from typing import List, Dict, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class CVMatcher:
    """
    Matcher CV-Offre avec similarité sémantique BERT
    Compare les compétences du CV avec celles de l'offre
    """
    
    def __init__(self, use_bert: bool = True):
        """
        Initialise le matcher
        
        Args:
            use_bert: Si True, utilise BERT (nécessite sentence-transformers)
                     Si False, utilise simple string matching
        """
        self.use_bert = use_bert
        self.model = None
        
        if use_bert:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("✅ BERT Sentence Transformer chargé")
            except ImportError:
                logger.warning("⚠️  sentence-transformers non installé, mode simple activé")
                self.use_bert = False
            except Exception as e:
                logger.warning(f"⚠️  Erreur chargement BERT : {e}, mode simple activé")
                self.use_bert = False
        
        logger.info("🎯 CVMatcher initialisé")
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
        
        Returns:
            float: Score de similarité entre 0 et 1
        
        Example:
            similarity = matcher.compute_similarity("Python", "Langage Python")
            # Résultat : 0.92 (92% similaire)
        """
        if self.use_bert and self.model:
            return self._compute_bert_similarity(text1, text2)
        else:
            return self._compute_simple_similarity(text1, text2)
    
    def _compute_bert_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité avec BERT
        
        Args:
            text1, text2: Textes à comparer
        
        Returns:
            float: Similarité cosinus entre 0 et 1
        """
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Encoder les textes en vecteurs
        embeddings = self.model.encode([text1, text2])
        
        # Calculer la similarité cosinus
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        return float(similarity)
    
    def _compute_simple_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité simple (sans BERT)
        Basé sur les mots en commun
        
        Args:
            text1, text2: Textes à comparer
        
        Returns:
            float: Score entre 0 et 1
        """
        # Normaliser
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # Exact match
        if text1_lower == text2_lower:
            return 1.0
        
        # Inclusion
        if text1_lower in text2_lower or text2_lower in text1_lower:
            return 0.8
        
        # Mots en commun
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        
        common_words = words1.intersection(words2)
        
        if not words1 or not words2:
            return 0.0
        
        # Score Jaccard
        jaccard = len(common_words) / len(words1.union(words2))
        
        return jaccard
    
    def match_skills(
        self, 
        cv_skills: List[str], 
        required_skills: List[str],
        threshold: float = 0.7
    ) -> Dict:
        """
        Compare les compétences du CV avec celles requises
        
        Args:
            cv_skills: Compétences du candidat
            required_skills: Compétences requises pour le poste
            threshold: Seuil de similarité (0.7 = 70%)
        
        Returns:
            dict: {
                "matched_skills": [...],  # Compétences matchées
                "missing_skills": [...],  # Compétences manquantes
                "match_score": 0.85,      # Score global
                "details": [...]          # Détails par compétence
            }
        
        Example:
            result = matcher.match_skills(
                cv_skills=["Python", "Django", "Docker"],
                required_skills=["Python", "Django", "PostgreSQL"]
            )
            # match_score: 0.67 (2/3 compétences)
        """
        matched_skills = []
        missing_skills = []
        match_details = []
        
        logger.info(f"🔍 Matching {len(cv_skills)} compétences CV avec {len(required_skills)} requises")
        
        # Pour chaque compétence requise
        for req_skill in required_skills:
            best_match = None
            best_score = 0.0
            
            # Chercher la meilleure correspondance dans le CV
            for cv_skill in cv_skills:
                similarity = self.compute_similarity(cv_skill, req_skill)
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = cv_skill
            
            # Si similarité suffisante
            if best_score >= threshold:
                matched_skills.append(req_skill)
                match_details.append({
                    "required": req_skill,
                    "found": best_match,
                    "similarity": round(best_score, 2),
                    "status": "✅ Match"
                })
            else:
                missing_skills.append(req_skill)
                match_details.append({
                    "required": req_skill,
                    "found": best_match if best_match else "Non trouvé",
                    "similarity": round(best_score, 2) if best_match else 0.0,
                    "status": "❌ Manquant"
                })
        
        # Calculer le score global
        if required_skills:
            match_score = len(matched_skills) / len(required_skills)
        else:
            match_score = 1.0
        
        result = {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_score": round(match_score, 2),
            "match_percentage": round(match_score * 100, 1),
            "details": match_details
        }
        
        logger.info(f"✅ Matching terminé : {result['match_percentage']}% ({len(matched_skills)}/{len(required_skills)})")
        
        return result
    
    def match_experience(
        self,
        cv_years: int,
        required_min_years: int,
        required_max_years: int = None
    ) -> Dict:
        """
        Compare l'expérience du candidat avec celle requise
        
        Args:
            cv_years: Années d'expérience du candidat
            required_min_years: Minimum requis
            required_max_years: Maximum requis (optionnel)
        
        Returns:
            dict: {
                "match": True/False,
                "score": 0.85,
                "message": "..."
            }
        """
        if cv_years is None:
            return {
                "match": False,
                "score": 0.0,
                "message": "Expérience non spécifiée dans le CV"
            }
        
        # Cas 1 : Expérience dans la fourchette
        if required_max_years:
            if required_min_years <= cv_years <= required_max_years:
                return {
                    "match": True,
                    "score": 1.0,
                    "message": f"✅ Expérience parfaite : {cv_years} ans (requis: {required_min_years}-{required_max_years} ans)"
                }
        
        # Cas 2 : Au-dessus du minimum
        if cv_years >= required_min_years:
            # Score décroissant si trop d'expérience
            if required_max_years and cv_years > required_max_years:
                over = cv_years - required_max_years
                score = max(0.7, 1.0 - (over * 0.05))  # -5% par année au-dessus
                return {
                    "match": True,
                    "score": round(score, 2),
                    "message": f"⚠️  Sur-qualifié : {cv_years} ans (requis: {required_min_years}-{required_max_years} ans)"
                }
            else:
                return {
                    "match": True,
                    "score": 1.0,
                    "message": f"✅ Expérience suffisante : {cv_years} ans (minimum: {required_min_years} ans)"
                }
        
        # Cas 3 : En dessous du minimum
        else:
            missing = required_min_years - cv_years
            score = max(0.0, 1.0 - (missing * 0.15))  # -15% par année manquante
            return {
                "match": False,
                "score": round(score, 2),
                "message": f"❌ Expérience insuffisante : {cv_years} ans (minimum: {required_min_years} ans)"
            }


# ============ Test du matcher ============

if __name__ == "__main__":
    """
    Test du matcher avec des exemples
    """
    print("\n" + "="*60)
    print("TEST DU CV MATCHER")
    print("="*60)
    
    # Créer le matcher
    matcher = CVMatcher(use_bert=True)
    
    print("\n📊 TEST 1 : SIMILARITÉ SÉMANTIQUE")
    print("-" * 60)
    
    tests = [
        ("Python", "Python"),
        ("Python", "Langage Python"),
        ("Python", "Programmation Python"),
        ("Django", "Framework Django"),
        ("PostgreSQL", "Base de données PostgreSQL"),
        ("Docker", "Kubernetes"),
        ("JavaScript", "Java")
    ]
    
    for text1, text2 in tests:
        similarity = matcher.compute_similarity(text1, text2)
        print(f"  '{text1}' ↔ '{text2}'")
        print(f"  Similarité: {similarity:.2%}\n")
    
    print("\n🎯 TEST 2 : MATCHING COMPÉTENCES")
    print("-" * 60)
    
    cv_skills = ["Python", "Django", "PostgreSQL", "Docker", "Git"]
    required_skills = ["Python", "Django", "Redis", "Kubernetes"]
    
    result = matcher.match_skills(cv_skills, required_skills)
    
    print(f"\n📋 CV Skills: {', '.join(cv_skills)}")
    print(f"📋 Required Skills: {', '.join(required_skills)}")
    print(f"\n✅ Matched: {len(result['matched_skills'])}/{len(required_skills)} ({result['match_percentage']}%)")
    print(f"   {result['matched_skills']}")
    print(f"\n❌ Missing: {len(result['missing_skills'])}")
    print(f"   {result['missing_skills']}")
    
    print("\n📊 Détails:")
    for detail in result['details']:
        print(f"  {detail['status']} {detail['required']}")
        if detail['found'] != "Non trouvé":
            print(f"      → Trouvé: {detail['found']} (similarité: {detail['similarity']:.0%})")
    
    print("\n📊 TEST 3 : MATCHING EXPÉRIENCE")
    print("-" * 60)
    
    tests_exp = [
        (5, 3, 5),   # Parfait
        (4, 3, 5),   # Dans la fourchette
        (7, 3, 5),   # Trop d'expérience
        (2, 3, 5),   # Pas assez
    ]
    
    for cv_years, min_years, max_years in tests_exp:
        result = matcher.match_experience(cv_years, min_years, max_years)
        print(f"\n  CV: {cv_years} ans | Requis: {min_years}-{max_years} ans")
        print(f"  Score: {result['score']:.0%}")
        print(f"  {result['message']}")
    
    print("\n" + "="*60 + "\n")