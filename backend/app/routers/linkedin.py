"""
Routes API pour l'intégration LinkedIn
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import secrets
import traceback 
from dotenv import load_dotenv  # ✅ AJOUT

from app.database import get_db
from app.models.linkedin_account import LinkedInAccount
from app.modules.linkedin.linkedin_service import LinkedInService

# ✅ CHARGER LES VARIABLES D'ENVIRONNEMENT
load_dotenv()

router = APIRouter(prefix="/api/linkedin", tags=["LinkedIn"])

# ✅ VÉRIFIER QUE LES VARIABLES SONT CHARGÉES
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# ✅ VALIDATION AU DÉMARRAGE
if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET or not LINKEDIN_REDIRECT_URI:
    print("⚠️  ERREUR : Variables LinkedIn manquantes dans .env")
    print(f"   LINKEDIN_CLIENT_ID: {LINKEDIN_CLIENT_ID}")
    print(f"   LINKEDIN_CLIENT_SECRET: {'***' if LINKEDIN_CLIENT_SECRET else 'None'}")
    print(f"   LINKEDIN_REDIRECT_URI: {LINKEDIN_REDIRECT_URI}")
else:
    print("✅ Variables LinkedIn chargées avec succès")
    print(f"   Client ID: {LINKEDIN_CLIENT_ID}")
    print(f"   Redirect URI: {LINKEDIN_REDIRECT_URI}")

# Initialiser le service LinkedIn
linkedin_service = LinkedInService(
    client_id=LINKEDIN_CLIENT_ID,
    client_secret=LINKEDIN_CLIENT_SECRET,
    redirect_uri=LINKEDIN_REDIRECT_URI
)


# ============ SCHEMAS PYDANTIC ============

class PublishPostRequest(BaseModel):
    """Schema pour publier un post"""
    text: str
    visibility: str = "PUBLIC"


class LinkedInAccountResponse(BaseModel):
    """Schema de réponse"""
    id: int
    linkedin_id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    scopes: str
    
    class Config:
        from_attributes = True


# ============ ENDPOINTS ============

@router.get("/connect")
async def connect_linkedin():
    """
    Étape 1 : Génère l'URL d'autorisation LinkedIn
    L'utilisateur sera redirigé vers LinkedIn pour autoriser l'app
    """
    # Générer un state token pour sécurité CSRF
    state = secrets.token_urlsafe(32)
    
    # Générer l'URL d'autorisation
    auth_url = linkedin_service.get_authorization_url(state=state)
    
    return {
        "authorization_url": auth_url,
        "state": state,
        "message": "Redirigez l'utilisateur vers cette URL"
    }


@router.get("/callback")
async def linkedin_callback(
    code: str = Query(...),
    state: str = Query(None),
    error: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Étape 2 : Callback après autorisation LinkedIn
    LinkedIn redirige ici avec un code d'autorisation
    """
    # Vérifier les erreurs
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?linkedin_error={error}"
        )
    
    try:
        # Échanger le code contre un access token
        token_data = linkedin_service.exchange_code_for_token(code)
        
        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 5184000)  # ~60 jours par défaut
        refresh_token = token_data.get("refresh_token")
        
        # Récupérer le profil utilisateur
        profile = linkedin_service.get_user_profile(access_token)
        
        linkedin_id = profile.get("sub")  # ID LinkedIn (OpenID)
        person_id = profile.get("person_id")  # ✅ ID person pour UGC API
        email = profile.get("email")
        first_name = profile.get("given_name")
        last_name = profile.get("family_name")
        profile_picture = profile.get("picture")
        
        print(f"✅ Profil récupéré:")
        print(f"   linkedin_id (sub): {linkedin_id}")
        print(f"   person_id: {person_id}")  # ✅ LOG
        print(f"   email: {email}")
        
        # Vérifier si le compte existe déjà
        existing_account = db.query(LinkedInAccount).filter(
            LinkedInAccount.linkedin_id == linkedin_id
        ).first()
        
        if existing_account:
            # Mettre à jour les tokens
            existing_account.access_token = access_token
            existing_account.refresh_token = refresh_token
            existing_account.person_id = person_id  # ✅ MISE À JOUR
            existing_account.expires_at = datetime.now() + timedelta(seconds=expires_in)
            existing_account.is_active = True
            existing_account.last_used_at = datetime.now()
            
            db.commit()
            print(f"✅ Compte mis à jour avec person_id: {person_id}")
            account = existing_account
        else:
            # Créer un nouveau compte
            account = LinkedInAccount(
                linkedin_id=linkedin_id,
                person_id=person_id,  # ✅ AJOUT
                email=email,
                first_name=first_name,
                last_name=last_name,
                profile_picture=profile_picture,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=datetime.now() + timedelta(seconds=expires_in),
                scopes=token_data.get("scope", ""),
                is_active=True,
                last_used_at=datetime.now()
            )
            
            db.add(account)
            db.commit()
            print(f"✅ Nouveau compte créé avec person_id: {person_id}")
        
        # Rediriger vers le frontend avec succès
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?linkedin_connected=true"
        )
    
    except Exception as e:
        print(f"❌ Erreur callback LinkedIn : {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(
            url=f"{FRONTEND_URL}/settings?linkedin_error=connection_failed"
        )
        

@router.get("/status", response_model=LinkedInAccountResponse)
async def get_linkedin_status(db: Session = Depends(get_db)):
    """
    Vérifier le statut de connexion LinkedIn
    """
    # Récupérer le compte actif (supposant 1 seul compte pour l'instant)
    account = db.query(LinkedInAccount).filter(
        LinkedInAccount.is_active == True
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Aucun compte LinkedIn connecté")
    
    # Vérifier si le token a expiré
    if account.expires_at and account.expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="Token expiré, reconnectez-vous")
    
    return account


@router.post("/publish")
async def publish_to_linkedin(
    post_data: PublishPostRequest,
    db: Session = Depends(get_db)
):
    """
    ✨ PUBLIER UN POST SUR LINKEDIN ✨
    """
    # Récupérer le compte LinkedIn actif
    account = db.query(LinkedInAccount).filter(
        LinkedInAccount.is_active == True
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=400,
            detail="Aucun compte LinkedIn connecté. Connectez-vous d'abord."
        )
    
    # Vérifier si le token a expiré
    if account.expires_at and account.expires_at < datetime.now():
        # Essayer de rafraîchir le token
        if account.refresh_token:
            try:
                new_token_data = linkedin_service.refresh_access_token(
                    account.refresh_token
                )
                
                account.access_token = new_token_data["access_token"]
                account.expires_at = datetime.now() + timedelta(
                    seconds=new_token_data.get("expires_in", 5184000)
                )
                db.commit()
            except:
                raise HTTPException(
                    status_code=401,
                    detail="Token expiré et échec du rafraîchissement"
                )
        else:
            raise HTTPException(
                status_code=401,
                detail="Token expiré, reconnectez-vous"
            )
    
    # Publier le post
    result = linkedin_service.publish_post(
        access_token=account.access_token,
        linkedin_id=account.linkedin_id,
        text=post_data.text,
        visibility=post_data.visibility
    )
    
    # Mettre à jour last_used_at
    account.last_used_at = datetime.now()
    db.commit()
    
    if result["success"]:
        return {
            "success": True,
            "message": "Post publié sur LinkedIn avec succès ! 🎉",
            "post_id": result.get("post_id"),
            "linkedin_url": f"https://www.linkedin.com/feed/update/{result.get('post_id')}"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Échec de la publication : {result.get('error')}"
        )


@router.delete("/disconnect")
async def disconnect_linkedin(db: Session = Depends(get_db)):
    """
    Déconnecter le compte LinkedIn
    """
    account = db.query(LinkedInAccount).filter(
        LinkedInAccount.is_active == True
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Aucun compte connecté")
    
    account.is_active = False
    db.commit()
    
    return {
        "success": True,
        "message": "Compte LinkedIn déconnecté"
    }