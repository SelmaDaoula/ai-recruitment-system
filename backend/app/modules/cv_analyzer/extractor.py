"""
Module 3 - CV Extractor
Extraction d'informations structurées depuis le texte du CV
Utilise : spaCy, BERT, Regex
"""

import re
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CVExtractor:
    """
    Extracteur d'informations de CV
    Extrait : nom, email, téléphone, compétences, expérience, formation
    """
    
    def __init__(self, nlp=None):
        """
        Initialise l'extracteur
        
        Args:
            nlp: Modèle spaCy (optionnel)
        """
        self.nlp = nlp
        
        # Liste de compétences techniques communes
        self.tech_skills = [
            # Langages
            "Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go",
            "TypeScript", "Kotlin", "Swift", "Rust", "Scala", "R",
            
            # Frameworks
            "Django", "Flask", "FastAPI", "React", "Vue", "Angular", "Node.js",
            "Spring", "Laravel", "Ruby on Rails", "Express",
            
            # Bases de données
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
            "Oracle", "SQL Server", "SQLite", "Cassandra",
            
            # DevOps & Cloud
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins",
            "Git", "GitLab", "GitHub", "CI/CD", "Terraform",
            
            # Data & IA
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "Pandas", "NumPy", "Scikit-learn", "Keras", "NLP",
            
            # Autres
            "API REST", "GraphQL", "Microservices", "Agile", "Scrum"
        ]
        
        logger.info("🧠 CVExtractor initialisé")
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrait les informations de contact
        
        Args:
            text: Texte du CV
        
        Returns:
            dict: {
                "email": "jean.dupont@email.com",
                "phone": "06 12 34 56 78",
                "name": "Jean Dupont"
            }
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
        # Patterns français : 06 12 34 56 78, 0612345678, +33612345678
        # ========== TÉLÉPHONE ==========
        # Patterns français : 06 12 34 56 78, 0612345678, +33612345678
        phone_patterns = [
            r'(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}',  # Format avec espaces
            r'(?:\+33|0)\d{9}',  # Format sans espaces
            r'\d{2}[\s.-]\d{2}[\s.-]\d{2}[\s.-]\d{2}[\s.-]\d{2}'  # Format strict
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                # Nettoyer le numéro
                phone = re.sub(r'[\s.-]', '', phones[0])
                # Normaliser : retirer le +33 et ajouter 0
                if phone.startswith('+33'):
                    phone = '0' + phone[3:]
                # Vérifier que c'est bien 10 chiffres
                if len(phone) == 10 and phone.isdigit():
                    contact["phone"] = phone
                    logger.debug(f"  📞 Téléphone trouvé : {contact['phone']}")
                    break
        
        # ========== NOM ==========
        # On cherche un nom en MAJUSCULES au début du CV
        name_pattern = r'^([A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]+ [A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]+)'
        name_match = re.search(name_pattern, text, re.MULTILINE)
        
        if name_match:
            contact["name"] = name_match.group(1).title()
            logger.debug(f"  👤 Nom trouvé : {contact['name']}")
        elif self.nlp:
            # Essayer avec spaCy NER
            doc = self.nlp(text[:500])  # Analyser les 500 premiers caractères
            for ent in doc.ents:
                if ent.label_ == "PER":  # Personne
                    contact["name"] = ent.text
                    logger.debug(f"  👤 Nom trouvé (spaCy) : {contact['name']}")
                    break
        
        return contact
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extrait les compétences techniques
        
        Args:
            text: Texte du CV
        
        Returns:
            list: Liste des compétences trouvées
        
        Example:
            ["Python", "Django", "PostgreSQL", "Docker"]
        """
        found_skills = []
        
        # Convertir le texte en minuscules pour la recherche
        text_lower = text.lower()
        
        for skill in self.tech_skills:
            # Recherche insensible à la casse
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Trier par ordre alphabétique
        found_skills.sort()
        
        logger.debug(f"  🎯 {len(found_skills)} compétences trouvées")
        
        return found_skills
    
    def extract_experience_years(self, text: str) -> Optional[int]:
        """
        Extrait le nombre d'années d'expérience
        
        Args:
            text: Texte du CV
        
        Returns:
            int: Nombre d'années d'expérience (ou None)
        
        Détecte des patterns comme :
        - "5 ans d'expérience"
        - "Expérience : 3 ans"
        - "2019-2024" (calcule la différence)
        """
        # Pattern 1 : "X ans d'expérience"
        pattern1 = r"(\d+)\s+ans?\s+d['\']expérience"
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
                
                if end.lower() in ['aujourd\'hui', 'présent'] or end.isdigit() == False:
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
        
        Args:
            text: Texte du CV
        
        Returns:
            list: Liste des formations
            [
                {"degree": "Master", "field": "Informatique", "year": "2019"},
                {"degree": "Licence", "field": "Mathématiques", "year": "2017"}
            ]
        """
        education = []
        
        # Diplômes courants
        degrees = [
            "Master", "Licence", "Bachelor", "Doctorat", "PhD",
            "BTS", "DUT", "Ingénieur", "MBA", "BAC"
        ]
        
        # Rechercher chaque diplôme
        for degree in degrees:
            # Pattern : "Master Informatique 2019"
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
        
        Args:
            text: Texte du CV
        
        Returns:
            list: [{"language": "Anglais", "level": "Courant"}]
        """
        languages_list = []
        
        # Langues courantes
        langs = ["Anglais", "Français", "Espagnol", "Allemand", "Italien", 
                 "Portugais", "Chinois", "Japonais", "Arabe"]
        
        # Niveaux
        levels = ["Débutant", "Intermédiaire", "Courant", "Bilingue", "Natif",
                  "A1", "A2", "B1", "B2", "C1", "C2"]
        
        for lang in langs:
            if lang.lower() in text.lower():
                # Chercher le niveau associé
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
        Extrait toutes les informations du CV
        
        Args:
            text: Texte complet du CV
        
        Returns:
            dict: Toutes les données extraites
        """
        logger.info("🔍 Extraction des données du CV...")
        
        extracted_data = {
            "contact": self.extract_contact_info(text),
            "skills": self.extract_skills(text),
            "experience_years": self.extract_experience_years(text),
            "education": self.extract_education(text),
            "languages": self.extract_languages(text)
        }
        
        logger.info("✅ Extraction terminée")
        
        return extracted_data


# ============ Test de l'extractor ============

if __name__ == "__main__":
    """
    Test de l'extractor avec un CV exemple
    """
    print("\n" + "="*60)
    print("TEST DU CV EXTRACTOR")
    print("="*60)
    
    # CV de test
    cv_text = """
    JEAN DUPONT
    Développeur Python Senior
    
    Email: jean.dupont@email.com
    Téléphone: 06 12 34 56 78
    LinkedIn: linkedin.com/in/jeandupont
    
    EXPÉRIENCE PROFESSIONNELLE
    
    Développeur Senior - TechCorp (2019-2024)
    - Développement d'applications web avec Python et Django
    - Gestion de bases de données PostgreSQL
    - Déploiement avec Docker et Kubernetes
    - 5 ans d'expérience en développement backend
    
    COMPÉTENCES TECHNIQUES
    
    Langages: Python, JavaScript, TypeScript
    Frameworks: Django, Flask, FastAPI, React
    Bases de données: PostgreSQL, MongoDB, Redis
    DevOps: Docker, Kubernetes, Git, CI/CD
    Cloud: AWS, Azure
    
    FORMATION
    
    Master Informatique - Université Paris 2019
    Licence Mathématiques Appliquées - Université Lyon 2017
    
    LANGUES
    
    Français: Natif
    Anglais: Courant (C1)
    Espagnol: Intermédiaire (B1)
    """
    
    # Créer l'extractor
    extractor = CVExtractor()
    
    # Extraire les données
    data = extractor.extract_all(cv_text)
    
    # Afficher les résultats
    print("\n📋 RÉSULTATS DE L'EXTRACTION:\n")
    
    print("👤 CONTACT:")
    print(f"  Nom: {data['contact']['name']}")
    print(f"  Email: {data['contact']['email']}")
    print(f"  Téléphone: {data['contact']['phone']}")
    
    print(f"\n🎯 COMPÉTENCES ({len(data['skills'])}):")
    for skill in data['skills'][:10]:
        print(f"  ✓ {skill}")
    if len(data['skills']) > 10:
        print(f"  ... et {len(data['skills']) - 10} autres")
    
    print(f"\n📊 EXPÉRIENCE:")
    print(f"  {data['experience_years']} ans")
    
    print(f"\n🎓 FORMATION ({len(data['education'])}):")
    for edu in data['education']:
        print(f"  • {edu['degree']} - {edu['field']} ({edu['year']})")
    
    print(f"\n🌍 LANGUES ({len(data['languages'])}):")
    for lang in data['languages']:
        print(f"  • {lang['language']}: {lang['level']}")
    
    print("\n" + "="*60 + "\n")