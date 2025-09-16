from fastapi import FastAPI
from sqladmin import Admin, ModelView

from db.session import engine

# 管理画面に表示したいモデルをインポート
from models.category import Category
from models.eco_action import EcoAction

# 管理画面のセットアップ関数
def setup_admin(app: FastAPI):
    # 1. 管理画面のメインインスタンスを作成
    admin = Admin(app=app, engine=engine)

    # 2. 各モデルをどのように管理画面に表示するかを定義
    class CategoryAdmin(ModelView, model=Category):
        # 管理画面の一覧に表示するカラム
        column_list = [
            Category.id,
            Category.category_name
        ]
        # 管理画面の名称
        name_plural = "Categories"
        # デフォルトのソート順を定義します。
        column_default_sort = ("id", True) # idの降順でソート

    class EcoActionAdmin(ModelView, model=EcoAction):
        # 一覧に表示するカラム。関連先のカテゴリ名も表示可能
        column_list = [
            EcoAction.id,
            EcoAction.content,
            EcoAction.money_saved,
            EcoAction.co2_reduction,
            EcoAction.category  # relationship名で関連先の情報を表示
        ]
        # 管理画面の名称
        name_plural = "Eco Actions"

        # デフォルトのソート順を定義します。
        column_default_sort = ("id", True) # idの降順でソート

    # 3. 定義したビューを管理画面に登録
    admin.add_view(CategoryAdmin)
    admin.add_view(EcoActionAdmin)