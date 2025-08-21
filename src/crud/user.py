from sqlalchemy.orm import Session

import models.user, auth # 先ほど作成したauth.py

def get_user_by_email(db: Session, email: str):
    # get user by email with SQLAlchemy ORM
    # filter is as WHERE clause in SQL
    return db.query(models.user.User).filter(models.user.User.email == email).first()

def create_user(db: Session, email: str, password: str):
    """新規ユーザーを作成する"""
    # ユーザーが既に存在するかチェック
    db_user = get_user_by_email(db, email=email)
    if db_user:
        return None # 本来はHTTPExceptionなどを返す

    # パスワードをハッシュ化
    hashed_password = auth.get_password_hash(password)
    
    # 新しいUserオブジェクトを作成
    new_user = models.user.User(email=email)
    
    # 新しいUserCredentialオブジェクトを作成し、Userに紐付ける
    new_credential = models.user.UserCredential(
        hashed_password=hashed_password,
        user=new_user
    )

    db.add(new_user)
    db.add(new_credential)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    """ユーザーを認証する"""
    user = get_user_by_email(db, email)
    
    # ユーザーが存在しない、またはアクティブでない場合は失敗
    if not user: # or not user.is_active:
        return None
        
    # パスワードを検証
    if not auth.verify_password(password, user.credential.hashed_password):
        return None
    
    return user