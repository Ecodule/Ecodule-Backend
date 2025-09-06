import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from core.token import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from core.email_verification import send_message, verify_verification_token
from crud.user import authenticate_user, get_user_by_email, get_user_by_google_id, create_user as crud_create_user
from crud.refresh_token import get_user_by_refresh_token
from schemas.user import TokenResponse
from db.session import get_db

load_dotenv()
# define the rule to get token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter()

# authentication and token generation
@router.post("/auth/login/", response_model=TokenResponse, tags=["auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # verify user credentials and generate token
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # existing user but not active
    if not user.is_active:
        send_message(user.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="メールアドレスが確認されていません。確認メールを再送信しました。",
        )
    
    # create access token
    access_token = create_access_token(
        data={"sub": user.email} # sub is the unique identifier in JWT, typically the user ID or email
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/verify-email/", tags=["auth"])
def verify_email(token: str, db: Session = Depends(get_db)):
    # test the email verification token and activate the user account
    email = verify_verification_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なトークンまたは有効期限切れです。"
        )

    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
    
    if user.is_active:
        return {"message": "このアカウントは既に有効化されています"}
    
    # ユーザーを有効化
    user.is_active = True
    db.add(user)
    db.commit()
    
    return {"message": "メールアドレスの有効化が成功しました"}

@router.post("/auth/refresh/", response_model=TokenResponse)
async def refresh_access_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    # 1. DBからリフレッシュトークンを検証
    user = get_user_by_refresh_token(db=db, refresh_token=refresh_token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    # 2. 新しいアクセストークンを生成
    new_access_token = create_access_token(data={"sub": user.email})

    # 本来なら、新しいリフレッシュトークンも発行してDBに保存し、古いリフレッシュトークンは無効化するべき
    # ここでは簡略化のため、同じリフレッシュトークンを返す

    return {
        "id": user.id,
        "is_active": user.is_active,
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,  # 今回は同じリフレッシュトークンを返す
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60 # 秒単位で返す
    }

"""ここからGoogleアカウントとの連携に関するAPIエンドポイント"""
ANDROID_CLIENT_ID = os.getenv("ANDROID_CLIENT_ID")

@router.post("/auth/google")
async def verify_google_token(token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Androidアプリから受け取ったGoogle IDトークンを検証する
    """
    try:
        # id_token.verify_oauth2_tokenが以下のトークンの検証をすべて行ってくれる
        # - 署名の検証
        # - 有効期限の確認
        # - aud（オーディエンス）がこちらのクライアントIDと一致するかの確認
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), ANDROID_CLIENT_ID
        )

        # ここまで来ればトークンは正当
        # idinfoからユーザー情報を取得
        google_user_id = idinfo['sub']      # Googleユーザーの一意のID
        email = idinfo['email']
        name = idinfo.get('name')

        # ユーザーをデータベースから取得
        user = get_user_by_google_id(db=db, google_id=google_user_id)

        # Googleアカウントと連携していない場合
        if not user:
            user = get_user_by_email(db=db, email=email)
            if user:
                user.credential.google_id = google_user_id
                db.commit()
            else:
                # google_idとemailでもユーザーが存在しない場合、有効化して新規作成
                user = crud_create_user(db=db, email=email, google_id=google_user_id)
                user.is_active = True
                db.commit()

        access_token = create_access_token(
            data={"sub": user.email} # sub is the unique identifier in JWT, typically the user ID or email
        )
        
        return {"email": email, "name": name, "access_token": access_token, "message": "Successfully authenticated"}

    except ValueError as e:
        # google authorizationトークンが無効な場合
        raise HTTPException(
            status_code=401, detail=f"Invalid token: {e}"
        )
