# models.py

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base # declarative_base()インスタンス

class EcoActionAchievement(Base):
    __tablename__ = 'eco_action_achievements'

    # ER図のカラム定義に対応
    id = Column("achievement_id", Integer, primary_key=True)
    achieved_at = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=True)

    # 外部キー制約
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('schedules.schedule_id'))
    eco_action_id = Column(UUID(as_uuid=True), ForeignKey('eco_actions.eco_action_id'))
    
    # 多対1のリレーションシップ
    schedule = relationship("Schedule", back_populates="eco_action_achievements")
    eco_action = relationship("EcoAction", back_populates="eco_action_achievements")