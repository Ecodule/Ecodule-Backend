import uuid
from pydantic import BaseModel, EmailStr

# Token
class Token(BaseModel):
  access_token: str
  token_type: str

# user
class UserCreate(BaseModel):
  email: EmailStr
  password: str
  
# User response model
class UserResponse(BaseModel):
  id: uuid.UUID
  email: EmailStr
  is_active: bool

  class Config:
    # config to convert SQLAlchemy models into Pydantic models
    from_attributes = True