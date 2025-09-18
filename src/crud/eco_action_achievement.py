from sqlalchemy.orm import Session
import uuid
from models.eco_action_achievement import EcoActionAchievement
from schemas.eco_action_achievement import AchievementCreate

def create_achievement(db: Session, achievement: AchievementCreate):
    """新しい達成記録を作成 (is_completed=True)"""
    
    db_achievement = EcoActionAchievement(
        **achievement.model_dump(),
        is_completed=False,
        eco_action_id=achievement.eco_action_id,
        schedule_id=achievement.schedule_id
    )
    
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement

def get_achievement_by_id(db: Session, achievement_id: uuid.UUID) -> EcoActionAchievement | None:
    """IDで達成記録を検索"""
    return db.query(EcoActionAchievement).filter(EcoActionAchievement.id == achievement_id).first()

def set_completed_status(db: Session, db_achievement: EcoActionAchievement, status: bool):
    """達成記録のis_completedステータスを更新"""
    db_achievement.is_completed = status
    db.commit()
    db.refresh(db_achievement)
    return db_achievement