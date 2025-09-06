from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from core.token import REFRESH_TOKEN_EXPIRE_DAYS, create_refresh_token
from core.security import verify_refresh_token, get_refresh_token_hash
from crud.user import get_user_by_email
import models.user
import schemas.user

def get_user_by_refresh_token(db: Session, email: str, refresh_token: str):
    # get user by refresh token with SQLAlchemy ORM
    user = get_user_by_email(db, email=email)

    if not user:
        return None
    
    expires_at_aware = user.refresh_token.expires_at.replace(tzinfo=timezone.utc)

    hashed_token = user.refresh_token.hashed_token
    if user.refresh_token.is_revoked:
        return None
    
    if expires_at_aware < datetime.now(timezone.utc):
        return None
    
    if verify_refresh_token(plain_token=refresh_token, hashed_token=hashed_token):
        return user

    return None
    

def insert_refresh_token(db: Session, user_id: str, refresh_token: str) -> schemas.user.TokenResponse:
    # create a new refresh token and store it in the database
    user = db.query(models.user.User).filter(models.user.User.id == user_id).first()

    if not user:
        None
    
    if not user.is_active:
        None

    hashed_token = get_refresh_token_hash(refresh_token)

    if user.refresh_token:
        print("Updating existing refresh token")
        user.refresh_token.hashed_token = hashed_token
        user.refresh_token.created_at = datetime.now(timezone.utc)
        user.refresh_token.expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        db.add(user.refresh_token)
        db.commit()
        db.refresh(user.refresh_token)

        return user.refresh_token

    else: 
        print("Creating new refresh token")
        new_refresh_token = models.user.RefreshToken(
            user_id=user.id,
            hashed_token=hashed_token,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

        db.add(new_refresh_token)
        db.commit()
        db.refresh(new_refresh_token)

        return new_refresh_token

def revoke_refresh_token(db: Session, user_id: str):
    # Revoke the existing refresh token for the user
    user = db.query(models.user.User).filter(models.user.User.id == user_id).first()

    if not user:
        return None
    
    if not user.refresh_token:
        return None

    user.refresh_token.is_revoked = True
    db.add(user.refresh_token)
    db.commit()
    db.refresh(user.refresh_token)

    return user.refresh_token