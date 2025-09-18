from sqlalchemy.orm import Session
from models.schedule import Schedule as ScheduleModel
from schemas.eco_action_achievement import AchievementCreate
from crud.eco_action import get_eco_actions_by_category
from crud.eco_action_achievement import create_achievement # 修正版のcreate_achievement

def create_achievements_for_schedule(db: Session, schedule: ScheduleModel) -> None:
    """
    指定されたスケジュールにカテゴリが設定されていれば、
    関連する全てのエコ活動の達成記録を作成する。
    """
    # スケジュールにカテゴリがなければ何もしない
    if not schedule.category_id:
        return

    # カテゴリに紐づくエコ活動を取得
    eco_actions = get_eco_actions_by_category(db, schedule.category_id)

    # 各エコ活動に対応する達成記録を作成
    for eco_action in eco_actions:
        create_achievement(
            db=db,
            achievement=AchievementCreate(
                schedule_id=schedule.id,
                eco_action_id=eco_action.id
            )
        )