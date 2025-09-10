# src/tests/auth_helper.py
from sqlalchemy.orm import Session

import core.email_verification
from schemas.user import UserResponse
import crud.user

# 一般的な認証で使用するヘルパー関数と定数

def user_create_and_login(client, email: str, password: str) -> str:
    """ユーザーを作成し、ログインしてJWTトークンを取得するヘルパー関数"""
    user_input = {"email": email, "password": password}
    login_data = {"username": email, "password": password}
    
    client.post("/users/create", json=user_input)

    # メールアドレスの検証トークンを生成
    token = core.email_verification.generate_verification_token(email)
    response = client.get(f"/auth/verify-email/?token={token}")

    # ログインしてトークンを取得
    response = client.post("/auth/login", data=login_data)
    jwt_token = response.json()["access_token"]
    
    return jwt_token

def user_create_and_get_user(client, db: Session, email: str, password: str) -> UserResponse:
    """ユーザーを作成するヘルパー関数"""
    user_input = {"email": email, "password": password}
    client.post("/users/create", json=user_input)

    # メールアドレスの検証
    token = core.email_verification.generate_verification_token(email)
    client.get(f"/auth/verify-email/?token={token}")

    user_data = crud.user.get_user_by_email(db, email=email)

    return user_data

def user_login_only(client, email: str, password: str) -> str:
    """既存ユーザーでログインしてJWTトークンを取得するヘルパー関数"""
    login_data = {"username": email, "password": password}
    response = client.post("/auth/login", data=login_data)
    jwt_token = response.json()["access_token"]
    
    return jwt_token

# google認証のテストで使用するヘルパー関数と定数

GOOGLE_ID = "test_google_id_123"

class mock_user_info(TypeError):
    sub: str
    email: str
    name: str

def setup_mock(mocker, email="new.user@example.com", name="New User") -> mock_user_info:
    # モックの設定: id_token.verify_oauth2_token が返す値を定義
    mock_user_info = {
        "sub": "test_google_id_123",
        "email": email,
        "name": name
    }
    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value=mock_user_info
    )

    return mock_user_info