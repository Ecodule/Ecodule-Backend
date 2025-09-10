import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

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
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID