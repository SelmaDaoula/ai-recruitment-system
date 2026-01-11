"""
Générateur de Dataset Synthétique V2 - AMÉLIORÉ
Annotations plus précises, pas de faux positifs
"""

import random
import json
from pathlib import Path
from typing import List, Tuple

# Dataset de base (IDENTIQUE)
FIRST_NAMES = ["Jean", "Marie", "Pierre", "Sophie", "Thomas", "Julie", "Nicolas", "Emma", "Alexandre", "Camille"]
LAST_NAMES = ["Dupont", "Martin", "Bernard", "Dubois", "Lambert", "Moreau", "Simon", "Michel", "Laurent", "Leroy"]

SKILLS = {
    "langages": ["Python", "JavaScript", "Java", "C++", "PHP", "Ruby", "Go", "TypeScript", "Rust", "Kotlin"],
    "frameworks": ["Django", "Flask", "FastAPI", "React", "Vue", "Angular", "Spring", "Laravel", "Node.js", "Express"],
    "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "Cassandra"],
    "devops": ["Docker", "Kubernetes", "Jenkins", "GitLab CI", "AWS", "Azure", "Terraform", "Ansible"],
    "tools": ["Git", "GitHub", "Jira", "Confluence", "VS Code", "IntelliJ"]
}

EXPERIENCE_TEMPLATES = [
    "J'ai {years} ans d'expérience en {skill}",
    "Expérience de {years} ans avec {skill}",
    "Maîtrise de {skill} depuis {years} ans",
    "{years} années d'expérience professionnelle en {skill}",
    "Compétent en {skill} avec {years} ans d'expérience",
    "Expert {skill} ({years} ans)",
    "Utilisation de {skill} pendant {years} ans"
]

# NOUVEAU : Templates sans mots de contexte
SKILL_TEMPLATES_CLEAN = [
    "{skills}",  # Juste les compétences
    "Stack : {skills}",
    "Technos : {skills}",
    "Outils : {skills}"
]

JOB_TITLES = [
    "Développeur Full Stack",
    "Ingénieur Logiciel",
    "Data Scientist",
    "DevOps Engineer",
    "Lead Developer",
    "Architecte Logiciel",
    "Développeur Backend",
    "Développeur Frontend",
    "Ingénieur Machine Learning"
]

COMPANIES = ["TechCorp", "DataLab", "CloudSystems", "StartupLab", "InnovateTech", "WebAgency", "CodeFactory"]

# NOUVEAU : Liste d'exclusion
EXCLUDED_WORDS = [
    "Compétences", "Langages", "Frameworks", "Technologies", "Stack", "Outils",
    "Français", "Anglais", "Espagnol", "Allemand", "Italien",
    "Natif", "Courant", "Intermédiaire", "Débutant", "Bilingue",
    "Email", "Téléphone", "Expérience", "Formation", "Langues",
    "Bases de données", "DevOps", "Cloud", "A1", "A2", "B1", "B2", "C1", "C2"
]


class CVDatasetGeneratorV2:
    """
    Générateur V2 avec annotations plus précises
    """
    
    def __init__(self, output_dir: str = "data/training"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.train_data = []
        
        # Créer la liste complète des compétences valides
        self.valid_skills = []
        for category in SKILLS.values():
            self.valid_skills.extend(category)
    
    def generate_cv_text(self) -> str:
        """
        Génère le texte d'un CV fictif (AMÉLIORÉ)
        """
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        job_title = random.choice(JOB_TITLES)
        
        # Header
        cv = f"{name}\n{job_title}\n\n"
        
        # Expérience
        cv += "EXPERIENCE PROFESSIONNELLE\n\n"  # Sans accents pour éviter confusion
        
        num_jobs = random.randint(1, 3)
        for _ in range(num_jobs):
            company = random.choice(COMPANIES)
            years = random.randint(1, 8)
            
            # Sélectionner des compétences
            all_skills = []
            for category in SKILLS.values():
                all_skills.extend(category)
            
            job_skills = random.sample(all_skills, random.randint(3, 5))
            
            # Expérience template
            exp_template = random.choice(EXPERIENCE_TEMPLATES)
            main_skill = job_skills[0]
            
            cv += f"{random.choice(JOB_TITLES)} - {company}\n"
            cv += exp_template.format(years=years, skill=main_skill) + "\n"
            
            # CHANGEMENT : Juste les technos, pas de préfixe
            cv += f"Technos : {', '.join(job_skills[1:])}\n\n"
        
        # Compétences (SECTION AMÉLIORÉE)
        cv += "COMPETENCES\n\n"  # Sans accents
        
        # Sélectionner des compétences par catégorie
        selected_skills = []
        for category, skills in SKILLS.items():
            selected_skills.extend(random.sample(skills, random.randint(2, 4)))
        
        # CHANGEMENT : Template sans mots-clés problématiques
        skill_text = random.choice(SKILL_TEMPLATES_CLEAN).format(skills=", ".join(selected_skills))
        cv += skill_text + "\n\n"
        
        # Formation
        cv += "FORMATION\n\n"
        cv += "Master Informatique - Universite Paris (2019)\n"
        
        # PAS de section langues (pour éviter confusion)
        
        return cv
    
    def annotate_cv_precise(self, text: str) -> Tuple[str, dict]:
        """
        Annote un CV avec PRÉCISION (V2)
        
        Règles strictes :
        1. Annoter SEULEMENT les compétences techniques valides
        2. NE PAS annoter les titres de section
        3. NE PAS annoter les langues
        4. NE PAS annoter les mots de contexte
        """
        entities = []
        
        for skill in self.valid_skills:
            # Trouver toutes les occurrences
            start = 0
            while True:
                pos = text.find(skill, start)
                if pos == -1:
                    break
                
                # Vérifier que c'est un mot complet
                if pos > 0 and text[pos-1].isalnum():
                    start = pos + 1
                    continue
                
                end = pos + len(skill)
                if end < len(text) and text[end].isalnum():
                    start = pos + 1
                    continue
                
                # NOUVEAU : Vérifier le contexte (50 chars avant)
                context_start = max(0, pos - 50)
                context = text[context_start:pos].lower()
                
                # Exclure si dans un contexte de langue
                language_keywords = ["français", "anglais", "espagnol", "allemand", "langue"]
                if any(keyword in context for keyword in language_keywords):
                    start = end
                    continue
                
                # Ajouter l'annotation
                entities.append((pos, end, "SKILL"))
                start = end
        
        # Trier par position
        entities.sort()
        
        # Supprimer les doublons
        unique_entities = []
        seen = set()
        for start, end, label in entities:
            key = (start, end)
            if key not in seen:
                unique_entities.append((start, end, label))
                seen.add(key)
        
        return (text, {"entities": unique_entities})
    
    def generate_dataset(self, n_samples: int = 500):
        """
        Génère un dataset complet V2
        """
        print(f"\n🔄 Génération de {n_samples} CVs (V2 - Qualité améliorée)...")
        
        for i in range(n_samples):
            # Générer un CV
            cv_text = self.generate_cv_text()
            
            # Annoter avec précision
            annotated = self.annotate_cv_precise(cv_text)
            
            self.train_data.append(annotated)
            
            if (i + 1) % 100 == 0:
                print(f"  ✅ {i + 1}/{n_samples} CVs générés")
        
        print(f"\n✅ {n_samples} CVs générés avec succès !")
        
        # Statistiques
        total_entities = sum(len(data[1]["entities"]) for data in self.train_data)
        print(f"📊 {total_entities} annotations de compétences au total")
        print(f"📊 Moyenne : {total_entities / n_samples:.1f} compétences par CV")
        
        # NOUVEAU : Vérifier la qualité
        self._check_quality()
    
    def _check_quality(self):
        """
        Vérifie qu'il n'y a pas de faux positifs évidents
        """
        print(f"\n🔍 Vérification de la qualité des annotations...")
        
        # Compter les annotations par mot
        word_counts = {}
        
        for text, annotations in self.train_data:
            for start, end, label in annotations["entities"]:
                word = text[start:end]
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Détecter les mots suspects (qui ne sont pas des compétences valides)
        suspect_words = []
        for word, count in word_counts.items():
            if word in EXCLUDED_WORDS:
                suspect_words.append((word, count))
        
        if suspect_words:
            print(f"⚠️  {len(suspect_words)} mots suspects détectés :")
            for word, count in suspect_words[:10]:
                print(f"   - {word} : {count} occurrences")
        else:
            print(f"✅ Aucun mot suspect détecté !")
        
        # Top 10 compétences
        print(f"\n📊 Top 10 compétences annotées :")
        top_skills = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for skill, count in top_skills:
            print(f"   • {skill} : {count} fois")
    
    def split_dataset(self, train_ratio: float = 0.8):
        """
        Sépare en train/test
        """
        random.shuffle(self.train_data)
        
        split_idx = int(len(self.train_data) * train_ratio)
        
        train_set = self.train_data[:split_idx]
        test_set = self.train_data[split_idx:]
        
        return train_set, test_set
    
    def save_dataset(self):
        """
        Sauvegarde le dataset V2
        """
        train_set, test_set = self.split_dataset()
        
        # Sauvegarder train
        train_file = self.output_dir / "train_data_v2.json"
        with open(train_file, 'w', encoding='utf-8') as f:
            json.dump(train_set, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Train set V2 sauvegardé : {train_file}")
        print(f"   {len(train_set)} exemples")
        
        # Sauvegarder test
        test_file = self.output_dir / "test_data_v2.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_set, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Test set V2 sauvegardé : {test_file}")
        print(f"   {len(test_set)} exemples")
        
        # Sauvegarder un exemple pour vérification
        example_file = self.output_dir / "example_v2.txt"
        with open(example_file, 'w', encoding='utf-8') as f:
            example = train_set[0]
            f.write("TEXTE:\n")
            f.write(example[0])
            f.write("\n\nANNOTATIONS:\n")
            for start, end, label in example[1]["entities"]:
                skill = example[0][start:end]
                f.write(f"  {skill} [{start}:{end}] → {label}\n")
        
        print(f"💾 Exemple sauvegardé : {example_file}")
        
        return train_file, test_file


# ============ Script principal ============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 GÉNÉRATEUR DE DATASET V2 (QUALITÉ AMÉLIORÉE)")
    print("="*60)
    
    # Créer le générateur V2
    generator = CVDatasetGeneratorV2()
    
    # Générer le dataset
    generator.generate_dataset(n_samples=500)
    
    # Sauvegarder
    train_file, test_file = generator.save_dataset()
    
    print("\n" + "="*60)
    print("✅ DATASET V2 PRÊT !")
    print("="*60)
    print("\nAméliorations :")
    print("  ✅ Pas d'annotations sur les titres de section")
    print("  ✅ Pas d'annotations sur les langues")
    print("  ✅ Pas de mots de contexte annotés")
    print("  ✅ Vérification de qualité automatique")
    print("\nProchaine étape : Ré-entraîner avec ce dataset amélioré")
    print("\n" + "="*60 + "\n")