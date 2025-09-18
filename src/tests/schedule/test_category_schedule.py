import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from schemas.schedule import ScheduleCreate
from models.schedule import Schedule as ScheduleModel
from models.category import Category as CategoryModel
from models.eco_action_achievement import EcoActionAchievement as EcoActionAchievementModel
from models.eco_action import EcoAction as EcoActionModel
from tests.auth_helper import user_login_only

def test_get_user_schedules(
        client, 
        db_session: Session, 
        test_user, 
        authorization_header, 
        seed_categories, 
        seed_eco_actions
    ):
    """
    カテゴリ付きのスケジュールを作成すると、関連するEcoActionAchievementが自動生成されることを確認
    """
    # Arrange: テストの準備
    # "通勤・通学"カテゴリを取得 (このカテゴリには2つのEcoActionが紐づいている想定)
    target_category = db_session.query(CategoryModel).filter(CategoryModel.category_name == '通勤・通学').first()
    assert target_category is not None

    # スケジュール作成用のデータ
    schedule_data = ScheduleCreate(
        title="週次ミーティング",
        all_day=False,
        start_schedule="2025-10-01T10:00:00",
        end_schedule="2025-10-01T11:00:00",
        category_id=target_category.category_id
    )

    # Act: スケジュール作成APIを呼び出す
    response = client.post(
        f"/users/{test_user.id}/schedules/", 
        headers=authorization_header,
        json=schedule_data.model_dump(mode='json')
    )

    # Assert: 検証
    assert response.status_code == 201 # 201 Created
    created_schedule = response.json()
    new_schedule_id = uuid.UUID(created_schedule["schedule_id"])

    # --- ここからが重要 ---
    # 副作用としてEcoActionAchievementが作成されたかをDBで直接確認
    linked_achievements = db_session.query(EcoActionAchievementModel).filter(
        EcoActionAchievementModel.schedule_id == new_schedule_id
    ).all()

    # "通勤・通学"カテゴリには2つのEcoActionをseedしたので、2つの達成記録が作られているはず
    assert len(linked_achievements) == 2

    # 作成された達成記録の内容を確認
    action_contents = {achievement.eco_action.content for achievement in linked_achievements}
    expected_contents = {"自転車で通勤する", "一駅手前で降りて歩く"}
    assert action_contents == expected_contents
    
    # is_completedはFalseで作成される想定
    assert not linked_achievements[0].is_completed 
    assert not linked_achievements[1].is_completed

def test_delete_schedule_with_achievements(
        client,
        db_session: Session,
        test_user,
        authorization_header,
        seed_categories,
        seed_eco_actions
):
    """
    スケジュールを削除すると、関連するEcoActionAchievementも削除されることを確認
    """
    # Arrange: テストの準備
    # 1. まず、EcoActionAchievementが紐づくスケジュールを作成する
    # ----------------------------------------------------------------
    target_category = db_session.query(CategoryModel).filter(CategoryModel.category_name == '通勤・通学').first()
    assert target_category is not None

    schedule_data = ScheduleCreate(
        title="削除対象のミーティング",
        all_day=False,
        start_schedule="2025-11-01T10:00:00",
        end_schedule="2025-11-01T11:00:00",
        category_id=target_category.category_id
    )

    # スケジュール作成APIを呼び出し
    create_response = client.post(
        f"/users/{test_user.id}/schedules/",
        headers=authorization_header,
        json=schedule_data.model_dump(mode='json')
    )
    assert create_response.status_code == 201
    created_schedule = create_response.json()
    schedule_id_to_delete = uuid.UUID(created_schedule["schedule_id"])

    # 念のため、この時点でEcoActionAchievementが作成されていることを確認
    achievements_before_delete = db_session.query(EcoActionAchievementModel).filter(
        EcoActionAchievementModel.schedule_id == schedule_id_to_delete
    ).all()
    assert len(achievements_before_delete) == 2 # "通勤・通学"カテゴリには2つのEcoActionが紐づいている想定

    # Act: スケジュール削除APIを呼び出す
    # 2. 作成したスケジュールを削除する
    # ----------------------------------------------------------------
    delete_response = client.delete(
        f"/schedules/{schedule_id_to_delete}",
        headers=authorization_header
    )

    # Assert: 検証
    # 3. スケジュールと関連データが削除されたか確認する
    # ----------------------------------------------------------------
    # レスポンスコードが成功(204 No Content)したか確認
    assert delete_response.status_code == 204

    # DBを直接確認し、EcoActionAchievementが削除されているか検証
    achievements_after_delete = db_session.query(EcoActionAchievementModel).filter(
        EcoActionAchievementModel.schedule_id == schedule_id_to_delete
    ).count()
    assert achievements_after_delete == 0

    # 念のため、スケジュール本体も削除されていることを確認
    deleted_schedule_from_db = db_session.query(ScheduleModel).filter(
        ScheduleModel.schedule_id == schedule_id_to_delete
    ).first()
    assert deleted_schedule_from_db is None