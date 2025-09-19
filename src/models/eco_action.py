# models.py

from sqlalchemy import Column, Float, String, ForeignKey, UUID, event
from sqlalchemy.orm import relationship
import uuid

from models.eco_action_achievement import EcoActionAchievement # noqa: F401

from db.session import Base
from scripts.notify import notify_frontend_update # declarative_base()インスタンス

class EcoAction(Base):
    __tablename__ = 'eco_actions'

    # ER図のカラム定義に対応
    eco_action_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String, nullable=False)
    money_saved = Column(Float)
    co2_reduction = Column(Float) # 単位はkg-CO2

    # 外部キー制約
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.category_id'))
    
    # 多対1のリレーションシップ (EcoAction -> Category)
    category = relationship("Category", back_populates="eco_actions")
    
    # 1対多のリレーションシップ (EcoAction -> EcoActionAchievement)
    eco_action_achievements = relationship("EcoActionAchievement", back_populates="eco_action")

    def __str__(self):
        # ドロップダウンに表示したいカラムを返す
        return self.content
    
# 1. EcoActionが新規作成された「後」に実行されるリスナー
@event.listens_for(EcoAction, 'after_insert')
def after_eco_action_insert(mapper, connection, target):
    """Called after an EcoAction is inserted."""
    # target引数に、作成されたEcoActionオブジェクトが入っている
    notify_frontend_update(target, action_type="INSERT")


# 2. EcoActionが更新された「後」に実行されるリスナー
@event.listens_for(EcoAction, 'after_update')
def after_eco_action_update(mapper, connection, target):
    """Called after an EcoAction is updated."""
    # target引数に、更新されたEcoActionオブジェクトが入っている
    notify_frontend_update(target, action_type="UPDATE")