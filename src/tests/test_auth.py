# tests/test_auth.py

from fastapi import status
from sqlalchemy.orm import Session
import crud, schemas

def test_password_hashing(db_session: Session):
    # パスワードのハッシュ化と検証が正しく機能するかをテスト
    from auth import verify_password, get_password_hash

    password = "testpassword123!"
    hashed_password = get_password_hash(password)

    assert hashed_password != password # ハッシュ化されているか
    assert verify_password(password, hashed_password) # 検証が成功するか
    assert not verify_password("wrongpassword", hashed_password) # 間違ったパスワードで失敗するか

def test_user_authentication(client, db_session: Session):
    # ユーザー認証とトークン発行のエンドポイントをテスト
    # テスト用のユーザーを作成
    test_email = "test@example.com"
    test_password = "testpassword123!"
    user_in = {"email": test_email, "password": test_password}
    login_data = {"username": test_email, "password": test_password}
    response_user_create = client.post("/users/create", json=user_in)
    
    # 1. ユーザー作成が成功することを確認
    assert response_user_create.status_code == status.HTTP_201_CREATED

    # 2. 作成したユーザーがデータベースに存在することを確認
    user_from_email = crud.user.get_user_by_email(db_session, email=test_email)
    assert user_from_email is not None

    # ログインしてトークンを取得
    response = client.post("/auth/login", data=login_data)
    
    # 3. ログインが成功して、アクセストークンが返されることを確認
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"

    # 間違ったパスワードでログインを試みる
    wrong_login_data = {"username": test_email, "password": "wrongpassword"}
    response = client.post("/auth/login", data=wrong_login_data)
    
    # 4. 間違ったパスワードでログインが失敗することを確認
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, db_session: Session):
    # 保護されたエンドポイントへのアクセスをテスト
    # 1. テスト用のユーザーとトークンを準備
    test_email = "test_me@example.com"
    test_password = "passwordforme!"
    user_in = schemas.user.UserCreate(email=test_email, password=test_password)
    crud.user.create_user(db_session, email=user_in.email, password=user_in.password)
    
    login_data = {"username": test_email, "password": test_password}
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. トークンを使って保護されたエンドポイントにアクセス
    response = client.get("/users/me/", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    current_user = response.json()
    assert current_user["email"] == test_email

    # 3. 不正なトークンでアクセスに失敗
    wrong_headers = {"Authorization": "Bearer wrongtoken"}
    response = client.get("/users/me/", headers=wrong_headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED