import random
from datetime import timedelta
import time
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from db.session import SessionLocal, engine, Base
from models.schedule import Schedule as ScheduleModel
from models.user import User as UserModel
from models.user import UserCredential as UserCredentialModel
from models.user import RefreshToken as RefreshTokenModel
from models.category import Category as CategoryModel
from core.security import get_password_hash

from crud.schedule import create_schedule
from schemas.schedule import ScheduleCreate

# --- 設定 ---
NUM_USERS = 20  # 作成するユーザー数
SCHEDULES_PER_USER = 50  # 1ユーザーあたりに作成するスケジュール数

# Fakerのインスタンスを日本語設定で初期化
fake = Faker('ja_JP')

def wait_for_db():
    """データベースが接続可能になるまで待機する"""
    max_retries = 10
    retry_interval = 5  # 秒
    for i in range(max_retries):
        try:
            # 接続を試みる
            connection = engine.connect()
            connection.close()
            print("✅ データベース接続に成功しました。")
            return
        except OperationalError as e:
            print(f"⏳ データベース接続待機中... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
    print("❌ データベースに接続できませんでした。")
    exit(1)

def generate_data(db: Session):
    """テストデータを生成してデータベースに保存する"""
    print("--- 既存データの削除を開始 ---")
    db.query(ScheduleModel).delete()
    db.query(UserCredentialModel).delete()
    db.query(RefreshTokenModel).delete()
    db.query(UserModel).delete()
    db.commit()
    print("--- 既存データの削除が完了 ---")

    print(f"--- {NUM_USERS}件のユーザー生成を開始 ---")

    for _ in range(NUM_USERS):
        email = fake.unique.email()
        password = "password123"
        verificated_users(db, email, password)

    print(f"--- {NUM_USERS}件のユーザー生成が完了 ---")

    created_users = db.query(UserModel).all()
    user_id = created_users[0].id

    print(f"カテゴリーを選択中...")
    first_category = db.query(CategoryModel).first()

    print(f"--- スケジュール生成を開始 ---")
    for _ in range(SCHEDULES_PER_USER):
        is_all_day = random.choice([True, False])
        start, end = (None, None)

        if not is_all_day:
            start = fake.date_time_between(start_date='-1y', end_date='+1y')
            end = start + timedelta(minutes=random.randint(30, 480))

        # ★★★ 変更点1: Pydanticスキーマオブジェクトを作成 ★★★
        # create_schedule関数が要求するデータ形式に合わせる
        schedule_data = ScheduleCreate(
            title=fake.sentence(nb_words=4),
            description=fake.text(max_nb_chars=100),
            all_day=is_all_day,
            start_schedule=start,
            end_schedule=end,
            category_id=first_category.category_id if first_category else None
        )

        # ★★★ 変更点2: CRUD関数を直接呼び出し ★★★
        create_schedule(db=db, schedule=schedule_data, user_id=user_id)

    print(f"--- スケジュール生成が完了 ---")

    print("ユーザーEmail: " + created_users[0].email)
    print("パスワード: password123")

def verificated_users(db: Session, email: str, password: str) -> UserModel:
    """ユーザーを作成し、関連データも生成する"""
    
    # 1. Userレコードを作成 (まだコミfットしない)
    db_user = UserModel(email=email, is_active=True)
    db.add(db_user)
    db.flush() # IDを確定させるためにDBと一度同期

    # 2. Credentialレコードを作成
    hashed = get_password_hash(password)
    db_credential = UserCredentialModel(user_id=db_user.id, hashed_password=hashed)
    db.add(db_credential)

    # 3. メール認証プロセスを開始
    # verification_service.start_verification(db, user_id=db_user.id)
    print(f"認証プロセスを開始: {email}") # ここではprintで代用

    # 4. 全ての変更をコミット
    db.commit()
    db.refresh(db_user)
    
    return db_user

if __name__ == "__main__":
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        generate_data(db)
        print("\n🎉 テストデータの生成が正常に完了しました！")
    except Exception as e:
        print(f"\n🔥 エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()