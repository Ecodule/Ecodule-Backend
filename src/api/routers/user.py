from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import core.auth as auth
import core.email_verification
import crud.user, schemas.user
from db.session import get_db

# define the rule to get token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter()

# endpoint to create a new user
@router.post("/users/create", response_model=schemas.user.UserResponse, status_code=status.HTTP_201_CREATED, tags=["users"])
def create_new_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    # check if the user already exists
    db_user = crud.user.get_user_by_email(db=db, email=user.email)
    if db_user and not db_user.is_active:
        # 再度メールアドレス確認用のメールを送信
        core.email_verification.send_message(user.email)
        raise HTTPException(status_code=400, detail="このメールアドレスを持つユーザーは既に存在します。再度確認メールを送信しました。")

    if db_user and db_user.is_active:
        # ユーザーが既に存在し、有効化されている場合
        raise HTTPException(status_code=400, detail="このメールアドレスを持つユーザーは既に存在します。")

    # create new user
    created_user = crud.user.create_user(db=db, email=user.email, password=user.password)

    core.email_verification.send_message(user.email)

    return created_user

# authentication and token generation
@router.post("/auth/login/", response_model=schemas.user.Token,tags=["auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # verify user credentials and generate token
    user = crud.user.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # existing user but not active
    if not user.is_active:
        core.email_verification.send_message(user.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="メールアドレスが確認されていません。確認メールを再送信しました。",
        )
    
    # create access token
    access_token = auth.create_access_token(
        data={"sub": user.email} # sub is the unique identifier in JWT, typically the user ID or email
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.user.UserResponse, tags=["users"])
def read_users_me(current_user: schemas.user.UserResponse = Depends(auth.get_current_user)):
    return current_user

@router.get("/verify-email/", tags=["auth"])
def verify_email(token: str, db: Session = Depends(get_db)):
    # test the email verification token and activate the user account
    email = core.email_verification.verify_verification_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なトークンまたは有効期限切れです。"
        )

    user = crud.user.get_user_by_email(db, email=email)
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