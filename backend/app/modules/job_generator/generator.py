"""
MODULE 1 : Générateur d'Annonces LinkedIn
Génère automatiquement des annonces professionnelles
Version 100% gratuite avec NLP
"""

import spacy
import json
from pathlib import Path
from typing import Dict, List


class JobOfferGenerator:
    """
    Génère des annonces d'emploi optimisées pour LinkedIn
    Utilise des templates + enrichissement NLP avec spaCy
    """
    
    def __init__(self):
        """
        Initialise le générateur
        Charge spaCy et les templates
        """
        print("📥 Initialisation du générateur d'annonces...")
        
        # Charger spaCy pour l'analyse linguistique
        try:
            self.nlp = spacy.load("fr_core_news_md")
            print("✅ spaCy chargé")
        except:
            print("⚠️  spaCy non disponible, mode simple activé")
            self.nlp = None
        
        # Charger les templates depuis data/templates/
        self.templates = self._load_templates()
        print(f"✅ {len(self.templates)} templates chargés")
        print("✅ Générateur prêt !")
    
    def _load_templates(self) -> Dict:
        """
        Charge tous les templates depuis le dossier data/templates/
        
        Returns:
            Dict: Templates organisés par secteur
            Exemple: {"tech": {...}, "marketing": {...}}
        """
        templates = {}
        templates_dir = Path("data/templates")
        
        # Vérifier que le dossier existe
        if not templates_dir.exists():
            print(f"⚠️  Dossier {templates_dir} non trouvé")
            return self._get_default_template()
        
        # Lire tous les fichiers JSON
        for file_path in templates_dir.glob("*.json"):
            try:
                sector = file_path.stem  # nom du fichier sans .json
                with open(file_path, 'r', encoding='utf-8') as f:
                    templates[sector] = json.load(f)
                print(f"  ✓ Template '{sector}' chargé")
            except Exception as e:
                print(f"  ✗ Erreur lors du chargement de {file_path}: {e}")
        
        # Si aucun template, utiliser le default
        if not templates:
            templates = self._get_default_template()
        
        return templates
    
    def _get_default_template(self) -> Dict:
        """
        Template par défaut si les fichiers ne sont pas trouvés
        
        Returns:
            Dict: Template générique
        """
        return {
            "general": {
                "sector": "general",
                "header": "{title} - Opportunité professionnelle",
                "body": "💼 Le poste\nNous recherchons un(e) {title}.\n\n🎯 Compétences\n{skills}\n\n📊 Expérience\n{experience}\n\n📍 Lieu\n{location}\n\n💰 Salaire\n{salary}",
                "footer": "📩 Postulez maintenant !\n\n#Emploi #Recrutement",
                "emojis": {"title": "💼", "skills": "✓"}
            }
        }
    
    def generate_offer(self, params: Dict) -> str:
        """
        ★★★ FONCTION PRINCIPALE ★★★
        Génère une annonce complète à partir des paramètres
        
        Args:
            params (Dict): Paramètres de l'offre
                - title: "Développeur Python"
                - industry: "tech" (ou "marketing", "general")
                - skills: ["Python", "Django", "PostgreSQL"]
                - experience: "3-5 ans"
                - location: "Paris / Remote"
                - salary_min: 45000 (optionnel)
                - salary_max: 55000 (optionnel)
        
        Returns:
            str: Annonce LinkedIn formatée et prête à publier
        
        Exemple:
            params = {
                "title": "Développeur Python",
                "industry": "tech",
                "skills": ["Python", "Django"],
                "experience": "3-5 ans",
                "location": "Paris"
            }
            annonce = generator.generate_offer(params)
        """
        print(f"\n🔧 Génération de l'annonce pour : {params.get('title', 'Poste')}")
        
        # 1️⃣ SÉLECTIONNER LE BON TEMPLATE
        template = self._select_template(params.get('industry', 'general'))
        print(f"  ✓ Template sélectionné : {template['sector']}")
        
        # 2️⃣ FORMATER LES COMPÉTENCES
        skills_text = self._format_skills(params.get('skills', []))
        print(f"  ✓ {len(params.get('skills', []))} compétences formatées")
        
        # 3️⃣ FORMATER LE SALAIRE
        salary_text = self._format_salary(
            params.get('salary_min'),
            params.get('salary_max')
        )
        
        # 4️⃣ ENRICHIR LE TITRE (avec spaCy si disponible)
        title = self._enrich_title(params.get('title', 'Poste'))
        
        # 5️⃣ REMPLIR LE TEMPLATE
        try:
            # Header
            header = template['header'].format(
                title=title
            )
            
            # Body
            body = template['body'].format(
                title=title,
                sector=template['sector'],
                skills=skills_text,
                experience=params.get('experience', 'Non spécifié'),
                location=params.get('location', 'À définir'),
                salary=salary_text
            )
            
            # Footer
            footer = template['footer']
            
        except KeyError as e:
            print(f"  ⚠️  Erreur de formatage : {e}")
            return self._generate_simple_offer(params)
        
        # 6️⃣ ASSEMBLER L'ANNONCE FINALE
        final_offer = self._format_for_linkedin(header, body, footer)
        
        print("  ✅ Annonce générée avec succès !")
        return final_offer
    
    def _select_template(self, industry: str) -> Dict:
        """
        Sélectionne le template approprié selon le secteur
        
        Args:
            industry: "tech", "marketing", "general", etc.
        
        Returns:
            Dict: Template sélectionné
        """
        # Normaliser le nom du secteur
        industry = industry.lower().strip()
        
        # Si le template existe, le retourner
        if industry in self.templates:
            return self.templates[industry]
        
        # Sinon, utiliser le template général
        if 'general' in self.templates:
            return self.templates['general']
        
        # En dernier recours, le premier template disponible
        return list(self.templates.values())[0]
    
    def _format_skills(self, skills: List[str]) -> str:
        """
        Formate la liste des compétences avec des emojis
        
        Args:
            skills: ["Python", "Django", "PostgreSQL"]
        
        Returns:
            str: "✓ Python\n✓ Django\n✓ PostgreSQL"
        """
        if not skills:
            return "Compétences à définir lors de l'entretien"
        
        # Formater chaque compétence avec un emoji
        formatted = []
        for skill in skills:
            formatted.append(f"✓ {skill}")
        
        return "\n".join(formatted)
    
    def _format_salary(self, salary_min: int = None, salary_max: int = None) -> str:
        """
        Formate la fourchette de salaire
        
        Args:
            salary_min: 45000
            salary_max: 55000
        
        Returns:
            str: "45-55K€" ou "Selon profil"
        """
        if salary_min and salary_max:
            min_k = salary_min // 1000
            max_k = salary_max // 1000
            return f"{min_k}-{max_k}K€ annuel"
        elif salary_min:
            min_k = salary_min // 1000
            return f"À partir de {min_k}K€ annuel"
        else:
            return "Salaire selon profil et expérience"
    
    def _enrich_title(self, title: str) -> str:
        """
        Enrichit le titre avec spaCy (analyse linguistique)
        
        Args:
            title: "Développeur Python"
        
        Returns:
            str: Titre potentiellement enrichi
        """
        # Si spaCy n'est pas disponible, retourner tel quel
        if not self.nlp:
            return title
        
        try:
            # Analyser le titre avec spaCy
            doc = self.nlp(title)
            
            # Pour l'instant, on retourne tel quel
            # Plus tard, on pourra ajouter des synonymes, variantes, etc.
            return title
            
        except Exception as e:
            print(f"  ⚠️  Erreur enrichissement titre : {e}")
            return title
    
    def _format_for_linkedin(self, header: str, body: str, footer: str) -> str:
        """
        Assemble et formate l'annonce finale pour LinkedIn
        
        Args:
            header: Titre de l'annonce
            body: Corps de l'annonce
            footer: Pied de page avec hashtags
        
        Returns:
            str: Annonce complète formatée
        """
        # Ajouter des emojis au début
        linkedin_post = f"""🚀 {header}

{body}

{footer}
        """.strip()
        
        return linkedin_post
    
    def _generate_simple_offer(self, params: Dict) -> str:
        """
        Génère une annonce simple en cas d'erreur
        Fallback pour garantir qu'on a toujours un résultat
        
        Args:
            params: Paramètres de l'offre
        
        Returns:
            str: Annonce basique
        """
        title = params.get('title', 'Poste à pourvoir')
        skills = params.get('skills', [])
        skills_text = "\n".join([f"• {s}" for s in skills]) if skills else "À définir"
        
        return f"""🚀 {title}

Nous recherchons un(e) {title} pour rejoindre notre équipe.

Compétences recherchées :
{skills_text}

Expérience : {params.get('experience', 'Variable selon profil')}
Localisation : {params.get('location', 'À définir')}

📩 Postulez dès maintenant !

#Emploi #Recrutement
        """.strip()


# ============ EXEMPLE D'UTILISATION ============

if __name__ == "__main__":
    """
    Script de test pour vérifier que le générateur fonctionne
    """
    print("="*60)
    print("TEST DU GÉNÉRATEUR D'ANNONCES")
    print("="*60)
    
    # Créer une instance du générateur
    generator = JobOfferGenerator()
    
    # Paramètres d'une offre d'emploi
    job_params = {
        "title": "Développeur Python Senior",
        "industry": "tech",
        "skills": [
            "Python",
            "Django",
            "PostgreSQL",
            "Docker",
            "Git"
        ],
        "experience": "3-5 ans d'expérience",
        "location": "Paris / Remote hybride",
        "salary_min": 45000,
        "salary_max": 55000
    }
    
    # Générer l'annonce
    print("\n" + "="*60)
    annonce = generator.generate_offer(job_params)
    
    # Afficher le résultat
    print("\n" + "="*60)
    print("ANNONCE GÉNÉRÉE")
    print("="*60)
    print(annonce)
    print("="*60)
    
    # Test 2 : Marketing
    print("\n\nTEST 2 : Annonce Marketing")
    print("="*60)
    
    job_params_marketing = {
        "title": "Chef de Projet Marketing Digital",
        "industry": "marketing",
        "skills": [
            "SEO/SEA",
            "Google Analytics",
            "Social Media",
            "Content Marketing"
        ],
        "experience": "2-4 ans",
        "location": "Lyon",
        "salary_min": 35000,
        "salary_max": 45000
    }
    
    annonce_marketing = generator.generate_offer(job_params_marketing)
    print("\n" + annonce_marketing)
    print("="*60)