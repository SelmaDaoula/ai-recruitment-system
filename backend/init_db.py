"""
Script pour initialiser la base de données PostgreSQL
Crée toutes les tables définies dans les modèles
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, Base
from app.models.job_offer import JobOffer
from app.models.candidate import Candidate

def init_database():
    """
    Crée toutes les tables dans PostgreSQL
    """
    print("\n" + "="*60)
    print("🔧 INITIALISATION DE LA BASE DE DONNÉES")
    print("="*60)
    
    try:
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ Tables créées avec succès !")
        print("\nTables créées :")
        print("  - job_offers")
        print("  - candidates")
        
        print("\n" + "="*60)
        print("✅ Base de données prête à l'emploi !")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des tables : {e}")
        print("="*60 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    init_database()