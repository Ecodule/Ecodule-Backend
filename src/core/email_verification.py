from config import settings
import os.path
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from itsdangerous import URLSafeTimedSerializer

# このスコープは、メールの送信権限を要求することを意味します。
# 変更する場合は、token.jsonを削除してください。
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
SENDER_EMAIL = "ecodule@gmail.com" # あなたのGmailアドレス
SENDER_NAME = "Ecodule"

# ----------------

def get_gmail_service():
    """
    Gmail APIサービスへの認証とビルドを行います。
    初回実行時はブラウザで認証が必要です。
    """
    creds = None
    # token.jsonファイルは、ユーザーのアクセストークンとリフレッシュトークンを保存します。
    # 認証フローが初めて完了したときに自動的に作成されます。
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # 有効な認証情報がない場合は、ユーザーにログインさせます。
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "../credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # 次回のために認証情報を保存します
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            
    return build("gmail", "v1", credentials=creds)


def create_message(sender, to, subject, verification_url):
    """
    MIMETextオブジェクトを作成し、Base64エンコードします。
    """

    # メール本文（HTML形式）
    message_text = f"""
    <html><body>
        <h2>ご登録ありがとうございます！</h2>
        <p>アカウントを有効にするには、以下のボタンをクリックしてください。</p>
        <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 14px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 8px;">
           メールアドレスを認証する
        </a>
    </body></html>
    """

    message = MIMEText(message_text, "html") # HTML形式で送信
    message["to"] = to
    message["from"] = f"{SENDER_NAME} <{sender}>"
    message["subject"] = subject
    
    # Gmail APIはBase64エンコードされた文字列を要求します
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_message(user_email: str):
    """
    Gmail APIを使ってメールを送信します。
    """
    # Gmail APIサービスを取得(準備)
    service = get_gmail_service()

    subject = "メールアドレスの確認"
    verification_token = generate_verification_token(user_email)

    # 確認用URLを生成、あとで環境変数にする
    verification_url = f"http://localhost:8000/auth/verify-email/?token={verification_token}"
    message = create_message(SENDER_EMAIL, user_email, subject, verification_url)

    try:
        message = (
            # meは認証済みユーザーであることを示す。
            service.users().messages().send(userId="me", body=message).execute()
        )
        print(f"メッセージが送信されました。Message ID: {message['id']}")
        return message
    except HttpError as error:
        print(f"エラーが発生しました: {error}")
        return None
    
# -----------------------------------

def generate_verification_token(email: str) -> str:
  # メールアドレス確認用のセキュアなトークンを生成する
  serializer = URLSafeTimedSerializer(settings.EMAIL_VERIFICATION_SECRET_KEY)
  return serializer.dumps(email, salt='email-verification-salt')

def verify_verification_token(token: str) -> str | None:
  # メールアドレス確認トークンを検証し、メールアドレスを返す
  serializer = URLSafeTimedSerializer(settings.EMAIL_VERIFICATION_SECRET_KEY)
  try:
    email = serializer.loads(
      token,
      salt='email-verification-salt',
      max_age=3600 # トークンの有効期限を秒で指定
    )
    return email
  except Exception:
    return None
  
