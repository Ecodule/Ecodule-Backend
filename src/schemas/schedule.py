import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from schemas.category import CategoryResponse
from schemas.eco_action_achievement import AchievementResponse

# --- Schedule Schemas ---
class ScheduleBase(BaseModel):
    title: str
    all_day: bool = False
    start_schedule: datetime | None = None
    end_schedule: datetime | None = None
    description: str | None = None
    category_id: uuid.UUID | None = Field(default=None, description="カテゴリIDです。指定しない場合はNoneになります。")

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    # 更新時は全てのフィールドがオプショナル
    title: str | None = None
    all_day: bool | None = None
    start_schedule: datetime | None = None
    end_schedule: datetime | None = None
    description: str | None = None
    category_id: uuid.UUID | None = Field(default=None, description="カテゴリIDです。指定しない場合はNoneになります。")                                   

class ScheduleResponse(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    schedule_id: uuid.UUID
    category: CategoryResponse | None = None
    eco_action_achievements: list[AchievementResponse] = []
    