import os.path
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- 設定項目 ---

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


def create_message(sender, to, subject, message_text):
    """
    MIMETextオブジェクトを作成し、Base64エンコードします。
    """
    message = MIMEText(message_text, "html") # HTML形式で送信
    message["to"] = to
    message["from"] = f"{SENDER_NAME} <{sender}>"
    message["subject"] = subject
    
    # Gmail APIはBase64エンコードされた文字列を要求します
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_message(service, user_id, message):
    """
    Gmail APIを使ってメールを送信します。
    """
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        print(f"メッセージが送信されました。Message ID: {message['id']}")
        return message
    except HttpError as error:
        print(f"エラーが発生しました: {error}")
        return None

# --- メインの処理 ---
if __name__ == "__main__":
    # 1. Gmailサービスを取得
    service = get_gmail_service()
    
    # 2. 送信するメールの内容を作成
    recipient_email = "miyazato2929@gmail.com" # 宛先
    verification_url = "https://example.com/verify?token=dummy-token" # ダミーのURL
    
    subject = f"【{SENDER_NAME}】メールアドレスの確認"
    body = f"""
    <html><body>
        <h2>ご登録ありがとうございます！</h2>
        <p>アカウントを有効にするには、以下のボタンをクリックしてください。</p>
        <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 14px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 8px;">
           メールアドレスを認証する
        </a>
    </body></html>
    """
    
    # 3. メッセージオブジェクトを作成
    message_to_send = create_message(SENDER_EMAIL, recipient_email, subject, body)
    
    # 4. メールを送信 (user_id='me'は認証済みユーザー自身を指します)
    send_message(service, "me", message_to_send)