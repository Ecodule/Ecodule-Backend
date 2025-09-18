from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

# 必要なモジュールをインポート
from db.session import get_db
from schemas.eco_action_achievement import AchievementCreate, AchievementResponse
from crud.eco_action_achievement import create_achievement, get_achievement_by_id, set_completed_status
from core.auth import get_current_user
from models.schedule import Schedule
from models.user import User as UserModel

router = APIRouter(
    prefix="/achievements",
    tags=["Eco Action Achievements"]
)

@router.post("/", response_model=AchievementResponse)
def create_new_achievement(
    achievement_in: AchievementCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    エコ活動を達成した記録を作成します (is_completed = True)
    """
    # スケジュールが存在し、かつログインユーザーのものであるかを確認
    schedule = db.query(Schedule).filter(Schedule.id == achievement_in.schedule_id).first()
    if not schedule or schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this schedule")
        
    return create_achievement(db=db, achievement=achievement_in)


@router.patch("/{achievement_id}/incomplete", response_model=AchievementResponse)
def mark_achievement_as_incomplete(
    achievement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    指定された達成記録を取り消します (is_completed = False)
    """
    db_achievement = get_achievement_by_id(db, achievement_id=achievement_id)
    
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    # 達成記録がログインユーザーのものであるかを、スケジュール経由で確認
    if db_achievement.schedule.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return set_completed_status(db=db, db_achievement=db_achievement, status=False)