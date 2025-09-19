from datetime import datetime
import uuid
from sqlalchemy.orm import Session

# 必要なモデルとスキーマをインポート
from models.schedule import Schedule as ScheduleModel
from models.user import User as UserModel
from models.eco_action_achievement import EcoActionAchievement

def test_update_achievement_status_success(
    client, db_session: Session, test_user: UserModel, authorization_header: dict,
    seed_categories: list, seed_eco_actions: list
):
    """正常系: 達成記録のステータスをFalseからTrueに正常に更新できることを確認"""
    # Arrange: テストの前提条件をセットアップ
    # -------------------------------------------
    # 1. テスト用のスケジュールを作成
    target_category = next(c for c in seed_categories if c.category_name == '通勤・通学')
    target_eco_action = next(a for a in seed_eco_actions if a.category_id == target_category.category_id)
    
    schedule = ScheduleModel(
        title="Test Schedule",
        user_id=test_user.id,
        category_id=target_category.category_id,
        start_schedule=datetime.fromisoformat("2025-10-01T10:00:00")
    )
    db_session.add(schedule)
    db_session.commit()

    # 2. テスト対象の達成記録を作成 (is_completed=Falseで作成)
    achievement = EcoActionAchievement(
        schedule_id=schedule.schedule_id,
        eco_action_id=target_eco_action.eco_action_id,
        is_completed=False
    )
    db_session.add(achievement)
    db_session.commit()

    # Act: APIエンドポイントを呼び出す
    # -------------------------------------------
    response = client.patch(
        "/achievements/status",
        headers=authorization_header,
        json={
            "schedule_id": str(schedule.schedule_id),
            "eco_action_id": str(target_eco_action.eco_action_id),
            "is_completed": True  # Trueに更新
        },
    )

    # Assert: 結果を検証
    # -------------------------------------------
    assert response.status_code == 200
    data = response.json()
    assert data["is_completed"] is True

    # DBのデータが実際に更新されたことを直接確認
    db_session.refresh(achievement)
    assert achievement.is_completed is True


def test_update_achievement_status_not_found(client, authorization_header):
    """異常系: 存在しない達成記録を更新しようとすると404エラーが返ることを確認"""
    # Arrange
    non_existent_id = str(uuid.uuid4())

    # Act
    response = client.patch(
        "/achievements/status",
        headers=authorization_header,
        json={
            "schedule_id": non_existent_id,
            "eco_action_id": non_existent_id,
            "is_completed": True
        },
    )

    # Assert
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized for this schedule"


def test_update_achievement_status_forbidden(
    client, db_session: Session, another_user: UserModel, authorization_header: dict, 
    seed_categories: list, seed_eco_actions: list
):
    """セキュリティ: 他人の達成記録を更新しようとすると403エラーが返ることを確認"""
    # Arrange: another_userのデータを作成
    # -------------------------------------------
    target_category = seed_categories[0]
    target_eco_action = next(a for a in seed_eco_actions if a.category_id == target_category.category_id)

    schedule_of_another_user = ScheduleModel(
        title="Another User's Schedule", user_id=another_user.id, category_id=target_category.category_id
    )
    db_session.add(schedule_of_another_user)
    db_session.commit()

    # Act: test_userの認証情報で、another_userのスケジュールを更新しようとする
    # -------------------------------------------
    response = client.patch(
        "/achievements/status",
        headers=authorization_header, # test_userのトークン
        json={
            "schedule_id": str(schedule_of_another_user.schedule_id),
            "eco_action_id": str(target_eco_action.eco_action_id),
            "is_completed": True
        },
    )

    # Assert
    # -------------------------------------------
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized for this schedule"