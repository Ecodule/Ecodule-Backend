import uuid
from sqlalchemy import UUID, Column, Float, DateTime
from sqlalchemy.sql import func
from db.session import Base

class OverallStats(Base):
    __tablename__ = 'overall_stats'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_money_saved = Column(Float)
    total_co2_reduction = Column(Float)
    calculated_at = Column(DateTime, default=func.now())