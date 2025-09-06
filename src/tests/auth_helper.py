# src/tests/auth_helper.py
import core.email_verification

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