from sqlalchemy.orm import Session

import models.user, core.auth as auth # 先ほど作成したauth.py

def get_user_by_email(db: Session, email: str):
    # get user by email with SQLAlchemy ORM
    # filter is as WHERE clause in SQL
    return db.query(models.user.User).filter(models.user.User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str):
    # get user by google_id with SQLAlchemy ORM
    return db.query(models.user.User).join(models.user.UserCredential).filter(models.user.UserCredential.google_id == google_id).first()

def create_user(db: Session, email: str, password: str = None, google_id: str = None):
    """新規ユーザーを作成する"""
    # ユーザーが既に存在するかチェック
    db_user = get_user_by_email(db, email=email)
    if db_user:
        return None # 本来はHTTPExceptionなどを返す 
    
    # 新しいUserオブジェクトを作成
    new_user = models.user.User(email=email)
    
    # パスワード認証の場合
    if password:
        hashed_password = auth.get_password_hash(password)
        # 新しいUserCredentialオブジェクトを作成し、Userに紐付ける
        new_credential = models.user.UserCredential(
            hashed_password=hashed_password,
            user=new_user
        )
    
    # Google認証の場合
    if google_id:
        new_credential = models.user.UserCredential(
            google_id=google_id,
            user=new_user
        )

    if not password and not google_id:
        return None

    db.add(new_user)
    db.add(new_credential)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    """ユーザーを認証する"""
    user = get_user_by_email(db, email)
    
    # ユーザーが存在しない場合は失敗
    if not user:
        return None
        
    # パスワードを検証
    if not auth.verify_password(password, user.credential.hashed_password):
        return None
    
    return user