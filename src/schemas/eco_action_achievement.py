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

    achievement_id: uuid.UUID
    achieved_at: datetime
    is_completed: bool

class AchievementStatusUpdate(AchievementBase):
    model_config = ConfigDict(from_attributes=True)
    
    is_completed: bool # 更新後の状態をクライアントから受け取る