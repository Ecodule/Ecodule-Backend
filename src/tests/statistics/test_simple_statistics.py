import uuid
from sqlalchemy.orm import Session

# 必要なモデルとスキーマをインポート
from models.user import User as UserModel
from models.user_statistics import UserStatistics
from models.overall_statistics import OverallStats as OverallStatsModel

def test_get_user_statistics_creates_if_not_exists(
    client, db_session: Session, test_user: UserModel, authorization_header: dict
):
    """
    正常系: ユーザー統計が存在しない場合、GETでアクセスすると自動で作成され、
    デフォルト値が返されることを確認
    """
    user_id = test_user.id

    # Act: 統計が存在しない状態でAPIを呼び出す
    response = client.get(f"/{user_id}/simple_statistics", headers=authorization_header)

    # Assert: 検証
    assert response.status_code == 200
    data = response.json()
    assert data["total_money_saved"] == 0.0
    assert data["total_co2_reduction"] == 0.0

    # DBにレコードが作成されたことを直接確認
    stats_in_db = db_session.query(UserStatistics).filter(UserStatistics.user_id == user_id).first()
    assert stats_in_db is not None
    assert stats_in_db.total_money_saved == 0.0


def test_post_achievement_updates_stats(
    client,
    db_session: Session,
    test_user: UserModel,
    seed_overall_statistics: OverallStatsModel,
    authorization_header: dict
):
    """
    正常系: POSTで数値を送ると、ユーザー統計と全体統計が正しく加算されることを確認
    """
    user_id = test_user.id
    # Arrange: まず初期状態の統計を作成（または取得）
    client.get(f"/{user_id}/simple_statistics", headers=authorization_header)

    # Act: 統計を更新するAPIを呼び出す
    response = client.post(
        f"/{user_id}/simple_statistics",
        # ★★★ 変更点: `params` から `json` に変更 ★★★
        json={"money_saved": 100.5, "co2_reduction": 1.25},
        headers=authorization_header,
    )

    # Assert: レスポンスが正しいか
    assert response.status_code == 200
    data = response.json()
    assert data["total_money_saved"] == 100.5
    assert data["total_co2_reduction"] == 1.25

    # Act: もう一度呼び出して、値が加算されることを確認
    response = client.post(
        f"/{user_id}/simple_statistics",
        # ★★★ 変更点: `params` から `json` に変更 ★★★
        json={"money_saved": 50.0, "co2_reduction": 0.5},
        headers=authorization_header,
    )

    # Assert: レスポンスが加算後の値になっているか
    assert response.status_code == 200
    data = response.json()
    assert data["total_money_saved"] == 150.5  # 100.5 + 50.0
    assert data["total_co2_reduction"] == 1.75  # 1.25 + 0.5

    # DBのユーザー統計が実際に更新されたことを直接確認
    user_stats_in_db = db_session.query(UserStatistics).filter(UserStatistics.user_id == user_id).first()
    assert user_stats_in_db.total_money_saved == 150.5

    # ★★★ 追加: 全体統計も更新されていることを確認 ★★★
    overall_stats_in_db = db_session.query(OverallStatsModel).first()
    assert overall_stats_in_db is not None
    assert overall_stats_in_db.total_money_saved == 5150.5
    assert overall_stats_in_db.total_co2_reduction == 76.75

def test_post_minus_achievement_updates_stats(
    client,
    db_session: Session,
    test_user: UserModel,
    seed_overall_statistics: OverallStatsModel,
    authorization_header: dict
):
    """
    正常系: POSTでマイナス数値を送ると、ユーザー統計と全体統計が正しく減算されることを確認
    """
    user_id = test_user.id
    # Arrange: まず初期状態の統計を作成（または取得）
    client.get(f"/{user_id}/simple_statistics", headers=authorization_header)

    # Act: 統計を更新するAPIを呼び出す
    response = client.post(
        f"/{user_id}/simple_statistics",
        # ★★★ 変更点: `params` から `json` に変更 ★★★
        json={"money_saved": 100.5, "co2_reduction": 1.25},
        headers=authorization_header,
    )

    # Assert: レスポンスが正しいか
    assert response.status_code == 200
    data = response.json()
    assert data["total_money_saved"] == 100.5
    assert data["total_co2_reduction"] == 1.25

    # Act: もう一度呼び出して、値が加算されることを確認
    response = client.post(
        f"/{user_id}/simple_statistics",
        # ★★★ 変更点: `params` から `json` に変更 ★★★
        json={"money_saved": -50.0, "co2_reduction": -0.5},
        headers=authorization_header,
    )

    # Assert: レスポンスが加算後の値になっているか
    assert response.status_code == 200
    data = response.json()
    assert data["total_money_saved"] == 50.5  # 100.5 - 50.0
    assert data["total_co2_reduction"] == 0.75  # 1.25 - 0.5

    # DBのユーザー統計が実際に更新されたことを直接確認
    user_stats_in_db = db_session.query(UserStatistics).filter(UserStatistics.user_id == user_id).first()
    assert user_stats_in_db.total_money_saved == 50.5

    # ★★★ 追加: 全体統計も更新されていることを確認 ★★★
    overall_stats_in_db = db_session.query(OverallStatsModel).first()
    assert overall_stats_in_db is not None
    assert overall_stats_in_db.total_money_saved == 5050.5
    assert overall_stats_in_db.total_co2_reduction == 75.75


def test_get_overall_statistics(
    client,
    db_session: Session,
    seed_overall_statistics: OverallStatsModel,
    authorization_header: dict
):
    """
    正常系: 全体統計が正しく取得できることを確認
    """
    # Act: 全体統計APIを呼び出す
    response = client.get("/overall_statistics", headers=authorization_header)

    # Assert: レスポンスが正しいか
    assert response.status_code == 200
    data = response.json()
    assert data["total_money_saved"] == seed_overall_statistics.total_money_saved
    assert data["total_co2_reduction"] == seed_overall_statistics.total_co2_reduction

