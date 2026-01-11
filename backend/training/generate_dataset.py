"""
Générateur de Dataset Synthétique pour Fine-tuning spaCy NER
Crée des CVs fictifs avec annotations de compétences
"""

import random
import json
from pathlib import Path
from typing import List, Tuple

# Dataset de base
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

SKILL_TEMPLATES = [
    "Compétences : {skills}",
    "Technologies : {skills}",
    "Stack technique : {skills}",
    "Maîtrise de {skills}",
    "Expertise en {skills}",
    "Compétent en {skills}",
    "Connaissance approfondie de {skills}"
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


class CVDatasetGenerator:
    """
    Génère un dataset de CVs synthétiques avec annotations spaCy
    """
    
    def __init__(self, output_dir: str = "data/training"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.train_data = []
    
    def generate_cv_text(self) -> str:
        """
        Génère le texte d'un CV fictif
        """
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        job_title = random.choice(JOB_TITLES)
        
        # Header
        cv = f"{name}\n{job_title}\n\n"
        
        # Expérience
        cv += "EXPÉRIENCE PROFESSIONNELLE\n\n"
        
        num_jobs = random.randint(1, 3)
        for _ in range(num_jobs):
            company = random.choice(COMPANIES)
            years = random.randint(1, 8)
            
            # Sélectionner 3-5 compétences aléatoires
            all_skills = []
            for category in SKILLS.values():
                all_skills.extend(category)
            
            job_skills = random.sample(all_skills, random.randint(3, 5))
            
            # Expérience template
            exp_template = random.choice(EXPERIENCE_TEMPLATES)
            main_skill = job_skills[0]
            
            cv += f"{random.choice(JOB_TITLES)} - {company}\n"
            cv += exp_template.format(years=years, skill=main_skill) + "\n"
            cv += f"Technologies utilisées : {', '.join(job_skills[1:])}\n\n"
        
        # Compétences
        cv += "COMPÉTENCES TECHNIQUES\n\n"
        
        # Sélectionner des compétences par catégorie
        selected_skills = []
        for category, skills in SKILLS.items():
            selected_skills.extend(random.sample(skills, random.randint(2, 4)))
        
        skill_text = random.choice(SKILL_TEMPLATES).format(skills=", ".join(selected_skills))
        cv += skill_text + "\n\n"
        
        # Formation
        cv += "FORMATION\n\n"
        cv += "Master Informatique - Université Paris (2019)\n"
        
        return cv
    
    def annotate_cv(self, text: str) -> Tuple[str, dict]:
        """
        Annote un CV avec les positions des compétences
        
        Format spaCy :
        (text, {"entities": [(start, end, "SKILL")]})
        """
        entities = []
        
        # Chercher toutes les compétences dans le texte
        all_skills = []
        for category in SKILLS.values():
            all_skills.extend(category)
        
        for skill in all_skills:
            # Trouver toutes les occurrences
            start = 0
            while True:
                pos = text.find(skill, start)
                if pos == -1:
                    break
                
                # Vérifier que c'est un mot complet (pas partie d'un autre mot)
                if pos > 0 and text[pos-1].isalnum():
                    start = pos + 1
                    continue
                
                end = pos + len(skill)
                if end < len(text) and text[end].isalnum():
                    start = pos + 1
                    continue
                
                entities.append((pos, end, "SKILL"))
                start = end
        
        # Trier par position
        entities.sort()
        
        return (text, {"entities": entities})
    
    def generate_dataset(self, n_samples: int = 500):
        """
        Génère un dataset complet
        
        Args:
            n_samples: Nombre de CVs à générer
        """
        print(f"\n🔄 Génération de {n_samples} CVs...")
        
        for i in range(n_samples):
            # Générer un CV
            cv_text = self.generate_cv_text()
            
            # Annoter
            annotated = self.annotate_cv(cv_text)
            
            self.train_data.append(annotated)
            
            if (i + 1) % 100 == 0:
                print(f"  ✅ {i + 1}/{n_samples} CVs générés")
        
        print(f"\n✅ {n_samples} CVs générés avec succès !")
        
        # Statistiques
        total_entities = sum(len(data[1]["entities"]) for data in self.train_data)
        print(f"📊 {total_entities} annotations de compétences au total")
        print(f"📊 Moyenne : {total_entities / n_samples:.1f} compétences par CV")
    
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
        Sauvegarde le dataset au format JSON
        """
        train_set, test_set = self.split_dataset()
        
        # Sauvegarder train
        train_file = self.output_dir / "train_data.json"
        with open(train_file, 'w', encoding='utf-8') as f:
            json.dump(train_set, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Train set sauvegardé : {train_file}")
        print(f"   {len(train_set)} exemples")
        
        # Sauvegarder test
        test_file = self.output_dir / "test_data.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_set, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Test set sauvegardé : {test_file}")
        print(f"   {len(test_set)} exemples")
        
        # Sauvegarder un exemple pour vérification
        example_file = self.output_dir / "example.txt"
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
    print("🚀 GÉNÉRATEUR DE DATASET POUR FINE-TUNING spaCy")
    print("="*60)
    
    # Créer le générateur
    generator = CVDatasetGenerator()
    
    # Générer le dataset
    generator.generate_dataset(n_samples=500)
    
    # Sauvegarder
    train_file, test_file = generator.save_dataset()
    
    print("\n" + "="*60)
    print("✅ DATASET PRÊT POUR L'ENTRAÎNEMENT !")
    print("="*60)
    print("\nProchaine étape : Fine-tuning spaCy avec ce dataset")
    print("\n" + "="*60 + "\n")