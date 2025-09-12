import uuid
from pydantic import BaseModel, ConfigDict

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    category_name: str