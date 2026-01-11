"""
Module d'analyse de CV amélioré avec matching réel
Extraction intelligente + Scoring basé sur la correspondance avec l'offre
Version universelle : Tech + Marketing + Business + Design
"""

import re
from typing import Dict, List, Any, Optional
from rapidfuzz import fuzz
import logging

logger = logging.getLogger(__name__)

# ============ LISTE DES COMPÉTENCES PROFESSIONNELLES ============

PROFESSIONAL_SKILLS = {
    # ========== DÉVELOPPEMENT & PROGRAMMATION ==========
    
    # Langages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "php", "ruby", "go", "rust",
    "swift", "kotlin", "scala", "r", "matlab", "perl", "shell", "bash", "powershell",
    
    # Frameworks Web
    "react", "react.js", "reactjs", "angular", "vue", "vue.js", "vuejs", "next.js", "nuxt",
    "node.js", "nodejs", "express", "express.js", "fastapi", "flask", "django", "spring",
    "laravel", "symfony", "rails", "asp.net", ".net", "jquery", "bootstrap", "tailwind", "redux",
    
    # Mobile
    "android", "ios", "react native", "flutter", "xamarin", "ionic",
    
    # Bases de données
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "cassandra",
    "dynamodb", "neo4j", "elasticsearch", "mariadb", "firestore", "firebase", "nosql",
    
    # DevOps & Cloud
    "docker", "kubernetes", "jenkins", "gitlab", "github", "aws", "azure", "gcp",
    "terraform", "ansible", "ci/cd", "nginx", "apache", "linux", "ubuntu", "debian",
    
    # Data Science & AI
    "hadoop", "spark", "pyspark", "kafka", "airflow", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "keras", "opencv", "nlp", "computer vision", "machine learning",
    "deep learning", "data science", "big data", "etl", "matplotlib", "seaborn", "jupyter",
    "statistics", "ml", "ai", "tableau", "power bi",
    
    # Frontend
    "html", "css", "sass", "less", "webpack", "vite", "babel", "responsive design",
    
    # Testing & Outils Dev
    "git", "rest", "graphql", "grpc", "api", "microservices", "jest", "pytest", 
    "selenium", "cypress", "postman",
    
    # ========== MARKETING DIGITAL ==========
    
    # SEO & SEM
    "seo", "sem", "sea", "google ads", "facebook ads", "linkedin ads", "instagram ads",
    "tiktok ads", "twitter ads", "ppc", "cpc", "cpm", "display advertising",
    
    # Analytics
    "google analytics", "google tag manager", "gtm", "mixpanel", "amplitude", "hotjar",
    "a/b testing", "conversion optimization", "cro", "data analysis", "web analytics",
    
    # Marketing Strategy
    "marketing digital", "digital marketing", "content marketing", "email marketing",
    "social media", "social media marketing", "inbound marketing", "outbound marketing",
    "growth hacking", "performance marketing", "affiliate marketing", "influencer marketing",
    "marketing automation", "lead generation",
    
    # Réseaux sociaux
    "facebook", "instagram", "twitter", "linkedin", "tiktok", "youtube", "pinterest",
    "snapchat", "social media management", "community management",
    
    # Outils Marketing
    "hubspot", "mailchimp", "sendinblue", "hootsuite", "buffer", "sprout social",
    
    # Publicité
    "programmatic", "retargeting", "remarketing", "display", "native advertising",
    
    # Content
    "content creation", "content strategy", "copywriting", "storytelling", "blogging",
    "video marketing", "podcast", "webinar",
    
    # E-commerce
    "e-commerce", "shopify", "woocommerce", "magento", "prestashop",
    
    # ========== DESIGN & CRÉATIVITÉ ==========
    
    # UI/UX
    "ui design", "ux design", "user experience", "user interface", "wireframing",
    "prototyping", "design thinking", "usability testing", "user research",
    
    # Outils Design
    "figma", "sketch", "adobe xd", "invision", "canva", "photoshop", "illustrator",
    "indesign", "premiere pro", "after effects", "adobe creative suite", "lightroom",
    
    # ========== BUSINESS & MANAGEMENT ==========
    
    # Management
    "leadership", "management", "team management", "project management", "people management",
    "team building", "coaching", "mentoring", "change management", "strategic planning",
    
    # Gestion de projet
    "agile", "scrum", "kanban", "pmo", "planning", "budgeting", "budget management",
    "resource management", "stakeholder management",
    
    # Business
    "strategy", "business strategy", "business development", "strategic planning",
    "market research", "competitive analysis", "swot analysis", "business intelligence",
    "kpi", "roi", "crm", "sales", "negotiation", "b2b", "b2c",
    
    # Finance
    "financial analysis", "forecasting", "accounting", "excel", "financial modeling",
    "reporting", "financial planning",
    
    # RH
    "recruitment", "talent acquisition", "hr", "human resources", "onboarding",
    "training", "employee engagement", "performance management",
    
    # ========== SOFT SKILLS MESURABLES ==========
    
    "communication", "presentation", "public speaking", "writing", "problem solving",
    "analytical thinking", "critical thinking", "creativity", "innovation",
    "time management", "organization", "adaptability", "collaboration"
}

# Niveaux d'éducation avec scores
EDUCATION_SCORES = {
    "doctorat": 100,
    "phd": 100,
    "master": 90,
    "mastère": 90,
    "ingénieur": 85,
    "ingenieur": 85,
    "mba": 90,
    "licence": 70,
    "bachelor": 70,
    "bac+5": 85,
    "bac+3": 70,
    "bac+2": 60,
    "bts": 60,
    "dut": 60,
    "bac": 40
}


class ImprovedCVAnalyzer:
    """Analyseur de CV amélioré - Universel (Tech, Marketing, Business)"""
    
    def __init__(self):
        """Initialise l'analyseur"""
        logger.info("🚀 ImprovedCVAnalyzer initialisé (Version Universelle)")
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrait les informations de contact (email, téléphone, nom)
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
            r'\+33\s*[1-9](?:[\s.-]?\d{2}){4}',  # +33 6 12 34 56 78
            r'\+33[1-9]\d{8}',                    # +33612345678
            r'0[1-9](?:[\s.-]?\d{2}){4}',        # 06 12 34 56 78
            r'0[1-9]\d{8}'                        # 0612345678
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                phone = phones[0]
                phone_clean = re.sub(r'[\s.-]', '', phone)
                
                if phone_clean.startswith('+33'):
                    phone_clean = '0' + phone_clean[3:]
                
                if len(phone_clean) == 10 and phone_clean.isdigit():
                    contact["phone"] = phone_clean
                    logger.debug(f"  📞 Téléphone trouvé : {contact['phone']}")
                    break
        
        # ========== NOM ==========
        lines = text.split('\n')[:15]
        
        # Mots à exclure
        exclude_words = [
            'CURRICULUM', 'VITAE', 'CV', 'PROFIL', 'COMPETENCES', 'COMPÉTENCES',
            'EXPERIENCE', 'EXPÉRIENCE', 'FORMATION', 'LANGUES', 'CONTACT',
            'EMAIL', 'TELEPHONE', 'TÉLÉPHONE', 'DEVELOPPEUR', 'DÉVELOPPEUR',
            'ENGINEER', 'INGENIEUR', 'INGÉNIEUR', 'DATA', 'SCIENTIST',
            'FRONTEND', 'BACKEND', 'FULLSTACK', 'FULL', 'STACK', 'SENIOR',
            'JUNIOR', 'DESIGNER', 'ANALYST', 'MANAGER', 'DEVELOPER',
            'ARCHITECTE', 'CONSULTANT', 'CHEF', 'DIRECTEUR', 'RESPONSABLE',
            'MARKETING', 'DIGITAL'
        ]
        
        for line in lines:
            line = line.strip()
            
            # Pattern 1 : Capitalisé (Emma Rousseau)
            name_pattern1 = r'^([A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ][a-zàâäéèêëïîôùûüÿç]+(?:\s+[A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ][a-zàâäéèêëïîôùûüÿç]+){1,2})(?:\s|$)'
            match = re.match(name_pattern1, line)
            
            if not match:
                # Pattern 2 : MAJUSCULES (EMMA ROUSSEAU)
                name_pattern2 = r'^([A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]+(?:\s+[A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]+){1,2})(?:\s|$)'
                match = re.match(name_pattern2, line)
            
            if match:
                name_candidate = match.group(1).strip()
                words = name_candidate.split()
                
                # Vérifications
                if len(words) < 2 or len(words) > 3:
                    continue
                
                name_upper = name_candidate.upper()
                if any(exclude_word in name_upper for exclude_word in exclude_words):
                    continue
                
                if any(len(word) < 2 for word in words):
                    continue
                
                if any(char.isdigit() for char in name_candidate):
                    continue
                
                if any(char in name_candidate for char in ['@', '#', '$', '%', '&', '*', '(', ')', '[', ']']):
                    continue
                
                contact["name"] = name_candidate.title()
                logger.debug(f"  👤 Nom trouvé : {contact['name']}")
                break
        
        return contact
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extrait TOUTES les compétences professionnelles
        Tech + Marketing + Business + Design
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in PROFESSIONAL_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                if '.' in skill:
                    found_skills.append(skill)
                else:
                    found_skills.append(skill.title())
        
        found_skills = sorted(list(set(found_skills)))
        
        logger.info(f"  🎯 {len(found_skills)} compétences professionnelles trouvées")
        
        return found_skills
    
    def extract_experience_years(self, text: str) -> int:
        """
        Extrait le nombre d'années d'expérience
        """
        patterns = [
            r'(\d+)\s*(?:ans?|années?)\s+(?:d\')?expérience',
            r'expérience\s+(?:de\s+)?(\d+)\s*(?:ans?|années?)',
            r'(\d+)\+?\s*(?:ans?|années?)\s+en'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(y) for y in matches])
        
        # Compter les périodes
        from datetime import datetime
        date_pattern = r'(\d{4})\s*[-–]\s*(?:(\d{4})|(?:aujourd\'hui|présent|actuel))'
        matches = re.findall(date_pattern, text.lower())
        
        if matches:
            total = 0
            current_year = datetime.now().year
            for start, end in matches:
                start_year = int(start)
                end_year = int(end) if end and end.isdigit() else current_year
                total += max(0, end_year - start_year)
            years.append(total)
        
        result = max(years) if years else 0
        logger.info(f"  📊 Expérience : {result} ans")
        return result
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """
        Extrait les diplômes
        """
        education = []
        text_lower = text.lower()
        
        degree_keywords = [
            ("Doctorat", ["doctorat", "phd"]),
            ("Master", ["master", "mastère"]),
            ("Ingénieur", ["ingénieur", "ingenieur", "diplôme d'ingénieur"]),
            ("Licence", ["licence", "bachelor", "bac+3"]),
            ("BTS/DUT", ["bts", "dut", "bac+2"]),
            ("Bac", ["baccalauréat", "bac"])
        ]
        
        for degree_name, keywords in degree_keywords:
            for keyword in keywords:
                if keyword in text_lower:
                    pattern = rf'{keyword}[^\n]{{0,100}}'
                    match = re.search(pattern, text_lower)
                    field = match.group(0).replace(keyword, "").strip()[:50] if match else ""
                    
                    education.append({
                        "degree": degree_name,
                        "field": field,
                        "year": ""
                    })
                    break
        
        logger.info(f"  🎓 {len(education)} formations trouvées")
        return education if education else [{"degree": "Non spécifié", "field": "", "year": ""}]
    
    def extract_languages(self, text: str) -> List[Dict[str, str]]:
        """
        Extrait les langues parlées
        """
        languages = []
        text_lower = text.lower()
        
        lang_map = {
            "français": "Français",
            "francais": "Français",
            "anglais": "Anglais",
            "arabe": "Arabe",
            "allemand": "Allemand",
            "espagnol": "Espagnol",
            "italien": "Italien",
            "chinois": "Chinois",
            "japonais": "Japonais"
        }
        
        level_patterns = {
            "Courant": ["courant", "c2", "bilingue", "natif"],
            "Avancé": ["avancé", "avance", "c1"],
            "Intermédiaire": ["intermédiaire", "intermediaire", "b2", "b1"],
            "Basique": ["basique", "débutant", "debutant", "a2", "a1"]
        }
        
        for key, value in lang_map.items():
            if key in text_lower:
                level = "Non spécifié"
                pattern = rf'{key}[^\n]{{0,80}}'
                match = re.search(pattern, text_lower)
                
                if match:
                    context = match.group(0)
                    for level_name, level_keywords in level_patterns.items():
                        if any(kw in context for kw in level_keywords):
                            level = level_name
                            break
                
                languages.append({"language": value, "level": level})
        
        logger.info(f"  🌍 {len(languages)} langues trouvées")
        return languages if languages else [{"language": "Non spécifié", "level": ""}]
    
    def calculate_match_score(
        self,
        cv_skills: List[str],
        cv_experience: int,
        cv_education: List[Dict],
        job_offer: Dict
    ) -> Dict[str, Any]:
        """
        Calcule le score de matching RÉEL entre CV et offre
        """
        logger.info("🔍 Calcul du matching CV-Offre...")
        
        required_skills = job_offer.get("required_skills", [])
        nice_to_have = job_offer.get("nice_to_have_skills", [])
        required_experience = job_offer.get("experience_min_years", 0)
        required_education = job_offer.get("education_level", "").lower()
        
        # ========== 1. COMPÉTENCES (40%) ==========
        skills_score = 0
        if required_skills:
            cv_skills_lower = [s.lower() for s in cv_skills]
            required_lower = [s.lower() for s in required_skills]
            
            matches = 0
            for req in required_lower:
                for cv in cv_skills_lower:
                    if fuzz.ratio(req, cv) > 80:
                        matches += 1
                        break
            
            skills_score = (matches / len(required_skills)) * 100
            
            if nice_to_have:
                nice_lower = [s.lower() for s in nice_to_have]
                nice_matches = sum(1 for nice in nice_lower 
                                  if any(fuzz.ratio(nice, cv) > 80 for cv in cv_skills_lower))
                bonus = (nice_matches / len(nice_to_have)) * 10
                skills_score = min(100, skills_score + bonus)
        else:
            skills_score = 70 if cv_skills else 30
        
        # ========== 2. EXPÉRIENCE (30%) ==========
        experience_score = 0
        if required_experience > 0:
            if cv_experience >= required_experience:
                experience_score = 100
            elif cv_experience >= required_experience * 0.7:
                experience_score = 80
            elif cv_experience >= required_experience * 0.5:
                experience_score = 60
            else:
                experience_score = max(0, (cv_experience / required_experience) * 50)
        else:
            experience_score = 70
        
        # ========== 3. ÉDUCATION (20%) ==========
        education_score = 70
        
        if cv_education and cv_education[0]["degree"] != "Non spécifié":
            best_degree_score = 0
            for edu in cv_education:
                degree = edu.get("degree", "").lower()
                for known_degree, score in EDUCATION_SCORES.items():
                    if known_degree in degree:
                        best_degree_score = max(best_degree_score, score)
            
            if best_degree_score > 0:
                education_score = best_degree_score
                
                if required_education:
                    required_score = EDUCATION_SCORES.get(required_education, 70)
                    if best_degree_score >= required_score:
                        education_score = 100
                    elif best_degree_score >= required_score * 0.8:
                        education_score = 85
                    else:
                        education_score = min(education_score, 75)
        
        # ========== 4. LANGUES (10%) ==========
        languages_score = 70
        
        # ========== SCORE FINAL ==========
        final_score = (
            skills_score * 0.4 +
            experience_score * 0.3 +
            education_score * 0.2 +
            languages_score * 0.1
        )
        
        logger.info(f"✅ Score final : {final_score:.1f}/100")
        
        return {
            "cv_score": round(final_score, 1),
            "score_breakdown": {
                "skills": round(skills_score, 1),
                "experience": round(experience_score, 1),
                "education": round(education_score, 1),
                "languages": round(languages_score, 1)
            }
        }
    
    def get_recommendation(self, score: float) -> str:
        """Génère une recommandation basée sur le score"""
        if score >= 80:
            return "Excellent candidat - Fortement recommandé pour un entretien"
        elif score >= 65:
            return "Bon candidat - Recommandé pour un entretien"
        elif score >= 50:
            return "Candidat acceptable - À considérer selon le pool"
        else:
            return "Candidat insuffisant pour ce poste"
    
    def get_category(self, score: float) -> str:
        """Détermine la catégorie A/B/C/D"""
        if score >= 80:
            return "A"
        elif score >= 65:
            return "B"
        elif score >= 50:
            return "C"
        else:
            return "D"
    
    def analyze(self, cv_text: str, job_offer: Dict) -> Dict[str, Any]:
        """
        Analyse complète du CV par rapport à l'offre
        
        Args:
            cv_text: Texte du CV
            job_offer: Dictionnaire avec les infos de l'offre
        
        Returns:
            Analyse complète avec score réel
        """
        logger.info("📋 Début de l'analyse du CV...")
        
        # Extraction des données
        contact = self.extract_contact_info(cv_text)
        skills = self.extract_skills(cv_text)
        experience = self.extract_experience_years(cv_text)
        education = self.extract_education(cv_text)
        languages = self.extract_languages(cv_text)
        
        # Calcul du score de matching
        score_data = self.calculate_match_score(
            skills, experience, education, job_offer
        )
        
        final_score = score_data["cv_score"]
        
        return {
            "extracted_data": {
                "contact": contact,
                "skills": skills,
                "experience_years": experience,
                "education": education,
                "languages": languages,
                "extraction_method": "Improved ML + Matching"
            },
            "cv_score": final_score,
            "score_breakdown": score_data["score_breakdown"],
            "recommendation": self.get_recommendation(final_score),
            "category": self.get_category(final_score)
        }


# ============ Test ============

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TEST DE L'ANALYSEUR UNIVERSEL")
    print("="*70)
    
    # Test Marketing
    cv_marketing = """
    EMMA ROUSSEAU
    Marketing Manager
    Email: emma.rousseau@email.com
    
    PROFIL
    7 ans d'expérience en marketing digital
    
    COMPÉTENCES
    SEO, SEM, Google Analytics, Social Media, Content Marketing
    
    EXPÉRIENCE
    Marketing Manager - E-commerce Plus (2020 - Présent)
    
    FORMATION
    Master Marketing Digital - ESSEC - 2017
    """
    
    job_marketing = {
        "required_skills": ["SEO", "SEM", "Google Analytics"],
        "experience_min_years": 5,
        "education_level": "master"
    }
    
    analyzer = ImprovedCVAnalyzer()
    result = analyzer.analyze(cv_marketing, job_marketing)
    
    print(f"\n✅ TEST MARKETING :")
    print(f"   Nom : {result['extracted_data']['contact']['name']}")
    print(f"   Compétences : {len(result['extracted_data']['skills'])}")
    print(f"   Score : {result['cv_score']}/100")
    print(f"   Catégorie : {result['category']}")
    print("\n" + "="*70 + "\n")