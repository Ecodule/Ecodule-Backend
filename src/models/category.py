import uuid
from sqlalchemy import Column, Integer, String, UUID
from sqlalchemy.orm import relationship
from db.session import Base # declarative_base()インスタンス

class Category(Base):
    __tablename__ = 'categories'

    # ER図のカラム定義に対応
    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name = Column("category_name", String, nullable=False, unique=True)

    # 1対多のリレーションシップを定義
    # CategoryからScheduleへの関連
    schedules = relationship("Schedule", back_populates="category")
    
    # CategoryからEcoActionへの関連
    eco_actions = relationship("EcoAction", back_populates="category")