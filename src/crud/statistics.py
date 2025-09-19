from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

# 必要なモデルをインポート
from models.user import User as UserModel
from models.schedule import Schedule as ScheduleModel
from models.eco_action_achievement import EcoActionAchievement as EcoActionAchievementModel
from models.eco_action import EcoAction as EcoActionModel

def get_user_statistics(db: Session, user_id: uuid.UUID):
    """
    指定されたユーザーの節約金額とCO2削減量を集計する
    """
    stats = (
        db.query(
            func.sum(EcoActionModel.money_saved).label("total_money_saved"),
            func.sum(EcoActionModel.co2_reduction).label("total_co2_reduction")
        )
        .join(EcoActionAchievementModel, EcoActionModel.eco_action_id == EcoActionAchievementModel.eco_action_id)
        .join(ScheduleModel, EcoActionAchievementModel.schedule_id == ScheduleModel.schedule_id)
        .filter(
            ScheduleModel.user_id == user_id,
            EcoActionAchievementModel.is_completed == True
        )
        .one()
    )

    return {
        "total_money_saved": stats.total_money_saved or 0.0,
        "total_co2_reduction": stats.total_co2_reduction or 0.0,
    }