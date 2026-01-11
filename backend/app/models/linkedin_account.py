"""
Modèle pour stocker les tokens LinkedIn
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class LinkedInAccount(Base):
    """
    Comptes LinkedIn connectés
    """
    __tablename__ = "linkedin_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants LinkedIn
    linkedin_id = Column(String(100), unique=True, index=True, nullable=False)
    person_id = Column(String(100))
    email = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_picture = Column(Text)
    
    # OAuth Tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_type = Column(String(50), default="Bearer")
    expires_at = Column(DateTime)  # Quand le token expire
    
    # Scopes autorisés
    scopes = Column(Text)  # "w_member_social,r_liteprofile"
    
    # Métadonnées
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LinkedInAccount(id={self.id}, email='{self.email}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "linkedin_id": self.linkedin_id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "profile_picture": self.profile_picture,
            "is_active": self.is_active,
            "scopes": self.scopes,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }