import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.session import Base, get_db

# テスト用のデータベース設定

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" # インメモリのSQLiteを使用

engine = create_engine(
  SQLALCHEMY_DATABASE_URL,
  connect_args={"check_same_thread": False}, # SQLiteで必要
  poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- テスト用のDBセッションでDIをオーバーライド ---
def override_get_db():
  """テスト用のDBセッションを提供する"""
  try:
    db = TestingSessionLocal()
    yield db
  finally:
    db.close()
        
# get_db依存関係をテスト用の物に置き換える
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
  # テストケースごとにテーブルを初期化し、セッションを提供するfixture
  Base.metadata.create_all(bind=engine) # テーブル作成
  yield TestingSessionLocal() # セッションを提供
  Base.metadata.drop_all(bind=engine) # テーブル削除
    
@pytest.fixture(scope="module")
def client():
  # テスト用のAPIクライアントを提供するfixture
  with TestClient(app) as c:
    yield c
