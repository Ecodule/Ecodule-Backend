import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.session import Base, get_db
from models.category import Category
from tests.auth_helper import user_create_and_get_user
from models.user import User as UserModel

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

@pytest.fixture(scope="function")
def test_user(db_session) -> UserModel:
  """テスト用のユーザーを作成し、DBに保存するfixture"""
  email = "test@example.com"
  password = "password123"

  return user_create_and_get_user(client=TestClient(app), db=db_session, email=email, password=password)

@pytest.fixture(scope="function")
def authorization_header(client, test_user):
  """認証ヘッダーを提供するfixture"""
  token = client.post("/auth/login", data={"username": test_user.email, "password": "password123"}).json()["access_token"]
  return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def seed_categories(db_session):
    """
    テスト用のカテゴリーデータをDBに投入し、後で削除するfixture
    """
    initial_categories = [
        Category(id=uuid.uuid4(), category_name='ゴミ出し'),
        Category(id=uuid.uuid4(), category_name='通勤・通学'),
        Category(id=uuid.uuid4(), category_name='外出'),
        Category(id=uuid.uuid4(), category_name='買い物'),
    ]
    db_session.add_all(initial_categories)
    db_session.commit()
    
    yield initial_categories # テスト実行
    
    # テスト終了後にデータをクリーンアップ
    for category in initial_categories:
        db_session.delete(category)
    db_session.commit()