"""
Script pour scraper et peupler la base de données avec des questions
"""
import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.modules.chatbot.scraper import InterviewQuestionScraper
from app.modules.chatbot.data_processor import QuestionProcessor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Script principal de scraping"""
    
    logger.info("🚀 DÉMARRAGE DU SCRAPING")
    logger.info("=" * 60)
    
    # 1. Scraper
    logger.info("📥 Étape 1/3 : Scraping des sources...")
    scraper = InterviewQuestionScraper()
    raw_questions = scraper.scrape_all_sources()
    
    logger.info(f"✅ {len(raw_questions)} questions brutes récupérées")
    logger.info("=" * 60)
    
    # 2. Traiter
    logger.info("🔧 Étape 2/3 : Traitement des données...")
    processor = QuestionProcessor()
    organized_questions = processor.process_scraped_questions(raw_questions)
    
    total_after = sum(len(qs) for qs in organized_questions.values())
    logger.info(f"✅ {total_after} questions finales organisées")
    logger.info("=" * 60)
    
    # 3. Sauvegarder
    logger.info("💾 Étape 3/3 : Sauvegarde...")
    output_path = os.path.join(
        os.path.dirname(__file__),
        '../data/interview_questions.json'
    )
    
    # Créer le dossier data si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    processor.save_to_json(organized_questions, output_path)
    
    logger.info("=" * 60)
    logger.info("🎉 SCRAPING TERMINÉ AVEC SUCCÈS !")
    logger.info(f"📊 Résultats :")
    for job, questions in organized_questions.items():
        logger.info(f"   • {job}: {len(questions)} questions")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()