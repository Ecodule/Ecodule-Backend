# test_auth.py

from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

# crudやauthモジュールもテストで利用する可能性がある
import crud.user, schemas, core.email_verification
from tests.auth_helper import user_create_and_login, setup_mock, GOOGLE_ID

# --- テストケース ---

def test_google_auth_new_user(client, mocker, db_session: Session):
    """正常系: Google認証で新規ユーザーが作成されるケース"""
    # モックの設定: id_token.verify_oauth2_token が返す値を定義
    mock_user_info = setup_mock(mocker)

    # APIをコール
    response = client.post("/auth/google", json={"token": "dummy_google_token"})

    # アサーション（結果の検証）
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == mock_user_info["email"]
    assert data["name"] == mock_user_info["name"]
    assert "access_token" in data
    assert data["message"] == "Successfully authenticated"


def test_google_auth_existing_user(client, mocker, db_session: Session):
    """正常系: 既存のGoogle連携済みユーザーがログインするケース"""
    # 1. 事前にDBにユーザーを作成しておく
    google_id = GOOGLE_ID
    email = "existing.user@example.com"
    crud.user.create_user(db=db_session, email=email, google_id=google_id)

    setup_mock(mocker, email=email, name="Existing User")

    # APIをコール
    response = client.post("/auth/google", json={"token": "another_dummy_token"})

    # アサーション
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["name"] == "Existing User"


def test_google_auth_link_to_existing_email(client, mocker, db_session: Session):
    """正常系: 既存のメールアドレスにGoogle IDを連携するケース"""
    # 1. Google IDが空の状態でユーザーを作成
    login_data = {"username": "email.only@example.com", "password": "password123"}

    new_google_id = GOOGLE_ID
    user = crud.user.create_user(db=db_session, email=login_data["username"], password=login_data["password"], google_id=None)
    assert user.credential.google_id is None # 事前確認

    # モックの設定
    setup_mock(mocker, email=login_data["username"])

    jwt_token = user_create_and_login(client, email=login_data["username"], password=login_data["password"])

    # 認証ヘッダーを設定
    auth_headers = { "Authorization": f"Bearer {jwt_token}" }
    # APIをコール
    response = client.patch("/users/me/link-google", json={"token": "linking_dummy_token"}, headers=auth_headers)

    # アサーション
    assert response.status_code == 200
    # DBの状態が更新されたことを確認
    db_session.refresh(user)
    assert user.credential.google_id == new_google_id


def test_google_auth_invalid_token(client, mocker, db_session: Session):
    """異常系: 無効なトークンが送られてきたケース"""
    # モックの設定: verify_oauth2_token が ValueError を発生させるようにする
    error_message = "Token is expired or invalid"
    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=ValueError(error_message)
    )

    # APIをコール
    response = client.post("/auth/google", json={"token": "invalid_token"})

    # アサーション
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == f"Invalid token: {error_message}"