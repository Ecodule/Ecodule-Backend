import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from schemas.schedule import ScheduleCreate
from models.schedule import Schedule as ScheduleModel
from tests.auth_helper import user_login_only

def test_get_user_schedules(client, db_session: Session, test_user, authorization_header, seed_categories):
    """特定ユーザーのスケジュール一覧が取得できることを確認"""
    response = client.get(f"/categories", headers=authorization_header)
    assert response.status_code == 200
    categories = response.json()

    assert len(categories) > 0
    
    first_category = categories[0]["category_id"]
    second_category = categories[1]["category_id"]
    third_category = categories[2]["category_id"]

    user_id = test_user.id

    # Arrange: テストデータを3件作成
    schedule1 = ScheduleCreate(title="タスク1", user_id=user_id, all_day=True, category_id=first_category)
    schedule1 = ScheduleModel(**schedule1.model_dump(), user_id=user_id)
    schedule2 = ScheduleCreate(title="タスク2", user_id=user_id, all_day=True, category_id=second_category)
    schedule2 = ScheduleModel(**schedule2.model_dump(), user_id=user_id)
    schedule3 = ScheduleCreate(title="タスク3", user_id=user_id, all_day=True, category_id=third_category)
    schedule3 = ScheduleModel(**schedule3.model_dump(), user_id=user_id)
    db_session.add_all([schedule1, schedule2, schedule3])
    db_session.commit()

    # Act
    response = client.get(f"/users/{user_id}/schedules", headers=authorization_header)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["title"] == "タスク1"
    print(data)

    assert data[0]["category_id"] == first_category
    assert data[1]["category_id"] == second_category
    assert data[2]["category_id"] == third_category
    assert data[0]["category"]["category_name"] == "ゴミ出し"
    assert data[1]["category"]["category_name"] == "通勤・通学"
    assert data[2]["category"]["category_name"] == "外出"