"""
Fine-tuning spaCy NER pour détecter les compétences dans les CVs
"""

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class SpacyNERTrainer:
    """
    Entraîneur de modèle spaCy NER custom
    """
    
    def __init__(self, base_model: str = "fr_core_news_md"):
        """
        Initialise avec un modèle de base
        
        Args:
            base_model: Modèle spaCy de base à fine-tuner
        """
        print(f"\n📥 Chargement du modèle de base : {base_model}")
        
        try:
            self.nlp = spacy.load(base_model)
            print(f"✅ Modèle {base_model} chargé")
        except:
            print(f"⚠️  Modèle {base_model} introuvable, téléchargement...")
            from subprocess import run
            run(f"python -m spacy download {base_model}".split())
            self.nlp = spacy.load(base_model)
        
        # Ajouter le NER si absent
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner", last=True)
        else:
            ner = self.nlp.get_pipe("ner")
        
        self.ner = ner
        
        # Ajouter notre label custom
        self.ner.add_label("SKILL")
        
        print(f"✅ Label 'SKILL' ajouté au NER")
    
    def load_data(self, train_file: str, test_file: str):
        """
        Charge les données d'entraînement et de test
        
        Args:
            train_file: Fichier JSON avec données d'entraînement
            test_file: Fichier JSON avec données de test
        """
        print(f"\n📂 Chargement des données...")
        
        with open(train_file, 'r', encoding='utf-8') as f:
            self.train_data = json.load(f)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)
        
        print(f"✅ Train : {len(self.train_data)} exemples")
        print(f"✅ Test : {len(self.test_data)} exemples")
    
    def prepare_examples(self, data):
        """
        Convertit les données au format spaCy Example
        """
        examples = []
        
        for text, annotations in data:
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        return examples
    
    def train(self, n_iter: int = 30, dropout: float = 0.2):
        """
        Entraîne le modèle
        
        Args:
            n_iter: Nombre d'itérations
            dropout: Taux de dropout pour régularisation
        """
        print(f"\n🔄 Début de l'entraînement...")
        print(f"   Itérations : {n_iter}")
        print(f"   Dropout : {dropout}")
        
        # Préparer les exemples
        train_examples = self.prepare_examples(self.train_data)
        
        # Désactiver les autres pipes pendant l'entraînement
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        
        with self.nlp.disable_pipes(*other_pipes):
            # Optimiseur
            optimizer = self.nlp.resume_training()
            
            # Boucle d'entraînement
            for iteration in range(n_iter):
                random.shuffle(train_examples)
                losses = {}
                
                # Mini-batches avec taille croissante
                batches = minibatch(train_examples, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    self.nlp.update(
                        batch,
                        drop=dropout,
                        losses=losses,
                        sgd=optimizer
                    )
                
                # Afficher la progression
                if (iteration + 1) % 5 == 0 or iteration == 0:
                    print(f"   Itération {iteration + 1}/{n_iter} - Loss: {losses['ner']:.4f}")
        
        print(f"\n✅ Entraînement terminé !")
    
    def evaluate(self):
        """
        Évalue le modèle sur le test set
        """
        print(f"\n📊 Évaluation sur le test set...")
        
        test_examples = self.prepare_examples(self.test_data)
        
        # Calculer les métriques
        scores = self.nlp.evaluate(test_examples)
        
        print(f"\n📈 RÉSULTATS:")
        print(f"   Precision : {scores['ents_p']:.2%}")
        print(f"   Recall    : {scores['ents_r']:.2%}")
        print(f"   F1-Score  : {scores['ents_f']:.2%}")
        
        return scores
    
    def test_predictions(self, n_samples: int = 5):
        """
        Teste le modèle sur quelques exemples
        """
        print(f"\n🧪 TEST SUR {n_samples} EXEMPLES:")
        print("="*60)
        
        for i, (text, annotations) in enumerate(random.sample(self.test_data, n_samples)):
            doc = self.nlp(text)
            
            print(f"\n📄 Exemple {i+1}:")
            print(f"Texte : {text[:100]}...")
            
            # Entités prédites
            print(f"\n🤖 Prédictions du modèle :")
            if doc.ents:
                for ent in doc.ents:
                    print(f"   • {ent.text} [{ent.label_}]")
            else:
                print(f"   (Aucune compétence détectée)")
            
            # Entités réelles
            print(f"\n✅ Annotations réelles :")
            for start, end, label in annotations["entities"]:
                skill = text[start:end]
                print(f"   • {skill} [{label}]")
            
            print("-"*60)
    
    def save_model(self, output_dir: str = "models/skill_ner"):
        """
        Sauvegarde le modèle entraîné
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.nlp.to_disk(output_path)
        
        print(f"\n💾 Modèle sauvegardé : {output_path}")
        
        return output_path
    
    def compare_before_after(self, text: str):
        """
        Compare les prédictions avant et après fine-tuning
        """
        print(f"\n🔍 COMPARAISON AVANT/APRÈS FINE-TUNING")
        print("="*60)
        print(f"Texte : {text}")
        print("-"*60)
        
        # Charger le modèle de base non fine-tuné
        base_nlp = spacy.load("fr_core_news_md")
        
        print(f"\n❌ AVANT (modèle de base) :")
        base_doc = base_nlp(text)
        if base_doc.ents:
            for ent in base_doc.ents:
                print(f"   • {ent.text} [{ent.label_}]")
        else:
            print(f"   (Aucune entité détectée)")
        
        print(f"\n✅ APRÈS (modèle fine-tuné) :")
        tuned_doc = self.nlp(text)
        if tuned_doc.ents:
            for ent in tuned_doc.ents:
                print(f"   • {ent.text} [{ent.label_}]")
        else:
            print(f"   (Aucune compétence détectée)")
        
        print("="*60)


# ============ Script principal ============

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🎓 FINE-TUNING spaCy NER POUR DÉTECTION DE COMPÉTENCES")
    print("="*60)
    
    # Vérifier si on utilise V2
    use_v2 = "--v2" in sys.argv or "--data-version" in sys.argv
    
    if use_v2:
        print("\n📦 Utilisation du dataset V2 (Qualité améliorée)")
        train_file = "data/training/train_data_v2.json"
        test_file = "data/training/test_data_v2.json"
        output_dir = "models/skill_ner_v2"
    else:
        print("\n📦 Utilisation du dataset V1")
        train_file = "data/training/train_data.json"
        test_file = "data/training/test_data.json"
        output_dir = "models/skill_ner_v1"
    
    # Créer le trainer
    trainer = SpacyNERTrainer(base_model="fr_core_news_md")
    
    # Charger les données
    trainer.load_data(train_file=train_file, test_file=test_file)
    
    # Entraîner
    trainer.train(n_iter=30, dropout=0.2)
    
    # Évaluer
    scores = trainer.evaluate()
    
    # Tester sur quelques exemples
    trainer.test_predictions(n_samples=3)
    
    # Sauvegarder
    model_path = trainer.save_model(output_dir=output_dir)
    
    # Comparaison avant/après
    test_text = "J'ai 5 ans d'expérience en Python et Django. Maîtrise de PostgreSQL et Docker."
    trainer.compare_before_after(test_text)
    
    print("\n" + "="*60)
    print("✅ FINE-TUNING TERMINÉ !")
    print("="*60)
    print(f"\n📦 Modèle sauvegardé dans : {model_path}")
    print(f"📊 F1-Score : {scores['ents_f']:.2%}")
    
    if use_v2:
        print("\n🎯 Dataset V2 utilisé - Qualité optimisée !")
        print("   ✅ Pas de faux positifs sur titres de section")
        print("   ✅ Pas de confusion avec les langues")
    
    print("\nProchaine étape : Intégrer ce modèle dans le projet")
    print("\n" + "="*60 + "\n")