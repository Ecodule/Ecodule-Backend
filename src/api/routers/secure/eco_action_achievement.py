from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

# 必要なモジュールをインポート
from db.session import get_db
from schemas.eco_action_achievement import AchievementStatusUpdate, AchievementResponse
from crud.eco_action_achievement import get_achievement_by_schedule_and_action, set_completed_status
from core.auth import get_current_user
from models.schedule import Schedule
from models.user import User as UserModel

router = APIRouter(
    tags=["Eco Action Achievements"]
)

@router.patch("/achievements/status")
def update_achievement_status(
    status_update: AchievementStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    指定されたスケジュールとエコ活動に対応する達成記録の完了状態を更新します。
    """
    # 1. スケジュールが存在し、かつログインユーザーのものであるかを確認
    current_schedule_id = status_update.schedule_id

    schedule = db.query(Schedule).filter(Schedule.schedule_id == current_schedule_id).first()
    if not schedule or schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this schedule")

    # 2. 対応する達成記録をDBから取得
    db_achievement = get_achievement_by_schedule_and_action(
        db,
        schedule_id=status_update.schedule_id,
        eco_action_id=status_update.eco_action_id
    )
    
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Achievement not found for the given schedule and eco action")

    # 3. 取得した達成記録のステータスを更新
    return set_completed_status(
        db=db, 
        db_achievement=db_achievement, 
        status=status_update.is_completed
    )
