import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from models.user import User, RefreshToken
import crud.user
import schemas.user
import core.security, core.token
import core.email_verification

# This should be consistent with the user creation in your other test files
TEST_USER_EMAIL = "test_refresh@example.com"
TEST_USER_PASSWORD = "testpassword123"

@pytest.fixture()
def created_user(client: TestClient, db_session: Session) -> User:
    """
    Creates a user, verifies their email, and returns the user object.
    This fixture has a 'module' scope, so it runs once per test file.
    """
    user_in = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    response = client.post("/users/create", json=user_in)
    assert response.status_code == status.HTTP_201_CREATED

    # Verify user's email to make them active
    token = core.email_verification.generate_verification_token(TEST_USER_EMAIL)
    response = client.get(f"/auth/verify-email/?token={token}")
    assert response.status_code == status.HTTP_200_OK
    
    user = crud.user.get_user_by_email(db_session, email=TEST_USER_EMAIL)
    return user

def test_login_returns_both_tokens(client: TestClient, created_user: User, db_session: Session):
    """
    正常系: /auth/login が access_token と refresh_token の両方を返すことを確認
    """
    login_data = {"username": created_user.email, "password": TEST_USER_PASSWORD}
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert "token_type" in tokens
    assert tokens["token_type"] == "bearer"

def test_successful_token_refresh(client: TestClient, db_session: Session, created_user: User):
    """
    正常系: 有効なリフレッシュトークンで新しいアクセストークンを取得できることを確認
    """
    # 1. ログインして初期トークンを取得
    login_data = {"username": created_user.email, "password": TEST_USER_PASSWORD}
    login_response = client.post("/auth/login", data=login_data)
    initial_tokens = login_response.json()
    initial_refresh_token = initial_tokens["refresh_token"]
    initial_access_token = initial_tokens["access_token"]
    
    # 2. リフレッシュエンドポイントをコール
    refresh_response = client.post(
        "/auth/refresh",
        json={
            "email": created_user.email, "refresh_token": initial_refresh_token
        }
    )

    # 3. アサーション
    assert refresh_response.status_code == status.HTTP_200_OK
    new_tokens = refresh_response.json()
    
    assert "access_token" in new_tokens
    assert "token_type" in new_tokens

    # 4. 新しいアクセストークンが有効か確認
    headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    me_response = client.get("/users/me/", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["email"] == created_user.email

def test_refresh_with_invalid_token(client: TestClient, db_session: Session, created_user: User):
    """
    異常系: 無効な形式のリフレッシュトークンで失敗することを確認
    """
    response = client.post(
        "/auth/refresh",
        json={
            "email": created_user.email,
            "refresh_token": "this-is-not-a-valid-token"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid refresh token" in response.json()["detail"]

def test_refresh_with_expired_token(client: TestClient, db_session: Session, created_user: User):
    """
    異常系: 期限切れのリフレッシュトークンで失敗することを確認
    """
    # 1. テスト用にDBに期限切れのトークンを直接作成
    plain_token = core.token.create_refresh_token() # 仮の平文トークン
    hashed_token = core.security.get_refresh_token_hash(plain_token)

    expired_datetime = datetime.now(timezone.utc) - timedelta(days=1)

    db_token = RefreshToken(
        user_id=created_user.id,
        hashed_token=hashed_token,
        expires_at=expired_datetime
    )
    db_session.add(db_token)
    db_session.commit()
    
    # 2. 期限切れトークンでリフレッシュを試みる
    response = client.post(
        "/auth/refresh", 
        json={
            "refresh_token": plain_token,
            "email": created_user.email
        }
    )
    
    # 3. アサーション
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid refresh token" in response.json()["detail"]

def test_refresh_with_revoked_token(client: TestClient, db_session: Session, created_user: User):
    """
    異常系: 失効済みのリフレッシュトークンで失敗することを確認
    """
    # 1. テスト用に失効済みのトークンをDBに直接作成
    plain_token = core.token.create_refresh_token()
    hashed_token = core.security.get_refresh_token_hash(plain_token)

    expires_datetime = datetime.now(timezone.utc) + timedelta(days=30)
    
    db_token = RefreshToken(
        user_id=created_user.id,
        hashed_token=hashed_token,
        expires_at=expires_datetime,
        is_revoked=True  # 失効フラグを立てる
    )
    db_session.add(db_token)
    db_session.commit()
    
    # 2. 失効済みトークンでリフレッシュを試みる
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": plain_token, 
            "email": created_user.email
        }
    )

    # 3. アサーション
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid refresh token" in response.json()["detail"]