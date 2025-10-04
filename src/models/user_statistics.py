import uuid
from sqlalchemy import UUID, Column, Float
from db.session import Base

from sqlalchemy.orm import relationship

class UserStatistics(Base):
    __tablename__ = 'user_statistics'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_money_saved = Column(Float)
    total_co2_reduction = Column(Float)

    user_id = Column(UUID(as_uuid=True), nullable=True)

    user = relationship("User", back_populates="statistics")