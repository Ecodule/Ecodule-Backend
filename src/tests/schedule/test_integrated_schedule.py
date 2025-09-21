import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from schemas.schedule import ScheduleCreate
from models.schedule import Schedule as ScheduleModel
from tests.auth_helper import user_login_only

# conftest.pyのtest_user fixtureを利用
EMAIL = "test@example.com"
PASSWORD = "password123"

# 上記で設定したclientとtest_userをfixtureとして利用
def test_create_schedule_success(client, test_user, authorization_header):
    """スケジュールの新規作成が成功することを確認"""
    # Arrange: テストデータの準備
    user_id = test_user.id
    schedule_data = {
        "title": "重要な会議",
        "start_schedule": datetime.utcnow().isoformat(),
        "end_schedule": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "all_day": False
    }

    # Act: APIエンドポイントを呼び出し
    response = client.post(f"/users/{user_id}/schedules", json=schedule_data, headers=authorization_header)

    # Assert: 結果を検証
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "重要な会議"

def test_create_schedule_for_unknown_user(client, authorization_header):
    """存在しないユーザーのスケジュールは作成できないことを確認"""
    unknown_user_id = uuid.uuid4()
    schedule_data = {"title": "存在しないユーザーのタスク"}

    response = client.post(f"/users/{unknown_user_id}/schedules", json=schedule_data, headers=authorization_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_get_user_schedules(client, db_session: Session, test_user, authorization_header):
    """特定ユーザーのスケジュール一覧が取得できることを確認"""
    user_id = test_user.id
    # Arrange: テストデータを3件作成
    schedule1 = ScheduleCreate(
        title="タスク1",
        all_day=False,
        start_schedule="2025-11-01T10:00:00",
        end_schedule="2025-11-01T11:00:00",
    )
    schedule1 = ScheduleModel(**schedule1.model_dump(), user_id=user_id)

    schedule2 = ScheduleCreate(
        title="タスク2",
        all_day=False,
        start_schedule="2025-11-01T10:00:00",
        end_schedule="2025-11-01T11:00:00",
    )
    schedule2 = ScheduleModel(**schedule2.model_dump(), user_id=user_id)

    schedule3 = ScheduleCreate(
        title="タスク3",
        all_day=False,
        start_schedule="2025-11-01T10:00:00",
        end_schedule="2025-11-01T11:00:00",
    )
    schedule3 = ScheduleModel(**schedule3.model_dump(), user_id=user_id)

    db_session.add(schedule1)
    db_session.add(schedule2)
    db_session.add(schedule3)
    db_session.commit()

    # Act
    response = client.get(f"/users/{user_id}/schedules", headers=authorization_header)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["title"] == "タスク1"

def test_get_single_schedule(client, db_session: Session, test_user, authorization_header):
    """単一のスケジュールがIDで取得できることを確認"""
    schedule = ScheduleCreate(
        title="取得テスト",
        all_day=False,
        start_schedule="2025-11-01T10:00:00",
        end_schedule="2025-11-01T11:00:00",
    )
    schedule = ScheduleModel(**schedule.model_dump(), user_id=test_user.id)

    db_session.add(schedule)
    db_session.commit()
    schedule_id = schedule.schedule_id

    response = client.get(f"/schedules/{schedule_id}", headers=authorization_header)

    assert response.status_code == 200
    assert response.json()["title"] == "取得テスト"

def test_update_schedule(client, db_session: Session, test_user, authorization_header):
    """スケジュールの更新ができることを確認"""
    schedule = ScheduleCreate(
        title="更新前のタイトル",
        all_day=False,
        start_schedule="2025-11-01T10:00:00",
        end_schedule="2025-11-01T11:00:00",
    )

    schedule = ScheduleModel(**schedule.model_dump(), user_id=test_user.id)

    db_session.add(schedule)
    db_session.commit()
    schedule_id = schedule.schedule_id
    
    update_data = {"title": "更新後のタイトル"}

    response = client.put(f"/schedules/{schedule_id}", json=update_data, headers=authorization_header)

    assert response.status_code == 200
    assert response.json()["title"] == "更新後のタイトル"

def test_delete_schedule(client, db_session: Session, test_user, authorization_header):
    """スケジュールの削除ができることを確認"""
    schedule = ScheduleCreate(
        title="削除対象のミーティング",
        all_day=False,
        start_schedule="2025-11-01T10:00:00",
        end_schedule="2025-11-01T11:00:00",
    )

    schedule = ScheduleModel(**schedule.model_dump(), user_id=test_user.id)
    
    db_session.add(schedule)
    db_session.commit()
    schedule_id = schedule.schedule_id

    # Act: 削除リクエスト
    delete_response = client.delete(f"/schedules/{schedule_id}", headers=authorization_header)

    # Assert: 削除の成功を確認
    assert delete_response.status_code == 204

    # Act: 削除されたか再取得して確認
    get_response = client.get(f"/schedules/{schedule_id}", headers=authorization_header)

    # Assert: 見つからない(404)ことを確認
    assert get_response.status_code == 404