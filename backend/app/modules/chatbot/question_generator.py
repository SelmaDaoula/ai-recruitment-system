"""
MODULE 2 : Générateur de Questions Intelligent
Génération automatique de questions d'entretien avec NLP
Utilise : T5, Question Generation, Named Entity Recognition
"""

from transformers import (
    T5ForConditionalGeneration, 
    T5Tokenizer,
    pipeline
)
import spacy
from typing import List, Dict
import torch

class QuestionGenerator:
    """
    Génère automatiquement des questions d'entretien pertinentes
    Approche 100% NLP professionnelle
    """
    
    def __init__(self, use_gpu: bool = False):
        """
        Initialise le générateur avec les modèles NLP
        
        Args:
            use_gpu: Utiliser GPU si disponible (plus rapide)
        """
        print("📥 Chargement des modèles de génération de questions...")
        
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        print(f"🖥️  Device: {self.device}")
        
        # Modèle spaCy pour l'analyse
        self.nlp = spacy.load("fr_core_news_md")
        
        # Option 1 : Modèle T5 pour Question Generation (multilingue)
        # C'est un modèle gratuit et open source
        self.qg_model_name = "doc2query/msmarco-french-mt5-base-v1"
        
        try:
            self.qg_tokenizer = T5Tokenizer.from_pretrained(self.qg_model_name)
            self.qg_model = T5ForConditionalGeneration.from_pretrained(
                self.qg_model_name
            ).to(self.device)
            print("✅ Modèle T5 Question Generation chargé")
        except Exception as e:
            print(f"⚠️  Erreur chargement T5, utilisation du modèle de base : {e}")
            # Fallback vers un modèle plus simple
            self.qg_model = None
        
        # Pipeline de génération de texte (backup)
        try:
            self.text_generator = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                device=0 if self.device == "cuda" else -1
            )
            print("✅ Pipeline de génération chargé")
        except:
            self.text_generator = None
            print("⚠️  Pipeline non disponible, utilisation des templates")
        
        # Templates de questions (backup professionnel)
        self.question_templates = self._load_question_templates()
        
        print("✅ Générateur de questions prêt")
    
    def generate_questions(
        self, 
        job_description: str,
        required_skills: List[str],
        difficulty: str = "medium",
        num_questions: int = 5
    ) -> List[Dict]:
        """
        FONCTION PRINCIPALE : Génère des questions personnalisées
        
        Args:
            job_description: Description complète du poste
            required_skills: ["Python", "Django", "PostgreSQL"]
            difficulty: "easy", "medium", "hard"
            num_questions: Nombre de questions à générer
        
        Returns:
            List[Dict]: [
                {
                    'question': "Comment optimiseriez-vous...",
                    'category': "technical",
                    'skill': "Python",
                    'difficulty': "medium",
                    'expected_keywords': ["performance", "cache", "algorithme"]
                },
                ...
            ]
        """
        questions = []
        
        # Analyser la description du poste avec spaCy
        doc = self.nlp(job_description)
        
        # Extraire les entités et concepts clés
        key_concepts = self._extract_key_concepts(doc)
        
        # Générer des questions pour chaque compétence
        for skill in required_skills:
            # Générer des questions spécifiques à la compétence
            skill_questions = self._generate_skill_questions(
                skill=skill,
                context=job_description,
                key_concepts=key_concepts,
                difficulty=difficulty,
                num=num_questions // len(required_skills)
            )
            questions.extend(skill_questions)
        
        # Ajouter des questions comportementales
        behavioral_questions = self._generate_behavioral_questions(
            job_description=job_description,
            num=2
        )
        questions.extend(behavioral_questions)
        
        return questions[:num_questions]
    
    def _extract_key_concepts(self, doc) -> List[str]:
        """
        Extrait les concepts clés d'une description de poste
        Utilise NER (Named Entity Recognition) et patterns
        
        Args:
            doc: Document spaCy
        
        Returns:
            List[str]: Concepts clés extraits
        """
        concepts = []
        
        # Extraire les entités nommées
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "TECH"]:
                concepts.append(ent.text)
        
        # Extraire les noms et verbes importants
        for token in doc:
            if token.pos_ in ["NOUN", "VERB"] and not token.is_stop:
                if len(token.text) > 3:  # Mots significatifs
                    concepts.append(token.lemma_)
        
        # Dédupliquer et garder les plus fréquents
        concepts = list(set(concepts))
        
        return concepts[:10]  # Top 10 concepts
    
    def _generate_skill_questions(
        self,
        skill: str,
        context: str,
        key_concepts: List[str],
        difficulty: str,
        num: int
    ) -> List[Dict]:
        """
        Génère des questions pour une compétence spécifique
        
        Args:
            skill: "Python", "Django", etc.
            context: Description du poste
            key_concepts: Concepts clés extraits
            difficulty: "easy", "medium", "hard"
            num: Nombre de questions
        
        Returns:
            List[Dict]: Questions générées
        """
        questions = []
        
        # Stratégie 1 : Utiliser T5 si disponible
        if self.qg_model is not None:
            generated = self._generate_with_t5(skill, context, difficulty, num)
            questions.extend(generated)
        
        # Stratégie 2 : Utiliser le pipeline si T5 échoue
        if len(questions) < num and self.text_generator is not None:
            generated = self._generate_with_pipeline(skill, context, difficulty, num)
            questions.extend(generated)
        
        # Stratégie 3 : Templates intelligents (toujours disponible)
        if len(questions) < num:
            generated = self._generate_with_templates(
                skill, 
                key_concepts, 
                difficulty, 
                num - len(questions)
            )
            questions.extend(generated)
        
        return questions[:num]
    
    def _generate_with_t5(
        self, 
        skill: str, 
        context: str, 
        difficulty: str, 
        num: int
    ) -> List[Dict]:
        """
        Génération avec modèle T5 (Question Generation)
        
        Args:
            skill: Compétence ciblée
            context: Contexte du poste
            difficulty: Niveau de difficulté
            num: Nombre de questions
        
        Returns:
            List[Dict]: Questions générées
        """
        questions = []
        
        try:
            # Construire le prompt pour T5
            # T5 est entraîné sur du Question Generation
            prompt = f"Génère une question d'entretien technique sur {skill}. Contexte : {context[:200]}"
            
            # Encoder le prompt
            inputs = self.qg_tokenizer.encode(
                prompt, 
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)
            
            # Générer plusieurs questions
            outputs = self.qg_model.generate(
                inputs,
                max_length=100,
                num_return_sequences=num,
                num_beams=5,
                temperature=0.7,
                do_sample=True
            )
            
            # Décoder les questions
            for output in outputs:
                question_text = self.qg_tokenizer.decode(
                    output, 
                    skip_special_tokens=True
                )
                
                questions.append({
                    'question': question_text,
                    'category': 'technical',
                    'skill': skill,
                    'difficulty': difficulty,
                    'expected_keywords': self._extract_keywords(question_text),
                    'generation_method': 't5'
                })
        
        except Exception as e:
            print(f"⚠️  Erreur génération T5 : {e}")
        
        return questions
    
    def _generate_with_pipeline(
        self, 
        skill: str, 
        context: str, 
        difficulty: str, 
        num: int
    ) -> List[Dict]:
        """
        Génération avec pipeline text2text
        
        Args:
            skill: Compétence
            context: Contexte
            difficulty: Difficulté
            num: Nombre
        
        Returns:
            List[Dict]: Questions générées
        """
        questions = []
        
        try:
            # Prompts selon le niveau de difficulté
            difficulty_prompts = {
                "easy": f"Pose une question simple sur les bases de {skill}",
                "medium": f"Pose une question de niveau intermédiaire sur {skill} dans le contexte : {context[:100]}",
                "hard": f"Pose une question avancée et technique sur {skill} nécessitant une expertise approfondie"
            }
            
            prompt = difficulty_prompts.get(difficulty, difficulty_prompts["medium"])
            
            # Générer avec le pipeline
            results = self.text_generator(
                prompt,
                max_length=100,
                num_return_sequences=num,
                temperature=0.8
            )
            
            for result in results:
                question_text = result['generated_text']
                
                questions.append({
                    'question': question_text,
                    'category': 'technical',
                    'skill': skill,
                    'difficulty': difficulty,
                    'expected_keywords': self._extract_keywords(question_text),
                    'generation_method': 'pipeline'
                })
        
        except Exception as e:
            print(f"⚠️  Erreur génération pipeline : {e}")
        
        return questions
    
    def _generate_with_templates(
        self, 
        skill: str, 
        key_concepts: List[str], 
        difficulty: str, 
        num: int
    ) -> List[Dict]:
        """
        Génération avec templates intelligents (backup)
        Templates structurés mais enrichis par NLP
        
        Args:
            skill: Compétence
            key_concepts: Concepts clés du poste
            difficulty: Difficulté
            num: Nombre
        
        Returns:
            List[Dict]: Questions générées
        """
        questions = []
        
        # Templates par niveau de difficulté
        templates = self.question_templates.get(difficulty, {}).get(skill.lower(), [])
        
        # Si pas de templates spécifiques, utiliser les génériques
        if not templates:
            templates = self.question_templates.get(difficulty, {}).get('generic', [])
        
        # Générer des questions en remplissant les templates
        for i, template in enumerate(templates[:num]):
            # Enrichir le template avec les concepts clés
            if key_concepts and "{concept}" in template:
                concept = key_concepts[i % len(key_concepts)]
                question_text = template.format(skill=skill, concept=concept)
            else:
                question_text = template.format(skill=skill)
            
            questions.append({
                'question': question_text,
                'category': 'technical',
                'skill': skill,
                'difficulty': difficulty,
                'expected_keywords': self._extract_keywords(question_text),
                'generation_method': 'template'
            })
        
        return questions
    
    def _generate_behavioral_questions(
        self, 
        job_description: str, 
        num: int = 2
    ) -> List[Dict]:
        """
        Génère des questions comportementales
        Basées sur le STAR method (Situation, Task, Action, Result)
        
        Args:
            job_description: Description du poste
            num: Nombre de questions
        
        Returns:
            List[Dict]: Questions comportementales
        """
        questions = []
        
        # Analyser la description pour extraire les soft skills
        doc = self.nlp(job_description)
        
        # Soft skills courantes
        soft_skills = {
            'travail en équipe': "Parlez-moi d'une situation où vous avez dû collaborer avec une équipe difficile. Comment avez-vous géré cela ?",
            'leadership': "Décrivez une situation où vous avez dû prendre le leadership sur un projet. Quels ont été les résultats ?",
            'gestion du stress': "Racontez-moi comment vous avez géré une deadline serrée ou une situation de pression.",
            'résolution de problèmes': "Donnez-moi un exemple d'un problème complexe que vous avez résolu. Quelle a été votre approche ?",
            'adaptabilité': "Parlez-moi d'une fois où vous avez dû vous adapter rapidement à un changement majeur.",
            'communication': "Décrivez une situation où vous avez dû expliquer un concept technique complexe à un non-technicien."
        }
        
        # Détecter les soft skills mentionnées dans la description
        detected_skills = []
        for skill_key in soft_skills.keys():
            if skill_key in job_description.lower():
                detected_skills.append(skill_key)
        
        # Si aucune détectée, utiliser les plus courantes
        if not detected_skills:
            detected_skills = ['travail en équipe', 'résolution de problèmes']
        
        # Générer les questions
        for skill in detected_skills[:num]:
            questions.append({
                'question': soft_skills[skill],
                'category': 'behavioral',
                'skill': skill,
                'difficulty': 'medium',
                'expected_keywords': ['situation', 'action', 'résultat', 'équipe', 'projet'],
                'generation_method': 'behavioral'
            })
        
        return questions
    
    def _extract_keywords(self, question: str) -> List[str]:
        """
        Extrait les mots-clés importants d'une question
        Utilisé pour évaluer les réponses
        
        Args:
            question: Texte de la question
        
        Returns:
            List[str]: Mots-clés extraits
        """
        doc = self.nlp(question)
        
        keywords = []
        for token in doc:
            # Garder les noms, verbes et adjectifs importants
            if token.pos_ in ["NOUN", "VERB", "ADJ"] and not token.is_stop:
                if len(token.text) > 3:
                    keywords.append(token.lemma_.lower())
        
        return list(set(keywords))[:5]  # Top 5 keywords
    
    def _load_question_templates(self) -> Dict:
        """
        Charge les templates de questions (backup)
        Structure : {difficulty: {skill: [templates]}}
        
        Returns:
            Dict: Templates organisés
        """
        return {
            "easy": {
                "python": [
                    "Quelle est la différence entre une liste et un tuple en {skill} ?",
                    "Expliquez ce qu'est un dictionnaire en {skill}.",
                    "Comment créer une fonction simple en {skill} ?"
                ],
                "javascript": [
                    "Quelle est la différence entre var, let et const en {skill} ?",
                    "Expliquez ce qu'est une fonction fléchée en {skill}.",
                    "Comment déclarer un tableau en {skill} ?"
                ],
                "generic": [
                    "Expliquez les bases de {skill}.",
                    "Quelle est votre expérience avec {skill} ?",
                    "Quels sont les concepts fondamentaux de {skill} ?"
                ]
            },
            "medium": {
                "python": [
                    "Comment gérez-vous les exceptions en {skill} ? Donnez un exemple.",
                    "Expliquez le concept de décorateur en {skill} avec {concept}.",
                    "Comment optimiseriez-vous une boucle en {skill} traitant {concept} ?"
                ],
                "javascript": [
                    "Expliquez le concept de closure en {skill}.",
                    "Comment fonctionne l'asynchronisme en {skill} avec {concept} ?",
                    "Quelle est la différence entre Promise et async/await en {skill} ?"
                ],
                "generic": [
                    "Comment utiliseriez-vous {skill} pour résoudre {concept} ?",
                    "Décrivez un projet où vous avez utilisé {skill}.",
                    "Quelles sont les meilleures pratiques en {skill} ?"
                ]
            },
            "hard": {
                "python": [
                    "Expliquez le Global Interpreter Lock (GIL) en {skill} et ses implications.",
                    "Comment implémenteriez-vous un système de cache avec {skill} pour {concept} ?",
                    "Décrivez l'architecture d'une application {skill} scalable gérant {concept}."
                ],
                "javascript": [
                    "Expliquez le mécanisme de l'event loop en {skill}.",
                    "Comment optimiseriez-vous les performances d'une application {skill} avec {concept} ?",
                    "Implémentez un système de gestion d'état complexe en {skill}."
                ],
                "generic": [
                    "Concevez une architecture complète utilisant {skill} pour {concept}.",
                    "Quels sont les défis de scalabilité avec {skill} ?",
                    "Comment débuguer un problème de performance complexe en {skill} ?"
                ]
            }
        }
    
    def adapt_difficulty(self, current_score: float, difficulty: str) -> str:
        """
        Adapte la difficulté des questions selon le score actuel
        
        Args:
            current_score: Score moyen actuel (0-100)
            difficulty: Difficulté actuelle
        
        Returns:
            str: Nouvelle difficulté suggérée
        """
        if current_score >= 85:
            return "hard"
        elif current_score >= 70:
            return "medium" if difficulty != "hard" else "hard"
        elif current_score >= 50:
            return "medium"
        else:
            return "easy"


# ============ EXEMPLE D'UTILISATION ============

if __name__ == "__main__":
    # Test du générateur
    generator = QuestionGenerator(use_gpu=False)
    
    # Description de poste exemple
    job_desc = """
    Nous recherchons un développeur Python senior avec une expertise en Django.
    Le candidat devra concevoir et maintenir des APIs RESTful, optimiser les 
    performances des bases de données PostgreSQL, et travailler en équipe agile.
    """
    
    # Générer des questions
    questions = generator.generate_questions(
        job_description=job_desc,
        required_skills=["Python", "Django", "PostgreSQL"],
        difficulty="medium",
        num_questions=5
    )
    
    # Afficher les résultats
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. {q['question']}")
        print(f"   Catégorie: {q['category']}")
        print(f"   Compétence: {q['skill']}")
        print(f"   Difficulté: {q['difficulty']}")
        print(f"   Méthode: {q['generation_method']}")
        print(f"   Mots-clés attendus: {', '.join(q['expected_keywords'])}")