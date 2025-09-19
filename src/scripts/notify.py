from fastapi import Depends
from sqlalchemy.orm import Session

from models.schedule import Schedule as ScheduleModel

from crud.helper.schedule_helper import update_achievements_by_update_schedule
from db.session import get_db

def notify_frontend_update(target_eco_action, action_type: str, db: Session):
    """
    フロントエンドに更新があったことを通知する（という想定の）スクリプト
    """
    print("--- 📢 Script Execution Triggered! ---")
    print(f"Action Type: {action_type}")
    print(f"EcoAction Content: {target_eco_action.content}")
    print("Notifying frontend to refresh master data...")
    print("------------------------------------")

    all_schedules = db.query(ScheduleModel).all()
    for schedule in all_schedules:
        update_achievements_by_update_schedule(db, schedule)
      
    print("All related achievements have been updated based on the latest EcoAction changes.")
    
