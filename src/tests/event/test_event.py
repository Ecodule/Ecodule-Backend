from sqlalchemy.orm import Session

# 必要なモデル、CRUD、スキーマをインポート
from models.user import User as UserModel
from models.category import Category as CategoryModel
from models.eco_action import EcoAction as EcoActionModel
from models.schedule import Schedule as ScheduleModel
from models.eco_action_achievement import EcoActionAchievement
from crud.schedule import create_schedule
from schemas.schedule import ScheduleCreate

def test_eco_action_update_triggers_achievement_reconciliation(
    db_session: Session, test_user: UserModel, seed_categories: list
):
    """
    EcoActionを更新すると、SQLAlchemyイベントが発火し、
    全スケジュールのEcoActionAchievementが再計算されることをテストする
    """
    # ===================================================================
    # 1. Arrange: テストのための複雑な初期状態をセットアップ
    # ===================================================================

    # カテゴリを取得
    category_A = next(c for c in seed_categories if c.category_name == '外出')
    category_B = next(c for c in seed_categories if c.category_name == '買い物')

    # EcoActionをセットアップ
    eco_action_1A = EcoActionModel(content="自転車通勤", category_id=category_A.category_id)
    eco_action_2A = EcoActionModel(content="一駅歩く", category_id=category_A.category_id)
    eco_action_3B = EcoActionModel(content="マイバッグ持参", category_id=category_B.category_id)
    db_session.add_all([eco_action_1A, eco_action_2A, eco_action_3B])
    db_session.commit()

    # スケジュールを2つ作成（それぞれ異なるカテゴリに属する）
    # create_scheduleを呼び出すと、紐づく達成記録も自動生成される
    schedule_A = create_schedule(
        db_session,
        ScheduleCreate(
            title="タスク1",
            all_day=False,
            start_schedule="2025-11-01T10:00:00",
            end_schedule="2025-11-01T11:00:00",
            category_id=category_A.category_id
        ),
        user_id=test_user.id,
    )
    schedule_B = create_schedule(
        db_session, 
        ScheduleCreate(
            title="タスク1",
            all_day=False,
            start_schedule="2025-11-01T10:00:00",
            end_schedule="2025-11-01T11:00:00",
            category_id=category_B.category_id
        ),
        user_id=test_user.id
    )

    # --- 初期状態の確認 ---
    # Schedule A には2つの達成記録 (1A, 2A) があるはず
    achievements_A_before = db_session.query(EcoActionAchievement).filter(EcoActionAchievement.schedule_id == schedule_A.schedule_id).all()
    assert len(achievements_A_before) == 2
    
    # Schedule B には1つの達成記録 (3B) があるはず
    achievements_B_before = db_session.query(EcoActionAchievement).filter(EcoActionAchievement.schedule_id == schedule_B.schedule_id).all()
    assert len(achievements_B_before) == 1

    # ===================================================================
    # 2. Act: イベントを発火させる操作を実行
    # ===================================================================
    print("\n>>> Triggering event by updating EcoAction...")
    # EcoAction 2A のカテゴリを A から B に変更する
    eco_action_2A.category_id = category_B.category_id
    db_session.add(eco_action_2A)
    db_session.commit() # このコミットでafter_updateイベントが発火する
    print(">>> Event triggered and processed.")


    # ===================================================================
    # 3. Assert: 副作用としてデータが正しく変更されたかを検証
    # ===================================================================

    # --- Schedule A の達成記録を再確認 ---
    # Category A に属するEcoActionは1Aだけになったので、達成記録は1つに減っているはず
    achievements_A_after = db_session.query(EcoActionAchievement).filter(EcoActionAchievement.schedule_id == schedule_A.schedule_id).all()
    assert len(achievements_A_after) == 1
    assert achievements_A_after[0].eco_action_id == eco_action_1A.eco_action_id

    # --- Schedule B の達成記録を再確認 ---
    # Category B には 3B と 2A(移動してきた) が属するので、達成記録は2つに増えているはず
    achievements_B_after = db_session.query(EcoActionAchievement).filter(EcoActionAchievement.schedule_id == schedule_B.schedule_id).all()
    assert len(achievements_B_after) == 2
    
    # 含まれるeco_actionのIDをセットで比較
    action_ids_in_B = {ach.eco_action_id for ach in achievements_B_after}
    expected_action_ids_in_B = {eco_action_2A.eco_action_id, eco_action_3B.eco_action_id}
    assert action_ids_in_B == expected_action_ids_in_B