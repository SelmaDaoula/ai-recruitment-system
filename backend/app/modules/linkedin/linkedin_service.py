"""
Service pour interagir avec l'API LinkedIn
Conforme à la documentation OpenID Connect de LinkedIn
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class LinkedInService:
    """
    Service d'intégration LinkedIn OAuth 2.0 et API
    Utilise OpenID Connect pour l'authentification
    """
    
    # URLs de l'API LinkedIn
    OAUTH_URL = "https://www.linkedin.com/oauth/v2"
    API_URL = "https://api.linkedin.com/v2"
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Génère l'URL d'autorisation LinkedIn
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email w_member_social",
            "state": state or "random_state_string"
        }
        
        url = f"{self.OAUTH_URL}/authorization?{urlencode(params)}"
        logger.info(f"📎 URL d'autorisation générée")
        logger.info(f"   Scopes: openid, profile, email, w_member_social")
        
        return url
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Échange le code d'autorisation contre un access token
        """
        logger.info("🔄 Échange du code contre access token...")
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(
                f"{self.OAUTH_URL}/accessToken",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            logger.info("✅ Access token obtenu avec succès")
            logger.info(f"   Expire dans: {token_data.get('expires_in', 'N/A')} secondes")
            
            return token_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur lors de l'échange du code : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response status: {e.response.status_code}")
                logger.error(f"   Response body: {e.response.text}")
            raise
    
    def get_user_profile(self, access_token: str) -> Dict:
        """
        Récupère le profil de l'utilisateur LinkedIn
        Utilise à la fois userinfo (OpenID) et l'API v2/me pour l'ID person
        """
        logger.info("👤 Récupération du profil utilisateur...")
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            # 1️⃣ Récupérer les infos OpenID Connect
            logger.info("   Appel /v2/userinfo...")
            userinfo_response = requests.get(
                f"{self.API_URL}/userinfo",
                headers=headers
            )
            userinfo_response.raise_for_status()
            userinfo_data = userinfo_response.json()
            
            logger.info(f"✅ Userinfo récupéré : {userinfo_data.get('email', 'No email')}")
            logger.info(f"   Name: {userinfo_data.get('name', 'N/A')}")
            logger.info(f"   Sub (OpenID): {userinfo_data.get('sub', 'N/A')}")
            
            # 2️⃣ Récupérer l'ID person réel via /v2/me
            logger.info("   Appel /v2/me pour récupérer person_id...")
            person_id = None
            me_data = None
            
            try:
                me_response = requests.get(
                    f"{self.API_URL}/me",
                    headers=headers
                )
                
                logger.info(f"   /v2/me status: {me_response.status_code}")
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    person_id = me_data.get('id')
                    logger.info(f"✅ Person ID depuis /v2/me : {person_id}")
                else:
                    logger.warning(f"⚠️  /v2/me a échoué : {me_response.status_code}")
                    logger.warning(f"   Response: {me_response.text}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur /v2/me : {e}")
            
            # ✅ FALLBACK : Si person_id est vide, utiliser le 'sub'
            if not person_id:
                person_id = userinfo_data.get('sub')
                logger.warning(f"⚠️  Utilisation du 'sub' comme person_id : {person_id}")
            else:
                logger.info(f"✅ Person ID final : {person_id}")
            
            # 3️⃣ Combiner les données
            profile_data = {
                **userinfo_data,
                "person_id": person_id,
                "me_data": me_data
            }
            
            logger.info("✅ Profil complet récupéré avec succès")
            
            return profile_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur récupération profil : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response status: {e.response.status_code}")
                logger.error(f"   Response body: {e.response.text}")
            raise
    
    def publish_post(
        self,
        access_token: str,
        linkedin_id: str,
        text: str,
        visibility: str = "PUBLIC"
    ) -> Dict:
        """
        ✨ PUBLICATION D'UN POST SUR LINKEDIN ✨
        """
        logger.info("\n" + "="*60)
        logger.info("📤 PUBLICATION DU POST SUR LINKEDIN")
        logger.info("="*60)
        logger.info(f"   Person ID utilisé : {linkedin_id}")
        logger.info(f"   Visibilité : {visibility}")
        logger.info(f"   Longueur du texte : {len(text)} caractères")
        logger.info(f"   Texte (100 premiers car.) : {text[:100]}...")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        post_data = {
            "author": f"urn:li:person:{linkedin_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        logger.info(f"   URN author : urn:li:person:{linkedin_id}")
        logger.info(f"   URL : {self.API_URL}/ugcPosts")
        logger.info("   Envoi de la requête...")
        
        try:
            response = requests.post(
                f"{self.API_URL}/ugcPosts",
                headers=headers,
                json=post_data,
                timeout=10
            )
            
            logger.info(f"\n   📡 RÉPONSE REÇUE")
            logger.info(f"   Status Code : {response.status_code}")
            logger.info(f"   Headers : {dict(response.headers)}")
            logger.info(f"   Body : {response.text}")
            
            # ✅ Vérifier le status code
            if response.status_code in [200, 201]:
                result = response.json() if response.text else {}
                post_id = response.headers.get('X-RestLi-Id', result.get("id", "N/A"))
                
                logger.info(f"\n✅ POST PUBLIÉ AVEC SUCCÈS !")
                logger.info(f"   Post ID : {post_id}")
                logger.info("="*60 + "\n")
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": "Post publié sur LinkedIn",
                    "data": result
                }
            else:
                # ❌ ERREUR
                logger.error(f"\n❌ ÉCHEC DE LA PUBLICATION")
                logger.error(f"   Status : {response.status_code}")
                logger.error(f"   Body : {response.text}")
                logger.error("="*60 + "\n")
                
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_body": response.text,
                    "message": f"Échec de la publication : {response.status_code}"
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"\n❌ EXCEPTION LORS DE LA PUBLICATION")
            logger.error(f"   Exception : {type(e).__name__}")
            logger.error(f"   Message : {str(e)}")
            
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response status: {e.response.status_code}")
                logger.error(f"   Response body: {e.response.text}")
            
            logger.error("="*60 + "\n")
            
            return {
                "success": False,
                "error": str(e),
                "response_body": e.response.text if hasattr(e, 'response') and e.response else None,
                "message": "Échec de la publication"
            }
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Rafraîchit un access token expiré
        """
        logger.info("🔄 Rafraîchissement du token...")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(
                f"{self.OAUTH_URL}/accessToken",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            response.raise_for_status()
            new_token_data = response.json()
            
            logger.info("✅ Token rafraîchi avec succès")
            
            return new_token_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur rafraîchissement token : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response: {e.response.text}")
            raise
    
    def validate_token(self, access_token: str) -> bool:
        """
        Vérifie si un token est toujours valide
        """
        try:
            response = requests.get(
                f"{self.API_URL}/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            is_valid = response.status_code == 200
            
            if is_valid:
                logger.info("✅ Token valide")
            else:
                logger.warning(f"⚠️  Token invalide (status: {response.status_code})")
            
            return is_valid
        
        except Exception as e:
            logger.error(f"❌ Erreur validation token : {e}")
            return False