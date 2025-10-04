from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from dotenv import load_dotenv
import os

# "templates"ディレクトリをテンプレートとして設定
templates = Jinja2Templates(directory="templates/html")

from api.routers import auth, user
# from api.routers.secure import statistics
from api.routers.secure import simple_statistics
from api.routers.secure import user as secure_user
from api.routers.secure import schedule
from api.routers.secure import category
from api.routers.secure import eco_action
from api.routers.secure import eco_action_achievement

import core.events  # 追加：イベントリスナーをインポートして登録

from db.admin import setup_admin, authentication_backend  # 追加したadmin.pyをimportしてFastAPIアプリに登録

load_dotenv()  # .envファイルの内容を環境変数に読み込む

app = FastAPI()

# "static"ディレクトリを "/static" パスでマウント
app.mount("/static", StaticFiles(directory="templates"), name="static")

# Nginxのようなリバースプロキシを信頼し、
# X-Forwarded-Protoヘッダーなどを解釈するように設定します。
# trusted_hosts="*"は、どのプロキシからでもヘッダーを信頼することを意味します。
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# app.add_middleware(
#     SessionMiddleware,
#     secret_key=os.getenv("ADMIN_KEY")
# )

# # Googleからの認証コールバックを受け取るルートを追加
# app.add_route("/admin/auth/google", route=authentication_backend.authenticate, methods=["GET"])

app.include_router(user.router)
app.include_router(secure_user.router)
app.include_router(auth.router)
# app.include_router(statistics.router)
app.include_router(simple_statistics.router)
app.include_router(schedule.router)
app.include_router(category.router)
app.include_router(eco_action.router)
app.include_router(eco_action_achievement.router)

setup_admin(app)


@app.get("/")
def read_root():
    return {"message": "Hello, Docker World!"}