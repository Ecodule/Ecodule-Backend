import uuid
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UUID, CheckConstraint
from sqlalchemy.orm import relationship

from models.category import Category # noqa: F401
from models.user import User # noqa: F401

from db.session import Base

class Schedule(Base):
    __tablename__ = 'schedules'

    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    all_day = Column(Boolean, default=False, nullable=False) # 終日かどうか
    start_schedule = Column(DateTime, nullable=False)
    end_schedule = Column(DateTime, nullable=False)
    description = Column(String, nullable=True) # 説明は空でも良い場合

    # 外部キー制約
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.category_id'), nullable=True)
    
    # ScheduleからUserとCategoryへの多対1の関係を定義
    owner = relationship("User", back_populates="schedules")
    category = relationship("Category", back_populates="schedules")
    eco_action_achievements = relationship("EcoActionAchievement", back_populates="schedule")

    def __str__(self):
        # ドロップダウンに表示したいカラムを返す
        return self.title