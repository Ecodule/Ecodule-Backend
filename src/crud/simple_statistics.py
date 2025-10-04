from sqlalchemy.orm import Session
import uuid

# 必要なモデルをインポート
from models.user import User as UserModel
from models.user_statistics import UserStatistics as UserStatisticsModel
from models.overall_statistics import OverallStats as OverallStatisticsModel

"""
READ
"""
def read_user_statistics(db: Session, user_id: uuid.UUID):
    """
    指定されたユーザーのスケジュール数を集計する
    """
    user_statistics = (
        db.query(UserStatisticsModel)
        .filter(UserStatisticsModel.user_id == user_id)
        .first()
    )

    if (not user_statistics):
        return None
    
    return user_statistics

def read_overall_statistics(db: Session):
    """
    全ユーザーの統計情報を集計する
    """
    overall_statistics = db.query(OverallStatisticsModel).first()

    if (not overall_statistics):
        return None
    
    return overall_statistics

"""
CREATE
"""
# ユーザーの統計情報がまだない場合に統計を作成する関数
# APIエンドポイント関数で上記条件分岐を行う
def create_user_statistics(db: Session, user_id: uuid.UUID):
    """
    ユーザーが統計情報を作成する
    """
    new_statistics = UserStatisticsModel(
        user_id=user_id,
        total_money_saved=0.0,
        total_co2_reduction=0.0
    )

    db.add(new_statistics)
    db.commit()
    db.refresh(new_statistics)

    return new_statistics

"""
UPDATE
"""
def update_user_statistics(db: Session, user_id: uuid.UUID, money_saved: float, co2_reduction: float):
    """
    ユーザーの統計情報を更新する
    """
    user_statistics = (
        db.query(UserStatisticsModel)
        .filter(UserStatisticsModel.user_id == user_id)
        .first()
    )

    if not user_statistics:
        return None

    user_statistics.total_money_saved += money_saved
    user_statistics.total_co2_reduction += co2_reduction

    db.commit()
    db.refresh(user_statistics)

    return user_statistics

def update_overall_statistics(db: Session, money_saved: float, co2_reduction: float):
    """
    全ユーザーの統計情報を更新する
    """
    overall_statistics = db.query(UserStatisticsModel).first()

    if not overall_statistics:
        return None

    overall_statistics.total_money_saved += money_saved
    overall_statistics.total_co2_reduction += co2_reduction

    db.commit()
    db.refresh(overall_statistics)

    return overall_statistics

