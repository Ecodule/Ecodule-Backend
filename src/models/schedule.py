import uuid
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UUID, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from models.user import User # noqa
# 以前作成した db/session.py からBaseをインポート
from db.session import Base

class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="schedule_id")
    title = Column(String)
    all_day = Column(Boolean, default=False)
    start_schedule = Column(DateTime, nullable=True)
    end_schedule = Column(DateTime, nullable=True)
    description = Column(String, nullable=True) # 説明は空でも良い場合

    # all_dayかstart & endどちらかが保存されている必要がある
    __table_args__ = (
        CheckConstraint(
            'all_day IS NOT NULL OR (start_schedule IS NOT NULL AND end_schedule IS NOT NULL)',
            name="ck_schedule_time_constraint"
        ),
    )

    # 外部キー制約
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    # category_id = Column(UUID(as_uuid=True), ForeignKey('categories.category_id'), nullable=True)
    
    # EventからUserとCategoryへの多対1の関係を定義
    owner = relationship("User", back_populates="schedules")
    # category = relationship("Category", back_populates="schedules")