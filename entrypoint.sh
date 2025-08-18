#!/bin/sh

# alembic upgrade head コマンドで、データベースのマイグレーションを最新の状態に更新する
echo "Running database migrations..."
alembic upgrade head

# その後、DockerfileのCMDで指定されたコマンドを実行する
# (例: uvicorn main:app --host 0.0.0.0 --port 8000)
exec "$@"