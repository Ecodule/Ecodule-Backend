# models.py

from sqlalchemy import Column, Float, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
import uuid
from db.session import Base # declarative_base()インスタンス

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
    
    # # 1対多のリレーションシップ (EcoAction -> EcoActionAchievement)
    # achievements = relationship("EcoActionAchievement", back_populates="eco_action")