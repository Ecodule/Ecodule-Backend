from fastapi import FastAPI
from sqladmin import Admin, ModelView
import os
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
load_dotenv()  # .envファイルの内容を環境変数に読み

from db.session import engine

# 管理画面に表示したいモデルをインポート
from models.category import Category
from models.eco_action import EcoAction

# GoogleのクライアントIDとシークレットを環境変数などから取得
GOOGLE_CLIENT_ID = os.getenv("ADMIN_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("ADMIN_CLIENT_SECRET")

# ログインを許可する管理者のメールアドレスをリスト化
ADMIN_EMAILS = ["ecodule@gmail.com"]

# OAuthのセットアップ
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        # ユーザーをGoogleの認証ページにリダイレクトさせる
        redirect_uri = request.url_for("admin:auth", provider="google")
        return await oauth.google.authorize_redirect(request, str(redirect_uri))

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        # Googleからのコールバックを処理し、ユーザートークンを取得
        token = await oauth.google.authorize_access_token(request)
        if not token:
            return False

        # トークンを使ってユーザー情報を取得
        user_info, _ = await oauth.google.get_profile(token)
        
        # ★★★ ここで管理者かどうかをチェック ★★★
        if user_info and user_info.get("email") in ADMIN_EMAILS:
            request.session.update({"user": user_info.get("email")})
            return True
            
        return False

authentication_backend = AdminAuth(secret_key=os.getenv("ADMIN_KEY"))

# 管理画面のセットアップ関数
def setup_admin(app: FastAPI):
    # 1. 管理画面のメインインスタンスを作成
    admin = Admin(
        app=app,
        engine=engine,
        # authentication_backend=authentication_backend,
    )

    # 2. 各モデルをどのように管理画面に表示するかを定義
    class CategoryAdmin(ModelView, model=Category):
        # 管理画面の一覧に表示するカラム
        column_list = [
            Category.category_id,
            Category.category_name
        ]
        # 管理画面の名称
        name_plural = "Categories"

    class EcoActionAdmin(ModelView, model=EcoAction):
        # 一覧に表示するカラム。関連先のカテゴリ名も表示可能
        column_list = [
            EcoAction.eco_action_id,
            EcoAction.content,
            EcoAction.money_saved,
            EcoAction.co2_reduction,
            EcoAction.category  # relationship名で関連先の情報を表示
        ]
        # 管理画面の名称
        name_plural = "Eco Actions"

    # 3. 定義したビューを管理画面に登録
    admin.add_view(CategoryAdmin)
    admin.add_view(EcoActionAdmin)