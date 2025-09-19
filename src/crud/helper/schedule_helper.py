from sqlalchemy.orm import Session

from models.schedule import Schedule as ScheduleModel
from models.eco_action_achievement import EcoActionAchievement as AchievementModel
from models.category import Category  # 遅延インポートで循環参照を回避
from models.eco_action import EcoAction

from schemas.eco_action_achievement import AchievementCreate, AchievementDelete

from crud.eco_action import get_eco_actions_by_category
from crud.eco_action_achievement import create_achievement, delete_achievement
def is_category_valid(db: Session, category_id) -> bool:
    """
    指定されたカテゴリIDが有効かどうかを確認する。
    有効な場合はTrue、無効な場合はFalseを返す。
    """
    
    category = db.query(Category).filter(Category.category_id == category_id).first()
    return category is not None

def create_achievements_for_schedule(db: Session, schedule: ScheduleModel) -> None:
    """
    指定されたスケジュールにカテゴリが設定されていれば、
    関連する全てのエコ活動の達成記録を作成する。
    """
    # スケジュールにカテゴリがなければ何もしない
    if not schedule.category_id:
        return
    
    # カテゴリが有効か確認
    if is_category_valid(db, schedule.category_id) is False:
        return  

    # カテゴリに紐づくエコ活動を取得
    eco_actions = get_eco_actions_by_category(db, schedule.category_id)

    # もし、エコ活動が存在しない場合、何もしない
    if not eco_actions:
        return 

    # 各エコ活動に対応する達成記録を作成
    for eco_action in eco_actions:
        create_achievement(
            db=db,
            achievement=AchievementCreate(
                schedule_id=schedule.schedule_id,
                eco_action_id=eco_action.eco_action_id
            )
        )

def update_achievements_by_update_schedule(db: Session, schedule: ScheduleModel) -> None:
    """
    スケジュールの変更またはエコ活動の変更に伴い、達成記録を更新する。
    ①古いカテゴリに基づく達成記録を削除し、新しいカテゴリに基づく達成記録を作成する。元の状態を維持する。
    ②エコ活動の削除、追加に伴う達成記録の削除、追加を行う。元の状態を維持する。
    """
    # スケジュールにカテゴリがなければ何もしない
    if not schedule.category_id:
        return
    
    # カテゴリが有効か確認
    if is_category_valid(db, schedule.category_id) is False:
        return  

    # 既存の達成記録を取得
    previous_achievements = db.query(AchievementModel).filter(
        AchievementModel.schedule_id == schedule.schedule_id
    ).all()
    
    # 既存のエコ活動を取得
    # Noneは除外
    previous_eco_actions: list[EcoAction] = [
        achievement.eco_action for achievement in previous_achievements if achievement.eco_action is not None
    ]

    # カテゴリに紐づくエコ活動を取得
    eco_actions: list[EcoAction] = get_eco_actions_by_category(db, schedule.category_id)

    # もし、エコ活動が存在しない場合、終了
    if not (previous_eco_actions or eco_actions):
        return

    # 既存のエコ活動と新しいエコ活動を比較して削除と追加を決定
    for eco_action in eco_actions:
        if eco_action not in previous_eco_actions:
            print(f"Adding new eco action: {eco_action}")
            # 新しいエコ活動に対する達成記録を作成
            create_achievement(
                db=db,
                achievement=AchievementCreate(
                    schedule_id=schedule.schedule_id,
                    eco_action_id=eco_action.eco_action_id
                )
            )

    for previous_eco_action in previous_eco_actions:
        if previous_eco_action not in eco_actions:
            # 削除されたエコ活動に対する達成記録を削除
            print(f"Removing old eco action: {previous_eco_action}")
            delete_achievement(
                db=db,
                achievement=AchievementDelete(
                    schedule_id=schedule.schedule_id,
                    eco_action_id=previous_eco_action.eco_action_id
                )
            )