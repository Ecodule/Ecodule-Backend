from sqlalchemy.orm import Session

import models.user, core.auth as auth # 先ほど作成したauth.py
import schemas.user

def get_user_by_refresh_token(db: Session, refresh_token: str):
    # get user by refresh token with SQLAlchemy ORM
    return db.query(models.user.User).join(models.user.RefreshToken).filter(
        models.user.RefreshToken.token == refresh_token,
        models.user.RefreshToken.is_revoked == False
    ).first()

def create_refresh_token(db: Session, user_id: str) -> schemas.user.UserTokenResponse:
    # create a new refresh token and store it in the database
    new_token = auth.create_refresh_token()