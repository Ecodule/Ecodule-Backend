# エコジュールバックエンド

## ディレクトリ構成（予定）
```
your-project-name/
├── app/                      # 👈 メインのソースコードを格納するディレクトリ
│   ├── __init__.py
│   ├── api/                  # 👈 APIエンドポイント（ルーター）を定義
│   │   ├── __init__.py
│   │   ├── deps.py           # 共通の依存性注入（例: ユーザー認証）
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── users.py      # ユーザー関連API (/users, /auth/token)
│   │       └── app_data.py   # アプリデータ関連API (/data)
│   │
│   ├── core/                 # 👈 プロジェクトのコア設定
│   │   ├── __init__.py
│   │   └── config.py         # 環境変数、秘密鍵などの設定管理
│   │
│   ├── crud/                 # 👈 DB操作（CRUD）のロジック
│   │   ├── __init__.py
│   │   ├── base.py           # 基本的なCRUD操作の基底クラス
│   │   └── crud_user.py      # usersテーブルに対する操作
│   │
│   ├── db/                   # 👈 データベース接続関連
│   │   ├── __init__.py
│   │   └── session.py        # DBセッションの生成・管理
│   │
│   ├── models/               # 👈 SQLAlchemyのデータベースモデル
│   │   ├── __init__.py
│   │   └── user.py           # usersテーブルのモデル定義
│   │
│   ├── schemas/              # 👈 Pydanticのデータ検証スキーマ
│   │   ├── __init__.py
│   │   └── user.py           # APIで受け渡しするデータの型定義
│   │
│   ├── services/             # 👈 軽い演算などのビジネスロジック
│   │   ├── __init__.py
│   │   └── statistics.py     # 統計計算などのサービス
│   │
│   ├── tasks/                # 👈 Celeryの非同期タスク
│   │   ├── __init__.py
│   │   └── process_data.py   # 時間のかかるデータ処理タスク
│   │
│   ├── main.py               # 👈 FastAPIアプリケーションのエントリーポイント
│   └── worker.py             # 👈 Celeryワーカーのエントリーポイント
│
├── tests/                    # 👈 自動テストコード
│
├── .env                      # 環境変数を記述（.gitignoreに必ず追加）
├── .gitignore                # Gitの追跡から除外するファイルを設定
├── Dockerfile                # アプリケーションのコンテナイメージを定義
├── docker-compose.yml        # Dockerコンテナ群（アプリ、DB、Redis）を起動
├── pyproject.toml            # [推奨] 依存パッケージ管理 (or requirements.txt)
└── README.md                 # プロジェクトの説明書
```

## docker環境下に適応したモジュールインポート
- モジュールをインポートする際のパスはsrc以下から記述してください
- 例: `from db.session`, `from models.user`