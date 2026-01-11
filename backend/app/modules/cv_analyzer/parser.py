"""
Module 3 - CV Parser
Extraction de texte depuis les fichiers PDF
"""

import pdfplumber
import logging
from pathlib import Path
from typing import Optional, Dict
import re

logger = logging.getLogger(__name__)


class CVParser:
    """
    Parseur de CV PDF
    Extrait le texte brut depuis un fichier PDF
    """
    
    def __init__(self):
        """
        Initialise le parser
        """
        logger.info("📄 CVParser initialisé")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrait tout le texte d'un PDF
        
        Args:
            pdf_path: Chemin vers le fichier PDF
        
        Returns:
            str: Texte extrait du PDF
        
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            Exception: Si l'extraction échoue
        
        Example:
            parser = CVParser()
            text = parser.extract_text_from_pdf("cv_jean_dupont.pdf")
            print(text)
        """
        pdf_file = Path(pdf_path)
        
        # Vérifier que le fichier existe
        if not pdf_file.exists():
            raise FileNotFoundError(f"Fichier PDF introuvable : {pdf_path}")
        
        try:
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"📖 Lecture du PDF : {pdf_file.name} ({len(pdf.pages)} pages)")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extraire le texte de la page
                    page_text = page.extract_text()
                    
                    if page_text:
                        text_content.append(page_text)
                        logger.debug(f"  Page {page_num}: {len(page_text)} caractères extraits")
                    else:
                        logger.warning(f"  Page {page_num}: Aucun texte extrait")
            
            # Joindre tout le texte
            full_text = "\n\n".join(text_content)
            
            # Nettoyer le texte
            full_text = self._clean_text(full_text)
            
            logger.info(f"✅ Extraction terminée : {len(full_text)} caractères au total")
            
            return full_text
        
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction du PDF : {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte extrait
        
        Args:
            text: Texte brut
        
        Returns:
            str: Texte nettoyé
        """
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les sauts de ligne excessifs
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Supprimer les caractères bizarres
        text = text.replace('\x00', '')
        
        # Trim
        text = text.strip()
        
        return text
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Extrait les métadonnées du PDF
        
        Args:
            pdf_path: Chemin vers le fichier PDF
        
        Returns:
            dict: Métadonnées (titre, auteur, nb pages, etc.)
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata = {
                    "filename": Path(pdf_path).name,
                    "num_pages": len(pdf.pages),
                    "metadata": pdf.metadata
                }
                
                return metadata
        
        except Exception as e:
            logger.error(f"Erreur extraction métadonnées : {e}")
            return {
                "filename": Path(pdf_path).name,
                "num_pages": 0,
                "metadata": {}
            }
    
    def is_valid_pdf(self, pdf_path: str) -> bool:
        """
        Vérifie si le fichier est un PDF valide
        
        Args:
            pdf_path: Chemin vers le fichier
        
        Returns:
            bool: True si valide, False sinon
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Essayer de lire la première page
                if len(pdf.pages) > 0:
                    pdf.pages[0].extract_text()
                    return True
                return False
        except:
            return False


# ============ Test du parser ============

if __name__ == "__main__":
    """
    Test du parser avec un exemple
    """
    print("\n" + "="*60)
    print("TEST DU CV PARSER")
    print("="*60)
    
    parser = CVParser()
    
    # Créer un CV de test (texte simulé)
    test_pdf_path = "test_cv.pdf"
    
    print("\n📝 Pour tester, créez un fichier 'test_cv.pdf' avec du texte")
    print("   Exemple de contenu :")
    print("   ---")
    print("   Jean DUPONT")
    print("   Développeur Python Senior")
    print("   Email: jean.dupont@email.com")
    print("   Tél: 06 12 34 56 78")
    print("")
    print("   EXPÉRIENCE:")
    print("   - Développeur chez TechCorp (2019-2024)")
    print("   - Stage chez DataLab (2018)")
    print("")
    print("   COMPÉTENCES:")
    print("   Python, Django, PostgreSQL, Docker, Git")
    print("   ---")
    
    if Path(test_pdf_path).exists():
        try:
            # Extraire le texte
            text = parser.extract_text_from_pdf(test_pdf_path)
            
            print(f"\n✅ Texte extrait ({len(text)} caractères):")
            print("="*60)
            print(text[:500] + "..." if len(text) > 500 else text)
            print("="*60)
            
            # Métadonnées
            metadata = parser.extract_metadata(test_pdf_path)
            print(f"\n📊 Métadonnées:")
            print(f"  Fichier: {metadata['filename']}")
            print(f"  Pages: {metadata['num_pages']}")
            
        except Exception as e:
            print(f"\n❌ Erreur : {e}")
    else:
        print(f"\n⚠️  Fichier '{test_pdf_path}' introuvable")
        print("   Créez-le pour tester le parser")
    
    print("\n" + "="*60 + "\n")