from sqlalchemy.orm import Session
import uuid
from models.eco_action_achievement import EcoActionAchievement
from schemas.eco_action_achievement import AchievementCreate, AchievementDelete

def create_achievement(db: Session, achievement: AchievementCreate):
    """新しい達成記録を作成 (is_completed=True)"""
    
    db_achievement = EcoActionAchievement(
        **achievement.model_dump(),
        is_completed=False, # 初期状態は未達成(False)
    )
    
    db.add(db_achievement)
    return db_achievement

def get_achievement_by_schedule_and_action(db: Session, schedule_id: uuid.UUID, eco_action_id: uuid.UUID):
    """スケジュールIDとエコ活動IDで達成記録を検索"""
    return db.query(EcoActionAchievement).filter(
        EcoActionAchievement.schedule_id == schedule_id,
        EcoActionAchievement.eco_action_id == eco_action_id
    ).first()

def set_completed_status(db: Session, db_achievement: EcoActionAchievement, status: bool):
    """達成記録のis_completedステータスを更新"""
    db_achievement.is_completed = status
    db.commit()
    db.refresh(db_achievement)
    return db_achievement

def get_achievements_by_schedule(db: Session, schedule_id: uuid.UUID):
    """
    指定されたschedule_idに紐づく全ての達成記録を取得します。
    """
    return db.query(EcoActionAchievement).filter(
        EcoActionAchievement.schedule_id == schedule_id
    ).all()

def delete_achievement(db: Session, db_achievement: AchievementDelete):
    """指定された達成記録を削除"""
    db_achievement = get_achievement_by_schedule_and_action(db, db_achievement.schedule_id, db_achievement.eco_action_id)

    # もし達成記録が存在すれば削除
    if db_achievement:
        db.delete(db_achievement)
        db.commit()
    
    return None