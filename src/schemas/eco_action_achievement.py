from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid

# ベーススキーマ
class AchievementBase(BaseModel):
    schedule_id: uuid.UUID
    eco_action_id: uuid.UUID

# 作成用スキーマ
class AchievementCreate(AchievementBase):
    pass

# レスポンス用スキーマ
class AchievementResponse(AchievementBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    achieved_at: datetime
    is_completed: bool