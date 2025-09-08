import os
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv

import core.auth as auth
import schemas.user
import crud.user, schemas.user
from db.session import get_db

load_dotenv()

# define the rule to get token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

ANDROID_CLIENT_ID = os.getenv("ANDROID_CLIENT_ID")

router = APIRouter(
    tags=["Secure Endpoints"],
    dependencies=[Depends(auth.get_current_user)]
)

@router.get("/users/me", response_model=schemas.user.UserResponse, tags=["users"])
def read_users_me(current_user: schemas.user.UserResponse = Depends(auth.get_current_user)):
    return current_user

@router.patch("/users/me/link-google", response_model=schemas.user.UserResponse, tags=["users"])
def link_google_account(
    db: Session = Depends(get_db),
    current_user: schemas.user.UserResponse = Depends(auth.get_current_user), # 独自トークンで認証
    google_token: str = Body(..., embed=True, alias="token")
):
    """
    ログイン中のユーザーにGoogleアカウントを紐付ける
    """
    # 1. Google IDトークンを検証、これはおまじない
    try:
        idinfo = id_token.verify_oauth2_token(
            google_token, requests.Request(), ANDROID_CLIENT_ID
        )
        google_user_id = idinfo["sub"]
        google_email = idinfo["email"]
    except ValueError:
        raise HTTPException(status_code=401, detail="無効なGoogleトークンです。")

    # 2. 安全性チェック
    # ログイン中ユーザーのemailとGoogleアカウントのemailが一致するか確認
    if current_user.email != google_email:
        raise HTTPException(
            status_code=400,
            detail="アカウントのメールアドレスとGoogleアカウントのメールアドレスが一致しません。"
        )

    # このGoogleアカウントが、他のユーザーに既に紐付けられていないか確認
    existing_google_user = crud.user.get_user_by_google_id(db, google_id=google_user_id)
    if existing_google_user and existing_google_user.id != current_user.id:
        raise HTTPException(
            status_code=409, # Conflict
            detail="このGoogleアカウントは既に他のアカウントに連携されています。"
        )
    
    # 3. ユーザー情報を更新
    current_user.credential.google_id = google_user_id

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user