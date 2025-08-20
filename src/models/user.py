import uuid
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UUID
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

class UserCredential(Base):
    """ユーザーの認証情報モデル"""
    __tablename__ = "user_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    hashed_password = Column(String, nullable=False)

    # UserCredentialからUserを逆引きできるように設定
    user = relationship("User", back_populates="credential")