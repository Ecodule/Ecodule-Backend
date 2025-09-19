# models.py

import uuid
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from db.session import Base # declarative_base()インスタンス

class EcoActionAchievement(Base):
    __tablename__ = 'eco_action_achievements'

    # ER図のカラム定義に対応
    achievement_id = Column("achievement_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achieved_at = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=True)

    # 外部キー制約
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('schedules.schedule_id'))
    eco_action_id = Column(UUID(as_uuid=True), ForeignKey('eco_actions.eco_action_id'))
    
    # 多対1のリレーションシップ
    schedule = relationship("Schedule", back_populates="eco_action_achievements")
    eco_action = relationship("EcoAction", back_populates="eco_action_achievements")

    def __str__(self):
        # ドロップダウンに表示したいカラムを返す
        return f"Achievement {self.achievement_id} - eco_action: {self.eco_action.content}"