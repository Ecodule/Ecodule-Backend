# schemas/eco_action.py

import uuid
from pydantic import BaseModel, ConfigDict

# ベーススキーマ：作成と読み取りで共通のフィールドを定義
class EcoActionBase(BaseModel):
    content: str
    money_saved: float | None = None
    co2_reduction: float | None = None
    category_id: uuid.UUID

# 読み取り・レスポンス用スキーマ：APIからEcoActionの情報を返す際の形式
class EcoActionResponse(EcoActionBase):
    model_config = ConfigDict(from_attributes=True)
    eco_action_id: uuid.UUID