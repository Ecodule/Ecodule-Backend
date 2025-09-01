# tests/test_auth.py

from fastapi import status
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import crud.user, schemas.user, core.email_verification

TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

def test_password_hashing(db_session: Session):
    # パスワードのハッシュ化と検証が正しく機能するかをテスト
    from core.auth import verify_password, get_password_hash

    hashed_password = get_password_hash(TEST_USER_PASSWORD)

    assert hashed_password != TEST_USER_PASSWORD # ハッシュ化されているか
    assert verify_password(TEST_USER_PASSWORD, hashed_password) # 検証が成功するか
    assert not verify_password("wrongpassword", hashed_password) # 間違ったパスワードで失敗するか

def test_user_authentication(client, db_session: Session):
    # ユーザー認証とトークン発行のエンドポイントをテスト
    # テスト用のユーザーを作成
    user_in = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    login_data = {"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    response_user_create = client.post("/users/create", json=user_in)
    
    # 1. ユーザー作成が成功することを確認
    assert response_user_create.status_code == status.HTTP_201_CREATED

    # 2. 作成したユーザーがデータベースに存在することを確認
    user_from_email = crud.user.get_user_by_email(db_session, email=TEST_USER_EMAIL)
    assert user_from_email is not None

    # メールアドレスの検証トークンを生成
    token = core.email_verification.generate_verification_token(TEST_USER_EMAIL)
    assert token is not None
    
    response = client.get(f"/verify-email/?token={token}")
    assert response.status_code == status.HTTP_200_OK

    # ログインしてトークンを取得
    response = client.post("/auth/login", data=login_data)
    
    # 3. ログインが成功して、アクセストークンが返されることを確認
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"

    # 間違ったパスワードでログインを試みる
    wrong_login_data = {"username": TEST_USER_EMAIL, "password": "wrongpassword"}
    response = client.post("/auth/login", data=wrong_login_data)
    
    # 4. 間違ったパスワードでログインが失敗することを確認
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, db_session: Session):
    # 保護されたエンドポイントへのアクセスをテスト
    # 1. テスト用のユーザーとトークンを準備
    user_in = schemas.user.UserCreate(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
    crud.user.create_user(db_session, email=user_in.email, password=user_in.password)

    # メールアドレスの検証トークンを生成
    token = core.email_verification.generate_verification_token(TEST_USER_EMAIL)
    response = client.get(f"/verify-email/?token={token}")
    assert response.status_code == status.HTTP_200_OK

    login_data = {"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. トークンを使って保護されたエンドポイントにアクセス
    response = client.get("/users/me/", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    current_user = response.json()
    assert current_user["email"] == TEST_USER_EMAIL

    # 3. 不正なトークンでアクセスに失敗
    wrong_headers = {"Authorization": "Bearer wrongtoken"}
    response = client.get("/users/me/", headers=wrong_headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED