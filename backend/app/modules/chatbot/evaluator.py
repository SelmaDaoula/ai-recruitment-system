# backend/app/modules/chatbot/evaluator.py
"""
Service d'analyse ML des réponses d'entretien
Utilise spaCy, BERT et Sentence Transformers
"""
import spacy
from typing import Dict, List, Tuple
import re

# Lazy loading des modèles pour optimiser le démarrage
_nlp = None
_sentiment_analyzer = None
_sentence_model = None


def get_nlp():
    """Charger spaCy (lazy loading)"""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("fr_core_news_md")
        except OSError:
            print("⚠️  Modèle spaCy non trouvé. Installez-le avec: python -m spacy download fr_core_news_md")
            _nlp = spacy.blank("fr")
    return _nlp


def get_sentiment_analyzer():
    """Charger BERT pour sentiment analysis (lazy loading)"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        try:
            from transformers import pipeline
            _sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                top_k=None
            )
        except Exception as e:
            print(f"⚠️  Impossible de charger BERT: {e}")
            _sentiment_analyzer = None
    return _sentiment_analyzer


def get_sentence_model():
    """Charger Sentence Transformers (lazy loading)"""
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            print(f"⚠️  Impossible de charger Sentence Transformers: {e}")
            _sentence_model = None
    return _sentence_model


class Evaluator:
    """Service d'évaluation des réponses d'entretien"""
    
    def __init__(self):
        self.nlp = get_nlp()
        self.sentiment_analyzer = get_sentiment_analyzer()
        self.sentence_model = get_sentence_model()
    
    def analyze_response(
        self,
        question_text: str,
        response_text: str,
        expected_keywords: List[str]
    ) -> Dict[str, float]:
        """
        Analyser une réponse complètement
        
        Returns:
            Dict avec tous les scores (keyword, sentiment, relevance, confidence)
        """
        analysis = {
            "keyword_score": self.calculate_keyword_score(response_text, expected_keywords),
            "sentiment_score": self.calculate_sentiment(response_text),
            "relevance_score": self.calculate_relevance(question_text, response_text),
            "confidence_score": self.calculate_confidence(response_text)
        }
        
        # Score global
        analysis["overall_score"] = self._calculate_overall_score(analysis)
        
        return analysis
    
    def calculate_keyword_score(
        self,
        response_text: str,
        expected_keywords: List[str]
    ) -> float:
        """
        Calculer le score de matching avec les mots-clés attendus
        Utilise spaCy pour la similarité sémantique
        
        Returns:
            Score 0-100
        """
        if not expected_keywords or not response_text:
            return 0.0
        
        try:
            # Tokenize response
            response_doc = self.nlp(response_text.lower())
            
            matches = 0
            for keyword in expected_keywords:
                keyword_doc = self.nlp(keyword.lower())
                
                # Calcul de similarité
                similarity = response_doc.similarity(keyword_doc)
                
                # Seuil de matching
                if similarity > 0.7:
                    matches += 1
                # Match partiel
                elif similarity > 0.5:
                    matches += 0.5
                # Chercher aussi dans les tokens individuels
                elif any(keyword.lower() in token.text.lower() for token in response_doc):
                    matches += 0.75
            
            # Score proportionnel au nombre de keywords matchés
            score = (matches / len(expected_keywords)) * 100
            return min(100, score)
            
        except Exception as e:
            print(f"⚠️  Erreur calcul keyword score: {e}")
            # Fallback: simple recherche de mots
            matches = sum(1 for kw in expected_keywords if kw.lower() in response_text.lower())
            return (matches / len(expected_keywords)) * 100
    
    def calculate_sentiment(self, response_text: str) -> float:
        """
        Analyser le sentiment de la réponse
        Utilise BERT
        
        Returns:
            Score -1 à 1 (négatif à positif)
        """
        if not response_text or len(response_text) < 10:
            return 0.0
        
        try:
            if self.sentiment_analyzer is None:
                return 0.0
            
            # Tronquer si trop long (BERT a une limite)
            text = response_text[:512]
            
            result = self.sentiment_analyzer(text)[0]
            
            # Le modèle retourne des scores pour 1-5 étoiles
            # On normalise vers -1 (négatif) à 1 (positif)
            label_to_score = {
                '1 star': -1.0,
                '2 stars': -0.5,
                '3 stars': 0.0,
                '4 stars': 0.5,
                '5 stars': 1.0
            }
            
            # Prendre le label avec le plus haut score
            top_label = max(result, key=lambda x: x['score'])
            sentiment_score = label_to_score.get(top_label['label'], 0.0)
            
            # Pondérer par la confiance du modèle
            return sentiment_score * top_label['score']
            
        except Exception as e:
            print(f"⚠️  Erreur calcul sentiment: {e}")
            # Fallback: analyse basique de mots positifs/négatifs
            return self._simple_sentiment(response_text)
    
    def _simple_sentiment(self, text: str) -> float:
        """Analyse de sentiment simple (fallback)"""
        positive_words = [
            'bon', 'excellent', 'super', 'bien', 'réussi', 'succès',
            'efficace', 'positif', 'intéressant', 'motivé', 'passionné'
        ]
        negative_words = [
            'mauvais', 'problème', 'difficile', 'échec', 'raté',
            'négatif', 'compliqué', 'stressant', 'peur', 'inquiet'
        ]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count + neg_count == 0:
            return 0.0
        
        return (pos_count - neg_count) / (pos_count + neg_count)
    
    def calculate_relevance(
        self,
        question_text: str,
        response_text: str
    ) -> float:
        """
        Calculer la pertinence de la réponse par rapport à la question
        Utilise Sentence Transformers
        
        Returns:
            Score 0-100
        """
        if not question_text or not response_text:
            return 0.0
        
        try:
            if self.sentence_model is None:
                return 50.0  # Score neutre par défaut
            
            # Encoder question et réponse
            question_emb = self.sentence_model.encode([question_text])
            response_emb = self.sentence_model.encode([response_text])
            
            # Similarité cosine
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(question_emb, response_emb)[0][0]
            
            # Convertir en score 0-100
            return float(similarity * 100)
            
        except Exception as e:
            print(f"⚠️  Erreur calcul relevance: {e}")
            # Fallback: longueur de réponse
            return min(100, len(response_text.split()) * 5)
    
    def calculate_confidence(self, response_text: str) -> float:
        """
        Évaluer la confiance dans l'expression
        Facteurs:
        - Longueur de réponse
        - Présence de mots de doute
        - Structure grammaticale
        
        Returns:
            Score 0-100
        """
        if not response_text:
            return 0.0
        
        confidence = 50.0  # Score de base
        
        # 1. Longueur de réponse
        word_count = len(response_text.split())
        if word_count > 30:
            confidence += 20
        elif word_count > 15:
            confidence += 10
        elif word_count < 5:
            confidence -= 30
        
        # 2. Mots de doute (réduisent la confiance)
        doubt_words = [
            'peut-être', 'je pense', 'je crois', 'probablement',
            'éventuellement', 'je suppose', 'pas sûr', 'incertain'
        ]
        doubt_count = sum(1 for word in doubt_words if word in response_text.lower())
        confidence -= doubt_count * 10
        
        # 3. Mots de confiance (augmentent la confiance)
        confidence_words = [
            'certain', 'sûr', 'convaincu', 'expérience', 'maîtrise',
            'expert', 'compétent', 'capable', 'efficace'
        ]
        confidence_count = sum(1 for word in confidence_words if word in response_text.lower())
        confidence += confidence_count * 5
        
        # 4. Structure (phrases complètes)
        sentences = re.split(r'[.!?]', response_text)
        complete_sentences = [s for s in sentences if len(s.strip()) > 10]
        if len(complete_sentences) >= 2:
            confidence += 10
        
        # Limiter entre 0 et 100
        return max(0, min(100, confidence))
    
    def _calculate_overall_score(self, analysis: Dict[str, float]) -> float:
        """
        Calculer le score global d'une réponse
        Pondération:
        - Keyword: 40%
        - Relevance: 30%
        - Confidence: 20%
        - Sentiment: 10%
        """
        # Normaliser sentiment de -1/1 vers 0-100
        sentiment_normalized = (analysis["sentiment_score"] + 1) * 50
        
        overall = (
            analysis["keyword_score"] * 0.4 +
            analysis["relevance_score"] * 0.3 +
            analysis["confidence_score"] * 0.2 +
            sentiment_normalized * 0.1
        )
        
        return round(overall, 2)
    
    def generate_feedback(
        self,
        analysis: Dict[str, float],
        response_text: str
    ) -> str:
        """
        Générer un feedback personnalisé basé sur l'analyse
        """
        feedback_parts = []
        
        # Feedback sur le score global
        overall = analysis["overall_score"]
        if overall >= 80:
            feedback_parts.append("Excellente réponse ! 🌟")
        elif overall >= 65:
            feedback_parts.append("Bonne réponse.")
        elif overall >= 50:
            feedback_parts.append("Réponse correcte.")
        else:
            feedback_parts.append("Réponse à améliorer.")
        
        # Feedback sur les keywords
        if analysis["keyword_score"] < 50:
            feedback_parts.append(
                "Essayez d'inclure plus de concepts clés liés à la question."
            )
        
        # Feedback sur la relevance
        if analysis["relevance_score"] < 60:
            feedback_parts.append(
                "Assurez-vous que votre réponse reste centrée sur la question posée."
            )
        
        # Feedback sur la confiance
        if analysis["confidence_score"] < 50:
            feedback_parts.append(
                "Exprimez-vous avec plus d'assurance et détaillez vos expériences."
            )
        
        # Feedback sur le sentiment
        if analysis["sentiment_score"] < -0.3:
            feedback_parts.append(
                "Adoptez un ton plus positif dans votre réponse."
            )
        
        # Longueur
        word_count = len(response_text.split())
        if word_count < 10:
            feedback_parts.append(
                "Développez davantage votre réponse pour être plus complet."
            )
        
        return " ".join(feedback_parts)