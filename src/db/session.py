import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 環境変数からデータベースのURLを取得
DATABASE_URL = os.getenv("DATABASE_URL")

# データベースエンジンを作成
engine = create_engine(DATABASE_URL)

# データベースセッションを作成するためのクラス
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORMモデルのベースクラス
Base = declarative_base()

def get_db():
    """データベースセッションを取得するための依存関係"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()