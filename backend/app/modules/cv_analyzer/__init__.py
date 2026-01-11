"""
Module 3: Analyse de CV avec NLP
Extraction, Matching, Scoring

Ce module fournit les outils pour analyser les CVs :
- CVParser : Extraction de texte depuis PDF
- CVMatcher : Matching sémantique avec BERT
- ImprovedCVAnalyzer : Analyseur amélioré avec matching réel
"""

from app.modules.cv_analyzer.parser import CVParser
from app.modules.cv_analyzer.matcher import CVMatcher

__all__ = [
    "CVParser",
    "CVMatcher",
]

# Note : Le nouvel analyseur (ImprovedCVAnalyzer) est importé
# dynamiquement dans candidates.py pour éviter les dépendances circulaires