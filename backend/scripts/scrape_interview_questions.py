# backend/scripts/scrape_interview_questions.py
"""
Script pour générer des questions d'entretien
"""
import json
import os
from typing import List, Dict


def scrape_generic_behavioral_questions() -> List[Dict]:
    """Questions comportementales génériques"""
    return [
        {
            "text": "Parlez-moi d'une situation où vous avez dû résoudre un problème complexe.",
            "category": "behavioral",
            "keywords": ["problème", "solution", "résoudre", "complexe", "analyse"],
            "difficulty": "medium",
            "weight": 1.0
        },
        {
            "text": "Décrivez une expérience où vous avez travaillé en équipe pour atteindre un objectif.",
            "category": "behavioral",
            "keywords": ["équipe", "collaboration", "objectif", "ensemble", "travail"],
            "difficulty": "easy",
            "weight": 1.0
        },
        {
            "text": "Comment gérez-vous les situations de stress ou de pression au travail ?",
            "category": "behavioral",
            "keywords": ["stress", "pression", "gestion", "calme", "organisation"],
            "difficulty": "medium",
            "weight": 1.0
        },
        {
            "text": "Racontez-moi un moment où vous avez dû apprendre quelque chose rapidement.",
            "category": "behavioral",
            "keywords": ["apprentissage", "rapide", "adaptation", "formation", "nouveau"],
            "difficulty": "medium",
            "weight": 1.0
        },
        {
            "text": "Donnez un exemple de conflit que vous avez résolu au travail.",
            "category": "behavioral",
            "keywords": ["conflit", "résolution", "communication", "médiation", "accord"],
            "difficulty": "hard",
            "weight": 1.2
        },
        {
            "text": "Parlez-moi d'un échec professionnel et ce que vous en avez appris.",
            "category": "behavioral",
            "keywords": ["échec", "apprentissage", "leçon", "amélioration", "résilience"],
            "difficulty": "hard",
            "weight": 1.2
        },
        {
            "text": "Comment priorisez-vous vos tâches quand vous avez plusieurs projets urgents ?",
            "category": "behavioral",
            "keywords": ["priorités", "organisation", "gestion", "urgent", "planification"],
            "difficulty": "medium",
            "weight": 1.0
        },
        {
            "text": "Décrivez votre style de leadership ou comment vous motivez une équipe.",
            "category": "behavioral",
            "keywords": ["leadership", "motivation", "équipe", "management", "inspiration"],
            "difficulty": "medium",
            "weight": 1.0
        }
    ]


def scrape_technical_python_questions() -> List[Dict]:
    """Questions techniques Python"""
    return [
        {
            "text": "Quelle est la différence entre une liste et un tuple en Python ?",
            "category": "technical",
            "job_title": "Python Developer",
            "keywords": ["liste", "tuple", "mutable", "immutable", "différence", "type"],
            "difficulty": "easy",
            "weight": 1.0
        },
        {
            "text": "Expliquez le concept de décorateur en Python et donnez un exemple d'utilisation.",
            "category": "technical",
            "job_title": "Python Developer",
            "keywords": ["décorateur", "fonction", "wrapper", "@", "métaprogrammation"],
            "difficulty": "medium",
            "weight": 1.2
        },
        {
            "text": "Comment optimiseriez-vous une requête SQL qui prend trop de temps ?",
            "category": "technical",
            "job_title": "Python Developer",
            "keywords": ["SQL", "optimisation", "index", "performance", "requête", "base de données"],
            "difficulty": "medium",
            "weight": 1.2
        },
        {
            "text": "Qu'est-ce que le GIL (Global Interpreter Lock) et quel est son impact ?",
            "category": "technical",
            "job_title": "Python Developer",
            "keywords": ["GIL", "thread", "concurrence", "performance", "parallélisme"],
            "difficulty": "hard",
            "weight": 1.5
        },
        {
            "text": "Expliquez les différences entre multiprocessing et threading en Python.",
            "category": "technical",
            "job_title": "Python Developer",
            "keywords": ["multiprocessing", "threading", "processus", "thread", "concurrence"],
            "difficulty": "medium",
            "weight": 1.2
        },
        {
            "text": "Comment testeriez-vous une application Python ? Quels outils utiliseriez-vous ?",
            "category": "technical",
            "job_title": "Python Developer",
            "keywords": ["test", "unittest", "pytest", "TDD", "qualité", "couverture"],
            "difficulty": "medium",
            "weight": 1.0
        },
        {
            "text": "Qu'est-ce qu'une API REST et comment l'implémenteriez-vous en Python ?",
            "category": "technical",
            "job_title": "Python Developer",
            "keywords": ["REST", "API", "FastAPI", "Flask", "HTTP", "endpoint"],
            "difficulty": "medium",
            "weight": 1.2
        },
        {
            "text": "Comment gérez-vous les exceptions en Python ? Donnez des exemples de bonnes pratiques.",
            "category": "technical",
            "job_title": "Python Developer",
            "keywords": ["exception", "try", "except", "finally", "erreur", "gestion"],
            "difficulty": "easy",
            "weight": 1.0
        }
    ]


def scrape_technical_data_science_questions() -> List[Dict]:
    """Questions Data Science"""
    return [
        {
            "text": "Expliquez la différence entre régression linéaire et régression logistique.",
            "category": "technical",
            "job_title": "Data Scientist",
            "keywords": ["régression", "linéaire", "logistique", "prédiction", "classification"],
            "difficulty": "medium",
            "weight": 1.2
        },
        {
            "text": "Qu'est-ce que l'overfitting et comment l'éviter ?",
            "category": "technical",
            "job_title": "Data Scientist",
            "keywords": ["overfitting", "surapprentissage", "validation", "régularisation", "généralisation"],
            "difficulty": "medium",
            "weight": 1.2
        },
        {
            "text": "Comment nettoyez-vous et préparez-vous des données avant modélisation ?",
            "category": "technical",
            "job_title": "Data Scientist",
            "keywords": ["nettoyage", "preprocessing", "données", "valeurs manquantes", "normalisation"],
            "difficulty": "easy",
            "weight": 1.0
        },
        {
            "text": "Expliquez le fonctionnement d'un réseau de neurones.",
            "category": "technical",
            "job_title": "Data Scientist",
            "keywords": ["réseau neurones", "deep learning", "couches", "activation", "backpropagation"],
            "difficulty": "hard",
            "weight": 1.5
        },
        {
            "text": "Quelle est la différence entre validation croisée et train-test split ?",
            "category": "technical",
            "job_title": "Data Scientist",
            "keywords": ["validation croisée", "train-test", "évaluation", "k-fold", "split"],
            "difficulty": "medium",
            "weight": 1.0
        },
        {
            "text": "Comment choisiriez-vous entre un modèle simple et un modèle complexe ?",
            "category": "technical",
            "job_title": "Data Scientist",
            "keywords": ["complexité", "simplicité", "compromis", "performance", "interprétabilité"],
            "difficulty": "medium",
            "weight": 1.2
        }
    ]


def scrape_technical_frontend_questions() -> List[Dict]:
    """Questions Frontend Development"""
    return [
        {
            "text": "Expliquez la différence entre let, const et var en JavaScript.",
            "category": "technical",
            "job_title": "Frontend Developer",
            "keywords": ["let", "const", "var", "scope", "hoisting", "variables"],
            "difficulty": "easy",
            "weight": 1.0
        },
        {
            "text": "Qu'est-ce que le Virtual DOM et comment React l'utilise-t-il ?",
            "category": "technical",
            "job_title": "Frontend Developer",
            "keywords": ["Virtual DOM", "React", "performance", "reconciliation", "rendering"],
            "difficulty": "medium",
            "weight": 1.2
        },
        {
            "text": "Comment optimisez-vous les performances d'une application web ?",
            "category": "technical",
            "job_title": "Frontend Developer",
            "keywords": ["performance", "optimisation", "lazy loading", "cache", "bundle", "minification"],
            "difficulty": "medium",
            "weight": 1.2
        },
        {
            "text": "Expliquez les concepts de closure et d'hoisting en JavaScript.",
            "category": "technical",
            "job_title": "Frontend Developer",
            "keywords": ["closure", "hoisting", "scope", "fonction", "variable"],
            "difficulty": "medium",
            "weight": 1.0
        },
        {
            "text": "Quelle est la différence entre CSS Grid et Flexbox ? Quand utilisez-vous l'un ou l'autre ?",
            "category": "technical",
            "job_title": "Frontend Developer",
            "keywords": ["Grid", "Flexbox", "layout", "responsive", "CSS"],
            "difficulty": "easy",
            "weight": 1.0
        },
        {
            "text": "Comment gérez-vous l'état global dans une application React ?",
            "category": "technical",
            "job_title": "Frontend Developer",
            "keywords": ["état", "state management", "Redux", "Context API", "React"],
            "difficulty": "medium",
            "weight": 1.2
        }
    ]


def generate_welcome_questions() -> List[Dict]:
    """Questions de bienvenue génériques"""
    return [
        {
            "text": "Bonjour ! Pouvez-vous vous présenter brièvement en quelques mots ?",
            "category": "welcome",
            "keywords": ["nom", "expérience", "formation", "compétences", "parcours"],
            "difficulty": "easy",
            "weight": 0.5
        },
        {
            "text": "Qu'est-ce qui vous motive à postuler pour ce poste ?",
            "category": "welcome",
            "keywords": ["motivation", "intérêt", "projet", "entreprise", "poste"],
            "difficulty": "easy",
            "weight": 0.5
        }
    ]


def generate_question_bank() -> Dict:
    """Générer la banque de questions complète"""
    
    question_bank = {
        "welcome": generate_welcome_questions(),
        "behavioral": scrape_generic_behavioral_questions(),
        "technical": {
            "Python Developer": scrape_technical_python_questions(),
            "Data Scientist": scrape_technical_data_science_questions(),
            "Frontend Developer": scrape_technical_frontend_questions(),
        }
    }
    
    return question_bank


def save_question_bank(filename: str = "interview_questions.json"):
    """Sauvegarder la banque de questions en JSON"""
    question_bank = generate_question_bank()
    
    # ✅ CRÉER LE DOSSIER S'IL N'EXISTE PAS
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(question_bank, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Banque de questions sauvegardée dans {filename}")
    
    # Statistiques
    total_welcome = len(question_bank["welcome"])
    total_behavioral = len(question_bank["behavioral"])
    total_technical = sum(len(questions) for questions in question_bank["technical"].values())
    
    print(f"📊 Statistiques:")
    print(f"   - Questions de bienvenue: {total_welcome}")
    print(f"   - Questions comportementales: {total_behavioral}")
    print(f"   - Questions techniques: {total_technical}")
    print(f"   - Total: {total_welcome + total_behavioral + total_technical}")


if __name__ == "__main__":
    print("🚀 Génération de la banque de questions d'entretien...")
    
    # Chemin absolu pour éviter les erreurs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "..", "data", "question_templates", "interview_questions.json")
    
    save_question_bank(output_path)
    print("✅ Terminé !")