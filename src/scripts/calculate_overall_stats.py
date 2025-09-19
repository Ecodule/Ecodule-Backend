from sqlalchemy.orm import Session
from sqlalchemy import func

from db.session import SessionLocal
from models.eco_action import EcoAction as EcoActionModel
from models.eco_action_achievement import EcoActionAchievement as EcoActionAchievementModel
from models.overall_statistics import OverallStats

def calculate_and_save_overall_stats(db: Session):
    print("Calculating overall statistics...")
    
    # 全ユーザーの統計情報を集計
    stats = (
        db.query(
            func.sum(EcoActionModel.money_saved).label("total_money_saved"),
            func.sum(EcoActionModel.co2_reduction).label("total_co2_reduction")
        )
        .join(EcoActionAchievementModel, EcoActionModel.eco_action_id == EcoActionAchievementModel.eco_action_id)
        .filter(EcoActionAchievementModel.is_completed == True)
        .one()
    )

    # 新しい統計レコードを作成して保存
    new_stats_record = OverallStats(
        total_money_saved=stats.total_money_saved or 0.0,
        total_co2_reduction=stats.total_co2_reduction or 0.0,
    )
    db.add(new_stats_record)
    db.commit()
    print("Successfully saved new overall statistics.")

if __name__ == "__main__":
    db = SessionLocal()
    calculate_and_save_overall_stats(db)
    db.close()