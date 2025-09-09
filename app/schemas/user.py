from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    name: str = Field(..., example="João Silva")
    registration: str = Field(..., example="20230001")
    course: Optional[str] = Field(None, example="Ciência da Computação")

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    registration: Optional[str] = None
    course: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass
