"""
Module 3 - CV Extractor avec Modèle NER Fine-tuné
Extraction d'informations avec spaCy custom model
"""

import re
import logging
import spacy
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CVExtractorML:
    """
    Extracteur de CV utilisant un modèle NER fine-tuné
    Détection automatique des compétences avec Machine Learning
    """
    
    def __init__(self, custom_model_path: str = "models/skill_ner_v1"):
        """
        Initialise l'extracteur avec le modèle custom
        
        Args:
            custom_model_path: Chemin vers le modèle NER fine-tuné
        """
        # Charger le modèle custom si disponible
        model_path = Path(custom_model_path)
        
        if model_path.exists():
            try:
                self.nlp = spacy.load(model_path)
                logger.info(f"✅ Modèle NER custom chargé : {custom_model_path}")
                self.use_custom_model = True
            except Exception as e:
                logger.warning(f"⚠️  Erreur chargement modèle custom : {e}")
                logger.info("📥 Utilisation du modèle de base...")
                self.nlp = spacy.load("fr_core_news_md")
                self.use_custom_model = False
        else:
            logger.warning(f"⚠️  Modèle custom introuvable : {custom_model_path}")
            logger.info("📥 Utilisation du modèle de base...")
            try:
                self.nlp = spacy.load("fr_core_news_md")
            except:
                self.nlp = None
            self.use_custom_model = False
        
        logger.info("🧠 CVExtractorML initialisé")
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrait les informations de contact
        """
        contact = {
            "email": None,
            "phone": None,
            "name": None
        }
        
        # ========== EMAIL ==========
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact["email"] = emails[0]
            logger.debug(f"  ✉️  Email trouvé : {contact['email']}")
        
        # ========== TÉLÉPHONE ==========
        phone_patterns = [
            r'(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}',
            r'(?:\+33|0)\d{9}',
            r'\d{2}[\s.-]\d{2}[\s.-]\d{2}[\s.-]\d{2}[\s.-]\d{2}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                phone = re.sub(r'[\s.-]', '', phones[0])
                if phone.startswith('+33'):
                    phone = '0' + phone[3:]
                if len(phone) == 10 and phone.isdigit():
                    contact["phone"] = phone
                    logger.debug(f"  📞 Téléphone trouvé : {contact['phone']}")
                    break
        
        # ========== NOM avec spaCy ==========
        if self.nlp:
            doc = self.nlp(text[:500])
            for ent in doc.ents:
                if ent.label_ == "PER":
                    contact["name"] = ent.text
                    logger.debug(f"  👤 Nom trouvé (spaCy) : {contact['name']}")
                    break
        
        # Fallback : chercher nom en MAJUSCULES
        if not contact["name"]:
            name_pattern = r'^([A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]+ [A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]+)'
            name_match = re.search(name_pattern, text, re.MULTILINE)
            if name_match:
                contact["name"] = name_match.group(1).title()
                logger.debug(f"  👤 Nom trouvé (regex) : {contact['name']}")
        
        return contact
    
    def extract_skills_ml(self, text: str) -> List[str]:
        """
        Extrait les compétences avec le modèle NER fine-tuné
        Applique un filtre de post-traitement pour retirer les faux positifs
        
        Args:
            text: Texte du CV
        
        Returns:
            list: Liste des compétences détectées
        """
        if not self.nlp:
            return []
        
        # Liste d'exclusion (mots qui ne sont PAS des compétences)
        EXCLUDED_WORDS = {
            # Titres de sections
            "Compétences", "Langages", "Frameworks", "Technologies", "Stack", 
            "Outils", "Bases de données", "DevOps", "Cloud", "Formation",
            "Expérience", "Langues", "Contact", "Profil",
            
            # Langues
            "Français", "Anglais", "Espagnol", "Allemand", "Italien", 
            "Portugais", "Chinois", "Japonais", "Arabe", "Russe",
            
            # Niveaux de langue
            "Natif", "Courant", "Intermédiaire", "Débutant", "Bilingue",
            "A1", "A2", "B1", "B2", "C1", "C2",
            
            # Mots génériques
            "Email", "Téléphone", "Tel", "Mobile", "Adresse",
            "Ville", "Pays", "Date", "Année",
            
            # Mots de liaison
            "avec", "depuis", "pendant", "durant", "Utilisation",
            "Maîtrise", "Connaissance", "Expérience", "Expertise",
            
            # Autres
            "CI/", "CD", "Déploiement", "Développement"
        }
        
        # Utiliser le modèle NER
        doc = self.nlp(text)
        
        # Extraire toutes les entités SKILL
        skills = []
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                skill = ent.text.strip()
                
                # Filtrer les exclusions (insensible à la casse)
                if skill and skill not in EXCLUDED_WORDS:
                    # Vérifier aussi en minuscules
                    if skill.lower() not in {w.lower() for w in EXCLUDED_WORDS}:
                        if skill not in skills:
                            skills.append(skill)
        
        # Trier par ordre alphabétique
        skills.sort()
        
        logger.debug(f"  🎯 {len(skills)} compétences détectées (ML + filtre)")
        
        return skills
    
    def extract_experience_years(self, text: str) -> Optional[int]:
        """
        Extrait le nombre d'années d'expérience
        """
        # Pattern 1 : "X ans d'expérience"
        pattern1 = r"(\d+)\s+ans?\s+d['\u2019']exp[ée]rience"
        match1 = re.search(pattern1, text, re.IGNORECASE)
        
        if match1:
            years = int(match1.group(1))
            logger.debug(f"  📊 Expérience : {years} ans (pattern texte)")
            return years
        
        # Pattern 2 : Dates "2019-2024"
        pattern2 = r'(\d{4})\s*[-–]\s*(\d{4}|aujourd\'hui|présent)'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        
        if matches2:
            total_years = 0
            current_year = datetime.now().year
            
            for start, end in matches2:
                start_year = int(start)
                
                if end.lower() in ['aujourd\'hui', 'présent'] or not end.isdigit():
                    end_year = current_year
                else:
                    end_year = int(end)
                
                years = end_year - start_year
                total_years += years
            
            logger.debug(f"  📊 Expérience : {total_years} ans (calcul dates)")
            return total_years
        
        return None
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """
        Extrait les formations
        """
        education = []
        
        degrees = [
            "Master", "Licence", "Bachelor", "Doctorat", "PhD",
            "BTS", "DUT", "Ingénieur", "MBA", "BAC"
        ]
        
        for degree in degrees:
            pattern = rf'{degree}[^\n]{{0,100}}?(\d{{4}})?'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                edu_text = match.group(0)
                year_match = re.search(r'\d{4}', edu_text)
                
                education.append({
                    "degree": degree,
                    "field": edu_text.replace(degree, "").replace(year_match.group(0) if year_match else "", "").strip()[:50],
                    "year": year_match.group(0) if year_match else ""
                })
        
        logger.debug(f"  🎓 {len(education)} formations trouvées")
        
        return education
    
    def extract_languages(self, text: str) -> List[Dict[str, str]]:
        """
        Extrait les langues parlées
        """
        languages_list = []
        
        langs = ["Anglais", "Français", "Espagnol", "Allemand", "Italien", 
                 "Portugais", "Chinois", "Japonais", "Arabe"]
        
        levels = ["Débutant", "Intermédiaire", "Courant", "Bilingue", "Natif",
                  "A1", "A2", "B1", "B2", "C1", "C2"]
        
        for lang in langs:
            if lang.lower() in text.lower():
                pattern = rf'{lang}[^\n]{{0,50}}'
                match = re.search(pattern, text, re.IGNORECASE)
                
                level = "Non spécifié"
                if match:
                    context = match.group(0)
                    for lvl in levels:
                        if lvl.lower() in context.lower():
                            level = lvl
                            break
                
                languages_list.append({
                    "language": lang,
                    "level": level
                })
        
        logger.debug(f"  🌍 {len(languages_list)} langues trouvées")
        
        return languages_list
    
    def extract_all(self, text: str) -> Dict:
        """
        Extrait toutes les informations du CV avec ML
        
        Args:
            text: Texte complet du CV
        
        Returns:
            dict: Toutes les données extraites
        """
        logger.info(f"🔍 Extraction des données du CV (ML Mode: {self.use_custom_model})...")
        
        extracted_data = {
            "contact": self.extract_contact_info(text),
            "skills": self.extract_skills_ml(text),  # ← Utilise le modèle NER !
            "experience_years": self.extract_experience_years(text),
            "education": self.extract_education(text),
            "languages": self.extract_languages(text),
            "extraction_method": "ML" if self.use_custom_model else "Rule-based"
        }
        
        logger.info(f"✅ Extraction terminée ({extracted_data['extraction_method']})")
        
        return extracted_data
    
    def compare_extractions(self, text: str, old_extractor) -> Dict:
        """
        Compare l'extraction ML vs Rule-based
        
        Args:
            text: Texte du CV
            old_extractor: Ancien extracteur (CVExtractor)
        
        Returns:
            dict: Comparaison des deux méthodes
        """
        logger.info("🔬 Comparaison ML vs Rule-based...")
        
        # Extraction ML
        ml_result = self.extract_all(text)
        
        # Extraction Rule-based
        rule_result = old_extractor.extract_all(text)
        
        # Comparer les compétences
        ml_skills = set(ml_result['skills'])
        rule_skills = set(rule_result['skills'])
        
        only_ml = ml_skills - rule_skills
        only_rule = rule_skills - ml_skills
        common = ml_skills & rule_skills
        
        comparison = {
            "ml_method": {
                "total_skills": len(ml_skills),
                "unique_skills": len(only_ml),
                "skills": list(ml_skills)
            },
            "rule_method": {
                "total_skills": len(rule_skills),
                "unique_skills": len(only_rule),
                "skills": list(rule_skills)
            },
            "comparison": {
                "common_skills": len(common),
                "only_in_ml": list(only_ml),
                "only_in_rules": list(only_rule),
                "agreement_rate": round(len(common) / max(len(ml_skills), len(rule_skills)) * 100, 1) if ml_skills or rule_skills else 0
            }
        }
        
        logger.info(f"✅ Comparaison terminée")
        logger.info(f"   ML: {len(ml_skills)} compétences")
        logger.info(f"   Rules: {len(rule_skills)} compétences")
        logger.info(f"   Agreement: {comparison['comparison']['agreement_rate']}%")
        
        return comparison


# ============ Test de l'extracteur ML ============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST DE L'EXTRACTEUR ML")
    print("="*60)
    
    # CV de test
    cv_text = """
    JEAN DUPONT
    Développeur Python Senior
    
    Email: jean.dupont@email.com
    Téléphone: 06 12 34 56 78
    
    EXPÉRIENCE PROFESSIONNELLE
    
    Développeur Senior - TechCorp (2019-2024)
    5 ans d'expérience en développement Python
    Technologies utilisées : Django, Flask, FastAPI, PostgreSQL
    Déploiement avec Docker et Kubernetes sur AWS
    
    COMPÉTENCES TECHNIQUES
    
    Langages: Python, JavaScript, TypeScript
    Frameworks: Django, Flask, FastAPI, React
    Bases de données: PostgreSQL, MongoDB, Redis
    DevOps: Docker, Kubernetes, Git, CI/CD, Jenkins
    Cloud: AWS, Azure
    
    FORMATION
    
    Master Informatique - Université Paris 2019
    Licence Mathématiques - Université Lyon 2017
    
    LANGUES
    
    Français: Natif
    Anglais: Courant (C1)
    Espagnol: Intermédiaire (B1)
    """
    
    # Créer l'extracteur ML
    extractor_ml = CVExtractorML()
    
    # Extraire les données
    data = extractor_ml.extract_all(cv_text)
    
    # Afficher les résultats
    print("\n📋 RÉSULTATS DE L'EXTRACTION ML:\n")
    
    print(f"🔧 Méthode: {data['extraction_method']}")
    
    print("\n👤 CONTACT:")
    print(f"  Nom: {data['contact']['name']}")
    print(f"  Email: {data['contact']['email']}")
    print(f"  Téléphone: {data['contact']['phone']}")
    
    print(f"\n🎯 COMPÉTENCES ({len(data['skills'])}):")
    for skill in data['skills']:
        print(f"  ✓ {skill}")
    
    print(f"\n📊 EXPÉRIENCE:")
    print(f"  {data['experience_years']} ans")
    
    print(f"\n🎓 FORMATION ({len(data['education'])}):")
    for edu in data['education']:
        print(f"  • {edu['degree']} - {edu['field']} ({edu['year']})")
    
    print(f"\n🌍 LANGUES ({len(data['languages'])}):")
    for lang in data['languages']:
        print(f"  • {lang['language']}: {lang['level']}")
    
    print("\n" + "="*60 + "\n")