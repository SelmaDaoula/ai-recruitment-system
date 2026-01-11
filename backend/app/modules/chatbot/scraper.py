"""
Scraper éthique pour récupérer des questions d'entretien
Sources : GitHub, StackOverflow, Reddit
"""
import requests
import time
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class InterviewQuestionScraper:
    """Scraper éthique pour questions d'entretien"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Purpose - Interview Bot)',
            'Accept': 'application/json'
        })
        
        # Rate limiting : 1 requête toutes les 2 secondes
        self.rate_limit_delay = 2
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Respecter le rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def scrape_github_awesome_lists(self) -> List[Dict]:
        """
        Scraper les listes 'awesome-interview-questions' sur GitHub
        Source : https://github.com/topics/interview-questions
        """
        logger.info("🔍 Scraping GitHub awesome lists...")
        questions = []
        
        try:
            # Liste connue de repos avec questions d'entretien
            repos = [
                "jwasham/coding-interview-university",
                "MaximAbramchuck/awesome-interview-questions",
                "DopplerHQ/awesome-interview-questions"
            ]
            
            for repo in repos:
                self._rate_limit()
                
                # Utiliser l'API GitHub (légale et encouragée)
                url = f"https://api.github.com/repos/{repo}/contents"
                
                try:
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        files = response.json()
                        
                        # Chercher fichiers README ou questions
                        for file in files:
                            if file['name'].lower().endswith(('.md', '.json')):
                                file_questions = self._parse_github_file(file)
                                questions.extend(file_questions)
                        
                        logger.info(f"✅ {len(questions)} questions de {repo}")
                    
                    elif response.status_code == 403:
                        logger.warning(f"⚠️  Rate limit GitHub atteint")
                        break
                
                except Exception as e:
                    logger.error(f"❌ Erreur repo {repo}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ Erreur GitHub scraping: {e}")
        
        return questions
    
    def _parse_github_file(self, file: Dict) -> List[Dict]:
        """Parser un fichier GitHub pour extraire questions"""
        questions = []
        
        try:
            # Télécharger le contenu du fichier
            self._rate_limit()
            response = self.session.get(file['download_url'], timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Parser selon le format
                if file['name'].endswith('.json'):
                    questions = self._parse_json_content(content)
                elif file['name'].endswith('.md'):
                    questions = self._parse_markdown_content(content)
        
        except Exception as e:
            logger.error(f"❌ Erreur parsing {file['name']}: {e}")
        
        return questions
    
    def _parse_json_content(self, content: str) -> List[Dict]:
        """Parser contenu JSON"""
        try:
            data = json.loads(content)
            
            questions = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'question' in item:
                        questions.append({
                            'text': item.get('question', ''),
                            'category': item.get('category', 'technical'),
                            'difficulty': item.get('difficulty', 'medium'),
                            'keywords': item.get('keywords', []),
                            'source': 'github'
                        })
            
            return questions
        
        except json.JSONDecodeError:
            return []
    
    def _parse_markdown_content(self, content: str) -> List[Dict]:
        """Parser contenu Markdown pour extraire questions"""
        questions = []
        
        try:
            lines = content.split('\n')
            current_category = 'technical'
            current_difficulty = 'medium'
            
            for line in lines:
                line = line.strip()
                
                # Détecter catégories
                if line.startswith('#'):
                    if 'python' in line.lower():
                        current_category = 'technical'
                    elif 'javascript' in line.lower():
                        current_category = 'technical'
                    elif 'behavioral' in line.lower():
                        current_category = 'behavioral'
                
                # Détecter questions (lignes qui commencent par - ou * ou nombre)
                if (line.startswith('- ') or 
                    line.startswith('* ') or 
                    line.startswith('Q:') or
                    (len(line) > 0 and line[0].isdigit() and '.' in line[:3])):
                    
                    # Nettoyer la question
                    question_text = line.lstrip('-*0123456789. Q:').strip()
                    
                    if len(question_text) > 20 and '?' in question_text:
                        questions.append({
                            'text': question_text,
                            'category': current_category,
                            'difficulty': current_difficulty,
                            'keywords': self._extract_keywords(question_text),
                            'source': 'github'
                        })
        
        except Exception as e:
            logger.error(f"❌ Erreur parsing markdown: {e}")
        
        return questions
    
    def scrape_stackoverflow_questions(self, tags: List[str] = None) -> List[Dict]:
        """
        Scraper StackOverflow via API officielle
        API : https://api.stackexchange.com/docs
        """
        logger.info("🔍 Scraping StackOverflow...")
        
        if tags is None:
            tags = ['python', 'javascript', 'java', 'interview-questions']
        
        questions = []
        
        try:
            for tag in tags:
                self._rate_limit()
                
                # API officielle StackExchange (légale)
                url = "https://api.stackexchange.com/2.3/questions"
                params = {
                    'order': 'desc',
                    'sort': 'votes',
                    'tagged': f'{tag};interview',
                    'site': 'stackoverflow',
                    'pagesize': 100,
                    'filter': 'withbody'
                }
                
                try:
                    response = self.session.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for item in data.get('items', []):
                            question_text = self._clean_html(item.get('title', ''))
                            
                            if len(question_text) > 20:
                                questions.append({
                                    'text': question_text,
                                    'category': 'technical',
                                    'difficulty': self._infer_difficulty(item),
                                    'keywords': [tag] + self._extract_keywords(question_text),
                                    'source': 'stackoverflow',
                                    'votes': item.get('score', 0)
                                })
                        
                        logger.info(f"✅ {len(questions)} questions de StackOverflow ({tag})")
                
                except Exception as e:
                    logger.error(f"❌ Erreur StackOverflow {tag}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ Erreur StackOverflow scraping: {e}")
        
        return questions
    
    def scrape_reddit_interviews(self, subreddits: List[str] = None) -> List[Dict]:
        """
        Scraper Reddit via API officielle
        Subreddits : cscareerquestions, learnprogramming
        """
        logger.info("🔍 Scraping Reddit...")
        
        if subreddits is None:
            subreddits = ['cscareerquestions', 'learnprogramming']
        
        questions = []
        
        try:
            for subreddit in subreddits:
                self._rate_limit()
                
                # API Reddit (légale, pas besoin auth pour lecture publique)
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': 'interview questions',
                    'restrict_sr': 'on',
                    'sort': 'top',
                    'limit': 100
                }
                
                try:
                    response = self.session.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for post in data.get('data', {}).get('children', []):
                            post_data = post.get('data', {})
                            title = post_data.get('title', '')
                            selftext = post_data.get('selftext', '')
                            
                            # Extraire questions du texte
                            extracted = self._extract_questions_from_text(
                                title + '\n' + selftext
                            )
                            
                            questions.extend(extracted)
                        
                        logger.info(f"✅ {len(questions)} questions de r/{subreddit}")
                
                except Exception as e:
                    logger.error(f"❌ Erreur Reddit {subreddit}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ Erreur Reddit scraping: {e}")
        
        return questions
    
    def _extract_questions_from_text(self, text: str) -> List[Dict]:
        """Extraire questions d'un texte"""
        questions = []
        
        try:
            # Chercher lignes avec "?"
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Ligne contient une question
                if '?' in line and len(line) > 30:
                    # Nettoyer
                    question_text = line.split('?')[0] + '?'
                    question_text = question_text.lstrip('-*0123456789. ').strip()
                    
                    if len(question_text) > 20:
                        questions.append({
                            'text': question_text,
                            'category': self._infer_category(question_text),
                            'difficulty': 'medium',
                            'keywords': self._extract_keywords(question_text),
                            'source': 'reddit'
                        })
        
        except Exception as e:
            logger.error(f"❌ Erreur extraction questions: {e}")
        
        return questions
    
    def _clean_html(self, text: str) -> str:
        """Nettoyer HTML"""
        try:
            soup = BeautifulSoup(text, 'html.parser')
            return soup.get_text().strip()
        except:
            return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extraire mots-clés d'une question"""
        # Mots techniques courants
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'django', 'node',
            'api', 'database', 'sql', 'algorithm', 'data structure',
            'optimization', 'design pattern', 'testing', 'debugging'
        ]
        
        text_lower = text.lower()
        keywords = []
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords[:5]
    
    def _infer_category(self, text: str) -> str:
        """Déduire la catégorie d'une question"""
        text_lower = text.lower()
        
        behavioral_keywords = [
            'team', 'conflict', 'leadership', 'challenge', 'failure',
            'success', 'communication', 'work with', 'manage', 'deadline'
        ]
        
        for keyword in behavioral_keywords:
            if keyword in text_lower:
                return 'behavioral'
        
        return 'technical'
    
    def _infer_difficulty(self, item: Dict) -> str:
        """Déduire la difficulté selon les votes"""
        score = item.get('score', 0)
        
        if score > 100:
            return 'hard'
        elif score > 20:
            return 'medium'
        else:
            return 'easy'
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scraper toutes les sources"""
        all_questions = []
        
        logger.info("🚀 Démarrage scraping multi-sources...")
        
        # 1. GitHub
        try:
            github_q = self.scrape_github_awesome_lists()
            all_questions.extend(github_q)
            logger.info(f"✅ GitHub : {len(github_q)} questions")
        except Exception as e:
            logger.error(f"❌ GitHub failed: {e}")
        
        # 2. StackOverflow
        try:
            stackoverflow_q = self.scrape_stackoverflow_questions()
            all_questions.extend(stackoverflow_q)
            logger.info(f"✅ StackOverflow : {len(stackoverflow_q)} questions")
        except Exception as e:
            logger.error(f"❌ StackOverflow failed: {e}")
        
        # 3. Reddit
        try:
            reddit_q = self.scrape_reddit_interviews()
            all_questions.extend(reddit_q)
            logger.info(f"✅ Reddit : {len(reddit_q)} questions")
        except Exception as e:
            logger.error(f"❌ Reddit failed: {e}")
        
        logger.info(f"🎉 TOTAL : {len(all_questions)} questions scrapées")
        
        return all_questions