import uuid
from datetime import datetime
from pydantic import BaseModel, Field

# --- Schedule Schemas ---
class ScheduleBase(BaseModel):
    title: str
    all_day: bool = False
    start_schedule: datetime | None = None
    end_schedule: datetime | None = None
    description: str | None = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    # 更新時は全てのフィールドがオプショナル
    title: str | None = None
    all_day: bool | None = None
    start_schedule: datetime | None = None
    end_schedule: datetime | None = None
    description: str | None = None                                                                                                                  


class ScheduleResponse(ScheduleBase):
    id: uuid.UUID

    # ORMモデルのインスタンスからPydanticモデルを生成できるようにする設定
    class Config:
        from_attributes = True