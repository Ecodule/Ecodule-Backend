# Dockerfile

# 1. ベースとなる公式Pythonイメージを指定
FROM python:3.10-slim

# 2. コンテナ内での作業ディレクトリを設定
WORKDIR /app

# 3. 依存ライブラリの定義ファイルをコンテナにコピー
COPY ./requirements.txt /app/requirements.txt

# 4. 依存ライブラリをインストール
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# 5. アプリケーションのソースコードをコンテナにコピー
COPY . /app

# 6. コンテナ起動時にこのコマンドを実行する
#    Uvicornサーバーを起動し、外部からのアクセスを許可する
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]