import uuid
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UUID, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

# 以前作成した db/session.py からBaseをインポート
from db.session import Base

class User(Base):
    """ユーザーの基本情報モデル"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # UserとUserCredentialを1対1で関連付ける
    credential = relationship("UserCredential", back_populates="user", uselist=False)
    refresh_token = relationship("RefreshToken", back_populates="user", uselist=False)

class UserCredential(Base):
    """ユーザーの認証情報モデル"""
    __tablename__ = "user_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 認証情報の保存
    hashed_password = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)

    # パスワードかgoogle_idどちらかが保存されている必要がある
    __table_args__ = (
        CheckConstraint(
            'hashed_password IS NOT NULL OR google_id IS NOT NULL',
            name="ck_user_auth_method"
        ),
    )

    # UserCredentialからUserを逆引きできるように設定
    user = relationship("User", back_populates="credential")

class RefreshToken(Base):
    """リフレッシュトークンモデル"""
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_token")