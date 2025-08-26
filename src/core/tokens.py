from itsdangerous import URLSafeTimedSerializer
from config import settings

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