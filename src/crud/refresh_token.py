from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from core.token import REFRESH_TOKEN_EXPIRE_DAYS, create_refresh_token
import models.user
import schemas.user

def get_user_by_refresh_token(db: Session, refresh_token: str):
    # get user by refresh token with SQLAlchemy ORM
    return db.query(models.user.User).join(models.user.RefreshToken).filter(
        models.user.RefreshToken.token == refresh_token,
        models.user.RefreshToken.is_revoked == False
    ).first()

def create_refresh_token(db: Session, user_id: str) -> schemas.user.UserTokenResponse:
    # create a new refresh token and store it in the database
    user = db.query(models.user.User).filter(models.user.User.id == user_id).first()

    if not user:
        raise ValueError("User not found")
    
    if not user.is_active:
        raise ValueError("User is not active")

    new_refresh_token = models.user.RefreshToken(
        user_id=user.id,
        token=create_refresh_token(),
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
        raise ValueError("User not found")
    
    if not user.refresh_token:
        return  # No refresh token to revoke
    
    user.refresh_token.is_revoked = True
    db.add(user.refresh_token)
    db.commit()
    db.refresh(user.refresh_token)

    return user.refresh_token