import uuid
from sqlalchemy.orm import Session

from models.schedule import Schedule as ScheduleModel

from crud.eco_action_achievement import create_achievement
from crud.eco_action import get_eco_actions_by_category
from crud.helper.schedule_helper import create_achievements_for_schedule

from schemas.eco_action_achievement import AchievementCreate
from schemas.schedule import ScheduleCreate, ScheduleUpdate

def get_schedule(db: Session, schedule_id: uuid.UUID):
    return db.query(ScheduleModel).filter(ScheduleModel.schedule_id == schedule_id).first()

def get_schedules_by_user(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100):
        return db.query(ScheduleModel).filter(ScheduleModel.user_id == user_id).offset(skip).limit(limit).all()

def create_schedule(db: Session, schedule: ScheduleCreate, user_id: uuid.UUID):
    db_schedule = ScheduleModel(**schedule.model_dump(), user_id=user_id) # 辞書型で展開

    create_achievements_for_schedule(db, db_schedule)  # スケジュールに基づいて達成記録を作成

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_schedule(db: Session, schedule_id: uuid.UUID, schedule_update: ScheduleUpdate):
    db_schedule = get_schedule(db, schedule_id)

    if not db_schedule:
        return None
    
    create_achievements_for_schedule(db, db_schedule)  # スケジュールに基づいて達成記録を作成
    
    # exclude_unset=Trueで、リクエストに含まれるフィールドのみを更新対象にする
    update_data = schedule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
        
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: uuid.UUID):
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        return None
    db.delete(db_schedule)
    db.commit()
    return db_schedule