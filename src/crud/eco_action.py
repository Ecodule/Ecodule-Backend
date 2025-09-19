from sqlalchemy.orm import Session
import uuid
from models.eco_action import EcoAction # あなたのEcoActionモデルをインポート

def get_eco_actions_by_category(db: Session, category_id: uuid.UUID) -> list[EcoAction]:
    """
    指定されたcategory_idに属する全てのEcoActionレコードを取得します。
    """
    return db.query(EcoAction).filter(EcoAction.category_id == category_id).all()