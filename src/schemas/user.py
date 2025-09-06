from __future__ import annotations

import string
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

# Token
class TokenResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  
  id: uuid.UUID
  is_active: bool
  access_token: str
  expires_in: int
  refresh_token: str
  token_type: str = "bearer"

# user
class UserCreate(BaseModel):
  email: EmailStr
  password: str
  
  @field_validator('password')
  @classmethod
  def validate_password(cls, v: str) -> str:
    # 条件1: 8文字以上
    if len(v) < 8:
      raise ValueError("パスワードは8文字以上である必要があります。")
    
    # 条件2: 英字、数字、記号のうち2種類以上を含む
    char_types = {
      "has_letter": any(c.isalpha() for c in v),
      "has_digit": any(c.isdigit() for c in v),
      "has_symbol": any(c in string.punctuation for c in v)
    }
    
    # 含まれている文字タイプの数をカウント
    if sum(char_types.values()) < 2:
      raise ValueError('パスワードには英字、数字、記号のうち2種類以上を含める必要があります')
  
    return v

# User response model
class UserResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  
  id: uuid.UUID
  email: EmailStr
  is_active: bool
  credential: UserCredentialResponse

class UserCredentialResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  
  id: uuid.UUID
  user_id: uuid.UUID
  hashed_password: str | None = None
  google_id: str | None = None
  