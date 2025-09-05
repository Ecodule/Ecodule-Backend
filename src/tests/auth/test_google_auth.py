# test_auth.py

from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

# main.pyからappインスタンスをインポート
from main import app 
# crudやauthモジュールもテストで利用する可能性がある
import crud, schemas 
# DBセッションの依存関係をオーバーライドするために必要
from db.session import get_db, Base, engine

# クリーンな状態のDBを用意
# 一時的になコメントアウト
# Base.metadata.create_all(bind=engine)

# FastAPIアプリの依存関係をテスト用DBに差し替える
# app.dependency_overrides[get_db] = override_get_db
 
client = TestClient(app)

# --- テストケース ---

def test_google_auth_new_user(mocker):
    """正常系: Google認証で新規ユーザーが作成されるケース"""
    # モックの設定: id_token.verify_oauth2_token が返す値を定義
    mock_user_info = {
        "sub": "unique_google_id_123",
        "email": "new.user@example.com",
        "name": "New User"
    }
    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value=mock_user_info
    )

    # APIをコール
    response = client.post("/auth/google", json={"token": "dummy_google_token"})

    # アサーション（結果の検証）
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == mock_user_info["email"]
    assert data["name"] == mock_user_info["name"]
    assert "access_token" in data
    assert data["message"] == "Successfully authenticated"


def test_google_auth_existing_user(mocker, db_session):
    """正常系: 既存のGoogle連携済みユーザーがログインするケース"""
    # 1. 事前にDBにユーザーを作成しておく
    google_id = "already_exists_google_id_456"
    email = "existing.user@example.com"
    crud.user.create_user(db=db_session, email=email, google_id=google_id)
    
    # モックの設定
    mock_user_info = {
        "sub": google_id,
        "email": email,
        "name": "Existing User"
    }
    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value=mock_user_info
    )

    # APIをコール
    response = client.post("/auth/google", json={"token": "another_dummy_token"})

    # アサーション
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email


def test_google_auth_link_to_existing_email(mocker, db_session):
    """正常系: 既存のメールアドレスにGoogle IDを連携するケース"""
    # 1. Google IDが空の状態でユーザーを作成
    email = "email.only@example.com"
    new_google_id = "newly_linked_google_id_789"
    user = crud.user.create_user(db=db_session, email=email, google_id=None)
    assert user.credential.google_id is None # 事前確認

    # モックの設定
    mock_user_info = {
        "sub": new_google_id,
        "email": email,
        "name": "Link User"
    }
    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value=mock_user_info
    )

    # APIをコール
    response = client.post("/auth/google", json={"token": "linking_dummy_token"})
    
    # アサーション
    assert response.status_code == 200
    # DBの状態が更新されたことを確認
    db_session.refresh(user)
    assert user.credential.google_id == new_google_id


def test_google_auth_invalid_token(mocker):
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